import bpy,json,pathlib,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path(__file__).resolve().parent;sc=bpy.context.scene
sc.render.resolution_x=1920;sc.render.resolution_y=1080;sc.render.resolution_percentage=100
names=['CentralGrid_VisibleAndCasting','RearFascia_Receiver','Feature_wall_backing','L_Timber_Return_BackStructure','Recess_side_arch_continuous_wall']
def bvh(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
ob=bpy.data.objects['CentralGrid_VisibleAndCasting'];tree=bvh(ob)
verts=[ob.matrix_world@v.co for v in ob.data.vertices]
# Actual per-component extents, without interpreting texture or color as structure.
adj=[[] for v in ob.data.vertices]
for e in ob.data.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
seen=set();components=[]
for i in range(len(verts)):
 if i in seen:continue
 q=[i];seen.add(i);ids=[]
 while q:
  v=q.pop();ids.append(v)
  for x in adj[v]:
   if x not in seen:seen.add(x);q.append(x)
 components.append({'vertex_count':len(ids),'bounds':[[min(verts[v][k] for v in ids),max(verts[v][k] for v in ids)] for k in range(3)]})
xs=np.linspace(-4.08,1.37,201);ys=np.linspace(-0.48,3.74,161);hits=0
for x in xs:
 for y in ys:
  if tree.ray_cast(Vector((float(x),float(y),6)),Vector((0,0,-1)),3)[0] is not None:hits+=1
sun=bpy.data.objects['Sun'];direction=(sun.matrix_world.to_quaternion()@Vector((0,0,1))).normalized()
# On the source-facing rear fascia only; geometric occlusion of direct solar rays.
shadow=[];n=0
for x in np.linspace(-4.08,1.39,275):
 for z in np.linspace(4.655,5.219,58):
  p=Vector((float(x),3.54029,float(z)));hit=tree.ray_cast(p,direction,10)[0];n+=1
  if hit is not None:shadow.append([float(x),float(z)])
projections={}
for cn in ['SOURCE_5586__01h33m06s','SOURCE_2727__00h45m27s']:
 cam=bpy.data.objects[cn];projections[cn]={}
 for name in names:
  o=bpy.data.objects[name]
  def proj(v):
   c=world_to_camera_view(sc,cam,v);return [float(c.x*1920),float((1-c.y)*1080),float(c.z)]
  projections[cn][name]={'vertices_2d':[proj(o.matrix_world@v.co) for v in o.data.vertices],'edges':[list(e.vertices) for e in o.data.edges]}
 if shadow:projections[cn]['grid_shadow_on_rear_fascia_samples']=[proj(Vector((x,3.54029,z))) for x,z in shadow]
report={'geometry_modified':False,'dimensions_are_model_units_not_metres':True,'grid_components':components,'grid_ray_sampling':{'object_only':'CentralGrid_VisibleAndCasting','x_range':[-4.08,1.37],'y_range':[-0.48,3.74],'origin_z':6,'direction':[0,0,-1],'max_distance':3,'grid_shape':[201,161],'excludes':'All other scene objects; not the whole roof open-area measurement'},'grid_ray_sample_count':len(xs)*len(ys),'grid_solid_vertical_sample_count':hits,'grid_open_sample_fraction':1-hits/(len(xs)*len(ys)),'rear_fascia_bottom':4.65484619140625,'grid_bottom':4.769845962524414,'rear_fascia_lower_than_grid':4.769845962524414-4.65484619140625,'solar_ray_direction':list(direction),'rear_fascia_surface_grid_shadow_samples':len(shadow),'rear_fascia_surface_sample_count':n,'shadow_xz_bbox':[[min(v[k] for v in shadow),max(v[k] for v in shadow)] for k in [0,1]] if shadow else None,'shadow_interpretation':'A geometric direct-sun occlusion test on the front surface only. Does not certify observed source shadow, soft penumbra, other lights, or occlusion by vegetation. No temporary caster or camera-specific geometry was added.','l_corner':'Feature wall bounds meet X=4 return wall; return Y=1.88..3.94 overlaps doorway wall Y up to 3.28. Door opening is in actual mesh; unobserved enclosure dimensions remain inferred.'}
report['grid_vertices_world']=[list(v) for v in verts];report['grid_edges']=[list(e.vertices) for e in ob.data.edges];report['collections']=[{'name':c.name,'hide_render':c.hide_render,'hide_viewport':c.hide_viewport} for c in bpy.data.collections]
report['ground_shadow_envelope_original_sun']={'plane_z':0,'grid_lowest_z':4.769845962524414,'delta_x':-direction.x/direction.z*4.769845962524414,'delta_y':-direction.y/direction.z*4.769845962524414,'interpretation':'Parallel direct-sun projection only; no scene change or claim of unique source lighting.'}
(P/'structural_audit.json').write_text(json.dumps(report,indent=2));(P/'structural_projections.json').write_text(json.dumps(projections))
print(json.dumps(report,indent=2))
