import bpy,json,hashlib,shutil,struct,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'checkpoint_r05c';O.mkdir(exist_ok=True);T=O/'textures';T.mkdir(exist_ok=True);m=json.loads((R/'analysis/trial_c_manifest.json').read_text());src=Path(m['file']);assert hashlib.sha256(src.read_bytes()).hexdigest()==m['sha256'];material=O/f'train_r05c_material_candidate_{m["sha256"][:12]}.blend';shutil.copyfile(src,material);material.chmod(0o444)
bpy.ops.wm.open_mainfile(filepath=str(material));s=bpy.context.scene
def geomhash():
 h=hashlib.sha256()
 for o in sorted((o for o in s.objects if o.type=='MESH'),key=lambda o:o.name):
  h.update(o.name.encode());h.update(struct.pack('<16f',*[x for row in o.matrix_world for x in row]))
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for p in o.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
  for u in o.data.uv_layers:
   for d in u.data:h.update(struct.pack('<2f',*d.uv))
 return h.hexdigest()
gh=geomhash();refs=[];used={}
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image:
   im=n.image;used[im.name]=im;refs.append({'material':mat.name,'node':n.name,'image':im.name,'colorspace':im.colorspace_settings.name,'source_path':im.filepath,'packed':bool(im.packed_file),'dimensions':list(im.size)})
images=[]
for name,im in sorted(used.items()):
 safe=re.sub(r'[^\w.\-]+','_',name)
 if not safe.lower().endswith('.png'):safe+='.png'
 out=T/safe
 if im.packed_file:out.write_bytes(im.packed_file.data);method='exact packed bytes'
 else:im.filepath_raw=str(out);im.file_format='PNG';im.save();method='actual loaded image saved'
 images.append({'image':name,'file':'textures/'+safe,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'method':method})
(O/'texture_reference_manifest.json').write_text(json.dumps({'source_blend_sha256':m['sha256'],'images':images,'references':refs,'scope':'Only actual current frozen blend image references; no stale archive substitution. Material node parameters remain in BLEND/GLB; images alone do not encode UV scale, normal strength or lighting.'},indent=2))
rows=[{'kind':'material','file':str(material),'sha256':m['sha256'],'bytes':material.stat().st_size,'geometry_topology_uv_hash':gh}]
w=bpy.data.materials.new('White matte r05c geometry inspection');w.use_nodes=True;b=w.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.66,.66,.66,1);b.inputs['Roughness'].default_value=.82
for o in s.objects:
 if o.type=='MESH' and not any('glazing' in mat.name.lower() for mat in o.data.materials if mat):o.data.materials.clear();o.data.materials.append(w)
 if o.type=='LIGHT':o.data.color=(1,1,1)
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.1,.1,.1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.12;s.view_settings.exposure=-.15;s['Version']='r05C shared proportion checkpoint white; source fit NOT accepted';s['White_geometry_scope']='Exact material mesh, world transforms, topology and UV; glazing kept; light hue neutralized';s.camera=bpy.data.objects['INSPECT_01_forward_aisle'];bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True);assert geomhash()==gh
p=O/'train_r05c_white_temp.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);h=hashlib.sha256(p.read_bytes()).hexdigest();white=p.with_name(f'train_r05c_white_candidate_{h[:12]}.blend');p.rename(white);white.chmod(0o444);rows.append({'kind':'white','file':str(white),'sha256':h,'bytes':white.stat().st_size,'geometry_topology_uv_hash':geomhash()})
exports=[]
for item in rows:
 p=Path(item['file']);assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'];bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;assert geomhash()==gh;bpy.ops.object.select_all(action='DESELECT')
 for o in s.objects:
  if o.type in ['MESH','CAMERA']:o.select_set(True)
 out=O/f'train_r05c_{item["kind"]}_candidate.glb';bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_cameras=True,export_extras=True,export_materials='EXPORT');exports.append({'kind':item['kind'],'file':str(out),'input_blend_sha256':item['sha256'],'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size}) # Actual18MB delivery constraint checked on semantic ZIP, not inner GLB
 assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
manifest={'status':'r05C shared proportion improvement checkpoint, source fit NOT accepted, does not replace r03 Library/CURRENT','blends':rows,'exports':exports,'same_geometry_topology_uv':True,'reference_material_trial_sha256':m['sha256']};(O/'checkpoint_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
