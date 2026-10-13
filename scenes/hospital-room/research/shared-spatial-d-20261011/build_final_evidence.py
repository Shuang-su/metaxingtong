from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image,ImageDraw,ImageFont
r=Path(__file__).parent;srcs={k:next((r.parent/'refs/extracted/hospital/frames').glob(f'*-{k}-*')) for k in 'FGH'};sources={x['view']:x for x in json.load(open(r/'source_and_baseline_references.json'))['sources']};font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21);head=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',27);media=[];checks=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for k in 'FGH':
 src=Image.open(srcs[k]).convert('RGB');assert src.size==(1920,1080) and sha(srcs[k])==sources[k]['sha256'];raw=r/f'{k}_D_full_1920_16spp_raw.png';normal=r/f'{k}_D_full_1920_16spp_raw_oidn.png';im=Image.open(raw).convert('RGB');assert im.size==src.size
 pixels=((np.asarray(src).astype(np.uint16)+np.asarray(im).astype(np.uint16))//2).astype(np.uint8);overlay=r/f'{k}_source_D_direct50_UNREGISTERED.png';Image.fromarray(pixels).save(overlay);actual=np.asarray(Image.open(overlay));assert np.array_equal(actual,pixels);checks.append({'view':k,'max_integer_difference':int(np.abs(actual.astype(int)-pixels).max()),'different_pixels':int(np.any(actual!=pixels,axis=2).sum())})
 base_raw=(r.parent/'candidate_c_outline'/f'{k}_B_same_camera_16spp_raw.png') if k!='H' else r/'H_B_full_1920_16spp_raw.png';base_normal=(r.parent/'candidate_c_outline'/f'{k}_B_same_camera_16spp_oidn.png') if k!='H' else r/'H_B_full_1920_16spp_raw_oidn.png'
 pan=Image.new('RGB',(1920,1250),'#161616');d=ImageDraw.Draw(pan);d.text((15,10),f'{k}: NATIVE SOURCE / B BASELINE / D SHARED-SPATIAL CANDIDATE (NOT ACCEPTED)',font=head,fill='white')
 warning={'F':'REGRESSION: middle-window-top proxy RMS 2.8 -> 40.6 px. Bed gains do not certify the full room.','G':'UNRESOLVED: source green chair is absent; left arm boundary requires recheck.','H':'CORRECTION: arm metric withdrawn; boundary requires recheck. Mattress / chair issues remain.'}[k];d.text((15,49),warning,font=font,fill='#ffb179');d.text((15,79),'Every cell is complete frame at 0.5x display scale. Full1920 raw and exact50 overlays supplied separately.',font=font,fill='#c6c6c6')
 cells=[('Native video source (unchanged)',srcs[k]),('B: 16 samples / OIDN display',base_normal),('D: 16 samples / OIDN display / one shared model',normal),('Native 50% + D RAW 50% / no registration',overlay)]
 for i,(label,p) in enumerate(cells):
  x=(i%2)*960;y=120+(i//2)*565;d.text((x+10,y),label,font=font,fill='white');pan.paste(Image.open(p).convert('RGB').resize((960,540),Image.Resampling.LANCZOS),(x,y+25))
 panel=r/f'{k}_source_B_D_fullframe_review.png';pan.save(panel)
 source_common={'source_view':k,'source_bv':sources[k]['source_bv'],'source_seconds':sources[k]['source_seconds'],'associated_source_seconds':sources[k]['source_seconds'],'render_video_seconds':None,'render_video_time_note':'Synthetic still render; no video timestamp. associated_source_seconds identifies comparison source only.','source_sha256':sources[k]['sha256'],'source_fixed_url':sources[k]['url'],'source_dimensions':[1920,1080],'new_source_capture':False}
 for p,role,extras in [(raw,'actual_fullframe_cycles_raw',{'samples':16,'adaptive_sampling':False,'denoise':False,'geometry_variant':'D'}),(normal,'normal_view_fullframe_display',{'input':raw.name,'input_sha256':sha(raw),'samples_in_input':16,'denoise':'OIDN2.5.1 RT LDR sRGB high CPU 2threads','main_view':k=='G'}),(overlay,'direct50_native_plus_raw',{'inputs':[srcs[k].name,raw.name],'formula':'floor((source uint16 + raw uint16)/2)','pixel_exact':True,'samples_in_render':16}),(panel,'source_baseline_candidate_and_direct50_fullframe_panel',{'cell_size':[960,540],'display_scale':.5,'baseline_raw':base_raw.name,'baseline_raw_sha256':sha(base_raw),'baseline_display':base_normal.name,'baseline_display_sha256':sha(base_normal),'cell_inputs':[p.name for _,p in cells],'panel_size':list(pan.size),'labels':True,'source_image_resize_only_for_display':True})]:
  media.append({'path':p.name,'role':role,'sha256':sha(p),'dimensions':list(Image.open(p).size),'registration':False,'warp':False,'crop':None,**source_common,**extras})
media.append({'path':'H_B_full_1920_16spp_raw.png','role':'fresh_matching_sample_baseline_control','source_view':'H','source_seconds':sources['H']['source_seconds'],'source_sha256':sources['H']['sha256'],'samples':16,'adaptive_sampling':False,'denoise':False,'baseline_model':'hospital_endboard_shape_B.blend','camera_changed':False,'dimensions':[1920,1080],'sha256':sha(r/'H_B_full_1920_16spp_raw.png'),'registration':False,'warp':False})
(r/'media_roles.json').write_text(json.dumps({'candidate_status':'NOT_ACCEPTED','final_main_view':'G_D_full_1920_16spp_raw_oidn.png','final_png_count':len(media),'source_originals_duplicated':False,'all_direct50_checks':checks,'media':media},ensure_ascii=False,indent=2))
(r/'direct50_pixel_checks.json').write_text(json.dumps(checks,indent=2));print('new final PNG',len(media),'all direct50 exact')

# Reapply the published annotation erratum when regenerating evidence from frozen renders.
metrics_path=r/'fit_and_holdout_metrics.json'
if metrics_path.exists():
    correction=json.load(open(metrics_path)).get('annotation_erratum')
    if correction:
        m=json.load(open(r/'media_roles.json'));m['annotation_erratum']=correction
        for row in m['media']:
            row['associated_source_seconds']=row.get('source_seconds');row['render_video_seconds']=None
            row['render_video_time_note']='Synthetic still render; associated_source_seconds identifies comparison source only.'
            if row['path']=='H_source_B_D_fullframe_review.png':row['left_arm_metric_status']='WITHDRAWN; no current numerical arm error.'
            if row['path']=='G_source_B_D_fullframe_review.png':row['caption_scope']='Qualitative only; old328.2->264.0px aggregate invalid and withdrawn.'
        m['caption_revisions']=[];m['historical_invalid_media']=[]
        for view,suffix in [('G','SUPERSEDED_UNVERIFIED_ARM_CLAIM'),('H','SUPERSEDED_INVALID_181PX')]:
            historical=r/f'{view}_source_B_D_fullframe_review_{suffix}.png'
            current=r/f'{view}_source_B_D_fullframe_review.png'
            if historical.exists():
                before=np.asarray(Image.open(historical));after=np.asarray(Image.open(current));delta=np.any(before!=after,axis=2);ys,xs=np.where(delta)
                assert not delta[:49,:].any() and not delta[79:,:].any()
                revision={'status':'CURRENT_CAPTION_CORRECTED','current_path':current.name,'old_library_version':0,'current_library_version_after_replace':1,'old_sha256':sha(historical),'new_sha256':sha(current),'historical_invalid_path':historical.name,'changed_pixel_bounds_xyxy':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],'all_four_image_cells_pixel_identical':True,'all_pixels_outside_header_y49_to78_identical':True,'caption_only':True}
                m['caption_revisions'].append(revision)
                m['historical_invalid_media'].append({'path':historical.name,'sha256':sha(historical),'role':'SUPERSEDED_ERRONEOUS_CAPTION_NOT_CURRENT_EVIDENCE','invalid_caption':'left sofa arm ~181 px error' if view=='H' else 'left sofa arm remains severely displaced','superseded_by':current.name})
                for row in m['media']:
                    if row['path']==current.name:row['caption_revision']=revision
        m['historical_invalid_png_count']=len(m['historical_invalid_media'])
        (r/'media_roles.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
