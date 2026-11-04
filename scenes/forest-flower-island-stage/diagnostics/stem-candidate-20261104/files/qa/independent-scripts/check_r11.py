import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R=Path('/workspace/scratch/fa58bfcf0425/forest-diagnostic-replay-20261104');O=Path('/workspace/scratch/fa58bfcf0425/independent-forest-replay-qa-20261104')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snap():
 meshes={};cams={}
 for ob in bpy.context.scene.objects:
  if ob.type=='MESH':
   vs=[tuple(ob.matrix_world@v.co) for v in ob.data.vertices];fs=[list(p.vertices) for p in ob.data.polygons]
   meshes[ob.name]={'v':vs,'f':fs,'sha':hashlib.sha256(repr((vs,fs)).encode()).hexdigest(),'hidden':ob.hide_render}
  elif ob.type=='CAMERA':
   cams[ob.name]={'matrix':[list(x) for x in ob.matrix_world],'rays':[[v.x/-v.z,v.y/-v.z] for v in ob.data.view_frame(scene=bpy.context.scene)]}
 return meshes,cams
old=json.loads((O/'R10-independent-check.json').read_text());res={}
for mode in ['material','white']:
 p=R/f'models/R11_support-diagnostic_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(p));mm,cc=snap();uv={}
 for ob in bpy.context.scene.objects:
  if ob.type=='MESH' and ob.name.endswith('_inferred_stems'):
   uv[ob.name]={'layers':len(ob.data.uv_layers),'loops':len(ob.data.uv_layers.active.data),'finite':all(__import__('math').isfinite(x) for u in ob.data.uv_layers.active.data for x in u.uv)}
 res[mode]={'blend_sha256':sha(p),'geometry_equal_r10':{k:v['sha'] for k,v in mm.items()}==old['models'][mode]['geometry'],'cameras_equal_r10':cc==old['models'][mode]['cameras'],'uv':uv}
(O/'R11-independent-diff.json').write_text(json.dumps(res,indent=2));print('DONE')
