from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
R=Path(__file__).resolve().parents[1];T=R/'textures'
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
im=Image.new('RGB',(2048,256),(3,115,132));d=ImageDraw.Draw(im)
for x in range(0,2048,8):d.line((x,0,x,256),fill=(7,140,155),width=1)
for y in range(0,256,8):d.line((0,y,2048,y),fill=(7,140,155),width=1)
f=ImageFont.truetype(font,74)
for x in (-540,380,1300):d.text((x,75),'2025 MUSIC FESTIVAL',font=f,fill=(205,255,255))
im.save(T/'display-teal-2025.png')
im=Image.new('RGB',(512,2048),(13,39,62));d=ImageDraw.Draw(im)
for x in range(0,512,16):d.line((x,0,x,2048),fill=(68,111,136),width=2)
for y in range(0,2048,16):d.line((0,y,512,y),fill=(68,111,136),width=2)
f=ImageFont.truetype(font,72)
for y in (130,700,1270,1840):d.text((35,y),'bilibili',font=f,fill=(160,245,255))
im.save(T/'curved-band-led-grid.png')
