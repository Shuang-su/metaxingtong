exec(open('/workspace/scratch/fa58bfcf0425/independent-observatory-portal-semantic-qa-20261105/check_model_door_views.py').read().split("for cn in")[0])
R={}
for cn in ['SOURCE_13_high','SOURCE_14_front','SOURCE_15_exterior']:
 c=bpy.data.objects[cn];out={}
 for k in [0,8]:
  n=f'DOOR_{k:02d}_gold_arch';o=bpy.data.objects[n];rows=[]
  for face in o.data.polygons:
   p=o.matrix_world@face.center;uv=world_to_camera_view(s,c,p)
   if not (uv.z>0 and 0<uv.x<1 and 0<uv.y<1):continue
   vec=p-c.matrix_world.translation;hit,loc,no,fi,obj,mat=s.ray_cast(dg,c.matrix_world.translation,vec.normalized(),distance=vec.length+.001)
   rows.append({'pixel':[uv.x*1192,(1-uv.y)*671],'nearest':obj.name if hit else None,'distance_error':(loc-c.matrix_world.translation).length-vec.length if hit else None})
  out[n]={'in_frame_face_centres':len(rows),'first_surface_same_arch':sum(x['nearest']==n for x in rows),'near_target_visible':sum(x['nearest']==n and abs(x['distance_error'])<1e-3 for x in rows),'witnesses':[x for x in rows if x['nearest']==n][:3]}
 R[cn]=out
(Q/'model-door-face-rays.json').write_text(json.dumps(R,indent=2));print(R)
