from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,numpy as np,shutil
R=Path('/workspace/scratch/fa58bfcf0425/ktv_fixed_visibility_20261010')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',24)
small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',21)
def rgb(p):return Image.open(p).convert('RGB')
def rend(model,view,state='fixed'):return rgb(R/'renders'/f'{model}_{view}_{state}_denoised.png')
def saveboard(name,cells,cols=2):
 w,h=1188,668;lh=72;rows=(len(cells)+cols-1)//cols
 out=Image.new('RGB',(w*cols,(h+lh)*rows),(21,24,31));d=ImageDraw.Draw(out)
 for i,(im,label,sub) in enumerate(cells):
  assert im.size==(w,h)
  x=i%cols*w;y=i//cols*(h+lh);out.paste(im,(x,y));d.text((x+10,y+h+3),label,font=font,fill='white');d.text((x+10,y+h+36),sub,font=small,fill=(200,205,217))
 out.save(R/'comparisons'/name,quality=92)
ref=rgb(R/'references/frame_7119_crop.png')
for model,state in [('legacy','historical_hidden'),('legacy','fixed'),('current','fixed'),('current_white','fixed')]:
 im=rend(model,'Empty_Stage',state);assert im.size==ref.size
 Image.blend(ref,im,.5).save(R/'comparisons'/f'Empty_Stage_source_{model}_{state}_direct_50pct.png')
for view in ['Empty_Stage','Telescope_Detail']:
 old=rend('legacy',view,'historical_hidden');fixed=rend('legacy',view);current=rend('current',view)
 Image.blend(old,fixed,.5).save(R/'comparisons'/f'{view}_legacy_hidden_fixed_render_only_50pct.png')
 Image.blend(old,current,.5).save(R/'comparisons'/f'{view}_legacy_current_render_only_50pct.png')
saveboard('Empty_Stage_source_and_visibility_regression.jpg',[
 (ref,'原帧 D · 01:58:39 · 原像素 1188×668','沙发/黄色伙伴未见；机位与时间布置尚未联合证实'),
 (rend('current','Empty_Stage'),'CURRENT · 固定可见性 · 未修改模型','沙发、星伙伴保留；相机名含 empty 不代表删物'),
 (rend('legacy','Empty_Stage','historical_hidden'),'历史隐藏逻辑重演 · 同采样控制图','旧模型隐藏 18 个沙发网格 + 7 个星伙伴网格'),
 (rend('legacy','Empty_Stage'),'旧模型固定可见性 · 同采样控制图','与左图只改变两个集合的渲染开关'),
 (rend('current_white','Empty_Stage'),'CURRENT 白模 · 同几何 / 同可见性','本图与材质版共用几何；白模光色按既有白版'),
 (rgb(R/'comparisons/Empty_Stage_source_current_fixed_direct_50pct.png'),'原帧 + CURRENT · 直接 50% 叠图','无裁切 / 透视变形 / 遮罩；差异如实保留')])
saveboard('Telescope_Detail_fixed_visibility_regression.jpg',[
 (rend('legacy','Telescope_Detail','historical_hidden'),'历史隐藏逻辑重演 · Telescope_Detail','合成诊断相机，无对应来源帧'),
 (rend('legacy','Telescope_Detail'),'旧模型固定可见性 · Telescope_Detail','与左图同模型 / 同相机，只恢复两个集合'),
 (rend('current','Telescope_Detail'),'CURRENT · 固定可见性 · 未修改模型','与旧模型另有已归档结构/灯光差异，非单变量'),
 (rend('current_white','Telescope_Detail'),'CURRENT 白模 · 同几何 / 同可见性','仅技术回归；不计来源验收或新增来源角度')])
saveboard('Source_temporal_state_review.jpg',[
 (rgb(R/'references/frame_4529_crop.png'),'来源 A · 01:15:29 · 有沙发状态','人物站立遮挡局部家具；黄色伙伴朝向与B不同'),
 (rgb(R/'references/frame_2117_crop.png'),'来源 B · 00:35:17 · 有沙发状态','人物坐姿遮挡家具；气球狗在右上方出现'),
 (ref,'来源 D · 01:58:39 · 空场候选状态','人物、沙发、黄色伙伴未见；气球狗在右侧低处')],cols=1)
diffs={}
for view in ['Empty_Stage','Telescope_Detail']:
 a=np.array(rend('legacy',view,'historical_hidden'),dtype=np.float32);b=np.array(rend('legacy',view),dtype=np.float32);diff=np.abs(a-b)
 diffs[view]={'mean_absolute_channel_delta_0_255':float(diff.mean()),'fraction_pixels_any_channel_delta_over_20':float((diff.max(axis=2)>20).mean()),'meaning':'Image change caused by collection visibility in a fixed geometry/camera/seed comparison. Includes shadows/reflections/Monte Carlo/denoising response; not a geometry-accuracy score or semantic object mask.'}
json.dump(diffs,open(R/'qa/visibility_image_delta.json','w'),indent=2)
print(json.dumps(diffs,indent=2))

verification=[]
for p in sorted((R/'comparisons').glob('*50pct.png')):
 name=p.name
 if '_source_' in name:
  tag=name.split('_source_')[1].removesuffix('_direct_50pct.png')
  model,state= ('legacy','historical_hidden') if tag=='legacy_historical_hidden' else (tag.removesuffix('_fixed'),'fixed')
  a_path=R/'references/frame_7119_crop.png';b_path=R/'renders'/f'{model}_Empty_Stage_{state}_denoised.png'
 else:
  view='Telescope_Detail' if name.startswith('Telescope_Detail') else 'Empty_Stage'
  a_path=R/'renders'/f'legacy_{view}_historical_hidden_denoised.png'
  b_path=R/'renders'/f'{"legacy" if "legacy_hidden_fixed" in name else "current"}_{view}_fixed_denoised.png'
 a,b=rgb(a_path),rgb(b_path);expected=Image.blend(a,b,.5);actual=rgb(p)
 errors=int(np.any(np.asarray(expected)!=np.asarray(actual),axis=2).sum());assert errors==0
 verification.append({'output':p.relative_to(R).as_posix(),'inputs':[a_path.relative_to(R).as_posix(),b_path.relative_to(R).as_posix()],'input_sha256':[hashlib.sha256(x.read_bytes()).hexdigest() for x in [a_path,b_path]],'alpha':0.5,'resizing':False,'cropping':False,'warping':False,'masking':False,'dimensions':list(actual.size),'pixel_mismatch_count':errors})
json.dump(verification,open(R/'qa/overlay_pixel_verification.json','w'),indent=2)
