import bpy,json,hashlib,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];base=R.parent/'castle_hall_fullroom/models/Xingtong_Castle_Hall_FullRoom.blend'
def inv():
 d={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  v=np.unique(np.round(np.array([list(o.matrix_world@v.co) for v in o.data.vertices]),5),axis=0);v[v==0]=0;d[o.name]=hashlib.sha256(v.astype('<f8').tobytes()).hexdigest()
 return d
bpy.ops.wm.open_mainfile(filepath=str(base));a=inv();bpy.ops.wm.open_mainfile(filepath=str(R/'models/CastleHall_Shared_White_Candidate.blend'));b=inv();out={'baseline_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256((R/'models/CastleHall_Shared_White_Candidate.blend').read_bytes()).hexdigest(),'unchanged_count':sum(a[k]==b[k] for k in a.keys()&b.keys()),'modified_existing':[k for k in a.keys()&b.keys() if a[k]!=b[k]],'removed':sorted(a.keys()-b.keys()),'added':sorted(b.keys()-a.keys()),'note':'World-vertex set comparison at 1e-5 nominal units; materials intentionally ignored. No per-view changes.'};out['modified_existing'].sort();out['images']=[{'name':i.name,'packed':bool(i.packed_file),'filepath':i.filepath} for i in bpy.data.images if i.name not in ['Render Result','Viewer Node']];(R/'qa/baseline_candidate_geometry_diff.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
