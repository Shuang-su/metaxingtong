# Conditional single-focal-length diagnostic, no geometry fitting.
import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from pathlib import Path
D=Path(__file__).resolve().parents[1]
# Axis estimates on near visible cap/base support and next inner-column cap/base.
# They are image silhouette estimates, NOT metrically known surface vertices.
obj=np.array([[0,0,0],[0,0,4.35],[3,0,0],[3,0,4.35]],float)
uv=np.array([[3210,1810],[3210,615],[2580,1600],[2580,750]],float)
f=4000.;center=np.array([1920.,1080.]);C=np.array([-6.,10.,3.]);fw=np.array([1.5,0,2.])-C;fw/=np.linalg.norm(fw);right=np.cross(fw,[0,0,1]);right/=np.linalg.norm(right);down=np.cross(fw,right);R=np.array([right,down,fw]);t=-R@C
p0=np.r_[Rotation.from_matrix(R).as_rotvec(),t]
def project(p):
 xyz=obj@Rotation.from_rotvec(p[:3]).as_matrix().T+p[3:];return xyz[:,:2]/xyz[:,2,None]*f+center
res=least_squares(lambda p:(project(p)-uv).ravel()/20,p0,max_nfev=500)
R=Rotation.from_rotvec(res.x[:3]).as_matrix();t=res.x[3:];pr=project(res.x)
out={'status':'single-source four soft axis estimates conditional diagnostic, NOT source calibration','source':'BV1mT411V72s_1842.088867_4k.png','source_dimensions':[3840,2160],'f_pixels_work_assumption':f,'principal_point_work_assumption':center.tolist(),'rotation_world_to_opencv':R.tolist(),'translation_world_to_opencv':t.tolist(),'camera_location':(-R.T@t).tolist(),'anchors':[{'name':n,'model':a.tolist(),'source':b.tolist(),'projected':c.tolist(),'residual_px':float(np.linalg.norm(b-c)),'uncertainty_px':20} for n,a,b,c in zip(['near_base_axis','near_cap_axis','next_inner_base_axis','next_inner_cap_axis'],obj,uv,pr)],'limitations':['cap/base axis pixels are estimated and source column height not proven same model landmark','four coplanar estimated axes do not determine unique focal length/physical scale','no geometry changed; no same-instance cross-source validation; 4000px is fixed illustrative assumption not true calibration']}
(D/'qa/near-bay-work-camera.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
