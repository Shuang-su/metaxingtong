from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import random
p=Path(__file__).resolve().parents[1];im=Image.new('RGB',(4096,512),(5,9,24));d=ImageDraw.Draw(im);rng=random.Random(20261102)
for i in range(12000):
 x=rng.randrange(4096);y=rng.randrange(512);c=rng.choice([(10,60,120),(20,130,200),(35,180,220)]);d.rectangle((x,y,x+1,y+2),fill=c)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',28)
for x in range(0,4096,420):d.text((x,210),'2024 MUSIC FESTIVAL',font=f,fill=(245,25,105))
im.save(p/'textures/led-continuous-authored-approximation.png')
