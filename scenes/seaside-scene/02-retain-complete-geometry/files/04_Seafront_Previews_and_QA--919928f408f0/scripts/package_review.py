import os,glob,json,subprocess,zipfile,hashlib
from PIL import Image,ImageDraw,ImageFont
import numpy as np
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';F=lambda n:ImageFont.truetype(font,n)
os.makedirs(R+'/previews',exist_ok=True)
OIDN='/workspace/scratch/fa58bfcf0425/teahouse_v2/oidn/bin/oidnDenoise'
def pfm_write(p,a):
 with open(p,'wb') as f:f.write(('PF\n%d %d\n-1.0\n'%(a.shape[1],a.shape[0])).encode());np.flipud(a.astype('<f4')).tofile(f)
def pfm_read(p):
 with open(p,'rb') as f:f.readline();w,h=map(int,f.readline().split());f.readline();return np.flipud(np.frombuffer(f.read(),dtype='<f4').reshape(h,w,3))
for path in sorted(glob.glob(R+'/renders/*.png')):
 im=Image.open(path).convert('RGB');a=np.asarray(im,dtype=np.float32)/255;pfm_write(R+'/qa/tmp_in.pfm',a)
 subprocess.run([OIDN,'--ldr',R+'/qa/tmp_in.pfm','--srgb','--threads','2','-o',R+'/qa/tmp_out.pfm'],check=True,stdout=subprocess.DEVNULL)
 out=Image.fromarray(np.uint8(np.clip(pfm_read(R+'/qa/tmp_out.pfm'),0,1)*255+.5));out.save(R+'/previews/'+os.path.basename(path).replace('.png','.jpg'),quality=94)
for p in ['tmp_in.pfm','tmp_out.pfm']:os.remove(R+'/qa/'+p)
shots=sorted(glob.glob(R+'/previews/QA*.jpg'));W=600;H=410;can=Image.new('RGB',(W*3,H*4),(24,29,35));d=ImageDraw.Draw(can)
for i,p in enumerate(shots):
 im=Image.open(p);im.thumbnail((W,H-38));x=i%3*W;y=i//3*H;can.paste(im,(x,y+38));d.text((x+10,y+5),os.path.basename(p).replace('.jpg',''),font=F(23),fill='white')
can.save(R+'/qa/完整检查总览.jpg',quality=94)
metrics=[]
for ts,cam in [('6170','A_reference_6170'),('6435','B_reference_6435'),('6310','C_side_6310')]:
 source=Image.open(R+'/source_evidence/references/home_'+ts+'.jpg').convert('RGB').crop((0,26,1188,694));source.save(R+'/qa/源图_'+ts+'_原比例裁剪.png')
 for variant,cn in [('Textured','材质'),('White','白模')]:
  model=Image.open(R+'/previews/'+variant+'_Camera_'+cam+'.jpg').convert('RGB');assert model.size==source.size
  ov=Image.blend(source,model,.5);ov.save(R+'/qa/'+ts+'_'+cn+'_50%叠图.jpg',quality=94)
  sheet=Image.new('RGB',(1188*3,712),(24,29,35));dr=ImageDraw.Draw(sheet)
  for i,(im,label) in enumerate([(source,'源图：360p播放，1188×668视口裁剪'),(model,cn+'：同一几何、普通透视'),(ov,'50%直接叠图：无形变、无局部对齐')]):sheet.paste(im,(i*1188,44));dr.text((i*1188+10,7),label,font=F(23),fill='white')
  sheet.save(R+'/qa/'+ts+'_'+cn+'_三联对照.jpg',quality=92)
  a=np.asarray(source,dtype=float);b=np.asarray(model,dtype=float);metrics.append({'frame_seconds':ts,'variant':variant,'RGB_MAE_0_255':float(np.mean(abs(a-b))),'RGB_RMSE_0_255':float(np.sqrt(np.mean((a-b)**2))),'interpretation':'仅全画面像素差，不是几何精度或相机标定残差；包括人物遮挡、天空、海面、UI和光照差异。'})
json.dump(metrics,open(R+'/qa/直接对照像素残差.json','w'),indent=2,ensure_ascii=False)
print('PREVIEW_READY')
# HD decode references: never resize the screenshots; render pixels match actual crop.
hdmetrics=[]
for key,base in [('A','seafront_A_6172'),('B','seafront_B_6433')]:
 source=Image.open(R+'/source_hd/'+base+'_crop.png').convert('RGB');meta=json.load(open(R+'/source_hd/'+base+'_metadata.json'))
 for variant,cn in [('Textured','材质'),('White','白模')]:
  model=Image.open(R+'/previews/HD_'+variant+'_'+key+'.jpg').convert('RGB');assert model.size==source.size==(1180,663)
  ov=Image.blend(source,model,.5);ov.save(R+'/qa/高清_'+key+'_'+cn+'_50%直接叠图.jpg',quality=95)
  sh=Image.new('RGB',(3540,715),(24,29,35));dr=ImageDraw.Draw(sh)
  for i,(im,label) in enumerate([(source,'新来源：1080解码 / 实际裁剪1180×663'),(model,cn+'：邻近旧参考相机，无图像形变'),(ov,'50%直接叠图：视点、光照与遮挡残差保留')]):sh.paste(im,(i*1180,52));dr.text((i*1180+12,10),label,font=F(23),fill='white')
  sh.save(R+'/qa/高清_'+key+'_'+cn+'_三联对照.jpg',quality=94)
  a=np.asarray(source,dtype=float);b=np.asarray(model,dtype=float);hdmetrics.append({'frame':key,'actual_seconds':meta['video'][0]['currentTime'],'paused':meta['video'][0]['paused'],'readyState':meta['video'][0]['readyState'],'decoded':[1920,1080],'crop':[1180,663],'variant':variant,'RGB_MAE_0_255':float(np.mean(abs(a-b))),'RGB_RMSE_0_255':float(np.sqrt(np.mean((a-b)**2))),'note':'Exact-size direct comparison, no source image warp; retained nearby reference camera is approximate, not calibrated to this later frame. RGB error includes scenery, person, illumination and UI; not geometry distance.'})
json.dump(hdmetrics,open(R+'/qa/高清对照元数据与像素残差.json','w'),indent=2,ensure_ascii=False)
print('HD_COMPARISONS_READY')
