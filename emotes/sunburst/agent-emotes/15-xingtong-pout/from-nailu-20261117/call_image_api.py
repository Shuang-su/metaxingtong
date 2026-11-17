"""One cached Images API production request; no automatic retries or secret logging."""
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
import argparse, base64, hashlib, io, json, os
from PIL import Image

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('job', type=Path); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    job_path = HERE / args.job; job = json.loads(job_path.read_text())
    inputs = [HERE / name for name in job['images']]; prompt = HERE / job['prompt']
    output = HERE / job['output']; receipt_path = output.with_suffix('.receipt.json')
    for path in inputs:
        with Image.open(path) as im:
            im.load(); assert im.format == 'PNG'
    assert prompt.is_file()
    if args.check:
        print(json.dumps({'job': job['name'], 'inputs_valid': True, 'key_present': bool(os.getenv('OPENAI_API_KEY'))})); return
    if output.exists() or receipt_path.exists():
        raise SystemExit('Existing production output/receipt preserved. Use another revision for a new request.')
    if not os.getenv('OPENAI_API_KEY'):
        raise SystemExit('Current runtime is missing OPENAI_API_KEY. No request sent.')
    from openai import OpenAI, APIConnectionError, APIStatusError
    client = OpenAI(base_url='https://api.openai.com/v1', max_retries=0, timeout=240.)
    receipt = {'job': job['name'], 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
               'endpoint': 'https://api.openai.com/v1/images/edits', 'model': 'gpt-image-2.6-sunburst',
               'parameters': job['parameters'], 'automatic_retries': 0,
               'inputs': {str(p.relative_to(HERE)): sha(p) for p in inputs + [prompt]}}
    try:
        with ExitStack() as stack:
            reply = client.images.edit(model=receipt['model'], image=[stack.enter_context(p.open('rb')) for p in inputs],
                prompt=prompt.read_text(), **job['parameters'])
    except APIStatusError as exc:
        receipt.update(status='failed', http_status=exc.status_code, request_id=exc.request_id)
        if isinstance(exc.body, dict):
            err = exc.body.get('error', exc.body)
            if isinstance(err, dict):
                receipt.update(error_type=err.get('type'), error_code=err.get('code'))
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n'); print(json.dumps(receipt)); raise SystemExit(3)
    except APIConnectionError as exc:
        receipt.update(status='failed', error_type=type(exc).__name__)
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n'); print(json.dumps(receipt)); raise SystemExit(4)
    encoded = reply.data[0].b64_json
    if not encoded:
        raise RuntimeError('Images API returned no image bytes')
    raw = base64.b64decode(encoded, validate=True)
    output.parent.mkdir(parents=True, exist_ok=True); output.write_bytes(raw)
    with Image.open(io.BytesIO(raw)) as im:
        im.load(); actual = {'format': im.format, 'size': list(im.size), 'frames': getattr(im, 'n_frames', 1)}
        if im.format == 'GIF':
            durations = []
            for i in range(im.n_frames):
                im.seek(i); durations.append(im.info.get('duration'))
            actual.update(durations_ms=durations, loop=im.info.get('loop'))
    receipt.update(status='completed', request_id=reply._request_id, output=str(output.relative_to(HERE)), output_sha256=sha(output), actual=actual)
    if reply.usage is not None:
        receipt['usage'] = reply.usage.model_dump()
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
