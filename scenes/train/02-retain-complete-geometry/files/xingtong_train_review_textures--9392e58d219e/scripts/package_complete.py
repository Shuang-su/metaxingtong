from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,shutil,zipfile,hashlib
R=Path(__file__).resolve().parents[1];O=R/'deliverables';V=R/'review';P=R/'upload';P.mkdir(exist_ok=True);(V/'references').mkdir(exist_ok=True)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',25);sm=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',19)
source={
'A':('train_015_918.jpg','MATCH_A_15m19_right_booth','15:19 近座位｜近端花束与遮挡仍有残差'),
'B':('train_2711.jpg','MATCH_B_45m12_left_booth','45:12 偏轴机位｜窗列与顶棚仍有近似误差'),
'D':('train_838.jpg','MATCH_D_13m59_wide','13:59｜椅背顶部、近端遮挡与整体纵深仍有显著残差')}
for k,(refname,rendername,title) in source.items():
 ref=Image.open(R/'original/review/references'/refname).convert('RGB').crop((0,26,1188,694));ren=Image.open(R/'renders'/(rendername+'.png')).convert('RGB');assert ren.size==ref.size==(1188,668)
 canvas=Image.new('RGB',(1188*3,770),(22,24,27));d=ImageDraw.Draw(canvas);d.text((18,6),k+' | '+title,font=font,fill='white')
 for i,(im,txt) in enumerate([(ref,'实际视频画面（人物/界面未建）'),(ren,'完整共享几何直接渲染'),(Image.blend(ref,ren,.5),'50% 直接叠图，无透视变形')]):
  canvas.paste(im,(i*1188,69));d.text((i*1188+16,39),txt,font=sm,fill=(200,206,214))
 d.text((18,740),'完整空间几何版；源片精确拟合未达标｜第6组与反向端部为推定；渲染仅做标准降噪',font=sm,fill=(197,205,210));canvas.save(V/f'comparison_{k}.jpg',quality=91,subsampling=0)
 shutil.copy2(R/'renders'/(rendername+'.png'),V/(k+'_material.png'))
labels=['正向过道','反向过道（端部推定）','右侧窗与相向座','左侧窗与相向座','完整斜顶与中央天花','桌脚、座椅与地面连接','正向端门和玻璃真开口','反向端门（推定补全）','前端外壳诊断','后端外壳诊断（推定）','独立诊断几何剖切（交付仍完整）']
paths=[]
for i in range(1,12):
 path=next((R/'renders').glob(f'INSPECT_{i:02d}_*.png'));paths.append(path);im=Image.open(path).convert('RGB');cv=Image.new('RGB',(im.width,im.height+45),(22,24,27));cv.paste(im,(0,45));ImageDraw.Draw(cv).text((14,8),f'{i:02d} | '+labels[i-1],font=font,fill='white');cv.save(V/(path.stem+'.jpg'),quality=90,subsampling=0)
