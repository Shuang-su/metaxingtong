"""Factory-empty GLB restoration; apply explicit missing AREA/World sidecar."""
import bpy,json,os,sys
from mathutils import Matrix
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'material'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=root+'/models/'+mode+'.glb')
d=json.load(open(root+'/models/environment.json'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False
s.render.resolution_x,s.render.resolution_y=d['resolution'];s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Restored world');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=d['world']['color'];s.world.node_tree.nodes['Background'].inputs[1].default_value=d['world']['strength']
for a in d['lights']:
 l=bpy.data.lights.new(a['name'],a['type']);l.energy=a['energy'];l.color=a['color'];l.size=a['size'];l.shape=a['shape'];o=bpy.data.objects.new(a['name'],l);s.collection.objects.link(o);o.matrix_world=Matrix(a['matrix_world'])
for a in d['cameras']:
 o=bpy.data.objects.get(a['name'])
 if not o:
  o=bpy.data.objects.new(a['name'],bpy.data.cameras.new(a['name']));s.collection.objects.link(o)
 o.matrix_world=Matrix(a['matrix_world']);o.data.lens=a['lens'];o.data.sensor_width=a['sensor_width'];o.data.sensor_fit=a['sensor_fit']
s.camera=bpy.data.objects['SOURCE03 conditional'];s.view_settings.view_transform='AgX'
meshes=[o for o in s.objects if o.type=='MESH']
report={'mode':mode,'factory_empty':True,'mesh_count':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'lights':len([o for o in s.objects if o.type=='LIGHT']),'cameras':len([o for o in s.objects if o.type=='CAMERA']),'resolution':[s.render.resolution_x,s.render.resolution_y],'denoising':s.cycles.use_denoising,'nonfinite_vertices':sum(not all(__import__('math').isfinite(x) for x in v.co) for o in meshes for v in o.data.vertices)}
json.dump(report,open(root+'/qa/restore-'+mode+'.json','w'),indent=2)
s.render.resolution_percentage=50;s.cycles.samples=4;s.render.filepath=root+'/renders/restored-'+mode+'03-low.png';bpy.ops.render.render(write_still=True)
print('RESTORE_COMPLETE',report)
