from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;S=Path('/workspace/shared/arcade-source-20261030')
# Manually inspected image-space regions; NOT calibrated quadrilaterals or full physical poster bounds.
regions=[{'id':'LOW_LEFT','source':'BV1nxQPBkEGH_2522.827654_low_angle.png','poster_inframe_envelope':[(616,0),(973,0),(1005,265),(643,303)],'foreground_envelope':[(950,168),(985,169),(1008,189),(1033,213),(1060,259),(1061,321),(1040,380),(899,383),(870,355),(856,310),(858,277),(875,235),(907,199),(932,180)],'out_of_frame':['upper poster boundary missing; entire above-frame extent unknown'],'boundary_margin':5},
{'id':'LOW_RIGHT','source':'BV1nxQPBkEGH_2522.827654_low_angle.png','poster_inframe_envelope':[(1490,0),(1919,0),(1919,161),(1507,196)],'foreground_envelope':[],'out_of_frame':['upper poster boundary missing','right poster boundary outside frame'],'boundary_margin':5},
{'id':'FRONT_CENTER','source':'BV1nxQPBkEGH_2490.122610_front.png','poster_inframe_envelope':[(774,0),(1175,0),(1180,75),(774,77)],'foreground_envelope':[(924,55),(965,53),(979,79),(975,115),(925,118)],'out_of_frame':['only low wordmark strip present; almost all upper poster outside frame'],'boundary_margin':5}]
rows=[]
for r in regions:
 im=Image.open(S/r['source']).convert('RGB');base=Image.new('L',im.size);ImageDraw.Draw(base).polygon(r['poster_inframe_envelope'],fill=255);occ=Image.new('L',im.size)
 if r['foreground_envelope']:ImageDraw.Draw(occ).polygon(r['foreground_envelope'],fill=255)
 # Conservatively exclude boundary and a dilation around foreground to avoid baking hair edges.
 safe=np.array(base.filter(ImageFilter.MinFilter(11)))>0;occ_d=np.array(occ.filter(ImageFilter.MaxFilter(15)))>0;inside=np.array(base)>0
 labels=np.zeros((1080,1920),dtype=np.uint8);labels[inside]=3;labels[safe & ~occ_d]=1;labels[inside & occ_d]=2
 Image.fromarray(labels).save(D/(r['id']+'_native_mask.png'))
 palette=np.zeros((1080,1920,3),dtype=np.uint8);palette[labels==1]=(40,210,95);palette[labels==2]=(235,65,65);palette[labels==3]=(255,195,0)
 arr=np.array(im);sel=labels>0;arr[sel]=(arr[sel]*.55+palette[sel]*.45).astype('uint8');annot=Image.fromarray(arr)
 b=r['poster_inframe_envelope'];x0=max(0,min(p[0]for p in b)-20);x1=min(1920,max(p[0]for p in b)+20);y1=max(p[1]for p in b)+30;crop=annot.crop((x0,0,x1,y1));canvas=Image.new('RGB',(crop.width,crop.height+72),(65,65,75));canvas.paste(crop,(0,72));dr=ImageDraw.Draw(canvas);dr.text((8,6),'OUT OF FRAME ABOVE: extent UNKNOWN',fill='white');dr.text((8,24),'Not a reconstructed poster area / not native image',fill='white');dr.text((8,45),'Green visible | Red foreground | Amber uncertainty',fill='white');canvas.save(D/(r['id']+'_visibility_diagram.png'))
 counts={str(k):int((labels==k).sum())for k in [1,2,3]};total=sum(counts.values());r.update(counts_native_pixels=counts,inframe_envelope_pixel_area=total,conservative_visible_fraction_of_inframe_envelope=counts['1']/total,full_physical_poster_coverage='NOT IDENTIFIABLE because top/right bounds missing',source_sha256=hashlib.sha256((S/r['source']).read_bytes()).hexdigest(),mask_legend={'0':'outside analyzed in-frame poster envelope, NOT all out-of-frame','1':'conservative visible source pixels including printed static silhouette','2':'foreground person/expanded exclusion margin','3':'manual boundary uncertainty; do not texture'},schematic_top_margin='72 derived diagram pixels solely mark missing field of view; not native pixels or estimated height')
 rows.append(r)
(D/'visibility_data.json').write_text(json.dumps(rows,indent=2))
print([(r['id'],r['counts_native_pixels'],r['conservative_visible_fraction_of_inframe_envelope'])for r in rows])
