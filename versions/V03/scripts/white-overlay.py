from PIL import Image
from pathlib import Path
V=Path(__file__).resolve().parents[1];R=V.parents[1]
s=Image.open(R/'sources/reta2-7.img').convert('RGB');a=Image.open(V/'renders/white-source7.png');assert s.size==a.size==(1080,603)
b=Image.new('RGBA',a.size,(0,0,0,255));b.alpha_composite(a)
Image.blend(s,b.convert('RGB'),.5).save(V/'renders/white-source7-direct-50pct.png')
