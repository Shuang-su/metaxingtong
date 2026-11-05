import bpy,numpy as np,json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent.parent
src=P.parent/'cyber-roof-stage-20261105/models/roof-r05.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));o=bpy.data.objects['ROOF_MAIN closed shell'];m=o.data;V=np.array([list(o.matrix_world@v.co) for v in m.vertices]);N=65*33
S=np.array([[11.4*u*(.74+.26*abs(t)),5.5+3*t,6+2.5*(1-abs(t))**2+.8*abs(u)**7*t*t] for t in np.linspace(-1,1,33) for u in np.linspace(-1,1,65)])
assert len(V)==2*N
faces=[list(p.vertices) for p in m.polygons];top=[f for f in faces if max(f)<N];bottom=[f for f in faces if min(f)>=N];rim=[f for f in faces if min(f)<N<=max(f)]
def cycle(f):return min(tuple(f[i:]+f[:i]) for i in range(len(f)))
bottomset={cycle(list(reversed([i-N for i in f]))) for f in bottom}
edges={tuple(sorted(e.vertices)) for e in m.edges};cross=[e for e in edges if e[0]<N<=e[1]]
# Reconstruct only the exact original open surface for evaluating its discrete normals and default Solidify, not a candidate.
orig=bpy.data.meshes.new('read-only baseline temporary');orig.from_pydata(S.tolist(),[],top);orig.update();norm=np.array([list(v.normal) for v in orig.vertices]);D=V[N:]-V[:N];L=np.linalg.norm(D,axis=1);cos=np.clip(np.sum(-D*norm,axis=1)/(L*np.linalg.norm(norm,axis=1)),-1,1)
tmp=bpy.data.objects.new('baseline exact construction temporary',orig);bpy.context.collection.objects.link(tmp);mod=tmp.modifiers.new('defaults','SOLIDIFY');mod.thickness=.12
settings={k:getattr(mod,k) for k in ['thickness','offset','use_even_offset','use_quality_normals','use_rim','use_rim_only','solidify_mode']}
bpy.context.view_layer.update();evalobj=tmp.evaluated_get(bpy.context.evaluated_depsgraph_get());ev=evalobj.to_mesh();EV=np.array([list(v.co) for v in ev.vertices]);regen=float(np.max(np.linalg.norm(EV-V,axis=1))) if EV.shape==V.shape else None
rows=[]
for k in range(N):
 rows.append({'top':k,'inner':k+N,'u':float(-1+2*(k%65)/64),'t':float(-1+2*(k//65)/32),'top_xyz':V[k].tolist(),'inner_xyz':V[k+N].tolist(),'paired_vector':D[k].tolist(),'length':float(L[k]),'inward_original_vertex_normal_angle_degrees':float(np.degrees(np.arccos(cos[k])))})
r={'input':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'scope':'baseline only; no alternate parameter, model save or render','vertices':len(V),'pairs':N,'faces_top_inner_rim':[len(top),len(bottom),len(rim)],'all_top_faces_reversed_paired_inner':all(cycle(f) in bottomset for f in top),'cross_edges_count':len(cross),'all_cross_edges_are_exact_pairs':all(b==a+N for a,b in cross),'rim_faces_all_two_exact_pairs':all(len(f)==4 and len({i%N for i in f})==2 for f in rim),'outer_surface_formula_max_error':float(np.max(np.linalg.norm(V[:N]-S,axis=1))),'paired_lengths_minmax':[float(L.min()),float(L.max())],'max_xy_offset':float(np.max(np.linalg.norm(D[:,:2],axis=1))),'max_angle_to_negative_original_discrete_vertex_normal_degrees':float(np.degrees(np.arccos(cos)).max()),'max_vector_error_vs_minus_point12_original_normal':float(np.linalg.norm(D+.12*norm,axis=1).max()),'original_default_solidify_settings':settings,'baseline_regenerated_vertex_max_error':regen,'baseline_regenerated_faces_exact_order':faces==[list(p.vertices) for p in ev.polygons],'baseline_regenerated_oriented_face_cycles_equal':sorted(cycle(f) for f in faces)==sorted(cycle(list(p.vertices)) for p in ev.polygons),'rows':rows}
(P/'results/pairs.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='rows'},indent=2))
