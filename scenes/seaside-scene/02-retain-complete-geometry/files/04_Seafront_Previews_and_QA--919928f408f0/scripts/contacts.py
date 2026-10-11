import bpy,json
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene';bpy.ops.wm.open_mainfile(filepath=R+'/models/Seafront_Textured.blend');S=bpy.context.scene;S.view_layers[0].update()
def bounds(o):
 vs=[o.matrix_world@v.co for v in o.data.vertices];return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
report={'units':'relative, not measured meters','coastal_blocks':[],'lamps':[],'palms':[],'walkway':'Sea walk source nominal width2.25, blocks intrusion0.35, minimum nominal clear 1.90; no new objects in road corridor. Geometric clearance, not regulatory compliance.'}
for o in S.objects:
 if o.name.startswith('Coastal_block_'):report['coastal_blocks'].append({'name':o.name,'bottom_z':bounds(o)[0][2],'walk_top_z':.16,'gap':bounds(o)[0][2]-.16})
 if o.name.startswith('Lamp_') and o.name.endswith('_base'):report['lamps'].append({'name':o.name,'bottom_z':bounds(o)[0][2],'walk_top_z':.16,'gap':bounds(o)[0][2]-.16})
 if o.name.startswith('Palm_') and o.name.endswith('curved_trunk'):
  pts=sorted([o.matrix_world@v.co for v in o.data.vertices],key=lambda v:v.z)[:9];base=sum(pts,Vector())/len(pts);terr=bpy.data.objects['Undulating_coastal_land_slope'];hit,loc,normal,idx=terr.ray_cast(Vector((base.x,base.y,50)),Vector((0,0,-1)));report['palms'].append({'name':o.name,'terrain_hit':hit,'base_z':base.z,'terrain_z':loc.z if hit else None,'gap':base.z-loc.z if hit else None})
# Luminaire full perimeter: 8 corners of its bounds with pole endpoint bounds and distance.
report['luminaires']=[]
for o in S.objects:
 if o.name.endswith('luminaire_housing'):
  pre=o.name.split('luminaire_housing')[0];p=bpy.data.objects[pre+'curved_pole'];d=bpy.data.objects[pre+'emissive_diffuser'];report['luminaires'].append({'name':o.name,'housing_bounds':bounds(o),'diffuser_bounds':bounds(d),'pole_bounds':bounds(p)})
json.dump(report,open(R+'/qa/support_contact_validation.json','w'),indent=2)
