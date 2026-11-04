"""Read-only parameter sensitivity, not a source fit or proposed accepted geometry.
Usage: blender -b --python THIS -- model.blend output.json
All scene modifications are memory-only; no save/export/render.
"""
import bpy, sys, json, hashlib, pathlib, re
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
args=sys.argv[sys.argv.index('--')+1:]; model=pathlib.Path(args[0]); output=pathlib.Path(args[1])
bpy.ops.wm.open_mainfile(filepath=str(model))
scene=bpy.context.scene
points=[(-2.8,1,5.35),(-2.45,1.8,5.3),(-1.4,2.6,5.5),(1.1,2.7,5.4),(2.7,1.1,5.45),(2.95,.1,5.15),(1.1,-2.65,5.05),(-.95,-2.7,5),(-2.6,-1.2,5.2),(-.25,2.85,5.4),(2.65,-1.15,5.45)]
groups={}
for ob in scene.objects:
 m=re.match(r'^(FAR_TREE_\d\d)(?:_|$)',ob.name)
 if m:groups.setdefault(m[1],[]).append(ob)
base={ob.name:ob.matrix_world.copy() for g in groups.values() for ob in g}
centres={}
for key,group in groups.items():
 trunk=bpy.data.objects.get(key)
 if trunk is None or trunk.type!='MESH':raise RuntimeError('No trunk '+key)
 vs=[trunk.matrix_world@v.co for v in trunk.data.vertices];zmin=min(v.z for v in vs)
 lower=[v for v in vs if v.z<zmin+.3]
 centres[key]=sum(lower,Vector())/len(lower)
cameras=sorted([o for o in scene.objects if o.type=='CAMERA' and o.name.startswith('SOURCE_')],key=lambda o:o.name)
trials=[]
for scale in [1.0,1.25,1.5,2.0]:
 for key,group in groups.items():
  c=centres[key];offset=Vector((c.x*(scale-1),c.y*(scale-1),0))
  for ob in group:
   ob.matrix_world=base[ob.name].copy();ob.matrix_world.translation+=offset
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();views=[]
 for cam in cameras:
  origin=cam.matrix_world.translation.copy();rays=[]
  for i,xyz in enumerate(points):
   target=Vector(xyz);direction=target-origin;dist=direction.length
   hit,loc,norm,face,ob,matrix=scene.ray_cast(dg,origin,direction.normalized(),distance=dist+.3)
   name=ob.name if hit else None
   ndc=world_to_camera_view(scene,cam,target); in_frame=ndc.z>0 and 0<=ndc.x<=1 and 0<=ndc.y<=1
   rays.append(dict(id='FLOWER_%02d'%i,hit=name,normalized_projection=list(ndc),in_frame=in_frame,target_distance=dist,first_distance=(loc-origin).length if hit else None,own_flower_first=bool(name and name.startswith('FLOWER_%02d_'%i)),far_tree_first=bool(name and name.startswith('FAR_TREE_'))))
  views.append(dict(camera=cam.name,rays=rays,far_tree_first=sum(r['far_tree_first'] and r['in_frame'] for r in rays),own_flower_first=sum(r['own_flower_first'] and r['in_frame'] for r in rays)))
 trials.append(dict(far_ring_radial_translation_factor=scale,views=views))
for name,matrix in base.items():bpy.data.objects[name].matrix_world=matrix
bpy.context.view_layer.update()
out=dict(model=str(model),sha256=hashlib.sha256(model.read_bytes()).hexdigest(),method='whole far-tree family rigid XY translations about global origin; no tree scaling/hiding/removal; all other objects/cameras fixed; restore original matrices at end; no model written',family_centres={k:list(v) for k,v in centres.items()},world_point_hypotheses=points,trials=trials,limits=['Sensitivity only: no observed tree location constraint yet; clearing one view is not evidence of correct geometry','Provisional flower centres/identities shared from R09; rays are sparse, not image visibility or entire surfaces','Earlier sources not proven same fixed world state','No source alignment acceptance; any followup change must compare all source views and retain regressions'])
output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(out,indent=2)+'\n')
print('DIAGNOSTIC_ONLY',output)
