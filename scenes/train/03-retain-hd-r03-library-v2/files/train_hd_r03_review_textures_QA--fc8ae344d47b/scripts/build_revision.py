import bpy,bmesh,json,math,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'xingtong_train/deliverables/01_train_material.blend'));s=bpy.context.scene
# HD source shows a second circular fitting between each pair of existing access-lid groups.
# Keep all original access lids and paired vents; do not mistake the round lights for full modules.
template=bpy.data.objects['Central round ceiling fitting.001']
added=[]
for y in [-4.58,-1.88,.82,3.52,4.87]:
 o=template.copy();o.data=template.data.copy();o.name='HD intermediate round ceiling fitting';o.location.y=y
 bpy.data.collections['06_Ceiling_fixtures'].objects.link(o);o['Evidence']='Repeated separate round fittings visible between access modules in HD A/B/D. Estimated shared spacing.';added.append(o.name)
# Shared high-back edge profile: preserve transforms and local extents, flatten inflated old bevel.
seat_changes=[]
for o in list(s.objects):
 if o.type!='MESH' or 'high back' not in o.name:continue
 lo=[min(v.co[k] for v in o.data.vertices) for k in range(3)];hi=[max(v.co[k] for v in o.data.vertices) for k in range(3)]
 mats=list(o.data.materials);old=o.data;me=bpy.data.meshes.new(o.name+' HD flatter padded profile');bm=bmesh.new();bmesh.ops.create_cube(bm,size=1)
 for v in bm.verts:
  for k in range(3):v.co[k]=(v.co[k]+.5)*(hi[k]-lo[k])+lo[k]
 bmesh.ops.bevel(bm,geom=list(bm.edges),offset=.035,segments=3,affect='EDGES',profile=.5);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o.data=me
 for m in mats:me.materials.append(m)
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 o['HD_change']='Common .035-unit padded edge radius, replacing inflated ~.08 radius; preserved transform/extents; source A/B/D flatter tops.';seat_changes.append(o.name)
# Global material update: suppress broad inflated highlights; keep original embedded texture maps and UV.
mat=bpy.data.materials['Dark forest green leather | authored UV PBR'];bs=mat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Specular IOR Level'].default_value=.25
for n in mat.node_tree.nodes:
 if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.24
# Roughness map remains exported; add a portable multiply-add through separate baked image pixels.
for n in mat.node_tree.nodes:
 if n.type=='TEX_IMAGE' and n.image and 'rough' in n.image.name.lower():
  im=n.image.copy();im.name='HD leather restrained roughness';px=list(im.pixels)
  for k in range(0,len(px),4):
   v=min(.83,max(.48,px[k]*.75+.25));px[k:k+3]=[v,v,v]
  im.pixels=px;im.pack();n.image=im
glass=bpy.data.materials['Dark night window glazing'];gb=glass.node_tree.nodes.get('Principled BSDF');gb.inputs['Base Color'].default_value=(.035,.05,.04,1);gb.inputs['IOR'].default_value=1.18;gb.inputs['Transmission Weight'].default_value=.92
# One shared end-bay ceiling bounce, supported by the observed bright end-wall illumination.
light=bpy.data.objects['Ceiling diffuse pool.005'].copy();light.data=light.data.copy();light.name='HD end bay ceiling diffuse';light.location.y=4.5;light.data.energy=35;light.data.size_y=1.3;bpy.data.collections['09_Lights'].objects.link(light)
light['Evidence']='Global warm illumination approximation for bright end bay in A/D/I; no per-camera state.'
# All cameras reference the exact same global state. Historical cameras remain untouched.
for label,old in [('A','MATCH_D_13m59_wide'),('B','MATCH_A_15m19_right_booth'),('D','MATCH_B_45m12_left_booth')]:
 o=bpy.data.objects[old].copy();o.data=o.data.copy();o.name='HD_'+label;bpy.data.collections['10_Cameras'].objects.link(o)
 if label in ['A','B','D']:
  p=json.loads((R/'analysis'/f'{label}_camera_fit.json').read_text())['params'];o.location=p[:3];o.rotation_euler=(p[3],0,p[4]);o.data.lens=24
 o['Evidence']='HD source camera estimate; residuals retained; not engineering measurement'
# Additional independent source-camera initializations, never per-camera furniture/visibility changes.
for label in ['I','F','H','J']:
 p=json.loads((R/'analysis'/f'{label}_camera_fit.json').read_text())['params']
 if label=='H':p=[.8,-4.2,1.65,1.45,.64,24]
 if label=='J':p=[.8,-.65,1.63,1.62,1.57,24]
 d=bpy.data.cameras.new('HD_'+label);o=bpy.data.objects.new('HD_'+label,d);bpy.data.collections['10_Cameras'].objects.link(o);o.location=p[:3];o.rotation_euler=(p[3],0,p[4]);d.lens=p[5];d.sensor_width=36;d.clip_start=.025
 o['Source_fit_status']='Plane initialization; unresolved whole-scene residuals' if label in ['I','F'] else 'Diagnostic only; exact camera/window proportions unresolved'
# Observed case color categories, individual hidden identities and count remain inferred.
for name,col in [('HD worn olive case',(.065,.085,.025,1)),('HD warm ochre case',(.30,.105,.025,1))]:
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=col;b.inputs['Roughness'].default_value=.62;m.diffuse_color=col
for o in s.objects:
 if o.name.startswith('Luggage case'):
  m=bpy.data.materials['HD worn olive case' if abs(o.location.y)>.5 else 'HD warm ochre case'];o.data.materials.clear();o.data.materials.append(m);o['Evidence']='Color categories olive/ochre visible in A/D/J; exact case identity/placement and unseen counterparts inferred.'
s.camera=bpy.data.objects['INSPECT_01_forward_aisle'];s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=32;s.cycles.use_denoising=False
s['HD_revision']='2026-10-10 candidate; repeated ceiling restored, shared leather updated. No source-specific geometry/light switching.'
s['Source_fit_status']='Candidate; full multi-source fidelity NOT accepted. Sparse camera fit is not full-scene accuracy.'
s['Inference_limits']='Six seat/window bays and unseen reverse closure remain inferred; model units not metres.'
for im in bpy.data.images:
 if im.has_data and not im.packed_file:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'deliverables/01_train_material.blend'),compress=True)
(R/'analysis/revision_changes.json').write_text(json.dumps({'added_round_fittings':added,'existing_access_groups':'unchanged; four original groups' ,'seat_highbacks':seat_changes,'leather':'same remaining tuft meshes; roughness floor .48, restrained specular .25, normal strength .24','unchanged':'all shell, furniture transforms, aperture dimensions, historical cameras and world; added one declared global warm end-bay light; longitudinal scale not changed due underconstraint','status':'candidate, pending HD regressions'},indent=2))
