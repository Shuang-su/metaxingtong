import bpy,sys,pathlib,json,re
from mathutils import Vector
R=pathlib.Path('forest-diagnostic-replay-20261104').resolve();M=R/'models/R09_material.blend';out=R/'renders/ring-diagnostic';out.mkdir(parents=True,exist_ok=True)
for scale in [1,2]:
 bpy.ops.wm.open_mainfile(filepath=str(M));s=bpy.context.scene
 groups={}
 for ob in s.objects:
  m=re.match(r'^(FAR_TREE_\d\d)(?:_|$)',ob.name)
  if m:groups.setdefault(m[1],[]).append(ob)
 for key,group in groups.items():
  trunk=bpy.data.objects[key];vs=[trunk.matrix_world@v.co for v in trunk.data.vertices];z=min(v.z for v in vs);low=[v for v in vs if v.z<z+.3];c=sum(low,Vector())/len(low);d=Vector((c.x*(scale-1),c.y*(scale-1),0))
  for ob in group:ob.matrix_world.translation+=d
 s.cycles.samples=4;s.cycles.use_denoising=False;s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2
 for cam in ['SOURCE_B_side','SOURCE_E_under','SOURCE_G_4K_top']:
  s.camera=bpy.data.objects[cam];s.render.filepath=str(out/(str(scale)+'_'+cam+'.png'));bpy.ops.render.render(write_still=True)
print('DIAGNOSTIC previews only; no original save, no source acceptance')
