from pathlib import Path
import hashlib,json
from PIL import Image
O=Path(__file__).resolve().parent;R=O.parent/'stargravity-report-source-20261104'
rows=[]
for n,box in [('03',[960,245,1192,440]),('04',[990,105,1192,330])]:
 p=R/(n+'.webp');rows.append({'source':n,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'size':list(Image.open(p).size),'native_pixel_crop_xyxy':box,'native_video_frame':False})
out={'sources':rows,'coordinate_system':'original screenshot pixels; x right y down','source03':{'visible_band_roi':[982,269,1192,347],'approx_upper_skirt_notch':[1091,303],'notch_subjective_error_px':[6,6],'dark_underside_roi':[983,331,1192,393],'notes':'crossing thin members behind the edge; right/top cropped, not complete canopy'},'source04':{'visible_band_roi':[1023,118,1192,209],'approx_upper_skirt_notch':[1159,151],'notch_subjective_error_px':[6,6],'approx_lower_edge_segment_notch':[1120,267],'lower_notch_subjective_error_px':[8,8],'dark_underside_roi':[1020,195,1192,268],'notes':'upper edge and lower visible edge are different projected segments; front/back correspondence not fixed'},'null':['true canopy apex and full top extent','rightmost/backmost silhouette beyond frame','full panel or rib count','precise whole-circle stripe count and continuity','fabric thickness','seams or physical attachment details','source03/04 exact same animated/light state','true metric dimensions','opposite-side valance contour'],'scope':'ROIs and approximate observations only; not homologous calibrated point pairs or fitted geometry'}
(O/'semantic-observations-v1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
