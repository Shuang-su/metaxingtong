import bpy,json,hashlib,datetime,collections,math
from mathutils import Vector
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];new=R/'models/CastleHall_Shared_White_Candidate.blend';old=R.parent/'castle_hall_fullroom/models/Xingtong_Castle_Hall_FullRoom.blend';G=R/'regression';bpy.ops.wm.open_mainfile(filepath=str(new));S=bpy.context.scene;white=bpy.data.materials['WHITE_Clay_uniform'];names=[('fit_4528','FIT_HD_4528_RIGHT_ARCH'),('holdout_4509','HOLDOUT_HD_4509_FRONT')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inv():
 d={}
 for o in S.objects:
  if o.type!='MESH':continue
  a=np.unique(np.round(np.array([list(o.matrix_world@v.co) for v in o.data.vertices]),5),axis=0);a[a==0]=0;d[o.name]=hashlib.sha256(a.astype('<f8').tobytes()).hexdigest()
 return d

def visibility(cam):
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();o=bpy.data.objects[cam];f=o.data.lens/36*1180;out=[]
 for v in range(4,664,8):
  for u in range(4,1180,8):
   ray=(o.matrix_world.to_3x3()@Vector(((u-590)/f,-(v-332)/f,-1))).normalized();h,p,n,i,obj,m=S.ray_cast(deps,o.location,ray,distance=100)
   out.append([u,v,obj.name if h else 'ESCAPE',float((p-o.location).length) if h else None])
 return out
newvis={n:visibility(c) for n,c in names};newinv=inv();lights=[]
for o in S.objects:
 if o.type=='LIGHT':lights.append({'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'matrix':[list(x) for x in o.matrix_world]})
conditions={'candidate_template_sha256':sha(new),'baseline_geometry_input_sha256':sha(old),'method':'Start from frozen candidate scene with identical cameras, lights (including added stair bounce), world and color management. Replace ALL candidate mesh objects with ALL 1597 baseline mesh objects. Apply the exact candidate white material. No walls hidden, no per-view geometry changes.','lights':lights,'white_material':{'base_color':list(white.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value),'roughness':white.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value},'world_background':list(S.world.node_tree.nodes['Background'].inputs[0].default_value),'world_strength':S.world.node_tree.nodes['Background'].inputs[1].default_value,'view_transform':S.view_settings.view_transform,'look':S.view_settings.look,'exposure':S.view_settings.exposure,'gamma':S.view_settings.gamma,'cameras':{n:{'name':c,'matrix':[list(x) for x in bpy.data.objects[c].matrix_world],'lens':bpy.data.objects[c].data.lens,'shift_x':bpy.data.objects[c].data.shift_x,'shift_y':bpy.data.objects[c].data.shift_y} for n,c in names}}
for o in list(S.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(old),link=False) as (src,dst):dst.objects=src.objects
coll=bpy.data.collections.new('REGRESSION_ALL_ORIGINAL_BASELINE_MESHES');S.collection.children.link(coll)
for o in dst.objects:
 if o and o.type=='MESH':coll.objects.link(o);o.data.materials.clear();o.data.materials.append(white)
# Preserve the baseline flags, and assert it is fully visible rather than hiding anything.
assert sum(o.type=='MESH' for o in S.objects)==1597
assert not [o.name for o in S.objects if o.type=='MESH' and (o.hide_render or o.hide_viewport or o.hide_get())]
bpy.context.view_layer.update();oldinv=inv();oldvis={n:visibility(c) for n,c in names};diff=json.loads((R/'qa/baseline_candidate_geometry_diff.json').read_text());unchanged=set(oldinv)&set(newinv)-set(diff['modified_existing']);assert len(unchanged)==1571 and all(oldinv[k]==newinv[k] for k in unchanged)
conditions['baseline_mesh_count']=len(oldinv);conditions['candidate_mesh_count']=len(newinv);conditions['unchanged_shared_mesh_hashes']=len(unchanged)
reports=[]
for n,c in names:
 changed=[];same=0;unaffected_to_changed=[]
 for oldr,newr in zip(oldvis[n],newvis[n]):
  assert oldr[:2]==newr[:2]
  if oldr[2]==newr[2] and oldr[3] is not None and newr[3] is not None and abs(oldr[3]-newr[3])<1e-4:same+=1
  else:
   r={'pixel':oldr[:2],'baseline_first':oldr[2],'candidate_first':newr[2],'baseline_depth':oldr[3],'candidate_depth':newr[3]};changed.append(r)
   if oldr[2] in unchanged and oldr[2]!=newr[2]:unaffected_to_changed.append(r)
 reports.append({'view':n,'sample_step_pixels':8,'total_sample_rays':len(oldvis[n]),'same_first_object_and_depth':same,'changed_rays':len(changed),'changed_object_pairs':[{'baseline':k[0],'candidate':k[1],'count':v} for k,v in collections.Counter((r['baseline_first'],r['candidate_first']) for r in changed).most_common()],'changed_pixel_bbox':[min(r['pixel'][0] for r in changed),min(r['pixel'][1] for r in changed),max(r['pixel'][0] for r in changed),max(r['pixel'][1] for r in changed)] if changed else None,'previously_unchanged_object_now_occluded_count':len(unaffected_to_changed),'previously_unchanged_object_now_occluded_examples':unaffected_to_changed[:40],'note':'Sampled first-hit regression is limited to these two cameras and this pixel grid. It cannot prove global absence of occlusion regressions.'})
(G/'same_condition_setup.json').write_text(json.dumps(conditions,indent=2));(G/'sampled_visibility_regression.json').write_text(json.dumps({'views':reports,'source_acceptance':False,'scope':'Two cameras only; no global no-regression claim'},indent=2))
S.render.engine='CYCLES';S.render.resolution_x=1180;S.render.resolution_y=664;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.cycles.samples=24;S.cycles.use_denoising=False;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB'
S.camera=bpy.data.objects['CANDIDATE_NORMAL_MAIN'];bpy.ops.wm.save_as_mainfile(filepath=str(G/'Baseline_White_Same_Conditions.blend'),compress=True)
for n,c in names:
 S.camera=bpy.data.objects[c];p=G/(n+'_baseline_raw.png');S.render.filepath=str(p);bpy.ops.render.render(write_still=True);m={'image':p.name,'sha256':sha(p),'geometry_baseline_sha256':sha(old),'render_template_candidate_sha256':sha(new),'regression_scene_sha256':sha(G/'Baseline_White_Same_Conditions.blend'),'camera':conditions['cameras'][n],'resolution':[1180,664],'samples':24,'threads':2,'engine':'Blender 4.3.2 Cycles CPU','white_material':conditions['white_material'],'conditions':'same_condition_setup.json','corresponding_candidate_image':'../renders/'+n+'_raw.png','corresponding_candidate_image_sha256':sha(R/'renders'/(n+'_raw.png')),'no_hidden_objects':True,'reference_warp':False};p.with_suffix('.json').write_text(json.dumps(m,indent=2));print('BASELINE_REGRESSION_RENDER_DONE '+n,flush=True)
print('BASELINE_REGRESSION_DONE',flush=True)
