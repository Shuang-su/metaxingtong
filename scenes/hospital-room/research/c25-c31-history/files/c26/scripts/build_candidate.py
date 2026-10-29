import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'c26';src=R/'v2b/hospital_C25_white_geometry_CONDITIONAL.blend'
bpy.ops.wm.open_mainfile(filepath=str(src))
def state():
 d={}
 for o in bpy.data.objects:
  if o.type=='MESH':
   d[o.name]={'matrix':[list(r) for r in o.matrix_world],'vertices':hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest(),'faces':hashlib.sha256(str([tuple(p.vertices) for p in o.data.polygons]).encode()).hexdigest()}
  elif o.type=='CAMERA':d[o.name]={'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens,'sensor':o.data.sensor_width,'shift':[o.data.shift_x,o.data.shift_y]}
 return d
before=state()
col=bpy.data.collections.new('C26_STRUCTURAL_CONTROLS__UNVERIFIED_SCALE');bpy.context.scene.collection.children.link(col)
ctl=bpy.data.objects.new('C26_PARAMETERS__defaults_preserve_C25',None);col.objects.link(ctl)
ctl['status']='CONDITIONAL topology inventory; no calibrated geometry change'
groups={};audit=[]
for o in list(bpy.data.objects):
 n=o.name
 group=None
 if n.startswith('Window •'):group='window'
 elif 'inferred beige column' in n:group='column'
 elif 'Curtain rail •' in n or 'rail end cross connector' in n:group='rail'
 elif n.startswith('TV wall •'):group='wall_seams'
 elif n.startswith('ROOM_SHELL'):group='shell'
 if not group:continue
 groups.setdefault(group,[]).append(n)
 o['C26_evidence']='Visible member/line identity supported; exact dimensions and placement NOT measured'
 o['C26_uncertainty']='Full extent, thickness, absolute scale and structural function unverified'
 o['C26_reference']='650/658 window-column lines; 1107/1116 wall junctions and rail candidates'
 if group=='shell':
  o['C26_evidence']='Visible wall-ceiling connection supported; hidden extents and orthogonal completion remain assumptions'
 else:
  # Independent per-object multipliers; defaults exactly preserve existing transforms.
  key=group+'_'+str(len(groups[group]))+'_scale'
  ctl[key]=1.0;ctl.id_properties_ui(key).update(min=0.5,max=1.5,description='Unmeasured dimension multiplier; 1 preserves C25. Use only with explicit evidence.')
  for ax in range(3):
   if o.animation_data and any(d.data_path=='scale' and d.array_index==ax for d in o.animation_data.drivers):raise RuntimeError('Existing driver conflict '+n)
   base=float(o.scale[ax]);fc=o.driver_add('scale',ax);d=fc.driver;d.type='SCRIPTED';v=d.variables.new();v.name='m';v.type='SINGLE_PROP';v.targets[0].id=ctl;v.targets[0].data_path='["'+key+'"]';d.expression=repr(base)+'*m'
  o['C26_control_key']=key
 audit.append({'object':n,'group':group,'location':list(o.location),'dimensions':list(o.dimensions),'evidence':o['C26_evidence'],'uncertainty':o['C26_uncertainty']})
bpy.context.view_layer.update()
after=state();assert before==after,'Default candidate altered protected scene state'
bpy.context.scene['C26_STATUS']='UNACCEPTED structure-controlled white candidate; same C25 geometry at defaults; original cameras frozen'
bpy.context.scene['C26_NO_CALIBRATION']='Image directions are not camera rotations; no DA3 dimensional fitting'
out=O/'hospital_C26_structure_controls_CONDITIONAL.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
D={'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'base_commit':'d3320bd7b5c8ba6e25190f4bcedfa06c7c20bebb','geometry_change':'NONE at default controls; existing structural members retained, no duplicates','groups':groups,'audit':audit,'all_original_meshes_and_cameras_equal':before==after,'protected_state':before}
(O/'candidate_manifest.json').write_text(json.dumps(D,indent=2)+'\n')
print('C26_READY',len(audit),len(before))
