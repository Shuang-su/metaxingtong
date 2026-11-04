from leaf_local_warp import Parameters, forward, inverse, jacobian_determinant
import random, json, math
from pathlib import Path

random.seed(110407)
rows=[]
for belly, shoulder in [(0,0),(-.08,0),(.08,0),(0,.08),(0,-.08),(.08,.08)]:
    p=Parameters(belly_dz=belly,shoulder_fraction=shoulder);p.validate()
    errors=[];dets=[]
    for _ in range(10000):
        v=(random.uniform(-5,5),random.uniform(-2,2),random.uniform(-.1,3))
        w=inverse(forward(v,p),p)
        errors.append(max(abs(v[i]-w[i]) for i in range(3)))
        dets.append(jacobian_determinant(v[0],p))
    for x in [-4.65,4.65]:
        for y in [-.1,0,.1]:
            assert forward((x,y,2),p)==(x,y,2)
    assert max(errors)<1e-12 and min(dets)>0
    rows.append(dict(belly_dz=belly,shoulder_fraction=shoulder,max_inverse_error=max(errors),min_determinant=min(dets)))
report=dict(scope='Pure mathematical point-map tests only; no recovered BLEND, source-image or production geometry validation.',random_points_per_case=10000,rows=rows,source_accepted=False,production_tested=False)
out=Path(__file__).resolve().parents[1]/'qa';out.mkdir(exist_ok=True)
(out/'warp-unit-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
