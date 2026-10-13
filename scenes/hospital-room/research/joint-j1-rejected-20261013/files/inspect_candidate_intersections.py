import bpy,json,bmesh,hashlib
from mathutils.bvhtree import BVHTree
from pathlib import Path
R=Path(__file__).parent;O=R/'diagnostic_outputs'
cur=bpy.data.objects['Curtain • rebuilt uniform eight-fold drape']; v=[cur.matrix_world@x.co for x in cur.data.vertices]; p=[list(f.vertices) for f in cur.data.polygons]; tree=BVHTree.FromPolygons(v,p,all_triangles=False,epsilon=0.000001)
inter=[]; bounds=[]
for o in bpy.data.objects:
 if not o.name.startswith('Blind bank 3') or o.type!='MESH':continue
 w=[o.matrix_world@x.co for x in o.data.vertices];polys=[list(f.vertices) for f in o.data.polygons]
 ov=tree.overlap(BVHTree.FromPolygons(w,polys,all_triangles=False,epsilon=0.000001))
 if ov:inter.append({'blind_object':o.name,'overlapping_face_pairs':len(ov)})
 bounds.extend(w)
qa={'candidate_status':'REJECTED_DIAGNOSTIC','source_fidelity_accepted':False,'physical_occlusion_accepted':False,'render_inspection':'Native G candidate render exposes horizontal blind slats visibly crossing in front of/through upper grey folded surface; source grey surface is opaque without those bars. This is geometry, not a shadow boundary.','grey_fold_world_y_minmax':[min(x.y for x in v),max(x.y for x in v)],'blind_bank3_world_y_minmax':[min(x.y for x in bounds),max(x.y for x in bounds)],'curtain_min_z':min(x.z for x in v),'curtain_max_z':max(x.z for x in v),'blind_objects_with_surface_intersections':len(inter),'surface_intersections':inter,'method':'Blender BVHTree polygon overlap on true world-space mesh; integer face pairs are implementation diagnostics, not pixel accuracy.','single_geometry_shared':True,'per_view_hiding_added':False,'source_color_boundaries_not_scored_as_geometry':True,'blender_images_packed':[{ 'name':i.name,'packed':bool(i.packed_file),'size':list(i.size)} for i in bpy.data.images if i.name!='Render Result']}
# Bed eye region checks on actual saved mattress (not the solver's own analytic box).
mat=bpy.data.objects['Bed • mattress and sheet']; vv=[mat.matrix_world@x.co for x in mat.data.vertices];mn=[min(x[i] for x in vv) for i in range(3)];mx=[max(x[i] for x in vv) for i in range(3)];qa['mattress_bounds']=[mn,mx];qa['camera_regions']={}
for k in 'ABFGH':
 c=bpy.data.objects['J1_'+k+'_uncalibrated'];a=c.matrix_world.translation;qa['camera_regions'][k]={'position':list(a),'inside_mattress_xy':all(mn[i]<=a[i]<=mx[i] for i in [0,1]),'height_above_mattress_top':a.z-mx[2],'anatomically_validated':False}
(O/'independent_physical_qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in qa.items() if k not in ['surface_intersections','blender_images_packed']},ensure_ascii=False))
