import bpy,json,sys,runpy
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
V=Path(__file__).resolve().parents[1]
def state():
 s=bpy.context.scene;cs={o.name:o for o in s.objects if o.type=='CAMERA'};vs={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in s.objects if o.type=='MESH'}
 # Compare object world-space BBOX corners, robust to glTF triangulation/vertex splits.
 from mathutils import Vector
 bounds={k:([min(v[i] for v in a) for i in range(3)],[max(v[i] for v in a) for i in range(3)]) for k,a in vs.items()}
 projections={}
 for n,c in cs.items():
  projections[n]={}
  for obj,(lo,hi) in bounds.items():
   arr=[]
   for x in [lo[0],hi[0]]:
    for y in [lo[1],hi[1]]:
     for z in [lo[2],hi[2]]:
      p=world_to_camera_view(s,c,Vector((x,y,z)));arr.append([1080*p.x,603*p.y])
   projections[n][obj]=arr
 return {'mesh_count':len(vs),'camera_count':len(cs),'bounds':bounds,'projections':projections,'camera_sensor_fits':{n:c.data.sensor_fit for n,c in cs.items()}}
def compare(a,b):
 errors={}
 for n,ps in a['projections'].items():
  if n not in b['projections']:errors[n]=None;continue
  errors[n]=max(abs(v-b['projections'][n][obj][i][j]) for obj,arr in ps.items() for i,p in enumerate(arr) for j,v in enumerate(p))
 return errors
out={}
for variant in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(V/f'models/phone-{variant}.blend'));a=state();bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.scene.world=None;bpy.ops.import_scene.gltf(filepath=str(V/f'models/phone-{variant}.glb'));bpy.context.view_layer.update();b=state()
 sys.argv=['verify','--',variant];runpy.run_path(str(V/'scripts/restore-state.py'),run_name='__main__');c=state();out[variant]={'blend':a,'native_glb_import':b,'restored_glb_import':c,'native_projection_max_error_pixels':compare(a,b),'restored_projection_max_error_pixels':compare(a,c),'restored_world_nodes':{'nodes':[{'name':n.name,'type':n.bl_idname,'inputs':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if hasattr(i,'default_value')}} for n in bpy.context.scene.world.node_tree.nodes],'links':[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name] for l in bpy.context.scene.world.node_tree.links]},'note':'Fresh import has world None before restoration. No render performed. Projection comparison at fixed1080x603. Native glTF lacks area/world illumination; restored import reconstructs archived lighting.'}
json.dump(out,open(V/'qa/camera-roundtrip.json','w'),indent=2)
