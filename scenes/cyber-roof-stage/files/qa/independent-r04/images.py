from PIL import Image
import numpy as np,pathlib,json,hashlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/cyber-roof-stage-20261105');Q=pathlib.Path(__file__).parent;files=list((P/'renders').glob('*.png'));rows=[]
for f in sorted(files):
 im=Image.open(f);im.load();a=np.asarray(im);rows.append({'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'size':list(im.size),'mode':im.mode,'alpha_range':[int(a[:,:,3].min()),int(a[:,:,3].max())]if a.ndim==3 and a.shape[2]==4 else None})
checks=[]
for src,mat,white in [('11','source11-r03.png','source11-white-r03.png'),('10','source10-auxiliary-r03.png','source10-auxiliary-r03-white.png')]:
 a=np.asarray(Image.open(P/'sources'/f'{src}.webp').convert('RGB')).astype(np.uint16)
 for mode,fn,overlay in [('material',mat,f'source{src}-direct50-r03.png'),('white',white,f'source{src}-white-direct50-r03.png')]:
  b=np.asarray(Image.open(P/'renders'/fn).convert('RGB')).astype(np.uint16);c=np.asarray(Image.open(P/'renders'/overlay).convert('RGB')).astype(np.int16);checks.append({'source':src,'mode':mode,'formula':'floor((RGB_source+RGB_render)/2), no resize/warp','size_equal':a.shape==b.shape==c.shape,'max_array_error':int(np.abs(((a+b)//2).astype(np.int16)-c).max())})
# each contact cell must be original 796x448 pixels, label bands excluded
boards=[]
for white in [False,True]:
 sheet=np.asarray(Image.open(P/'renders'/('white-check-contact-sheet.png'if white else 'check-contact-sheet.png')).convert('RGB'));fs=sorted(f for f in (P/'renders').glob('check-*.png')if ('-white.png'in f.name)==white and 'contact'not in f.name)
 for i,f in enumerate(fs):
  a=np.asarray(Image.open(f).convert('RGB'));x=(i%2)*796;y=(i//2)*478+30;b=sheet[y:y+448,x:x+796];boards.append({'file':f.name,'same_cell':a.shape==b.shape and bool(np.array_equal(a,b))})
(Q/'image-integrity.json').write_text(json.dumps({'files':rows,'direct50':checks,'board_cells':boards,'main_alias':(P/'renders/main-candidate-r04.png').read_bytes()==(P/'renders/check-01-front-oblique.png').read_bytes()if(P/'renders/main-candidate-r04.png').exists()else None},indent=2));print(checks,boards)
