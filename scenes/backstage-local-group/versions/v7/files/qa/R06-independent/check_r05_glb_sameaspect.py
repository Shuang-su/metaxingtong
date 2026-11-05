import bpy,json,hashlib,pathlib,math
from mathutils.kdtree import KDTree
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-mannequin-qa-20261104')
def snap():
 return ({o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in bpy.context.scene.objects if o.type=='MESH'},{o.name:([list(r) for r in o.matrix_world],[tuple(x.normalized()) for x in o.data.view_frame(scene=bpy.context.scene)]) for o in bpy.context.scene.objects if o.type=='CAMERA'})
def dist(a,b):
 k=KDTree(len(b))
 for i,p in enumerate(b):k.insert(p,i)
 k.balance();return max(k.find(p)[2] for p in a)
R={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R05_{mode}.blend'));bpy.context.scene.render.resolution_x=1192;bpy.context.scene.render.resolution_y=671;bpy.context.scene.render.resolution_percentage=100;v,c=snap();f=P/'models'/f'R05_{mode}.glb';bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(f));bpy.context.scene.render.resolution_x=1192;bpy.context.scene.render.resolution_y=671;bpy.context.scene.render.resolution_percentage=100;v2,c2=snap()
 R[mode]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'mesh_counts':[len(v),len(v2)],'camera_counts':[len(c),len(c2)],'missing_mesh':list(v.keys()-v2.keys()),'extra_mesh':list(v2.keys()-v.keys()),'world_vertex_nearest_error':{n:max(dist(v[n],v2[n]),dist(v2[n],v[n])) for n in v.keys()&v2.keys()},'camera_matrix_error':{n:max(abs(c[n][0][i][j]-c2[n][0][i][j]) for i in range(4) for j in range(4)) for n in c.keys()&c2.keys()},'camera_frame_normalized_ray_error':{n:max(abs(c[n][1][i][j]-c2[n][1][i][j]) for i in range(4) for j in range(3)) for n in c.keys()&c2.keys()}}
(Q/'R05-glb-projection-check.json').write_text(json.dumps(R,indent=2));print('DONE')
