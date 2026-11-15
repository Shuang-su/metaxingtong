#!/usr/bin/env python3
"""Smooth donor warp anchored at the real bow and sleeve, not time interpolation."""
from try_shared_collar import *
from scipy.interpolate import RBFInterpolator
from motion_registration import match_translation

def patch_shared(im,n):
    a=np.array(im);b=base('03-awake');source=Image.open(b/'original-decoded/54.png').convert('RGB');target=Image.open(b/'original-decoded'/f'{n:02d}.png').convert('RGB')
    rec=json.loads((b/'v6-contour-and-motion/dynamic-candidate-r1/validation.json').read_text())['frames'][n-1]['construction']['shoulder']['placement'];dx,dy=rec['dx'],rec['dy']
    bow=match_translation(source,target,[200,537,240,568],[-8,8],[-4,24]);cuff=match_translation(source,target,[235,565,300,608],[-8,8],[-8,8])
    sp=np.array([[264,458],[302,478],[247,514],[219,550],[319,502],[280,550],[230,505]],float)
    tp=np.array([[270+dx,481+dy],[310+dx,498+dy],[241+dx,528+dy],[219+bow['dx'],550+bow['dy']],[319+dx,514+dy],[280+cuff['dx'],550+cuff['dy']],[230+bow['dx'],505+bow['dy']]],float)
    pts=np.array([[214,550],[219,536],[231,516],[246,495],[263,482],[277,475],[296,484],[311,499],[322,508],[326,523],[314,532],[300,528],[280,537],[257,547]])+[dx,dy]
    old=np.array(Image.open(b.parent/'20261115-boundary-refinement/v8-local-r2'/f'allowed-mask-{n:02d}.png'))>0
    mask=(old|polygon(pts))&~protect('03-awake',n);mask[:450]=False;mask[552:]=False
    yy,xx=np.indices(a.shape[:2]);outer_cap=(yy>=496+dy)&(xx>314+dx+(503+dy-yy)*.8)
    mask&=~outer_cap
    ys,xs=np.where(mask);co=RBFInterpolator(tp,sp,kernel='thin_plate_spline',smoothing=0)(np.column_stack([xs,ys]));src=np.array(source);paint=a.astype(float)
    for c in range(3):paint[ys,xs,c]=map_coordinates(src[:,:,c].astype(float),[co[:,1],co[:,0]],order=1,mode='nearest')
    arr=compose(a,paint,mask,2);result=quantize_exact_outside(im,Image.fromarray(arr),mask).convert('RGB')
    return result,mask,{'method':'single F54 real-pixel donor, smooth thin-plate spatial warp','source_points':sp.tolist(),'target_points':tp.tolist(),'bow_registration':bow,'cuff_registration':cuff,'polygon':pts.tolist(),'preserve_outer_blue_cap':'y >= 496+dy and x > 314+dx+(503+dy-y)*0.8','temporal_interpolation':False}

def main():
    out=DOC/'prototype-r2';out.mkdir(exist_ok=False);ims,_=frames(base('03-awake').parent/'20261115-boundary-refinement/v8-local-r2/03-v8-CANDIDATE-master-768.gif')
    for n in [5,9,17,21]:
        result,m,details=patch_shared(ims[n-1],n);stem=f'F{n:02d}-D_bow_anchored';result.save(out/(stem+'.png'));Image.fromarray(m.astype('uint8')*255).save(out/(stem+'-mask.png'));(out/(stem+'.json')).write_text(json.dumps(details,indent=2)+'\n')
        box=(210,450,340,560);w=260;h=220;sheet=Image.new('RGB',(w*2,h+24),'#ddd');dr=ImageDraw.Draw(sheet)
        for j,im in enumerate([ims[n-1],result]):sheet.paste(im.crop(box).resize((w,h),Image.Resampling.NEAREST),(j*w,24));dr.text((j*w+3,3),f'F{n} '+['v8','D bow anchored'][j],font=FONT,fill='black')
        sheet.save(out/(stem+'-comparison.png'))
if __name__=='__main__':main()
