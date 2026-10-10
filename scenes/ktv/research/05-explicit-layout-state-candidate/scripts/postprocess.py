from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,subprocess,sys
import numpy as np
root=Path(__file__).resolve().parents[1];workspace=Path(sys.argv[1]);sys.path.insert(0,str(root/'scripts'))
from layout_states import choose_state,timeline_state,visibility_targets
m=json.loads((root/'layout_state_manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
images=[];denoise=[];overlays=[];associations=[]
def add(p,role,caption,source=None,parents=None,transform=None):
 row={'file':str(p.relative_to(root)),'sha256':sha(p),'bytes':p.stat().st_size,'pixels':list(Image.open(p).size),'role':role,'caption':caption,'source_url':m['source_url'] if source else None,'source_camera_calibrated':False,'transform':transform or 'none'}
 if source:
  meta=json.loads((root/'references'/source).with_suffix('.json').read_text());row.update(source_reference='references/'+source,source_video_before_seconds=meta['before']['time'],source_video_after_seconds=meta['after']['time'],source_decoded_dimensions=meta['before']['decoded'])
 if parents:row['parents']=parents
 images.append(row)

def denoise_png(inp,out):
 a=np.asarray(Image.open(inp).convert('RGB'),np.float32)/255;pi=inp.with_suffix('.pfm');po=out.with_suffix('.pfm')
 with pi.open('wb') as f:f.write(f'PF\n{a.shape[1]} {a.shape[0]}\n-1.0\n'.encode());np.flipud(a).tofile(f)
 subprocess.run([str(workspace/'teahouse_v2/oidn/bin/oidnDenoise'),'--ldr',str(pi),'--srgb','-o',str(po),'--threads','2'],check=True,stdout=subprocess.DEVNULL)
 with po.open('rb') as f:
  f.readline();w,h=map(int,f.readline().split());f.readline();b=np.flipud(np.fromfile(f,dtype='<f4').reshape(h,w,3))
 Image.fromarray((np.clip(b,0,1)*255+.5).astype(np.uint8)).save(out);pi.unlink();po.unlink()
 denoise.append({'input':str(inp.relative_to(root)),'output':str(out.relative_to(root)),'input_sha256':sha(inp),'output_sha256':sha(out),'method':'Standalone OIDN 2.5.1 LDR sRGB color-only, 2 threads; raw PNG retained'})
for state in ['furnished','unfurnished']:
 source=m['diagnostic_render']['source_reference_state_labels'][state];sp=root/'references'/source;sm=json.loads(sp.with_suffix('.json').read_text())
 state_result,sel=choose_state(m,state,sm['before']['time'])
 assert sel['manual_override'] and sel['timeline_result']=='unknown'
 associations.append({'render':'renders/fixed_01_front_'+state+'.png','reference':'references/'+source,'source_before_seconds':sm['before']['time'],'source_after_seconds':sm['after']['time'],'timeline_result_at_before':timeline_state(m,sm['before']['time']),'manual_observed_image_selection':sel,'association_created_after_render':True,'note':'Render command selected manual state without source-time input. This separate association documents the boundary image state without rewriting the command log.'})
 add(sp,'new_hd_boundary_source','边界源截图；'+state+'；1920×1080解码，截图1180×757；来源时间精度为前/后读取。',source)
 raw=root/'renders'/f'fixed_01_front_{state}.png';dn=raw.with_name(raw.stem+'_denoised.png');denoise_png(raw,dn)
 for render,tag in [(raw,'raw'),(dn,'denoised')]:
  add(render,'fixed_camera_state_render_'+tag,f'固定已有01_front机位，显式{state}状态；不是源机位还原。',source,transform='Standalone OIDN; no geometric transform' if tag=='denoised' else 'Unmodified Cycles render')
  r=Image.open(render).convert('RGB');assert r.size==(1180,664)
  canvas=Image.new('RGB',(1180,757),(0,0,0));canvas.paste(r,(0,27));cp=root/'comparisons'/f'{state}_{tag}_canvas.png';canvas.save(cp)
  add(cp,'render_canvas_'+tag,f'{state}诊断渲染嵌入源截图尺寸；未拟合对齐。',source,[str(render.relative_to(root))],'Black padding only; paste at x0 y27 from DOM picture y26.625 rounded; no resize/crop/warp')
  si=Image.open(sp).convert('RGB');op=root/'comparisons'/f'{state}_{tag}_overlay50.png';Image.blend(si,canvas,.5).save(op)
  actual=np.asarray(Image.open(op)).astype(np.int16);expected=(np.asarray(si).astype(np.uint16)+np.asarray(canvas).astype(np.uint16))//2
  mismatch=int(np.count_nonzero(actual!=expected));assert mismatch==0
  overlays.append({'file':str(op.relative_to(root)),'source':str(sp.relative_to(root)),'render_canvas':str(cp.relative_to(root)),'alpha':.5,'pixel_formula':'floor((source_uint16+render_canvas_uint16)/2)','mismatched_channels':mismatch,'geometric_alignment_fitted':False})
  add(op,'direct_50pct_overlay_'+tag,f'{state}源图与固定未校准机位渲染直接50%叠图；机位/尺度差异保留，不能作为来源还原通过。',source,[str(sp.relative_to(root)),str(cp.relative_to(root))],'Exact 50% blend; no feature fitting or image warp')
fnt='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';small=ImageFont.truetype(fnt,17);title=ImageFont.truetype(fnt,25)
w=590;ph=round(757*w/1180);header=92;lh=62
board=Image.new('RGB',(w*3,header+(ph+lh)*2),(18,21,27));d=ImageDraw.Draw(board)
d.text((15,8),'显式沙发状态：来源、固定未校准机位渲染与直接50%叠图',font=title,fill='white')
d.text((15,44),'同一01_front机位 / 同一几何、材料、坐标 / 仅18沙发+8推断附件显隐变化 / 不宣称源相机匹配或还原验收',font=small,fill='#f4cf83')
for row,state in enumerate(['furnished','unfurnished']):
 source=m['diagnostic_render']['source_reference_state_labels'][state]
 paths=[root/'references'/source,root/'comparisons'/f'{state}_denoised_canvas.png',root/'comparisons'/f'{state}_denoised_overlay50.png']
 labels=['真实HD来源截图','已有固定机位，独立OIDN副本','直接50%叠图，差异完整保留']
 for col,p in enumerate(paths):
  y=header+row*(ph+lh);x=col*w;board.paste(Image.open(p).convert('RGB').resize((w,ph),Image.Resampling.LANCZOS),(x,y));d.text((x+8,y+ph+4),state+' · '+labels[col],font=small,fill='white')
  tm=json.loads((root/'references'/source).with_suffix('.json').read_text());d.text((x+8,y+ph+29),f'来源 {tm["before"]["time"]:.6f}–{tm["after"]["time"]:.6f}s',font=small,fill='#a9cce7')
p=root/'comparisons/Source_fixed_camera_state_overlay_board.jpg';board.save(p,quality=93,subsampling=0)
add(p,'source_render_overlay_board','两状态来源/固定未校准机位/直接50%叠图总览；只证明显式状态规则。',parents=[x['file'] for x in images],transform='Uniform downscale and external labels; source originals retained')
images[-1]['source_url']=m['source_url'];images[-1]['source_references']=[{'file':a['reference'],'before':a['source_before_seconds'],'after':a['source_after_seconds']} for a in associations];images[-1]['source_decoded_dimensions']=[1920,1080]
pair=Image.new('RGB',(1180,430),(18,21,27));d=ImageDraw.Draw(pair);d.text((12,8),'固定01_front机位：切18沙发+8推断附件，动态组保留原设置',font=title,fill='white')
for x,state in [(0,'furnished'),(590,'unfurnished')]:
 pic=Image.open(root/'renders'/f'fixed_01_front_{state}_denoised.png').resize((590,332),Image.Resampling.LANCZOS);pair.paste(pic,(x,55));d.text((x+12,394),state+'；共享几何/材料/坐标',font=small,fill='white')
p=root/'comparisons/Fixed_camera_state_pair.jpg';pair.save(p,quality=93,subsampling=0);add(p,'render_only_state_pair','渲染间固定机位两态对照；没有对应精确源机位。',parents=['renders/fixed_01_front_furnished_denoised.png','renders/fixed_01_front_unfurnished_denoised.png'],transform='Uniform downscale and external labels')
a=json.loads((root/'qa/render_furnished.json').read_text());b=json.loads((root/'qa/render_unfurnished.json').read_text())
for k in ['input_blend_sha256','manifest_sha256','state_module_sha256','camera','camera_world_matrix','lens_mm','sensor_width_mm','sensor_fit','shift','resolution','samples','seed','threads','collection_visibility']:assert a[k]==b[k],k
changed=[n for n in a['visibility'] if a['visibility'][n]!=b['visibility'][n]];assert set(changed)==set(visibility_targets(m))
dump(root/'qa/render_pair_check.json',{'same_camera_geometry_input_render_settings':True,'changed_object_visibility':changed,'changed_count':len(changed),'only_explicit_18_plus_8_allowlist':True,'all_collection_visibility_equal':True,'source_camera_calibration':False})
dump(root/'qa/render_source_associations.json',associations);dump(root/'qa/overlay_pixel_checks.json',overlays);dump(root/'qa/denoise_log.json',denoise);dump(root/'image_evidence_manifest.json',{'image_count':len(images),'images':images})
print('POSTPROCESS_PASS',len(images),'images; 4 direct overlays pixel-exact; 18 furniture + 8 inferred attachment flags only')
