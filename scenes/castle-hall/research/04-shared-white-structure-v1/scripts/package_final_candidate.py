from pathlib import Path
import json,hashlib,zipfile,datetime
from PIL import Image
R=Path(__file__).resolve().parents[1];D=R/'delivery_r2';D.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert 'EVIDENCE_FINISHED' in (R/'qa/finish_evidence.log').read_text()
models=json.loads((R/'models_frozen_sha256.json').read_text())
for name,m in models.items():assert sha(R/'models'/name)==m['sha256']
assert json.loads((R/'qa/input_freeze_recheck.json').read_text())['pass']
views=['fit_4528','fit_4529','holdout_4527','holdout_4509'];all_names=views+['normal_main','qa_arch_inside','qa_stair_return']
for name in all_names:
 for kind in ['raw','clean']:
  p=R/'renders'/(name+'_'+kind+'.png');m=json.loads(p.with_suffix('.json').read_text());assert sha(p)==m['sha256'];assert Image.open(p).size==(1180,664);assert m['model_sha256']==models['CastleHall_Shared_White_Candidate.blend']['sha256']
for name in views:
 for kind in ['raw','clean']:
  p=R/'qa'/('overlay50_'+name+'_'+kind+'.png');m=json.loads(p.with_suffix('.json').read_text());assert sha(p)==m['sha256']
base=[R/'QA_r2_更正与回归.md',R/'ISSUE_结构阶段说明.md',R/'README_结构候选与残差.md',R/'models_frozen_sha256.json',R/'source_and_view_ledger.json']
model=[R/'models'/n for n in models]+base+list((R/'scripts').glob('*.py'))
qa_json=[p for p in (R/'qa').glob('*.json') if p.name!='candidate_initial_geometry_audit.json']
model+=qa_json
refs=list((R/'inputs').glob('*'))+[R/'inputs_frozen_sha256.json',R/'source_and_view_ledger.json']
def comparegroup(names):
 files=[]
 for n in names:
  files+=list((R/'renders').glob(n+'_*'))+list((R/'qa').glob('overlay50_'+n+'_*'))+[R/'qa'/('compare_'+n+'_contact.jpg')]
 return files
fits=comparegroup(views[:2]);holdouts=comparegroup(views[2:]);inspection=[]
for n in all_names[4:]:inspection+=list((R/'renders').glob(n+'_*'))
inspection+=[p for p in (R/'qa').iterdir() if p.suffix in ['.png','.jpg','.svg','.md'] and not p.name.startswith(('overlay50_','compare_'))]+list((R/'qa/masks').glob('*'))+[R/'renders/preview_fit_4528_white.png']
regression=[p for p in (R/'regression').iterdir() if p.suffix in ['.json','.jpg','.png']]
groups={'Baseline_Regression':regression,'Models_and_Technical_QA':model,'Frozen_References':refs,'Fit_Comparisons':fits,'Heldout_Comparisons':holdouts,'Normal_and_Inspection':inspection}
unique=sorted(set(p for group in groups.values() for p in group),key=lambda p:str(p));assert all(p.is_file() for p in unique)
manifest={'stage':'Shared white structural candidate v1 QA r2: actual UV corner roundtrip + old/new same-condition regression; source acceptance false','frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in unique]};(R/'SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
# A separate explicitly named final figure inventory lets the archiver embed all final comparisons, not only the model.
figures=[]
for n in views:
 for rel,role in [('qa/compare_'+n+'_contact.jpg','source / cleaned render / direct raw overlay contact'),('qa/overlay50_'+n+'_raw.png','literal raw-render 50% overlay'),('qa/overlay50_'+n+'_clean.png','clean-render 50% overlay; secondary'),('renders/'+n+'_raw.png','raw source-camera render'),('renders/'+n+'_clean.png','OIDN presentation render')]:
  p=R/rel;figures.append({'path':rel,'role':role,'sha256':sha(p),'bytes':p.stat().st_size})
for rel in ['renders/normal_main_clean.png','qa/normal_and_internal_inspection.jpg','qa/fit_4528_tread_residuals.png','qa/holdout_4527_tread_residuals.png']:
 p=R/rel;figures.append({'path':rel,'role':'normal/technical/residual evidence; see caption','sha256':sha(p),'bytes':p.stat().st_size})
for p in sorted((R/'regression').glob('*')):
 if p.suffix in ['.jpg','.png']:figures.append({'path':str(p.relative_to(R)),'role':'QA r2 baseline / candidate same-condition regression; see individual metadata','sha256':sha(p),'bytes':p.stat().st_size})
(R/'ISSUE_figure_manifest.json').write_text(json.dumps({'source_acceptance':False,'model_sha256':models['CastleHall_Shared_White_Candidate.blend']['sha256'],'figures':figures},indent=2))
packages=[]
for label,files in groups.items():
 dest=D/('CastleHall_SharedWhite_v1_QAr2_'+label+'_20261010.zip')
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,6) as z:
  for p in sorted(set(files),key=lambda p:str(p)):z.write(p,str(p.relative_to(R)))
  z.write(R/'SHA256.json','SHA256.json');z.write(R/'ISSUE_figure_manifest.json','ISSUE_figure_manifest.json')
 assert dest.stat().st_size<18000000,(str(dest),dest.stat().st_size)
 with zipfile.ZipFile(dest) as z:assert z.testzip() is None
 packages.append({'file':dest.name,'bytes':dest.stat().st_size,'sha256':sha(dest)})
(D/'packages.json').write_text(json.dumps(packages,indent=2));print(json.dumps(packages,indent=2));print('ALL_PACKAGES_VERIFIED')
