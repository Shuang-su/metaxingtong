"""Local ordinary-file integrity and delivery-role manifests; no upload/publication claim."""
from pathlib import Path
import hashlib, json, mimetypes
from PIL import Image

R = Path(__file__).resolve().parents[1]
O = R / 'stages/r06-review-candidate'
def row(p):
    data = p.read_bytes()
    return {'path': str(p.relative_to(R)), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(),
            'git_blob': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()}
def write(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2))

roles = []
def image_role(p, role):
    x = row(p)
    with Image.open(p) as im:
        im.load()
        x['dimensions'] = list(im.size)
    x.update({'role': role, 'source_acceptance': 'NOT_PASSED',
              'Issue_display_visibility': 'pending parent publication and actual per-position viewport check'})
    roles.append(x)
for p in sorted((R / 'sources').rglob('*.png')):
    image_role(p, 'original native decoded source; all construction input, not holdout')
for directory, role in [
    ('source-renders', 'source-bound conditional camera render or native direct50 overlay; not calibrated'),
    ('checks', 'internal diagnostic angle, not a source view'),
    ('object-crops', 'native integer-coordinate local crop or direct50 crop, no new source angle'),
    ('preflight', 'R06 UV/material technical preflight'),
    ('qa/glb-render', 'actual native/GLB same-light-rig comparison'),
    ('delivery-previews', 'explicitly labeled derived delivery display')]:
    for p in sorted((O / directory).rglob('*.png')):
        image_role(p, role)
write(O / 'image-role-manifest.json', roles)

attachments = []
for p, role in [
    (O / 'source-renders/preview-front/material.png', 'original 1920x1080 candidate main render'),
    (O / 'delivery-previews/three-source-failed-overview-derived.png', 'derived source-failure overview'),
    (O / 'delivery-previews/eight-angle-material-derived.png', 'derived material diagnostic contact sheet'),
    (O / 'delivery-previews/review-brief-zh.md', 'repo-relative master of brief; publish absolute-link variant after remote commit is known')]:
    x = row(p);x.update({'role': role, 'mime_type': mimetypes.guess_type(p.name)[0]});attachments.append(x)
write(O / 'delivery-previews/user-attachment-manifest.json', {
    'recommended_chat_attachment_count': 4, 'items': attachments,
    'Space_preview_report_retention': 'permanent review artifacts, distinct from temporary model bundle',
    'publication_status': 'not published by builder; parent to bind actual private Git commit and replace relative links in Space report variant'})

stage_manifest = O / 'file-manifest.json'
write(stage_manifest, [row(p) for p in sorted(O.rglob('*')) if p.is_file() and p != stage_manifest])
full_manifest = R / 'evidence/final-file-manifest.json'
paths = [p for p in sorted(R.rglob('*')) if p.is_file() and '.git' not in p.relative_to(R).parts and p != full_manifest]
files = [row(p) for p in paths]
assert all(x['bytes'] < 100 * 1024 * 1024 for x in files), 'Stop: ordinary-file size checkpoint exceeded; do not use LFS/splitting'
assert not any(p.suffix in ('.safetensors', '.ckpt', '.pt') or 'venv' in p.parts for p in paths), 'Do not package model weights/venv'
write(full_manifest, {'scope': 'all local ordinary project files except this self-referential manifest and .git internals',
      'excluded': ['.git/**', 'evidence/final-file-manifest.json'], 'file_count': len(files),
      'total_bytes': sum(x['bytes'] for x in files), 'largest_file': max(files, key=lambda x: x['bytes']),
      'files': files, 'remote_verified': False,
      'size_check': 'every ordinary file below 100 MiB; final remote service limits and acceptance checked by parent normal Git route'})
print('MANIFESTS_READY', len(roles), 'images;', len(files), 'files;', sum(x['bytes'] for x in files), 'bytes')
