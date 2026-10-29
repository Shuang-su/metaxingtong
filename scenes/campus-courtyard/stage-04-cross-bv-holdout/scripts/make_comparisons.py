"""Direct native-coordinate comparison, not an image alignment/warping operation."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
D=Path(__file__).resolve().parents[1];Q=D/'qa';C=D/'comparisons';C.mkdir(exist_ok=True)
source=Image.open(D/'source/BV1fwSEBqEPJ_t96.994858_native.png').convert('RGB');src=np.array(source)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
records=[];contact=Image.new('RGB',(1920,792),'#ececec');dr=ImageDraw.Draw(contact)
rois={'blue_net':[0,390,1430,720],'central_hoop':[650,0,930,720],'left_stair':[0,270,320,530],'right_lamp_benches':[1190,340,1500,675],'right_track_goal':[1430,390,1920,675],'green_red_key':[250,715,1430,1080]}
for row,name in enumerate(['FORWARD_COURT_ORDER_F35','REVERSE_TRACK_SIDE_F35']):
    render=Image.open(D/'renders'/(name+'.png')).convert('RGB');a=np.array(render);assert a.shape==src.shape==(1080,1920,3)
    expected=((src.astype(np.uint16)+a.astype(np.uint16))//2).astype(np.uint8);overlay=Image.fromarray(expected)
    op=C/(name+'_overlay50.png');overlay.save(op);assert np.array_equal(np.array(Image.open(op)),expected)
    render.save(D/'renders'/(name+'_display_preview.jpg'),quality=90,subsampling=0)
    strip=Image.new('RGB',(5760,1080));strip.paste(source,(0,0));strip.paste(render,(1920,0));strip.paste(overlay,(3840,0));strip.save(C/(name+'_native_triptych.png'))
    for col,(im,label) in enumerate([(source,'Original holdout'),(render,'Frozen model camera trial'),(overlay,'Direct 50% overlay')]):
        contact.paste(im.resize((640,360),Image.Resampling.LANCZOS),(col*640,row*396+36));dr.text((col*640+8,row*396+8),name+' | '+label,fill='black',font=font)
    for key,box in rois.items():
        folder=C/'native_crops'/name;folder.mkdir(parents=True,exist_ok=True)
        for role,im in [('source',source),('render',render),('overlay50',overlay)]:im.crop(box).save(folder/(key+'_'+role+'.png'))
    records.append({'name':name,'shape':list(a.shape),'overlay_rule':'uint8 floor((source_uint16 + render_uint16)/2), in native RGB pixel coordinates','overlay_exact_pixel_verified':True,'source_warp':False,'source_resize_for_native_overlay':False,'overlay_sha256':hashlib.sha256(op.read_bytes()).hexdigest(),'native_triptych_layout':'source | render | direct overlay; 5760x1080, no resizing'})
contact.save(C/'HOLDOUT_source_render_overlay_contact_preview.jpg',quality=88,subsampling=0)
# Separate annotated measurement copy: original pixels are never overwritten.
annotated=source.copy();draw=ImageDraw.Draw(annotated);picks=json.loads((Q/'independent_pixel_picks.json').read_text())['points']
for i,(name,p) in enumerate(picks.items()):
    color='#ffd900' if p['role']=='fit' else '#ff62ca'
    if 'xy' in p:
        x,y=p['xy'];draw.ellipse((x-8,y-8,x+8,y+8),outline=color,width=3);draw.text((x+10,y-24),name,fill=color,font=font)
    elif 'bbox' in p:
        box=p['bbox'];draw.rectangle(box,outline=color,width=3);draw.text((box[0],max(0,box[1]-23)),name,fill=color,font=font)
annotated.save(Q/'source_anchor_annotations.png')
# Explicitly reduced review contact sheet; not a new source or native comparison.
names=list(json.loads((Q/'camera_fit.json').read_text())['hypotheses'])
sheet=Image.new('RGB',(1920,1152),'#ececec');d=ImageDraw.Draw(sheet)
for i,name in enumerate(names):
    p=D/('renders' if name.endswith('_F35') else 'trials')/(name+('' if name.endswith('_F35') else '_960x540_preview')+'.png')
    im=Image.open(p).convert('RGB');x=i%3*640;y=i//3*576;d.text((x+8,y+8),name,fill='black',font=font);sheet.paste(im.resize((640,360),Image.Resampling.LANCZOS),(x,y+36))
    c=json.loads((Q/'camera_fit.json').read_text())['hypotheses'][name]
    d.text((x+8,y+411),'Conditional, not accepted. Fit mean %.1f px'%c['mean_error_px'],fill='black',font=font)
    d.text((x+8,y+441),'Held-out far-left corner %.1f px'%c['heldout_far_left']['error_px'],fill='black',font=font)
    d.text((x+8,y+471),'Camera height %.3f model units'%c['location'][2],fill='black',font=font)
    d.text((x+8,y+501),'All objects/lights/materials unchanged',fill='black',font=font)
sheet.save(C/'six_camera_trials_contact_preview.jpg',quality=88,subsampling=0)
(Q/'comparison_verification.json').write_text(json.dumps({'comparisons':records,'roi_coordinates_native':rois,'preview_contact_size':[1920,792],'six_trial_preview_size':[1920,1152],'native_images_unchanged':True},indent=2))
print(json.dumps(records,indent=2))
