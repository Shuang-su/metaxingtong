import numpy as np,json
from PIL import Image,ImageDraw
from pathlib import Path
D=Path(__file__).resolve().parent
src=np.array([[590,162],[595,257],[1030,99],[1055,200]],float);dst=np.array([[-1.045,3.58],[-1.045,3.12],[1.045,3.58],[1.045,3.12]])
def Hsolve(a,b):
 rows=[];rhs=[]
 for (u,v),(x,z)in zip(a,b):rows.extend([[u,v,1,0,0,0,-x*u,-x*v],[0,0,0,u,v,1,-z*u,-z*v]]);rhs.extend([x,z])
 return np.append(np.linalg.solve(rows,rhs),1).reshape(3,3)
H=Hsolve(src,dst);mask=np.array(Image.open(D/'LOW_LEFT_native_mask.png'))
# Existing R09b central board face coordinates, not measured source dimensions.
n=256;xx,zz=np.meshgrid(np.linspace(-.80465,.80465,n),np.linspace(4.45,2.88,n));world=np.stack([xx.ravel(),zz.ravel(),np.ones(n*n)])
def getlabels(h,scale=1,dx=0,dz=0):
 # Only proposed texture coordinate sensitivity, NEVER geometry/camera transforms.
 w=world.copy();w[0]=(w[0]-dx)/scale;w[1]=(w[1]-3.665-dz)/scale+3.665
 q=np.linalg.inv(h)@w;u=np.rint(q[0]/q[2]).astype(int);v=np.rint(q[1]/q[2]).astype(int);valid=(u>=0)&(u<1920)&(v>=0)&(v<1080);lab=np.full(n*n,4,dtype=np.uint8);lab[valid]=mask[v[valid],u[valid]];return lab.reshape(n,n)
base=getlabels(H);palette=np.array([[65,65,75],[40,210,95],[235,65,65],[255,195,0],[140,140,150]],np.uint8);out=Image.fromarray(palette[base]);out=out.resize((512,512),Image.Resampling.NEAREST);canvas=Image.new('RGB',(512,572),(20,20,20));canvas.paste(out,(0,60));dr=ImageDraw.Draw(canvas);dr.text((8,8),'CONDITIONAL UV MASK ONLY - NO SOURCE TEXTURE',fill='white');dr.text((8,25),'Green visible / red person / amber uncertainty',fill='white');dr.text((8,42),'Gray missing/outside. NOT measured full-board coverage.',fill='white');canvas.save(D/'conditional_uv_mask_analysis.png')
rng=np.random.default_rng(20261030);point=[]
for i in range(300):
 try:lab=getlabels(Hsolve(src+rng.uniform(-3,3,src.shape),dst));point.append(float(np.mean(lab==1)))
 except np.linalg.LinAlgError:pass
cases=[]
for scale in [.95,1,1.05]:
 for dx in [-.05,0,.05]:
  for dz in [-.05,0,.05]:
   lab=getlabels(H,scale,dx,dz);cases.append({'scale':scale,'dx':dx,'dz':dz,'usable_fraction_current_inferred_uv':float(np.mean(lab==1))})
res={'scope':'READ ONLY mathematical projection/mask feasibility. No texture generated, no model/camera modified.','source_anchor_pixel_coordinates':src.tolist(),'anchor_identity':'approximate centers of four protruding black circular units, NOT four poster corners','destination_working_xz':dst.tolist(),'H_source_to_working_xz':H.tolist(),'poster_face_R09b':{'x':[-.80465,.80465],'z':[2.88,4.45],'front_y':-.1255,'all_dimensions':'existing inferred working geometry, not source metric'},'mask_uv_grid':[n,n],'baseline_fractions':{str(k):float(np.mean(base==k))for k in range(5)},'manual_anchor_3px_perturbation_300_samples':{'usable_fraction_2_50_98_percentiles':np.percentile(point,[2,50,98]).tolist(),'is_confidence_interval':False},'systematic_working_stress_cases':cases,'stress_min_max':[min(q['usable_fraction_current_inferred_uv']for q in cases),max(q['usable_fraction_current_inferred_uv']for q in cases)],'limitations':'black units protrude ahead of poster plane; homography anchor centroid and exact shape errors; systematic scale/offset range arbitrary sensitivity stress not proved error bound; board top inferred; this is conditional placement not camera calibration'}
(D/'conditional_projection_parameters.json').write_text(json.dumps(res,indent=2));print(res['baseline_fractions'],res['manual_anchor_3px_perturbation_300_samples'],res['stress_min_max'])
