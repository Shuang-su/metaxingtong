import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/scratch/fa58bfcf0425/forest-diagnostic-replay-20261104');out={}
def nodes(tree):
 return {'nodes':[{ 'name':n.name,'type':n.bl_idname,'values':{x.name:(list(x.default_value) if hasattr(x.default_value,'__len__') and not isinstance(x.default_value,str) else x.default_value) for x in n.inputs if hasattr(x,'default_value') and isinstance(x.default_value,(int,float,str)) or hasattr(x,'default_value') and hasattr(x.default_value,'__len__') and not isinstance(x.default_value,bpy.types.ID)}} for n in tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in tree.links]} if tree else None
for rev in ['R12_support-diagnostic','R13_root-diagnostic']:
 for mode in ['material','white']:
  bpy.ops.wm.open_mainfile(filepath=str(R/f'models/{rev}_{mode}.blend'));s=bpy.context.scene
  out[rev+'_'+mode]={'lights':{o.name:{'matrix':[list(x)for x in o.matrix_world],'type':o.data.type,'color':list(o.data.color),'energy':o.data.energy,'size':getattr(o.data,'size',None),'nodes':nodes(o.data.node_tree)}for o in s.objects if o.type=='LIGHT'},'world':nodes(s.world.node_tree),'camera':{o.name:{'matrix':[list(x)for x in o.matrix_world],'lens':o.data.lens,'shift':[o.data.shift_x,o.data.shift_y],'sensor':[o.data.sensor_width,o.data.sensor_height,o.data.sensor_fit]}for o in s.objects if o.type=='CAMERA'}}
result={'data':out,'material_unchanged':out['R12_support-diagnostic_material']==out['R13_root-diagnostic_material'],'white_unchanged':out['R12_support-diagnostic_white']==out['R13_root-diagnostic_white']}
Path('/workspace/scratch/fa58bfcf0425/independent-forest-replay-qa-20261104/R13-light-world-camera-check.json').write_text(json.dumps(result,indent=2));print(result['material_unchanged'],result['white_unchanged'])

from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath=str(R/'models/R12_support-diagnostic_material.blend'));ob=bpy.data.objects['ISLAND_turf_blades_procedural'];bed=bpy.data.objects['ISLAND_moss_bedding_inferred'];vs=[ob.matrix_world@v.co for v in ob.data.vertices];bt=BVHTree.FromPolygons([bed.matrix_world@v.co for v in bed.data.vertices],[p.vertices[:]for p in bed.data.polygons]);groups=[[]for _ in range(4500)]
for f in ob.data.polygons:groups[f.vertices[0]//6].append([i%6 for i in f.vertices])
rows=[]
for i in range(4500):
 vv=vs[i*6:i*6+6];k=min(range(6),key=lambda k:vv[k].z);base=vv[k];hit=bt.ray_cast(base+Vector((0,0,.001)),Vector((0,0,-1)),2)[0];over=bool(BVHTree.FromPolygons(vv,groups[i]).overlap(bt));gap=base.z-hit.z if hit is not None else None;rows.append({'leaf':i,'base_vertex':i*6+k,'overlap':over,'ray_hit':hit is not None,'gap':gap})
selected=[v['base_vertex']for v in rows if v['ray_hit'] and v['gap']>1e-4 and not v['overlap']];new=json.loads(Path('/workspace/scratch/fa58bfcf0425/independent-forest-replay-qa-20261104/R13-independent-check.json').read_text());o={'rows':rows,'selected_matches_changed_material':selected==new['material']['changed_vertices'],'selected_matches_changed_white':selected==new['white']['changed_vertices']};Path('/workspace/scratch/fa58bfcf0425/independent-forest-replay-qa-20261104/R13-independent-baseline.json').write_text(json.dumps(o,indent=2));print('BASELINE',len(selected),o['selected_matches_changed_material'],o['selected_matches_changed_white'])
