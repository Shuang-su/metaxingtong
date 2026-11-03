"""Archive exact-frame comparisons; contact sheets are labeled viewing aids only."""
from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parents[1]
pairs={'SOURCE_A':'cityroom-native-1193.600873.png','SOURCE_B':'cityroom-native-1352.177747.png','SOURCE_C':'cityroom-native-high-1308.663295.png','SOURCE_D_low':'cityroom-native-low-1214.175651.png','SOURCE_E_oblique':'cityroom-native-oblique-1356.934381.png','SOURCE_F_fan4k':'fan4k-native-oblique-55.048960.png'}
O=D/'comparisons/R08';O.mkdir(parents=True,exist_ok=True)
for mode in ['material','white']:
 for cam,src in pairs.items():
  subprocess.run(['python','scripts/overlay_native.py',str(D/'sources'/src),str(D/f'renders/R08_{mode}/{cam}.png'),str(O/f'{mode}-{cam}-direct50.png')],cwd=D,check=True)
 # Eight diagnostic cameras: thumbnails are not original source/acceptance frames.
 sheet=Image.new('RGB',(1600,2000),'#17171b');dr=ImageDraw.Draw(sheet)
 for i in range(8):
  im=Image.open(D/f'renders/R08_{mode}/CHECK_{i+1:02}.png').convert('RGB');im.thumbnail((800,450));x=(i%2)*800;y=(i//2)*500
  sheet.paste(im,(x,y+25));dr.text((x+10,y+5),f'R08 {mode} CHECK {i+1:02} - diagnostic view, inferred structure',fill='white')
 sheet.save(O/f'{mode}-8-check-views.jpg',quality=95)
# Fixed source-B crop rectangles, same exact coordinates on all 3 images. Not warped/aligned.
regions={'bed':(0,520,460,1080),'left-curtain':(420,0,780,930),'hourglass':(850,735,1120,1080),'bar':(1390,560,1920,1080)}
records=[]
for name,box in regions.items():
 for role,path in [('source',D/'sources'/pairs['SOURCE_B']),('material',D/'renders/R08_material/SOURCE_B.png'),('white',D/'renders/R08_white/SOURCE_B.png'),('overlay',O/'material-SOURCE_B-direct50.png')]:
  Image.open(path).crop(box).save(O/f'detail-B-{name}-{role}.png')
 records.append({'object':name,'box_xyxy':box,'method':'identical crop coordinates, no warp/rescale; B full frames retained'})
(O/'detail-crops.json').write_text(json.dumps(records,indent=2))
print('12 native-size direct overlays, 2 labeled check sheets and 16 equal-coordinate object crops saved')
