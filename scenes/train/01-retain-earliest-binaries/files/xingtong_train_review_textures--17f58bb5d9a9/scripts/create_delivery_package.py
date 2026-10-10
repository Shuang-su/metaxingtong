from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,shutil,zipfile,hashlib
R=Path(__file__).resolve().parents[1];O=R/'deliverables';P=R/'upload';P.mkdir(exist_ok=True);review=O/'review';review.mkdir(exist_ok=True);refout=review/'references';refout.mkdir(exist_ok=True)
F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';font=ImageFont.truetype(F,28);small=ImageFont.truetype(F,21)
for src,dest in [('packed_normal_material_denoised.png','normal_material.png'),('normal_white_denoised.png','normal_white.png'),('final_D_material_denoised.png','D_material.png'),('final_D_white_denoised.png','D_white.png'),('final_B_material_denoised.png','B_material.png'),('packed_A_material_denoised.png','A_material_approx.png')]:shutil.copy2(R/'renders'/src,review/dest)
for key,refn,render,title in [('A','train_015_918','A_material_approx.png','A｜15:19 近座位：近端花束/遮挡仍有差异'),('B','train_2711','B_material.png','B｜45:12 左侧偏轴：相机近似，所有家具共用同一几何'),('D','train_838','D_material.png','D｜13:59 纵深：只调真实相机；稀疏5点平均约3px，不代表全图精确')]:
 source=Path('/workspace/shared/xingtong_batch02/screenshots_jpg')/(refn+'.jpg');ref=Image.open(source).convert('RGB').crop((0,26,1188,694));ref=ImageOps.fit(ref,(1200,675));model=Image.open(review/render).convert('RGB');overlay=Image.blend(ref,model,.5)
 canvas=Image.new('RGB',(3600,790),(23,25,28));d=ImageDraw.Draw(canvas);d.text((22,10),title,font=font,fill='white')
 for idx,(im,label) in enumerate([(ref,'视频参考（人物和界面不属于模型）'),(model,'真实Blender网格渲染（未做透视变形）'),(overlay,'50%叠图：保留可见差异')]):canvas.paste(im,(idx*1200,82));d.text((idx*1200+18,49),label,font=small,fill=(197,205,211))
 d.text((22,759),'统一尺寸与布局｜至少5组有证据，第6组为推定｜白模/材质版室内几何一致',font=small,fill=(191,199,204));canvas.save(review/f'comparison_{key}.jpg',quality=91,subsampling=0)
# Main normal full-view pair, not a reference-match camera.
canvas=Image.new('RGB',(2400,746),(23,25,28));d=ImageDraw.Draw(canvas);d.text((20,8),'正常水平18mm广角｜同一真实网格、同一机位｜白模与材质',font=font,fill='white');canvas.paste(Image.open(review/'normal_material.png'),(0,55));canvas.paste(Image.open(review/'normal_white.png'),(1200,55));canvas.save(review/'normal_pair.jpg',quality=92,subsampling=0)
keys=['train_695','train_710','train_720','train_747','train_781','train_838','train_843','train_855','train_015_918','train_2109','train_2711','train_3615','train_6014']
for k in keys:
 p=Path('/workspace/shared/xingtong_batch02/screenshots_jpg')/(k+'.jpg')
 if p.exists():shutil.copy2(p,refout/p.name)
shutil.copy2('/workspace/shared/xingtong_batch02/train_coverage.json',review/'source_coverage.json')
shutil.copy2('/workspace/shared/xingtong_batch02/train_evidence_brief.txt',review/'source_evidence_中文.txt')
meta=json.loads((O/'verification.json').read_text());mean=meta['D_alignment']['mean_residual_pixels'];mx=max(meta['D_alignment']['residual_pixels'].values())
readme=(R/'README_中文.txt').read_text();extra=f'''\n最终验证（2026-10-07）\n- 1742个室内网格，均有UV；GLB回导后267840个三角面，坐标有限。\n- 两版Blender的室内几何哈希一致；两版GLB的规范化世界坐标三角形哈希也一致。\n- 19张图像全部嵌入材质版（18张512×512 PBR图＋站牌）；GLB没有外部图像URI。\n- D机位固定24mm，仅拟合相机位置/朝向。5个手读结构锚点在1188×668参考中的平均残差{mean:.2f}px、最大{mx:.2f}px。锚点本身有低清读数误差；这不是全图对齐分数。\n- 对比A可见近端花束与原图遮挡不同，B的窗列/顶棚仍有误差；花束位置、皮面细节并非原资产测量结果。\n- normal_material.png和normal_white.png是优先检查空间合理性的正常广角；comparison_B/D是不同参考机位的诚实对比，comparison_A额外保留近景局限。\n- 展示PNG经过OIDN降噪，没有任何几何/透视变形。\n'''
if '最终验证（2026-10-07）' not in readme:readme+=extra
(R/'README_中文.txt').write_text(readme);(O/'README_中文.txt').write_text(readme)
# Only finished files, no intermediate blends or unverified backups.
common=[O/'README_中文.txt',O/'verification.json',O/'glb_validation.json']
sets=[('xingtong_train_material_models.zip',[O/'01_train_material.blend',O/'03_train_material.glb']+common),('xingtong_train_white_models.zip',[O/'02_train_white.blend',O/'04_train_white.glb']+common),('xingtong_train_review_textures.zip',list(review.rglob('*'))+list((O/'textures').glob('*.png'))+list((R/'scripts').glob('*.py'))+common)]
manifest=[]
for name,files in sets:
 z=P/name
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as zz:
  for f in files:
   if f.is_file():
    if f.is_relative_to(O):arc=f.relative_to(O)
    elif f.is_relative_to(R/'scripts'):arc=Path('scripts')/f.name
    else:arc=f.name
    zz.write(f,str(arc))
 with zipfile.ZipFile(z) as zz:assert zz.testzip() is None
 sz=z.stat().st_size;assert sz<18*1024*1024,(name,sz)
 manifest.append({'path':str(z),'bytes':sz,'MiB':round(sz/1024/1024,3),'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'zip_crc_test':'passed'})
images=[{'path':str(review/f),'purpose':purpose} for f,purpose in [('normal_material.png','Primary normal horizontal wide material view'),('normal_white.png','Matching normal wide white model'),('normal_pair.jpg','Combined normal wide comparison'),('comparison_B.jpg','Reference / actual render / 50% overlay, left-side angle'),('comparison_D.jpg','Reference / actual render / 50% overlay, long carriage angle')]]
result={'archives':manifest,'images':images,'verification':{'same_blend_geometry':meta['same_interior_geometry'],'same_glb_geometry':meta['glb_validation']['same_canonical_geometry'],'all_material_images_embedded':meta['glb_validation']['03_train_material.glb']['all_images_embedded'],'D_sparse_mean_px':mean},'notes':'All ZIPs under 18 MiB. Upload 2 primary PNGs first, then 3 ZIPs. No Library upload performed.'};(P/'upload_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
