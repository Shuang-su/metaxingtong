import bpy,json,pathlib,hashlib,numpy as np
from mathutils import Euler,Vector,Matrix
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/cyber-roof-stage-20261105');Q=pathlib.Path(__file__).parent

def sig(m):
 if not m:return None
 return {'nodes':sorted((n.bl_idname,tuple((i.name,tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value)for i in n.inputs if hasattr(i,'default_value')))for n in m.node_tree.nodes),'links':sorted((l.from_node.bl_idname,l.from_socket.name,l.to_node.bl_idname,l.to_socket.name)for l in m.node_tree.links)}
states={}
for stage in ['r03','r04']:
 for mode in ['','-white']:
  bpy.ops.wm.open_mainfile(filepath=str(P/f'models/roof-{stage}{mode}.blend'));s=bpy.context.scene
  states[stage+mode]={'mats':{o.name:[sig(m)for m in o.data.materials]for o in s.objects if o.type=='MESH'},'world':sig(s.world),'cam':{o.name:[list(r)for r in o.matrix_world]for o in s.objects if o.type=='CAMERA'}}
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r04.blend'));s=bpy.context.scene
records=json.load(open(P/'qa/render-cameras.json'));checks=[]
for r in records:
 o=bpy.data.objects[r['camera']];expected=Matrix.Translation(r['location'])@Euler(r['rotation']).to_matrix().to_4x4();checks.append({'name':o.name,'matrix_max_difference':max(abs(expected[i][j]-o.matrix_world[i][j])for i in range(4)for j in range(4)),'lens_equal':o.data.lens==r['lens'],'sensor_fit_equal':o.data.sensor_fit==r['sensor_fit']})
# Independent numeric homogeneous projection of all finite annulus vertices, no world_to_camera_view reused.
manual=json.load(open(P/'qa/source11-manual-points.json'));old=json.load(open(P/'qa/camera-height-only-test.json'));cam=bpy.data.objects['SOURCE11 conditional camera'];o=bpy.data.objects['STAGE_INNER annulus'];verts=np.array([list(o.matrix_world@v.co)+[1]for v in o.data.vertices]);rows=[]
for item in old['rows']:
 cam.location.z=item['camera_z'];cam.rotation_euler=(Vector((0,2.4,3.8))-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();M=np.array(cam.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=1192,y=671))@np.linalg.inv(np.array(cam.matrix_world));clip=verts@M.T;ndc=clip[:,:2]/clip[:,3,None];px=np.column_stack(((ndc[:,0]+1)*596,(1-ndc[:,1])*335.5));ext={'inner_left_extreme':px[np.argmin(px[:,0])],'inner_right_extreme':px[np.argmax(px[:,0])],'inner_front_lower':px[np.argmax(px[:,1])]};res={k:(v-manual['points'][k]['xy']).tolist()for k,v in ext.items()};rms=float(np.sqrt(np.mean(np.array(list(res.values()))**2)));rows.append({'z':item['camera_z'],'residuals':res,'coordinate_component_RMSE':rms,'reported_RMSE_difference':rms-item['rms_px'],'min_forward_depth':float(clip[:,3].min())})
(Q/'reuse-and-scan.json').write_text(json.dumps({'shared_material_nodes_r03_r04':states['r03']['mats']==states['r04']['mats'],'shared_white_nodes_r03_r04':states['r03-white']['mats']==states['r04-white']['mats'],'world_same':states['r03']['world']==states['r04']['world'],'original_source_cameras_same':all(states['r03']['cam'][n]==states['r04']['cam'][n]for n in states['r03']['cam']),'render_recipe_camera_checks':checks,'scan':rows},indent=2));print('DONE')
