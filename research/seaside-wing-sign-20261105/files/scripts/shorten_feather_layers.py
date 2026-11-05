import bpy,os,json
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
patches=[[(282,188),(293,197),(308,204),(316,209),(318,214),(310,217),(299,210),(286,205),(281,199)],[(281,208),(292,215),(307,220),(312,223),(313,228),(306,230),(297,226),(284,222),(280,217)]]
def smooth(pts):
 for _ in range(2):pts=[q for i,a in enumerate(pts) for q in [tuple(.75*a[k]+.25*pts[(i+1)%len(pts)][k] for k in range(2)),tuple(.25*a[k]+.75*pts[(i+1)%len(pts)][k] for k in range(2))]]
 return pts
out={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=r+'/models/'+mode+'.blend');records=[]
 for side in ['L','R']:
  for i,p in enumerate(patches):
   o=bpy.data.objects['SIGN_'+side+'_layer_'+str(i)];old=[v.co.copy() for v in o.data.vertices];q=[]
   for u,v in smooth(p):
    x=-1.5-(339-u)*.73/61;z=2.73+(255-v)*1.13/93;q.append((x if side=='L' else -x,z))
   N=len(q);verts=[(x,y,z) for y in [3.13,3.17] for x,z in q];faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)];new=bpy.data.meshes.new(o.name+' corrected inner end');new.from_pydata(verts,[],faces);new.update()
   for mat in o.data.materials:new.materials.append(mat)
   o.data=new;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False);records.append({'object':o.name,'source04_manual_patch_pixels':p,'max_same_index_coordinate_change':max((a-v.co).length for a,v in zip(old,o.data.vertices))})
 bpy.ops.wm.save_as_mainfile(filepath=r+'/models/'+mode+'.blend');bpy.ops.export_scene.gltf(filepath=r+'/models/'+mode+'.glb',export_format='GLB',export_cameras=True,export_lights=False);out[mode]=records
json.dump({'purpose':'Shorten only added feather layers that occluded the visible curl mark; no body/curl/font/base scene/camera changes; manual source estimates not exact trace','changes':out},open(r+'/qa/sign-layer-adjust-r05.json','w'),indent=2)
