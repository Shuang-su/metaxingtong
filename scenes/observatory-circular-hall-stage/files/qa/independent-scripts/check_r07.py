import bpy,bmesh,json,pathlib,hashlib,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-qa-20261104')
def h(x):return hashlib.sha256(repr(x).encode()).hexdigest()
def snap():
 out={}
 for o in bpy.context.scene.objects:
  e={'type':o.type,'matrix':list(map(list,o.matrix_world)),'hide_render':o.hide_render}
  if o.type=='MESH':e.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],materials=[m.name for m in o.data.materials],uv=[list(x.uv) for u in o.data.uv_layers for x in u.data])
  if o.type=='CAMERA':e['intrinsics']=[o.data.lens,o.data.sensor_width,o.data.sensor_height,o.data.shift_x,o.data.shift_y,o.data.sensor_fit]
  if o.type=='LIGHT':e['light']=[o.data.type,o.data.energy,list(o.data.color),o.data.size]
  out[o.name]=e
 return out
R={};D=json.load(open(P/'qa/R07-band-trial.json'));idx={'S1':26,'S2':24,'S3':30,'S4':28}
for mode in ['material','white']:
 fs=P/'models'/f'R06_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(fs));old=snap();f=P/'models'/f'R07_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));new=snap();star='FLOOR_four_point_inlay';a=old[star];b=new[star];changed=[i for i,(x,y) in enumerate(zip(a['vertices'],b['vertices'])) if x!=y]
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[star].data);top={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces),'volume':bm.calc_volume(signed=True)};bm.free()
 rr={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'baseline_sha256':hashlib.sha256(fs.read_bytes()).hexdigest(),'changed_objects':[n for n in old if old[n]!=new[n]],'changed_vertex_indices':changed,'changed_z':any(a['vertices'][i][2]!=b['vertices'][i][2] for i in changed),'faces_uv_materials_matrix_same':all(a[k]==b[k] for k in ['faces','uv','materials','matrix']),'topology':top,'geometry_hashes':{n:h((v['vertices'],v['faces'],v['matrix'])) for n,v in new.items() if v['type']=='MESH'},'projection':{}}
 s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();o=bpy.data.objects[star]
 for name,rows in D['trial'].items():
  cam=bpy.data.objects[name];ps=[]
  for row in rows:
   basept=o.matrix_world@Vector(a['vertices'][idx[row['id']]]);buv=world_to_camera_view(s,cam,basept);basepix=[buv.x*1192,(1-buv.y)*671];pt=o.matrix_world@o.data.vertices[idx[row['id']]].co;uv=world_to_camera_view(s,cam,pt);pix=[uv.x*1192,(1-uv.y)*671];dr=pt-cam.matrix_world.translation;hit,loc,nor,fi,obj,ma=s.ray_cast(deps,cam.matrix_world.translation,dr.normalized(),distance=dr.length+.002)
   ps.append({'id':row['id'],'actual_world':list(pt),'projected':pix,'observed':row['observed'],'error_px':math.dist(pix,row['observed']),'baseline_actual_error_px':math.dist(basepix,row['observed']),'producer_error_difference':math.dist(pix,row['observed'])-row['error_px'],'depth':uv.z,'first_hit':obj.name if hit else None,'hit_distance':(loc-cam.matrix_world.translation).length if hit else None,'target_distance':dr.length})
  rr['projection'][name]=ps
 R[mode]=rr
R['material_white_geometry_equal']=R['material']['geometry_hashes']==R['white']['geometry_hashes'];(Q/'R07-independent-check.json').write_text(json.dumps(R,indent=2));print('DONE',[(m,r['changed_objects'],r['topology']) for m,r in R.items() if isinstance(r,dict)])
