from pathlib import Path
import json,hashlib,zipfile,shutil
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];D=P/'deliverables';D.mkdir(exist_ok=True);Q=P/'qa';R=P/'renders';I=Q/'independent'
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';F=ImageFont.truetype(font,32);S=ImageFont.truetype(font,23);T=ImageFont.truetype(font,18)
BG=(18,19,28);TX=(230,230,235)
def fit(im,size):
 im=im.copy().convert('RGB');im.thumbnail(size);return im
# Direct overlays have exactly the source pixel dimensions; source frame is never warped.
for key in ['A','B','C']:
 src=Image.open(P/f'references/{key}_source.png').convert('RGB');mat=Image.open(R/f'源机位_{key}_材质.png').convert('RGB');white=Image.open(I/f'源机位_{key}_白模.png').convert('RGB')
 assert src.size==mat.size==white.size==(1180,663)
 ov=Image.blend(src,mat,.5);ov.save(Q/f'{key}_材质50直叠.png');Image.blend(src,white,.5).save(Q/f'{key}_白模50直叠.png')
 sheet=Image.new('RGB',(2400,1465),BG);dr=ImageDraw.Draw(sheet);dr.text((20,12),f'星光舞台候选｜{key}源机位｜同一几何、材质、固定灯光',font=F,fill=TX)
 for k,(im,cap) in enumerate([(src,'原始来源裁图（保留人物与播放器遮挡）'),(mat,'统一材质模型'),(white,'同几何白模'),(ov,'原图＋材质：50%直接叠图（残差未抹除）')]):
  x=20+(k%2)*1200;y=65+(k//2)*700;sheet.paste(im,(x,y));dr.text((x,y+665),cap,font=S,fill=TX)
 sheet.save(D/f'来源{key}_原图材质白模直接叠图.jpg',quality=92)
# Nine ordinary views, separately marked as model inspection rather than source checks.
for typ,folder in [('材质',R),('白模',I)]:
 files=sorted(folder.glob(f'普通*_{typ}.png'));assert len(files)>=9,(typ,len(files));out=Image.new('RGB',(2440,1540),BG);dr=ImageDraw.Draw(out);dr.text((20,12),f'九个普通检查视角｜{typ}｜不是九个来源机位',font=F,fill=TX)
 for k,f in enumerate(files[:9]):
  x=20+(k%3)*810;y=65+(k//3)*485;im=fit(Image.open(f),(800,450));out.paste(im,(x,y));dr.text((x,y+451),f.stem.replace('_'+typ,''),font=S,fill=TX)
 out.save(D/f'九视角_{typ}_中文预览.jpg',quality=91)
# Small review lead image, candid status at the top.
out=Image.new('RGB',(1600,1170),BG);dr=ImageDraw.Draw(out);dr.text((22,12),'星光颁奖舞台｜结构可检查，来源贴合仍有残差',font=F,fill=TX)
items=[(R/'普通01_前方全台_材质.png','完整有顶舞台：摄像方向开敞'),(R/'显式剖切_检查.png','显式几何剖切：看顶/墙/底及隐藏连接'),(P/'references/C_source.png','C真实来源：1180×663视口裁图'),(Q/'C_材质50直叠.png','C直接50%叠图：保留不匹配与人物遮挡')]
for k,(file,cap)in enumerate(items):
 x=22+(k%2)*789;y=66+(k//2)*525;im=fit(Image.open(file),(770,480));out.paste(im,(x,y));dr.text((x,y+483),cap,font=S,fill=TX)
dr.text((22,1122),'比例单位非测绘米｜同一几何用于全部视角｜候选近似重建，未宣称忠实复刻通过',font=S,fill=(255,190,120));out.save(D/'星光舞台_候选预览.jpg',quality=93)
# Verified source manifest, only the selected frames are counted.
source_manifest={'source_url':'https://www.bilibili.com/video/BV1xgBEYYEXF/','capture_environment':'cloud browser','decoded_stream':[1920,1080],'actual_viewport':[1180,757],'actual_source_crops':[1180,663],'source_warped':False,'independent_source_views':3,'sources':[]}
for key,file,meta,box in [('A','source_A_3850_viewport.png','source_A_3850.json',[0,27,1180,690]),('B','source_B_3815_viewport.png','source_B_3815.json',[0,27,1180,690]),('C','sample_3871p934.png',None,[0,27,1180,690])]:
 m=json.loads((P/'references'/meta).read_text())if meta else next(x for x in json.loads((P/'references/samples_c.json').read_text())if x['file']==file)
 source_manifest['sources'].append({'key':key,'raw_file':file,'crop_file':key+'_source.png','crop_box':box,'metadata':m,'raw_sha256':hashlib.sha256((P/'references'/file).read_bytes()).hexdigest(),'note':'C time is read before viewport screenshot; nearby video instant, not an exact decoded frame index.'if key=='C'else'paused screenshot'})
(Q/'source_manifest.json').write_text(json.dumps(source_manifest,ensure_ascii=False,indent=2))
final={'candidate_status':'近似重建候选；结构与源图忠实度分开判定；忠实度未通过','release_date_utc':'2026-10-10','previous_verified_release':None,'shared_camera_geometry':True,'files':[]}
for f in [P/'Star_Awards_Candidate.blend',P/'Star_Awards_Candidate.glb',P/'Star_Awards_White.blend',P/'Star_Awards_White.glb']:
 final['files'].append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(Q/'冻结文件清单.json').write_text(json.dumps(final,ensure_ascii=False,indent=2))
# Each archive is a separate, ordinary ZIP, never a split archive.
def zipset(name,files):
 dest=D/name
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for f in files:
   if f.is_file():z.write(f,str(f.relative_to(P)))
 assert dest.stat().st_size<18000000,(dest,dest.stat().st_size)
 return {'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
base=[P/'README_中文.md',Q/'冻结文件清单.json',Q/'真实修改记录.json',Q/'source_manifest.json']
render_manifest={'main_blend_sha256':final['files'][0]['sha256'],'samples':{'source':24,'ordinary':12,'section':16},'all_views_same_geometry_materials_lights':True,'renders':[{'file':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in sorted(R.glob('*.png')) if f.name.startswith(('源机位_','普通','显式剖切'))]};(Q/'最终渲染绑定.json').write_text(json.dumps(render_manifest,ensure_ascii=False,indent=2));base.append(Q/'最终渲染绑定.json')
packages=[]
packages.append(zipset('01_材质与白模_Blender.zip',base+[P/'Star_Awards_Candidate.blend',P/'Star_Awards_White.blend']+list((P/'textures').glob('*.png'))+list((P/'scripts').glob('*.py'))))
packages.append(zipset('02_材质与白模_GLB.zip',base+[P/'Star_Awards_Candidate.glb',P/'Star_Awards_White.glb',Q/'white_geometry_identity.json']))
sources=[P/'references'/f for f in ['A_source.png','B_source.png','C_source.png','source_A_3850_viewport.png','source_B_3815_viewport.png','sample_3871p934.png','source_3723_viewport.png','source_3723_crop.png']]
reviews=list(D.glob('来源*_原图材质白模直接叠图.jpg'))+list(Q.glob('*_材质50直叠.png'))+list(Q.glob('*_白模50直叠.png'))+[R/f'源机位_{k}_材质.png'for k in 'ABC']+[I/f'源机位_{k}_白模.png'for k in 'ABC']
packages.append(zipset('03_三源机位对照证据.zip',base+sources+list(D.glob('来源*_原图材质白模直接叠图.jpg'))+[Q/'camera_fit.json',Q/'shared_prop_fit.json']))
packages.append(zipset('05_三源原尺寸渲染与直叠.zip',base+[f for f in reviews if f.suffix=='.png']))
ordinary=list(R.glob('普通*_材质.png'))+list(I.glob('普通*_白模.png'))+[R/'显式剖切_检查.png']+list(D.glob('九视角_*.jpg'))
reports=[f for f in I.glob('*.json')]+list(I.glob('*.md'))+[Q/'technical_audit.json',Q/'white_geometry_identity.json']
packages.append(zipset('04_九视角剖切与技术检查.zip',base+ordinary+reports))
(Q/'交付包清单.json').write_text(json.dumps(packages,ensure_ascii=False,indent=2));print(json.dumps(packages,ensure_ascii=False,indent=2))
