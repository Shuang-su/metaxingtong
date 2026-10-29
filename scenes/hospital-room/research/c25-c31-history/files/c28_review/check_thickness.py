# Uses only analysis definitions above the optimizer in compare_low_dof.
from pathlib import Path
exec(Path(__file__).with_name('compare_low_dof.py').read_text().split("bounds={'tilt_deg'")[0])
from PIL import Image
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks,peak_widths
fit=json.loads((O/'low_dof_comparison.json').read_text());par=fit['models']['tilt_deg+trim_dx']['parameters'];out={}
for k in keys:
 x=float(np.median(lc[k]['sample_x']));out[k]={'sample_x':x,'models':{}}
 for label,params in [('C27',{}),('tilt_trim',par)]:
  vv=transform(list(params.values()),list(params));q=projection(k,vv);hull=q[ConvexHull(q).vertices];ys=[a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]) for a,b in zip(hull,np.roll(hull,-1,axis=0)) if min(a[0],b[0])<=x<=max(a[0],b[0]) and abs(a[0]-b[0])>1e-9];out[k]['models'][label]={'top_y':min(ys),'bottom_y':max(ys),'vertical_thickness_px':max(ys)-min(ys)}
 # Compare local dark-ridge shape at given x; this is descriptive intensity, not opacity ground truth.
 im=np.array(Image.open(R/'inputs'/f['sources'][k]['name']).convert('RGB'),float).mean(2);xx=int(round(x));yy=np.arange(max(0,int(np.polyval(lc[k]['fit_y_ax_b'],x))-12),int(np.polyval(lc[k]['fit_y_ax_b'],x))+13);vals=im[yy,xx];out[k]['source_intensity_y']=yy.tolist();out[k]['source_intensity']=vals.tolist()
(O/'thickness_diagnosis.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:{a:b for a,b in d.items() if a in ['sample_x','models']} for k,d in out.items()},indent=2))
