import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];m=json.loads((R/'analysis/trial_b_manifest.json').read_text());p=Path(m['file']);assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'];bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;cam=bpy.data.objects['R05_J_LOCAL_UNRESOLVED_BAY']
def bounds(o):
 a=[o.matrix_world@v.co for v in o.data.vertices];return [(min(v[k] for v in a),max(v[k] for v in a)) for k in range(3)]
def proj(p):
 q=world_to_camera_view(s,cam,Vector(p));return [q.x*1180,(1-q.y)*664]
# Source J independently read: dark sash body center y394+-4 viewport; widthwise bright core77+-1px.
# Same-camera projection solves relative shared dimensions; focal/absolute scale remains conditional.
sash=bpy.data.objects['Window mid sash.002'];bb=bounds(sash)
# Select the left-side sash closest to local bay y=-.9 without relying on suffix.
sash=min((o for o in s.objects if o.name.startswith('Window mid sash') and sum(bounds(o)[0])/2<0),key=lambda o:abs(sum(bounds(o)[1])/2+.9));bb=bounds(sash);x,y,z=[sum(b)/2 for b in bb]
lo,hi=1.08,1.725
for _ in range(50):
 zmid=(lo+hi)/2
 if proj([x,y,zmid])[1]>367:lo=zmid
 else:hi=zmid
newz=(lo+hi)/2
# Black physical main band ~14px. Avoid counting blue reflected edge; target thickness 0.030 working units.
changed=[]
for o in s.objects:
 if o.type!='MESH':continue
 if not o.name.startswith(('Window mid sash','Window head warm strip')):continue
 bb=bounds(o);center=Vector([sum(b)/2 for b in bb]);inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  q=o.matrix_world@v.co
  if o.name.startswith('Window mid sash'):q.z=newz+(q.z-center.z)*(.030/(bb[2][1]-bb[2][0]))
  elif o.name.startswith('Window head warm strip diffuser'):q.y=center.y+(q.y-center.y)*(.150/.290)
  else:q.y=center.y+(q.y-center.y)*(.190/.350)
  v.co=inv@q
 changed.append(o.name)
# Keep lighting energy and LIGHT geometry, cameras, shell and every table untouched.
s['Candidate_status']='r05 C shared sash and headbar proportions trial; source precision NOT passed; J focal24 gauge and bay unresolved.'
# Explicit table visibility evidence, without inferring source foreground object identity.
tables=[]
for o in s.objects:
 if o.type=='MESH' and 'rounded wood table' in o.name:
  bb=bounds(o); pp=[proj(o.matrix_world@Vector(v)) for v in o.bound_box]
  tables.append({'name':o.name,'world_bounds':bb,'J_projected_bbox':[min(a[0] for a in pp),min(a[1] for a in pp),max(a[0] for a in pp),max(a[1] for a in pp)]})
(R/'analysis/table_entity_visibility.json').write_text(json.dumps({'tables':tables,'count':len(tables),'source_foreground':'Gray rectangular surface with a black raised handle; identification as fixed booth table unsupported. No added/moved/deleted/hidden tables.'},indent=2))
out=R/'trial_c_shared.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));h=hashlib.sha256(out.read_bytes()).hexdigest();dest=R/f'trial_c_shared_{h[:12]}.blend';out.rename(dest);dest.chmod(0o444)
data={**m,'file':str(dest),'sha256':h,'parent_trial_b_sha256':m['sha256'],'c_only_changed_objects':changed,'sash_z':newz,'sash_thickness':.030,'head_diffuser_length':.150,'head_housing_length':.190,'dimension_scope':'All 12 fixtures/sashes share same revision. Relative source proportions at fixed windowwidth1.232 gauge; camera and absolute scale nonunique. Headbar trial length derived from actual trialB projection about148px vs source77px.','geometry_unchanged_from_trial_a':False,'status':'frozen review trial C, source precision not accepted'};data['parent_b_geometry_vertex_hash']=data.pop('geometry_vertex_hash');data['parent_b_changed_objects']=data.pop('changed_objects');data['changed_objects']=changed;data['caveat']='J focal24 gauge; unresolved bay; C sash/light fitted not heldout';(R/'analysis/trial_c_manifest.json').write_text(json.dumps(data,indent=2));print(dest,h,'sash',newz, 'tables',len(tables))
