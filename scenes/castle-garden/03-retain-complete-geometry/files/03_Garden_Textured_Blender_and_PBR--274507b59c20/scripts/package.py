from PIL import Image,ImageDraw,ImageFont
import os,glob,json,zipfile,hashlib,shutil
R='/workspace/scratch/fa58bfcf0425/castle_garden_fullscene';D=R+'/delivery';font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
os.makedirs(D+'/references',exist_ok=True);os.makedirs(D+'/scripts',exist_ok=True);os.makedirs(R+'/packages',exist_ok=True)
for f in glob.glob(R+'/source/evidence/references/*')+glob.glob(R+'/source/hd/*'):shutil.copy2(f,D+'/references/')
for f in glob.glob(R+'/scripts/*.py'):shutil.copy2(f,D+'/scripts/')
for tag,fn,crop in [('A','castle_1510.jpg',(0,27,1188,695)),('B','garden_1319.jpg',(0,46,1188,714))]:
 src=Image.open(D+'/references/'+fn).convert('RGB').crop(crop);src.save(D+'/views/源矩形裁切_'+tag+'.png')
 for variant in ['材质','白模']:
  im=Image.open(D+'/views/'+variant+'_源匹配_'+tag+'.png').convert('RGB');assert im.size==src.size
  Image.blend(src,im,.5).save(D+'/views/50%直接叠图_'+variant+'_'+tag+'.jpg',quality=94)
  sheet=Image.new('RGB',(1188*3,718),(30,30,35));draw=ImageDraw.Draw(sheet)
  for i,(x,label) in enumerate([(src,'来源矩形裁切，无变形'),(im,variant+'重建，相同模型'),(Image.blend(src,im,.5),'50%直接叠图，双边缘为残差')]):sheet.paste(x,(1188*i,50));draw.text((1188*i+12,12),label,font=font,fill='white')
  sheet.save(D+'/views/三联对照_'+variant+'_'+tag+'.jpg',quality=88)
files=sorted(glob.glob(D+'/views/[0-9][0-9]_*.png'));sheet=Image.new('RGB',(1440,1140),(27,27,31));dr=ImageDraw.Draw(sheet)
for i,f in enumerate(files):
 im=Image.open(f).convert('RGB');im.thumbnail((480,280));x=i%3*480;y=i//3*285;sheet.paste(im,(x,y+30));dr.text((x+5,y+2),os.path.basename(f).replace('.png',''),font=font,fill='white')
sheet.save(D+'/views/环绕_背面_底面_剖视总览.jpg',quality=90)
json.dump({'source_A_crop':[0,27,1188,695],'source_B_crop':[0,46,1188,714],'operation':'rectangular crop only; no warp; render 1188x668; blend exactly 0.5','source_native_quality':'360P per player UI, screenshot dimensions do not indicate native stream resolution'},open(D+'/qa/叠图方法.json','w'),ensure_ascii=False,indent=2)
# Lossless PNG diagnostic originals retained locally; pack normal views as high quality JPG to stay below size cap.
for f in glob.glob(D+'/views/*.png'):
 im=Image.open(f).convert('RGB');im.save(f[:-4]+'.jpg',quality=93)
common=['说明_中文.md']+['qa/'+os.path.basename(f) for f in glob.glob(D+'/qa/*.json')+glob.glob(D+'/qa/*.md')]
packs={'01_Garden_White_Model.zip':['models/Garden_Complete_White.blend','models/Garden_Complete_White.glb'], '02_Garden_Textured_GLB.zip':['models/Garden_Complete_Textured.glb'],'03_Garden_Textured_Blender_and_PBR.zip':['models/Garden_Complete_Textured.blend']+['textures/'+os.path.basename(f) for f in glob.glob(D+'/textures/*')]+['scripts/'+os.path.basename(f) for f in glob.glob(D+'/scripts/*')],'04_Garden_Views_and_QA.zip':['models/Garden_DIAGNOSTIC_CUTAWAY.blend']+['views/'+os.path.basename(f) for f in glob.glob(D+'/views/*.jpg')]+['references/'+os.path.basename(f) for f in glob.glob(D+'/references/*')]}
manifest=[]
for name,fs in packs.items():
 p=R+'/packages/'+name
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,6) as z:
  for f in fs+common:z.write(D+'/'+f,f)
 sz=os.path.getsize(p);assert sz<18000000,(name,sz)
 manifest.append({'filename':name,'path':p,'bytes':sz,'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest()})
json.dump(manifest,open(R+'/packages/frozen_manifest.json','w'),indent=2);print(json.dumps(manifest,indent=2))
