import bpy,pathlib,json,math
from mathutils import Matrix,Vector
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/lakeleaf-r05-material.blend'));s=bpy.context.scene
# Add only a finite second observed forest direction. Do not close an unsupported full lake ring.
col=bpy.data.collections.new('07_SecondObservedBank_InferredRegistration');s.collection.children.link(col);rot=Matrix.Rotation(math.pi/2,4,'Z');added=[]
for o in list(bpy.data.collections['04_ForestHypothesis'].objects)+list(bpy.data.collections['03_VisibleShoreHypothesis'].objects):
 if o.type!='MESH' or o.name.startswith(('ROCK','OUTCROP')):continue
 n=o.copy();n.data=o.data;n.name='WEST_'+o.name;col.objects.link(n);n.matrix_world=rot@o.matrix_world;n['stable_id']=n.name;n['inference']='Source 6.585758 and 108.755584 show forest in this direction. Finite sector placement, connection, species/instance identity remain inferred. Linked geometry proxy, not a claimed observed duplicate.';added.append({'id':n.name,'shared_mesh':n.data.name,'source_proxy':o.name})
# Raw glTF supports instances reliably without global evaluated-object duplication.
# Apply only the primary leaf modifiers as real editable mesh, preserving evaluated shape.
o=bpy.data.objects['LEAF_001_ThinConcaveShell'];bpy.context.view_layer.objects.active=o;o.select_set(True)
for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
o.select_set(False)
for name,loc,target in [('AUX_006585758_REAR',(4.1,-2.7,2.5),(-2,0,2.45)),('SOURCE_108755584_OBLIQUE',(1.5,-6.5,2.7),(-1.2,0,2.35))]:
 c=bpy.data.objects[name];c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c['calibration']='R06 joint four-view preflight hypothesis; not fully calibrated or accepted'
s['R06_changes']='Finite west forest/shore sector added because forest presence is explicitly seen in auxiliary rear and oblique source. Linked proxies; no full enclosing lake. Rear/oblique camera estimates jointly revised. R05 repaired veins preserved.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/lakeleaf-r06-material.blend'));bpy.ops.export_scene.gltf(filepath=str(R/'models/lakeleaf-r06.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_apply=False,export_texcoords=True,export_normals=True,export_materials='EXPORT')
w=bpy.data.materials.new('WHITE_R06_DiagnosticOnly');w.use_nodes=True;p=w.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.66,.67,.64,1);p.inputs['Roughness'].default_value=.75
for o in s.objects:
 if o.type=='MESH':
  for k in range(len(o.data.materials)):o.data.materials[k]=w
s['white_model_note']='Same R06 geometry/transforms/cameras and linked instances; material-only diagnostic replacement.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/lakeleaf-r06-white.blend'))
(R/'qa/r06').mkdir(parents=True,exist_ok=True);(R/'qa/r06/second-bank-manifest.json').write_text(json.dumps({'source_evidence':'Visible forest background in native 6.585758 auxiliary and 108.755584 oblique frames, not inferred from water colour','scope':'One finite west-facing sector, not a closed full lake','proxy_warning':'Linked procedural foliage instances; specific source plant identities and bank connection unproved','export_apply':False,'shell_modifiers_baked_explicitly':True,'added_instances':added},indent=2)+'\n')
