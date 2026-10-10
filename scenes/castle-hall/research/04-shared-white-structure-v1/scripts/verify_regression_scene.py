import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];G=R/'regression';old=R.parent/'castle_hall_fullroom/models/Xingtong_Castle_Hall_FullRoom.blend';new=R/'models/CastleHall_Shared_White_Candidate.blend'
def inv():
 d={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  a=np.unique(np.round(np.array([list(o.matrix_world@v.co) for v in o.data.vertices]),5),axis=0);a[a==0]=0;d[o.name]=hashlib.sha256(a.astype('<f8').tobytes()).hexdigest()
 return d

def settings():
 S=bpy.context.scene;ls={};cs={}
 for o in S.objects:
  if o.type=='LIGHT':
   d={'matrix':[list(v) for v in o.matrix_world]}
   for k in ['type','energy','color','shape','size','size_y','spot_size','spot_blend','shadow_soft_size','use_shadow','use_nodes']:
    if hasattr(o.data,k):v=getattr(o.data,k);d[k]=list(v) if k=='color' else v
   ls[o.name]=d
  if o.name in ['FIT_HD_4528_RIGHT_ARCH','HOLDOUT_HD_4509_FRONT']:cs[o.name]={'matrix':[list(v) for v in o.matrix_world],'lens':o.data.lens,'sensor_width':o.data.sensor_width,'sensor_fit':o.data.sensor_fit,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y}
 mat=S.objects[next(o.name for o in S.objects if o.type=='MESH')].data.materials[0];bs=mat.node_tree.nodes.get('Principled BSDF')
 return {'lights':ls,'cameras':cs,'world_color':list(S.world.node_tree.nodes['Background'].inputs[0].default_value),'world_strength':S.world.node_tree.nodes['Background'].inputs[1].default_value,'view_transform':S.view_settings.view_transform,'look':S.view_settings.look,'exposure':S.view_settings.exposure,'gamma':S.view_settings.gamma,'white_base':list(bs.inputs['Base Color'].default_value),'white_roughness':bs.inputs['Roughness'].default_value}

def depths(cam):
 S=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();o=bpy.data.objects[cam];f=o.data.lens/36*1180;vals=[]
 for v in range(4,664,8):
  for u in range(4,1180,8):
   dr=(o.matrix_world.to_3x3()@Vector(((u-590)/f,-(v-332)/f,-1))).normalized();h,p,n,i,obj,m=S.ray_cast(deps,o.location,dr,distance=100);vals.append(float((p-o.location).length) if h else 1000)
 return np.array(vals)

bpy.ops.wm.open_mainfile(filepath=str(old));a=inv()
bpy.ops.wm.open_mainfile(filepath=str(G/'Baseline_White_Same_Conditions.blend'));base=inv();bc=settings();bd=depths('HOLDOUT_HD_4509_FRONT')
bpy.ops.wm.open_mainfile(filepath=str(new));cand=inv();cc=settings();cd=depths('HOLDOUT_HD_4509_FRONT')
diff=json.loads((R/'qa/baseline_candidate_geometry_diff.json').read_text());modified=sorted(k for k in base.keys()&cand.keys() if base[k]!=cand[k]);added=sorted(cand.keys()-base.keys());removed=sorted(base.keys()-cand.keys());errs=np.abs(bd-cd)
out={'original_baseline_geometry_unchanged_in_regression_scene':a==base,'baseline_meshes':len(base),'camera_light_world_white_and_color_settings_exactly_equal':bc==cc,'modified_existing_exactly_matches_declared_list':modified==diff['modified_existing'],'added_exactly_matches_declared_list':added==diff['added'],'removed_exactly_matches_declared_list':removed==diff['removed'],'modified':modified,'added':added,'removed':removed,'wide_4509_geometry_depth_regression':{'sample_step_pixels':8,'sample_rays':len(errs),'max_depth_difference_nominal_units':float(errs.max()),'rays_above_1e_minus4':int(np.sum(errs>1e-4)),'note':'This camera and sample grid only. Does not prove zero global occlusion regression or source acceptance.'}}
out['technical_regression_setup_pass']=all(out[k] for k in ['original_baseline_geometry_unchanged_in_regression_scene','camera_light_world_white_and_color_settings_exactly_equal','modified_existing_exactly_matches_declared_list','added_exactly_matches_declared_list','removed_exactly_matches_declared_list'])
(G/'regression_setup_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));print('REGRESSION_SETUP_CHECK_DONE')
