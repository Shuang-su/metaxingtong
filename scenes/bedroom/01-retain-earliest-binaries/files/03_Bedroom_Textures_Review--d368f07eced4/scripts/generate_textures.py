from PIL import Image,ImageDraw,ImageFilter
import numpy as np, os, json, math, shutil
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); out=root+'/textures';os.makedirs(out,exist_ok=True)
rng=np.random.default_rng(42); N=512;y,x=np.mgrid[0:N,0:N]
def save(name,rgb,rough=.7,height=None):
    a=np.uint8(np.clip(rgb,0,255));Image.fromarray(a,'RGB').save(out+'/'+name+'_BaseColor.png',optimize=True)
    n=rng.normal(0,1,(N,N));rr=np.uint8(np.clip(rough*255+n*2,0,255));Image.fromarray(rr,'L').save(out+'/'+name+'_Roughness.png',optimize=True)
    if height is None: height=rng.normal(0,.15,(N,N))
    gy,gx=np.gradient(height.astype(float));vec=np.dstack([-gx,-gy,np.ones((N,N))]);vec/=np.linalg.norm(vec,axis=2)[:,:,None]
    Image.fromarray(np.uint8(np.clip((vec*.5+.5)*255,0,255)),'RGB').save(out+'/'+name+'_Normal.png',optimize=True)
fabric=(np.sin(x*np.pi)*.5+np.sin(y*2.08)*1.8+np.sin(x*2.13)*1.8+rng.normal(0,1.3,(N,N)))
for name,col,rough in [('Linen',[187,175,161],.89),('Rug',[183,166,145],.96),('Wall',[172,151,132],.86),('Cabinet',[216,211,200],.46),('Orange',[181,91,30],.32)]:
    noise=fabric if name in ['Linen','Rug'] else rng.normal(0,.7,(N,N)); save(name,np.array(col)[None,None,:]+noise[:,:,None],rough,noise*.06)
grain=np.sin(y*.105 + 4*np.sin(x*.009)+np.sin(x*.073)) + .4*np.sin(y*.48+2*np.sin(x*.025))+rng.normal(0,.16,(N,N))
wood=np.array([135,98,65])[None,None,:]+grain[:,:,None]*np.array([9,7,5]);save('Oak',wood,.61,grain*.08)
checker=((x//64+y//64)%2);c=checker[:,:,None]*np.array([185,176,163])+(1-checker[:,:,None])*np.array([15,14,14]);c=c+fabric[:,:,None]*.7
save('Checker',c,.91,fabric*.05)
leaf=np.array([34,67,31])[None,None,:]+rng.normal(0,1,(N,N))[:,:,None]*2+np.sin(y*.2+x*.4)[:,:,None]*2
save('Leaf',leaf,.4,np.sin(y*.2+x*.4)*.15)
# Original drawn approximation of the visible red comic wall print, not a screenshot backdrop.
s=512;im=Image.new('RGB',(s,s),(170,31,41));d=ImageDraw.Draw(im)
d.polygon([(0,0),(175,0),(512,185),(512,230)],fill=(185,37,71));d.polygon([(0,360),(512,125),(512,512)],fill=(186,37,28))
def star(cx,cy,r):
    p=[(cx+math.cos(i*math.pi/5-math.pi/2)*(r if i%2==0 else r*.42),cy+math.sin(i*math.pi/5-math.pi/2)*(r if i%2==0 else r*.42)) for i in range(10)];d.polygon(p,fill=(238,195,61),outline=(30,22,22),width=6)
star(92,310,41);star(434,258,43)
d.rounded_rectangle((139,42,386,257),80,fill=(228,218,193),outline=(22,20,23),width=9)
d.polygon([(144,172),(89,203),(37,174),(136,112),(160,132),(97,175),(134,183)],fill=(230,203,184),outline=(22,20,23),width=8)
d.ellipse((166,105,347,267),fill=(228,196,180),outline=(24,18,20),width=7)
d.polygon([(146,81),(212,73),(230,143),(264,89),(280,153),(348,133),(337,68),(284,41),(214,43)],fill=(230,222,205),outline=(24,19,22),width=7)
d.polygon([(184,263),(304,256),(345,441),(160,451)],fill=(175,25,35),outline=(21,17,18),width=8)
d.line([(183,271),(234,304),(307,265)],fill=(237,216,180),width=13)
d.ellipse((204,180,217,195),fill=(26,23,27));d.ellipse((289,179,302,194),fill=(26,23,27));d.arc((236,204,266,229),0,180,fill=(23,18,19),width=5)
d.polygon([(369,362),(509,315),(503,511),(357,507)],fill=(229,218,195),outline=(20,18,20),width=8)
d.text((375,416),'WOW!',fill=(28,22,25),stroke_width=1)
d.text((17,15),'XINGTONG / POP',fill=(242,198,104));d.text((20,485),'RECONSTRUCTED GRAPHIC',fill=(232,188,166))
im.save(out+'/Poster_approximation.png',optimize=True)
# Small framed character study, also hand drawn approximation.
im=Image.new('RGB',(256,300),(209,198,172));d=ImageDraw.Draw(im);d.ellipse((35,52,220,251),fill=(229,218,207),outline=(105,96,94),width=4);d.polygon([(38,75),(106,36),(179,43),(221,102),(207,116),(185,86),(171,133),(143,85),(115,125),(98,85),(57,110)],fill=(219,221,213),outline=(123,112,97));d.ellipse((75,139,94,172),fill=(34,157,199));d.ellipse((167,139,186,172),fill=(34,157,199));d.arc((109,196,147,214),0,180,fill=(120,89,79),width=3);im.save(out+'/Portrait_approximation.png',optimize=True)
for f in ['home_3007.jpg','home_3040.jpg','home_3010.jpg','home_674.jpg','home_911.jpg','home_4503.jpg','home_5420.jpg']:
    shutil.copy('/workspace/shared/xingtong_batch03/screenshots/'+f,root+'/references/'+f)
json.dump({'resolution':512,'sets':['Linen','Rug','Wall','Cabinet','Orange','Oak','Checker','Leaf'],'channels':['BaseColor','Roughness','Normal'],'source':'Procedurally authored seamless-ish surfaces; artwork drawn approximation. No room screenshots used as material.'},open(root+'/analysis/texture_manifest.json','w'),indent=2)