cs=Image.new('RGB',(1920,4*590+70),(22,24,27));d=ImageDraw.Draw(cs);d.text((16,12),'完整车厢：8个室内检查视角｜均非新增来源证据',font=font,fill='white')
for i,path in enumerate(paths[:8]):
 im=Image.open(path).convert('RGB');cs.paste(im,(i%2*960,70+i//2*590+40));d.text((i%2*960+14,70+i//2*590+6),f'{i+1:02d} | '+labels[i],font=font,fill='white')
cs.save(V/'eight_view_inspection.jpg',quality=89,subsampling=0)
ma=Image.open(paths[0]).convert('RGB');wh=Image.open(R/'renders/white_INSPECT_01_forward_aisle.png').convert('RGB');assert ma.size==wh.size
pair=Image.new('RGB',(ma.width*2,ma.height+72),(22,24,27));pair.paste(ma,(0,50));pair.paste(wh,(ma.width,50));ImageDraw.Draw(pair).text((14,8),'同一完整室内几何、同一检查机位｜材质与白模（不是来源匹配图）',font=font,fill='white');pair.save(V/'normal_pair.jpg',quality=92,subsampling=0)
white_labels={'white_INSPECT_01_forward_aisle':'白模：完整正向过道','white_INSPECT_03_right_booth':'白模：侧窗回边与窗帘','white_INSPECT_05_ceiling':'白模：中央天花与斜顶收口','white_INSPECT_07_forward_door':'白模：正向端门窗真开口','white_INSPECT_08_reverse_door':'白模：推定反向端门收口','white_INSPECT_12_support_detail':'白模：桌脚与座椅的实体支撑'}
wc=Image.new('RGB',(1920,3*590+70),(22,24,27));wd=ImageDraw.Draw(wc);wd.text((16,12),'完整几何白模核对：门窗、顶棚与支撑｜全部为检查视图',font=font,fill='white')
for wi,(stem,title) in enumerate(white_labels.items()):
 im=Image.open(R/'renders'/(stem+'.png')).convert('RGB');cc=Image.new('RGB',(960,585),(22,24,27));cc.paste(im,(0,45));ImageDraw.Draw(cc).text((14,8),title,font=font,fill='white');cc.save(V/(stem+'.jpg'),quality=93,subsampling=0);wc.paste(im,(wi%2*960,70+wi//2*590+40));wd.text((wi%2*960+14,70+wi//2*590+6),title,font=font,fill='white')
wc.save(V/'white_geometry_inspection.jpg',quality=92,subsampling=0)
detail=Image.open(R/'renders/white_INSPECT_12_support_detail.png').convert('RGB');dc=Image.new('RGB',(detail.width,detail.height+48),(22,24,27));dc.paste(detail,(0,48));ImageDraw.Draw(dc).text((14,8),'白模诊断：桌脚底座、墙边连接与双侧座椅落地',font=font,fill='white');dc.save(V/'white_support_detail.jpg',quality=93,subsampling=0)
shutil.copy2(paths[0],V/'normal_material.png');shutil.copy2(R/'renders/white_INSPECT_01_forward_aisle.png',V/'normal_white.png')
for p in (R/'original/review/references').glob('*.jpg'):shutil.copy2(p,V/'references'/p.name)
for fn in ['source_evidence_中文.txt','source_coverage.json']:shutil.copy2(R/'original/review'/fn,V/fn)
shutil.copy2(R/'README_中文.txt',O/'README_中文.txt')
common=[O/'README_中文.txt',O/'verification.json',O/'glb_validation.json',O/'验证摘要_中文.json']
# Independent findings are delivered as factual audits after any required repairs.
independent=[R/'analysis/independent/independent_geometry_summary.json',R/'analysis/light_footprint_qa.json'] if (R/'analysis/independent/independent_geometry_summary.json').exists() else []
sets=[('xingtong_train_material_models.zip',[O/'01_train_material.blend',O/'03_train_material.glb']+common),('xingtong_train_white_models.zip',[O/'02_train_white.blend',O/'04_train_white.glb']+common),('xingtong_train_review_textures.zip',list(V.rglob('*'))+list((R/'original/textures').glob('*.png'))+list((R/'scripts').glob('*.py'))+common+independent)]
out=[]
for name,files in sets:
 p=P/name
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for f in files:
   if not f.is_file():continue
   if f.is_relative_to(O):arc=f.relative_to(O)
   elif f.is_relative_to(V):arc=Path('review')/f.relative_to(V)
   elif f.is_relative_to(R/'original/textures'):arc=Path('textures')/f.name
   elif f.is_relative_to(R/'scripts'):arc=Path('scripts')/f.name
   else:arc=Path('independent_qa')/f.name
   z.write(f,str(arc))
 assert p.stat().st_size<18_000_000,(name,p.stat().st_size)
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 out.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'crc_test':'passed'})
(R/'upload/upload_manifest.json').write_text(json.dumps({'archives':out,'library_replacements':{'material':'libfile_e9f001d8d5408191b036812b72bd5888','white':'libfile_e44875a45ce88191b9850c446b95bc7b','review':'libfile_4147bdaa285881918bc18cfb8693990e'},'expected_current_version':0,'uploaded':False},indent=2));print(json.dumps(out,indent=2))
