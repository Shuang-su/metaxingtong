import bpy,json,csv,math
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];Q=R/'qa'
bpy.ops.wm.open_mainfile(filepath=str(R/'stage-02-material-candidate/campus-courtyard_material.blend'))
out=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 m=o.data;m.calc_loop_triangles();n=len(m.vertices);parent=list(range(n))
 def find(a):
    while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
    return a
 for e in m.edges:
    a,b=map(find,e.vertices)
    if a!=b:parent[b]=a
 vv=np.array([tuple(o.matrix_world@v.co) for v in m.vertices],dtype=np.float64);tt=np.array([t.vertices[:] for t in m.loop_triangles]);a,b,c=vv[tt[:,0]],vv[tt[:,1]],vv[tt[:,2]];vol=np.einsum('ij,ij->i',a,np.cross(b,c))/6
 roots=np.array([find(int(i)) for i in tt[:,0]]);tot=np.bincount(roots,weights=vol,minlength=n);used=np.unique(roots);out.append({'id':o.name,'closed_primitive_components':len(used),'negative_volume_components':int(np.sum(tot[used]<-1e-8)),'near_zero_volume_components':int(np.sum(np.abs(tot[used])<1e-8)),'minimum_component_signed_volume':float(tot[used].min()),'scope':'orientation check for each disconnected closed primitive; intentionally intersecting assembly pieces not unioned'})
(Q/'component_normals.json').write_text(json.dumps(out,indent=2))
treads=list(csv.DictReader((Q/'stair_tread_instances.csv').open()));obj=bpy.data.objects['STAIR-01'];checks=[]
for row in treads:
 vv=np.array([tuple(obj.matrix_world@obj.data.vertices[i].co) for i in range(int(row['mesh_vertex_start']),int(row['mesh_vertex_end_exclusive']))]);expected=np.array([float(row['x']),float(row['y']),float(row['top_z'])]);actual=np.r_[vv[:,:2].mean(axis=0),vv[:,2].max()];err=float(np.max(np.abs(expected-actual)));checks.append({'id':row['id'],'vertices':len(vv),'expected_xyz_top':expected.tolist(),'actual_xyz_top':actual.tolist(),'max_error':err,'pass':err<1e-4})
(Q/'stair_tread_vertex_validation.json').write_text(json.dumps(checks,indent=2))
ground=bpy.data.objects['SITE-PAVERS'];contacts=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith(('TREE-','TREEBED-','BENCH-','LAMP-','HOOP-','STAIR-')):continue
 z=min((o.matrix_world@v.co).z for v in o.data.vertices);contacts.append({'id':o.name,'minimum_z':z,'base_near_or_crosses_ground':z<=.011,'scope':'lower-bound only; not complete support-contact certification'})
(Q/'base_contact_bounds.json').write_text(json.dumps(contacts,indent=2))
print('NORMAL_SUPPORT_COMPLETE',json.dumps({'negative_components':sum(x['negative_volume_components'] for x in out),'tread_instance_positions_pass':all(x['pass'] for x in checks),'treads':len(checks)}))
