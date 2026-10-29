from pathlib import Path
import runpy,itertools,json,numpy as np
from scipy.optimize import minimize_scalar
P=Path(__file__).resolve().parents[1];scope=runpy.run_path(str(P/'scripts/fit_bank1.py'));proj=scope['proj'];base=scope['obs'];rows=[]
for signs in itertools.product([-1,1],repeat=4):
 target={k:np.array(base[k],dtype=float)+2*np.array(signs[i*2:i*2+2]) for i,k in enumerate(['H','G'])};trials=[]
 for n in range(3):
  def fun(dx):return sum(np.sum((proj(k,n,dx)-target[k])**2) for k in ['H','G'])
  fit=minimize_scalar(fun,bounds=(-.18,0),method='bounded',options={'xatol':1e-10});trials.append((fit.fun,n,float(fit.x)))
 _,n,dx=min(trials);rows.append({'endpoint_perturbation_signs':list(signs),'removed_count':n,'trim':dx,'N642_endpoint_error_original_unperturbed_px':float(np.linalg.norm(proj('N642',n,dx)-base['N642']))})
out={'meaning':'Deterministic sensitivity to all 16 corners of +/-2px H/G endpoint boxes, NOT a statistical confidence interval; does not change chosen parameters','removed_counts':sorted(set(x['removed_count'] for x in rows)),'trim_range':[min(x['trim'] for x in rows),max(x['trim'] for x in rows)],'N642_endpoint_error_range':[min(x['N642_endpoint_error_original_unperturbed_px'] for x in rows),max(x['N642_endpoint_error_original_unperturbed_px'] for x in rows)],'cases':rows}
(P/'endpoint_sensitivity.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='cases'})
