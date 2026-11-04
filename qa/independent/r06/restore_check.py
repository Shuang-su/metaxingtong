import bpy,json,runpy,sys
from pathlib import Path
O=Path(__file__).parent;R=Path('/workspace/scratch/fa58bfcf0425/keyring-hall-candidate-20261104/versions/R06')
def state():
 s=bpy.context.scene;w=s.world
 return {'lights':{o.name:{'matrix':[list(r) for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'shape':o.data.shape,'size':o.data.size} for o in s.objects if o.type=='LIGHT'},'world':{'use_nodes':w.use_nodes,'background':list(w.node_tree.nodes.get('Background').inputs['Color'].default_value),'strength':w.node_tree.nodes.get('Background').inputs['Strength'].default_value,'links':[(l.from_node.bl_idname,l.from_socket.name,l.to_node.bl_idname,l.to_socket.name) for l in w.node_tree.links]},'cameras':{o.name:{'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end} for o in s.objects if o.type=='CAMERA'},'render':{'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'engine':s.render.engine,'samples':s.cycles.samples,'denoise':s.cycles.use_denoising,'active':s.camera.name,'view':{k:getattr(s.view_settings,k) for k in ['view_transform','look','exposure','gamma']}}}
out={}
for variant in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/keyring-{variant}.blend'));old=state();bpy.ops.wm.read_factory_settings(use_empty=True)
 sys.argv=['restore','--',str(R/f'models/keyring-{variant}.glb'),str(R/'docs/render-sidecar.json'),str(O/f'restored-{variant}.blend')];runpy.run_path(str(R/'scripts/restore_glb_lighting.py'),run_name='__main__');new=state(); light_name_map={n:(n if n in old['lights'] else n.rsplit('.',1)[0]) for n in new['lights']}; new['lights']={light_name_map[n]:v for n,v in new['lights'].items()}
 le={n:max(abs(old['lights'][n]['matrix'][i][j]-v['matrix'][i][j]) for i in range(4) for j in range(4)) for n,v in new['lights'].items()};ce={n:max(abs(old['cameras'][n]['matrix'][i][j]-v['matrix'][i][j]) for i in range(4) for j in range(4)) for n,v in new['cameras'].items()}
 out[variant]={'original':old,'restored':new,'world_exact':old['world']==new['world'],'render_exact':old['render']==new['render'],'light_matrix_errors':le,'camera_matrix_errors':ce,'light_parameters_exact':all({k:v for k,v in old['lights'][n].items() if k!='matrix'}=={k:v for k,v in x.items() if k!='matrix'} for n,x in new['lights'].items())}
(O/'restore-check.json').write_text(json.dumps(out,indent=2));print('DONE')
