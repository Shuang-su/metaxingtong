import bpy,bmesh,json,numpy as np,hashlib
from pathlib import Path
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
R=Path(__file__).resolve().parents[1];I=R/'v2';O=R/'v2_clean';O.mkdir(exist_ok=True);names=['hospital_C25_structural_volume_CONDITIONAL.blend','hospital_C25_white_geometry_CONDITIONAL.blend'];D=[]
for name in names:
 p=I/name;bpy.ops.wm.open_mainfile(filepath=str(p));ob=bpy.data.objects['Chair • slim back support'];me=ob.data;E=np.array([list(e.vertices) for e in me.edges]);g=coo_matrix((np.ones(len(E)),(E[:,0],E[:,1])),shape=(len(me.vertices),len(me.vertices)));nc,lab=connected_components(g,directed=False);counts=np.bincount(lab);main=int(np.argmax(counts));drop=set(np.where(lab!=main)[0].tolist());bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();removed=[bm.verts[i] for i in drop];bmesh.ops.delete(bm,geom=removed,context='VERTS');result=bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,dist=1e-8,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();out=O/name;bpy.ops.wm.save_as_mainfile(filepath=str(out));D.append({'input':name,'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'original_components':int(nc),'component_vertex_counts':counts.tolist(),'kept_component':main,'discarded_vertices':len(drop),'cleaning':'Keep largest connected component; remove double vertices within1e-7 and degenerate edges within1e-8; no vertex smoothing or shape fitting','output_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
json.dump(D,open(O/'numerical_cleanup_manifest.json','w'),indent=2)
for n in ['panel_vertex_semantics.json','build_manifest.json']:(O/n).write_bytes((I/n).read_bytes())
