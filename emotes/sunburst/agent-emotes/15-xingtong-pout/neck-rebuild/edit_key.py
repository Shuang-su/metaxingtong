"""Run one explicitly prepared image edit; cache successes and never retry automatically."""
from pathlib import Path
from contextlib import ExitStack
import argparse, base64, hashlib, io, json, os
from datetime import datetime, timezone
from PIL import Image

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    job = json.loads(args.manifest.read_text())
    inputs = [HERE / p for p in job['images']]
    mask = HERE / job['mask']
    prompt = HERE / job['prompt']
    out = HERE / job['output']
    receipt_path = out.with_suffix('.receipt.json')
    for p in inputs + [mask]:
        with Image.open(p) as im:
            im.load()
            assert im.format == 'PNG' and im.size == (1024, 1024), str(p)
    with Image.open(mask) as im:
        assert im.mode == 'RGBA' and im.getchannel('A').getextrema() == (0, 255)
    assert prompt.is_file()
    if args.check:
        print(json.dumps({'inputs_valid': True, 'job': job['name'], 'key_present': bool(os.getenv('OPENAI_API_KEY'))}))
        return
    if out.exists() or receipt_path.exists():
        raise SystemExit('Existing output/receipt preserved. Choose a new revision for another request.')
    if not os.getenv('OPENAI_API_KEY'):
        raise SystemExit('OPENAI_API_KEY is missing; no request sent.')
    from openai import OpenAI, APIStatusError, APIConnectionError
    client = OpenAI(base_url='https://api.openai.com/v1', max_retries=0, timeout=180.0)
    receipt = {'job': job['name'], 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
               'endpoint': 'https://api.openai.com/v1/images/edits', 'model': 'gpt-image-2.6-sunburst',
               'size': [1024, 1024], 'quality': 'medium', 'n': 1, 'automatic_retries': 0,
               'inputs': {str(p.relative_to(HERE)): sha(p) for p in inputs + [mask, prompt]}}
    try:
        with ExitStack() as stack:
            reply = client.images.edit(model=receipt['model'],
                image=[stack.enter_context(p.open('rb')) for p in inputs],
                mask=stack.enter_context(mask.open('rb')), prompt=prompt.read_text(),
                size='1024x1024', quality='medium', output_format='png', n=1)
    except APIStatusError as exc:
        receipt.update(status='failed', http_status=exc.status_code, request_id=exc.request_id)
        if isinstance(exc.body, dict):
            err = exc.body.get('error', exc.body)
            if isinstance(err, dict):
                receipt['error_type'] = err.get('type')
                receipt['error_code'] = err.get('code')
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps(receipt)); raise SystemExit(3)
    except APIConnectionError as exc:
        receipt.update(status='failed', error_type=type(exc).__name__)
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps(receipt)); raise SystemExit(4)
    encoded = reply.data[0].b64_json
    if not encoded:
        raise RuntimeError('No PNG bytes returned')
    raw = base64.b64decode(encoded, validate=True)
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        assert im.format == 'PNG' and im.size == (1024, 1024)
    out.write_bytes(raw)
    receipt.update(status='completed', request_id=reply._request_id, output=str(out.relative_to(HERE)), output_sha256=sha(out))
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
