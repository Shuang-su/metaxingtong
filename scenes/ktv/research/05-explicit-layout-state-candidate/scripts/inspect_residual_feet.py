import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'));from layout_states import *
m=json.loads((root/'layout_state_manifest.json').read_text());workspace=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(workspace/m['base_blend']['workspace_relative_path']));sc=bpy.context.scene;sc.camera=sc.objects['01_front'];sc.render.resolution_x=1180;sc.render.resolution_y=664;sc.render.resolution_percentage=100
state,sel=choose_state(m,'unfurnished');apply_layout(sc,m,state,sel);bpy.context.view_layer.update()
points=[(438,497),(426,523),(564,523),(566,498),(625,497),(630,523),(753,498),(769,523)]
rows=[]
for o in sc.objects:
 if o.type!='MESH' or o.hide_render or any(c.hide_render for c in o.users_collection):continue
 coords=[world_to_camera_view(sc,sc.camera,o.matrix_world@Vector(c)) for c in o.bound_box]
 box=[min(p.x for p in coords)*1180,(1-max(p.y for p in coords))*664,max(p.x for p in coords)*1180,(1-min(p.y for p in coords))*664]
 if any(box[0]-2<=x<=box[2]+2 and box[1]-2<=y<=box[3]+2 for x,y in points):rows.append({'name':o.name,'collections':[c.name for c in o.users_collection],'screen_bbox':box,'world_translation':list(o.matrix_world.translation),'dimensions':list(o.dimensions),'material_names':[s.material.name if s.material else None for s in o.material_slots]})
(root/'qa/residual_floor_details.json').write_text(json.dumps({'query':'Visible small floor shapes after sofa-state switch; candidate shared geometry not edited','candidates':rows},ensure_ascii=False,indent=2)+'\n');print(json.dumps(rows,ensure_ascii=False))
