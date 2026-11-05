import bpy,bmesh,json,math
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r06-experiment.blend'));s=bpy.context.scene
r=json.loads((P/'research-r06/manual-outline.json').read_text());x0,x1=r['existing_cloud2_bounds'][0];z0,z1=r['existing_cloud2_bounds'][2]
# The manual trace mapping extrema recorded by build source; get exact centers from existing path mesh average for conservative local shrink.
o=bpy.data.objects['CLOUD_2 embedded motif 01'];cx=sum(v.co.x for v in o.data.vertices)/len(o.data.vertices);cz=sum(v.co.z for v in o.data.vertices)/len(o.data.vertices)
def front(x,z):return 4.3-.022-.035*math.exp(-(((x-x0)/(x1-x0)-.65)**2/.09+((z-z0)/(z1-z0)-.5)**2/.20))
for v in o.data.vertices:
 delta=v.co.y-front(v.co.x,v.co.z);v.co.x=cx+(v.co.x-cx)*.8;v.co.z=cz+(v.co.z-cz)*.8;v.co.y=front(v.co.x,v.co.z)+delta
for o in s.objects:
 if not o.name.startswith('CLOUD_2') or o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);ed=[e for e in bm.edges if e.is_boundary]
 if ed:bmesh.ops.holes_fill(bm,edges=ed,sides=0)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(o.data);bm.free();o.data.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r06b-experiment.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'models/roof-r06b-experiment.glb'),export_format='GLB',export_cameras=True,export_extras=True)
d=json.loads((P/'models/roof-r05-recovery.json').read_text());d['source_blend']='roof-r06b-experiment.blend';d['glb']='roof-r06b-experiment.glb';d['experimental_scope']='CLOUD_2 only; front area/shallow relief family proxy, not confirmed instance';d['objects']=[r for r in d['objects'] if not r['name'].startswith('CLOUD_2')]
for o in s.objects:
 if o.name.startswith('CLOUD_2'):d['objects'].append({'name':o.name,'type':'MESH','matrix_world':[list(r) for r in o.matrix_world],'properties':dict(o.items())})
(P/'models/roof-r06b-recovery.json').write_text(json.dumps(d,indent=2))
w=bpy.data.materials.new('White diagnostic R06b');w.use_nodes=True;w.diffuse_color=(.66,.66,.66,1);bs=w.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.66,.66,.66,1);bs.inputs['Roughness'].default_value=.7
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r06b-white.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'models/roof-r06b-white.glb'),export_format='GLB',export_cameras=True,export_extras=True)
