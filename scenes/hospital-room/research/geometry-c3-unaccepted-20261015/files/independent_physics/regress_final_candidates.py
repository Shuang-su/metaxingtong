"""Independent read-only regression for P0/P1/C2 candidate .blends against D.
Usage blender -b --python regress_final_candidates.py -- candidate.blend [...]
Checks real evaluated world meshes, contact classification, sofa support contact,
visibility flags and source immutability. Never saves a Blender scene.
"""
import bpy,json,sys,hashlib,math,time
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
ns={'__file__':str(OUT/'audit_physics.py')}
exec(Path(ns['__file__']).read_text().split('for s in sys.argv[sys.argv.index')[0],ns)
extract,record_pair,bounds=ns['extract'],ns['record_pair'],ns['bounds'];CN=ns['CURTAIN'];SN='Sofa • reclined back cushion 1'
BASE=Path('/workspace/scratch/fa58bfcf0425/hospital_anchor_preparation_20261014/restored/hospital_D_before_J1_cameras.blend')

def visibility(o):
 return {'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hidden_in_view_layer':o.hide_get(),'visible_camera':getattr(o,'visible_camera',None),'visible_shadow':getattr(o,'visible_shadow',None),'visible_diffuse':getattr(o,'visible_diffuse',None),'visible_glossy':getattr(o,'visible_glossy',None),'visible_transmission':getattr(o,'visible_transmission',None)}
def mat_sig(m):
 r={'name':m.name,'diffuse_color':list(m.diffuse_color),'use_nodes':m.use_nodes}
 if m.use_nodes:
  r['nodes']=[]
  for n in m.node_tree.nodes:
   d={'name':n.name,'type':n.type,'inputs':{}}
   for inp in n.inputs:
    if hasattr(inp,'default_value'):
     v=inp.default_value
     if isinstance(v,(str,int,float,bool)):d['inputs'][inp.name]=v
     elif hasattr(v,'__iter__'):
      try:d['inputs'][inp.name]=list(v)
      except:pass
   r['nodes'].append(d)
 return r

