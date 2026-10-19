from PIL import Image,ImageChops,ImageStat
import numpy as np,json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parent
src=Image.open(r/'baseline/terrace-main-front-BV1g64y1P7VV-t5586.011739-native.png').convert('RGB');before=Image.open(r/'baseline/new_main_normal.png').convert('RGB');box=(1430,580,1650,845)
qa={}
for role in ['material','white']:
 after=Image.open(r/f'T3_{role}_raw.png').convert('RGB');assert after.size==src.size==(1920,1080)
 arr=((np.array(src).astype(np.uint16)+np.array(after).astype(np.uint16))//2).astype(np.uint8);out=Image.fromarray(arr);out.save(r/f'T3_source_{role}_direct50.png')
 assert np.max(abs(np.asarray(Image.open(r/f'T3_source_{role}_direct50.png')).astype(int)-arr.astype(int)))==0
 after.crop(box).save(r/f'T3_{role}_native_crop.png');qa[role]={'resolution':[1920,1080],'overlay_formula':'floor((source RGB uint16 + render RGB uint16)/2)','max_formula_difference':0,'no_warp_no_registration':True}
src.crop(box).save(r/'source_native_crop.png');before.crop(box).save(r/'before_native_crop.png')
imgs=[src.crop(box),before.crop(box),Image.open(r/'T3_material_native_crop.png')];board=Image.new('RGB',(660,265))
for i,im in enumerate(imgs):board.paste(im,(i*220,0))
board.save(r/'T3_source_before_after_native_strip.png')
json.dump({'panels_left_to_right':['source 5586.011739','Oct11 candidate OIDN historical baseline','T3 raw 8spp'],'crop_box':box,'crop_size':[220,265],'no_scaling':True,'overlays':qa,'warning':'Different raw/OIDN noise conditions; not a quantitative material-color acceptance. Front camera uncalibrated; no second independent table view.'},open(r/'comparison_manifest.json','w'),indent=2)
