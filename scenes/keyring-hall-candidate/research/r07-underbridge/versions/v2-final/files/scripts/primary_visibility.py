import bpy,json,numpy as np,hashlib,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/r07b-material.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();W,H=1192,671;ids={'inferred-low-bridge-central-step':1,'inferred-low-bridge-step-outer':2};out=[]
for src in [17,20,21]:
 c=s.objects[f'source{src}-conditional'];frame=c.data.view_frame(scene=s);xmin,xmax=min(v.x for v in frame),max(v.x for v in frame);ymin,ymax=min(v.y for v in frame),max(v.y for v in frame);z=frame[0].z;rot=c.matrix_world.to_3x3();origin=c.matrix_world.translation;mask=np.zeros((H,W),dtype=np.uint8);start=time.monotonic()
 for y in range(H):
  yy=ymax-(y+.5)/H*(ymax-ymin)
  for x in range(W):
   direction=rot@Vector((xmin+(x+.5)/W*(xmax-xmin),yy,z));hit=s.ray_cast(dg,origin,direction.normalized(),distance=c.data.clip_end)
   if hit[0] and hit[4].name in ids:mask[y,x]=ids[hit[4].name]
 p=R/'results'/f'source{src}-primary-object-id.npy';np.save(p,mask);rows=[]
 for n,i in ids.items():
  yy,xx=np.where(mask==i);rows.append({'object':n,'id':i,'pixel_center_first_hits':len(xx),'bbox_xyxy':None if len(xx)==0 else [int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1]})
 out.append({'source':src,'resolution':[W,H],'sample_count':W*H,'counts':rows,'seconds':time.monotonic()-start,'mask_sha256':hashlib.sha256(p.read_bytes()).hexdigest()});print(out[-1],flush=True)
(R/'results/source-primary-visibility.json').write_text(json.dumps({'model_sha256':hashlib.sha256((R/'models/r07b-material.blend').read_bytes()).hexdigest(),'method':'Full scene ray_cast at every actual camera pixel center, nearest visible mesh, same camera 1192x671. Mask is categorical object ID, NOT depth.','limitation':'No subpixel antialiasing, reflection/refraction, indirect illumination or all-sample visibility proof; zero hits would not prove completely invisible. These are new R07 probes, not reused R06 images.','sources':out},indent=2))
