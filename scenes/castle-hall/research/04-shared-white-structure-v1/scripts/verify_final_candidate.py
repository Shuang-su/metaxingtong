import bpy,bmesh,math,json,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; M=R/'models';out={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory():
 d={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();a=np.unique(np.round(np.array([list(o.matrix_world@v.co) for v in o.data.vertices]),5),axis=0);a[a==0]=0
  d[o.name]={'triangles':len(o.data.loop_triangles),'unique_positions':len(a),'position_sha_1e5':hashlib.sha256(a.astype('<f8').tobytes()).hexdigest(),'uv':bool(o.data.uv_layers)}
 return d
bpy.ops.wm.open_mainfile(filepath=str(M/'CastleHall_Shared_White_Candidate.blend'));S=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();a=inventory()
out['white_sha256']=sha(M/'CastleHall_Shared_White_Candidate.blend');out['mesh_count']=len(a);out['triangles']=sum(v['triangles'] for v in a.values());out['mesh_issues']=[];out['hidden_meshes']=[];out['animated_objects']=[]
for o in S.objects:
 if o.animation_data:out['animated_objects'].append(o.name)
 if o.type!='MESH':continue
 if o.hide_render or o.hide_viewport or o.hide_get():out['hidden_meshes'].append(o.name)
 bm=bmesh.new();bm.from_mesh(o.data);d={'name':o.name,'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True),'degenerate':sum(f.calc_area()<1e-10 for f in bm.faces)};bm.free()
 if d['boundary'] or d['nonmanifold'] or d['signed_volume']<=0 or d['degenerate']:out['mesh_issues'].append(d)
out['all_uv']=all(v['uv'] for v in a.values());out['aperture_grid']=[]
for y in np.linspace(.65,2.87,13):
 for z in np.linspace(.35,3.62,19):
  if z>2.4 and (y-1.76)**2+(max(0,z-2.55))**2>1.12**2:continue
  hit,p,n,i,o,m=S.ray_cast(deps,Vector((6.58,float(y),float(z))),Vector((1,0,0)),distance=.91)
  out['aperture_grid'].append({'y':float(y),'z':float(z),'blocked':bool(hit),'first':o.name if hit else None})
out['aperture_blocked']=[r for r in out['aperture_grid'] if r['blocked']]
out['beyond_opening_rays']=[]
for y in [.8,1.76,2.7]:
 for z in [.4,1,2,3]:
  h,p,n,i,o,m=S.ray_cast(deps,Vector((6.58,y,z)),Vector((1,0,0)),distance=8)
  out['beyond_opening_rays'].append({'origin':[6.58,y,z],'object':o.name if h else 'ESCAPE','at':list(p) if h else None})
out['tread_support']=[]
for k in range(8):
 x=7.36+(k+.5)*.33;expected=(k+1)*.18;h,p,n,i,o,m=S.ray_cast(deps,Vector((x,1.76,expected+.08)),Vector((0,0,-1)),distance=.3)
 out['tread_support'].append({'tread':k+1,'expected_z':expected,'object':o.name if h else None,'actual_z':float(p.z) if h else None,'pass':bool(h and o.name=='RIGHT_STAIR_monolithic_8_treads' and abs(p.z-expected)<1e-4)})
# Finite-shell rays supplement (not replace) explicit mesh/aperture checks; props can occlude shell.
out['enclosure_samples']=[]
for loc in [(0,3,1.6),(0,15,2.1),(8.6,1.76,2.5),(10.55,1.76,2.5)]:
 escaped=[]
 for j in range(512):
  z=1-2*(j+.5)/512;r=math.sqrt(1-z*z);phi=j*math.pi*(3-math.sqrt(5));d=Vector((r*math.cos(phi),r*math.sin(phi),z));h,p,n,i,o,m=S.ray_cast(deps,Vector(loc),d,distance=100)
  if not h:escaped.append(list(d))
 out['enclosure_samples'].append({'origin':loc,'rays':512,'escaped':escaped})
out['normal_main_camera']=list(bpy.data.objects['CANDIDATE_NORMAL_MAIN'].location)
out['geometry_signature']=hashlib.sha256(json.dumps(a,sort_keys=True).encode()).hexdigest();(R/'qa/white_mesh_inventory.json').write_text(json.dumps(a,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(M/'CastleHall_Shared_Structure_Candidate.blend'));s=inventory();out['structure_white_same_geometry']=s==a
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(M/'CastleHall_Shared_White_Candidate.glb'));g=inventory()
out['glb']={'sha256':sha(M/'CastleHall_Shared_White_Candidate.glb'),'meshes':len(g),'triangles':sum(v['triangles'] for v in g.values()),'same_names':set(a)==set(g),'all_uv':all(v['uv'] for v in g.values()),'position_hash_differences':[k for k in a.keys()&g.keys() if a[k]['position_sha_1e5']!=g[k]['position_sha_1e5']],'method':'Unique world-space vertices rounded to 1e-5 nominal model units; technical reimport parity, not source validation.'}
out['glb']['pass']=out['glb']['same_names'] and out['glb']['triangles']==out['triangles'] and out['glb']['all_uv'] and not out['glb']['position_hash_differences']
out['technical_pass']=not out['mesh_issues'] and not out['hidden_meshes'] and not out['animated_objects'] and out['all_uv'] and not out['aperture_blocked'] and all(x['pass'] for x in out['tread_support']) and all(not x['escaped'] for x in out['enclosure_samples']) and out['glb']['pass'] and out['structure_white_same_geometry']
out['source_acceptance']=False;out['limitations']='Nominal scale. No complete staircase destination known. Lower 6 treads approximately source-supported, upper 2/landing/enclosure inferred. Nearby held-out view is not an independent baseline. Existing hall proportions/columns/floor/furniture remain approximate.'
(R/'qa/final_geometry_and_reimport_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['aperture_grid','beyond_opening_rays']},indent=2));print('FINAL_AUDIT_DONE')