def load(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get();rr={o.name:extract(o,dg) for o in bpy.data.objects if o.type=='MESH'}
 meta={'visibility':{o.name:visibility(o) for o in bpy.data.objects if o.type=='MESH'},'collections':{c.name:{'hide_render':c.hide_render,'hide_viewport':c.hide_viewport} for c in bpy.data.collections},'materials':{m.name:mat_sig(m) for m in bpy.data.materials},'object_material_names':{o.name:[m.name for m in o.data.materials if m] for o in bpy.data.objects if o.type=='MESH'},'geometry_hash':{n:hashlib.sha256(json.dumps({'v':[list(x) for x in r['verts']],'f':r['triangles']},sort_keys=True).encode()).hexdigest() for n,r in rr.items()}}
 return rr,meta

def all_contacts(rr,focus):
 pairs=[];seen=set()
 for n in focus:
  if n not in rr:continue
  for other,b in rr.items():
   if other==n:continue
   key=tuple(sorted((n,other)))
   if key in seen:continue
   seen.add(key);p=record_pair(rr[n],b)
   if p:pairs.append(p)
 return pairs

def sampled_min_distance(a,b):
 best=None;points=None
 for first,second in ((a,b),(b,a)):
  for p in first['verts']:
   hit,normal,index,d=second['bvh'].find_nearest(p)
   if d is not None and (best is None or d<best):best=float(d);points=[list(p),list(hit)]
 return {'vertex_to_opposite_triangle_surface_distance_upper_bound':best,'witness_points':points,'note':'Not an exact global triangle-triangle minimum and not load-bearing simulation.'}

base_sha=hashlib.sha256(BASE.read_bytes()).hexdigest();br,bm=load(BASE);base_sofa=all_contacts(br,[SN])
for arg in sys.argv[sys.argv.index('--')+1:]:
 path=Path(arg);sha=hashlib.sha256(path.read_bytes()).hexdigest();t=time.time();rr,mm=load(path)
 added=sorted(set(rr)-set(br));removed=sorted(set(br)-set(rr));changed=sorted(n for n in set(rr)&set(br) if mm['geometry_hash'][n]!=bm['geometry_hash'][n])
 focus=sorted(set(changed+added+[CN,SN]));pairs=all_contacts(rr,focus);curtain_pairs=[p for p in pairs if CN in (p['a'],p['b'])];sofa_pairs=[p for p in pairs if SN in (p['a'],p['b'])]
 vischanges={n:{'before':bm['visibility'][n],'after':mm['visibility'][n]} for n in set(rr)&set(br) if bm['visibility'][n]!=mm['visibility'][n]}
 colch={n:{'before':bm['collections'].get(n),'after':mm['collections'].get(n)} for n in set(bm['collections'])|set(mm['collections']) if bm['collections'].get(n)!=mm['collections'].get(n)}
 matchanges=[n for n in set(bm['materials'])&set(mm['materials']) if bm['materials'][n]!=mm['materials'][n]]
 deltas={}
 for n in changed:
  old,new=br[n],rr[n]
  if len(old['verts'])==len(new['verts']):
   ds=[b-a for a,b in zip(old['verts'],new['verts'])];deltas[n]={'per_vertex_displacement_bounds':bounds(ds),'maximum_vertex_displacement_length':max(x.length for x in ds),'new_bounds':new['meta']['bounds']}
  else:deltas[n]={'vertex_count_changed':[len(old['verts']),len(new['verts'])],'new_bounds':new['meta']['bounds']}
 bymin=min(r['meta']['bounds'][0][1] for n,r in rr.items() if n.startswith('Blind'));cymax=rr[CN]['meta']['bounds'][1][1]
 support=[]
 for n,r in rr.items():
  if n.startswith('Sofa') and n!=SN:
   bpair=next((p for p in base_sofa if n in (p['a'],p['b'])),None);apair=next((p for p in sofa_pairs if n in (p['a'],p['b'])),None)
   support.append({'other':n,'before_pair':bpair,'after_pair':apair,'after_distance':sampled_min_distance(rr[SN],r) if apair is None else None,'before_distance':sampled_min_distance(br[SN],br[n]) if bpair is None and n in br else None})
 report={'candidate':str(path),'candidate_sha256_before':sha,'base':str(BASE),'base_sha256':base_sha,'source_fidelity_accepted':False,'physical_contact_audit_not_source_or_support_engineering_acceptance':True,'units':'arbitrary D scene units','added_meshes':added,'removed_meshes':removed,'changed_meshes':changed,'changed_mesh_details':deltas,'object_visibility_changes':vischanges,'collection_visibility_changes':colch,'existing_material_parameter_changes':matchanges,'added_mesh_visibility':{n:mm['visibility'][n] for n in added},'curtain_bounds':rr[CN]['meta']['bounds'],'global_y_clearance_curtain_to_blinds_and_cords':bymin-cymax,'curtain_all_scene_contacts':curtain_pairs,'curtain_strict_surface_crossing_object_count':sum(p['strict_transverse_crossing_pairs']>0 for p in curtain_pairs),'changed_and_added_mesh_contacts':pairs,'sofa_back_cushion_1_contact_comparison':support,'objects':[r['meta'] for r in rr.values()],'method':'Evaluated world meshes and zero-epsilon BVH with strict transverse triangle-edge crossings >1e-7; zero-AABB-depth contacts retained as contact rather than interpenetration; architectural/cushion seams interpreted separately.','source_unchanged':base_sha==hashlib.sha256(BASE.read_bytes()).hexdigest(),'candidate_unchanged':sha==hashlib.sha256(path.read_bytes()).hexdigest(),'seconds':time.time()-t}
 (OUT/(path.stem+'_final_regression.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False))
 export={n:{'vertices_world':[list(v) for v in rr[n]['verts']],'triangles':rr[n]['triangles']} for n in focus if n in rr}
 (OUT/(path.stem+'_changed_evaluated_world_meshes.json')).write_text(json.dumps(export,ensure_ascii=False))
 print(path.stem,'changed',len(changed),'added',len(added),'curtain crossings',report['curtain_strict_surface_crossing_object_count'],'clearance',report['global_y_clearance_curtain_to_blinds_and_cords'],'visibilitychanges',len(vischanges),'seconds',report['seconds'],flush=True)
