import bpy,math,json
R='/workspace/scratch/fa58bfcf0425/terrace_table_candidate_v2'
changes=[]
for o in bpy.data.collections['T2_Visible_Table_Decor_CANDIDATE'].objects:
 if '_leaf_' not in o.name:continue
 side='Left' if 'Left' in o.name else 'Right';cx,cy=(3.32,2.86) if side=='Left' else (3.66,2.90)
 tier=int(o.name.split('_leaf_')[1].split('_')[0]);j=int(o.name.rsplit('_',1)[1]);rad=.145 if side=='Left' else .162; L=rad*[1,.79,.52][tier]
 delta=(.038 if side=='Left' else .055)*(1+.12*math.sin(j*2.3+tier))
 for v in o.data.vertices:
  t=max(0,min(1,(math.hypot(v.co.x-cx,v.co.y-cy)-.012)/L));v.co.z+=delta*t*t
 changes.append({'name':o.name,'tip_raise':delta})
json.dump({'changes':changes,'scope':'leaf tips only; all pot geometry, placement, materials and other scene objects unchanged'},open(R+'/T2b_tip_refinement.json','w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=R+'/Terrace_T2_TwoPots_Candidate.blend')
s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=32;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.cycles.seed=0;s.render.use_compositing=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1430/1920;s.render.border_max_x=1650/1920;s.render.border_min_y=1-845/1080;s.render.border_max_y=1-580/1080;s.render.filepath=R+'/T2b_preview_crop.png';bpy.ops.render.render(write_still=True)
