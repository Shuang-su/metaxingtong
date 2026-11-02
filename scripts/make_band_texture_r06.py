from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parents[1]
im=Image.new('RGB',(2048,512),(13,39,62));d=ImageDraw.Draw(im)
for x in range(0,2048,16):d.line((x,0,x,512),fill=(68,111,136),width=2)
for y in range(0,512,16):d.line((0,y,2048,y),fill=(68,111,136),width=2)
f=ImageFont.truetype(str(R/'textures/fonts/DejaVuSans-Bold.ttf'),250)
for x in (40,1110):d.text((x,125),'bilibili',font=f,fill=(160,245,255))
im.save(R/'textures/curved-band-led-grid-r06.png')
