import bpy,json,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];T=R/'textures_r03';T.mkdir(exist_ok=True)
with zipfile.ZipFile(R.parent/'xingtong_train/upload/xingtong_train_review_textures.zip') as z:
 for n in z.namelist():
  if n.startswith('textures/') and n.endswith('.png'):(T/Path(n).name).write_bytes(z.read(n))
src=next(x for x in json.loads((R/'frozen_r03/freeze_manifest.json').read_text())['blends'] if x['kind']=='material');bpy.ops.wm.open_mainfile(filepath=src['file']);m=bpy.data.materials['Dark forest green leather | authored UV PBR'];images=[]
for n in m.node_tree.nodes:
 if n.type=='TEX_IMAGE' and n.image and 'roughness' in n.image.name.lower():
  im=n.image;im.filepath_raw=str(T/'forest_leather_roughness.png');im.file_format='PNG';im.save();images.append(im.name)
assert images, 'Actual r03 roughness image missing';assert hashlib.sha256(Path(src['file']).read_bytes()).hexdigest()==src['sha256']
(T/'texture_manifest.json').write_text(json.dumps({'source_blend_sha256':src['sha256'],'rule':'18 source authored rasters retained; forest_leather_roughness.png updated from actual frozen r03 image pixels. Normal strength and UV frequency are material/mesh properties, not raster edits.','images':[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(T.glob('*.png'))]},indent=2));print('EXPORTED',images)
