"""Restore Blender off-axis cameras from explicit sidecar after raw standard GLB import.
Standard glTF cannot encode a shifted principal point. This is an explicit importer-
side restoration, not a claim that a standalone GLB camera retains off-axis projection.
Run: blender -b --python scripts/restore_glb_cameras.py
"""
import bpy,pathlib,json
from mathutils import Matrix
R=pathlib.Path(__file__).resolve().parents[1];side=R/'models/lakeleaf-r04-cameras.json'
if not side.exists():
 bpy.ops.wm.open_mainfile(filepath=str(R/'models/lakeleaf-r04-material.blend'));rows=[]
 for o in bpy.context.scene.objects:
  if o.type=='CAMERA':rows.append({'name':o.name,'matrix_world':[list(row) for row in o.matrix_world],'data':{k:getattr(o.data,k) for k in ['type','lens','sensor_fit','sensor_width','sensor_height','shift_x','shift_y','clip_start','clip_end']},'custom':{k:o[k] for k in ['source_width','source_height','calibration'] if k in o}})
 side.write_text(json.dumps({'source_blend':'lakeleaf-r04-material.blend','role':'Lossless camera sidecar, necessary for the top source camera off-axis projection that standard glTF omits','cameras':rows},indent=2)+'\n')
d=json.loads(side.read_text());bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'models/lakeleaf-r04.glb'))
for row in d['cameras']:
 o=bpy.data.objects[row['name']];assert o.type=='CAMERA';o.matrix_world=Matrix(row['matrix_world'])
 for k,v in row['data'].items():setattr(o.data,k,v)
 for k,v in row['custom'].items():o[k]=v
bpy.context.scene['restoration_note']='Actual GLB reimport plus explicit camera sidecar. Standard raw GLB loses off-axis shift; no geometry/material edits.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/lakeleaf-r04-glb-camera-restored-check.blend'))
