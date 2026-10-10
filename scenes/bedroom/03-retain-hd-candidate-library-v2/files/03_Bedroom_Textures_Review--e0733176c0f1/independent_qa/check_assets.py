import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector, kdtree
R=Path('/workspace/scratch/fa58bfcf0425/bedroom_hd_revision_20261010'); O=R/'independent_qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snap():
 bpy.context.view_layer.update();out={}
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  me=ob.data;me.calc_loop_triangles();v=[list(ob.matrix_world@x.co) for x in me.vertices];uv=me.uv_layers.active
  corners=[(v[l.vertex_index],list(uv.data[l.index].uv)) for l in me.loops] if uv else []
  out[ob.name]={'v':v,'tri':len(me.loop_triangles),'uv':corners,'geometry':sha_bytes(repr((v,[list(p.vertices) for p in me.polygons])).encode()),'bounds':[[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]],'materials':[m.name for m in me.materials if m]}
 return out

def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def mats():
 out={}
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if p:out[m.name]={'color':list(p.inputs['Base Color'].default_value),'metallic':p.inputs['Metallic'].default_value,'roughness':p.inputs['Roughness'].default_value,'images':[{'size':list(n.image.size),'pixels_sha':sha_bytes(bytes(str(list(n.image.pixels[:])).encode()))} for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]}
 return out
report={'inputs':{},'roundtrip':[]}
bpy.ops.wm.open_mainfile(filepath=str(R/'frozen/bedroom_material_v1.blend'));base=snap()
for b,g in [('01_HD_candidate_material.blend','03_HD_candidate_material.glb'),('02_HD_candidate_white.blend','04_HD_candidate_white.glb')]:
 bp=R/'models/hd_v2'/b;gp=R/'models/hd_v2'/g;report['inputs'][b]=sha(bp);report['inputs'][g]=sha(gp)
 bpy.ops.wm.open_mainfile(filepath=str(bp));a=snap();am=mats()
 if b.startswith('01'):
  report['baseline_delta']={'added':sorted(a.keys()-base.keys()),'removed':sorted(base.keys()-a.keys()),'changed':[n for n in a.keys()&base.keys() if a[n]['geometry']!=base[n]['geometry']]}
  report['cameras']=[{'name':o.name,'clip_start':o.data.clip_start,'lens':o.data.lens} for o in bpy.context.scene.objects if o.type=='CAMERA']
  report['material_exposure']=bpy.context.scene.view_settings.exposure
  report['handle_and_doors']={n:a[n]['bounds'] for n in a if 'pull' in n.lower() or 'door' in n.lower() or 'rug' in n.lower()}
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(gp));c=snap();cm=mats();err=0;uv_err=0;uv_missing=[];bad=[]
 for n in a.keys()&c.keys():
  for s,d in [(a[n]['v'],c[n]['v']),(c[n]['v'],a[n]['v'])]:
   tree=kdtree.KDTree(len(d))
   for i,v in enumerate(d):tree.insert(Vector(v),i)
   tree.balance();err=max(err,max(tree.find(Vector(v))[2] for v in s))
  if a[n]['tri']!=c[n]['tri']:bad.append(n)
  if bool(a[n]['uv'])!=bool(c[n]['uv']):uv_missing.append(n)
  if a[n]['uv'] and c[n]['uv']:
   # Match every imported world-space corner against source corners at same position, allowing seams.
   tree=kdtree.KDTree(len(a[n]['uv']))
   for i,(v,u) in enumerate(a[n]['uv']):tree.insert(Vector(v),i)
   tree.balance()
   for v,u in c[n]['uv']:
    ids=tree.find_range(Vector(v),1e-5)
    ue=min(max(abs(u[k]-a[n]['uv'][i][1][k]) for k in (0,1)) for _,i,_ in ids)
    uv_err=max(uv_err,ue)
 material_diffs=[]
 for n in am.keys()&cm.keys():
  for k in ('color','metallic','roughness','images'):
   if am[n][k]!=cm[n][k]:material_diffs.append({'name':n,'field':k,'source':am[n][k],'import':cm[n][k]})
 report['roundtrip'].append({'blend':b,'glb':g,'meshes':[len(a),len(c)],'triangles':[sum(x['tri'] for x in a.values()),sum(x['tri'] for x in c.values())],'missing':sorted(a.keys()-c.keys()),'extra':sorted(c.keys()-a.keys()),'triangle_mismatch':bad,'world_vertex_max_error':err,'uv_missing':uv_missing,'world_matched_corner_uv_max_error':uv_err,'source_materials':am,'import_materials':cm,'material_property_differences':material_diffs})
(O/'independent_assets.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('INDEPENDENT QA COMPLETE')
