from PIL import Image,ImageDraw,ImageFont
import os,json,zipfile,glob
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for tag,ref,crop in [('A','castle_1510.jpg',(0,27,1188,695)),('B','garden_1319.jpg',(0,46,1188,714))]:
 a=Image.open(R+'/references/'+ref).convert('RGB').crop(crop);b=Image.open(R+'/renders/Final_Textured_Match_'+tag+'_clean.png').convert('RGB').resize(a.size)
 a.save(R+'/qa/Source_Crop_'+tag+'.png');Image.blend(a,b,.5).save(R+'/qa/Overlay_50pct_'+tag+'.png')
 out=Image.new('RGB',(1188*2,708),(22,22,28));out.paste(a,(0,40));out.paste(b,(1188,40));d=ImageDraw.Draw(out);d.text((20,12),'SOURCE: '+ref+' | character/UI excluded from model',fill='white');d.text((1208,12),'RECONSTRUCTION: approximate same camera',fill='white');out.save(R+'/qa/Source_vs_Model_'+tag+'.jpg',quality=92)
ims=[('Final_Textured_Wide','TEXTURED / NORMAL WIDE'),('Final_White_Wide','WHITE / NORMAL WIDE'),('Final_Textured_Oblique','TEXTURED / VISIBLE PATCH'),('Final_White_Oblique','WHITE / VISIBLE PATCH')];out=Image.new('RGB',(1600,980),(22,22,28));d=ImageDraw.Draw(out)
for i,(f,label) in enumerate(ims):
 im=Image.open(R+'/renders/'+f+'_clean.png').convert('RGB').resize((800,450));xx=(i%2)*800;yy=(i//2)*490;out.paste(im,(xx,yy+40));d.text((xx+15,yy+12),label,fill='white')
out.save(R+'/renders/Garden_Wide_Overview.jpg',quality=93)
packs={'01_Garden_White_Model.zip':['models/Xingtong_Castle_Garden_White.blend','models/Xingtong_Castle_Garden_White.glb'],'02_Garden_Textured_GLB.zip':['models/Xingtong_Castle_Garden_Textured.glb'],'03_Garden_Textured_Blender_and_PBR.zip':['models/Xingtong_Castle_Garden_Textured.blend']+['textures/'+os.path.basename(p) for p in glob.glob(R+'/textures/*.png')]+['scripts/'+os.path.basename(p) for p in glob.glob(R+'/scripts/*.py')],'04_Garden_Views_and_QA.zip':['renders/'+os.path.basename(p) for p in glob.glob(R+'/renders/Final*_clean.png')]+['renders/Garden_Wide_Overview.jpg']+['qa/'+os.path.basename(p) for p in glob.glob(R+'/qa/*') if p.endswith(('.png','.jpg','.json'))]+['references/'+os.path.basename(p) for p in glob.glob(R+'/references/*')]}
manifest=[]
for name,files in packs.items():
 with zipfile.ZipFile(R+'/delivery/'+name,'w',zipfile.ZIP_DEFLATED,6) as z:
  for f in files+['README.txt']:z.write(R+'/'+f,f)
 manifest.append({'name':name,'bytes':os.path.getsize(R+'/delivery/'+name),'files':files})
json.dump(manifest,open(R+'/delivery/manifest.json','w'),indent=2);print(json.dumps(manifest,indent=2))
