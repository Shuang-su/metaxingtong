import bpy,json,hashlib
from pathlib import Path
V=Path(__file__).resolve().parents[1];record=[]
for variant in ['material','white']:
 p=V/f'models/phone-{variant}.blend';bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene
 for role,cam in [('source7','SOURCE7_CONDITIONAL_NOT_CALIBRATED'),('side','DIAGNOSTIC_side')]:
  s.camera=bpy.data.objects[cam];s.render.filepath=str(V/f'renders/{variant}-{role}.png');bpy.ops.render.render(write_still=True)
  record.append({'file':f'renders/{variant}-{role}.png','blend_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'camera':cam,'matrix_world':[list(row) for row in s.camera.matrix_world],'lens':s.camera.data.lens,'resolution':[s.render.resolution_x,s.render.resolution_y],'percentage':s.render.resolution_percentage,'pixel_aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y],'samples':s.cycles.samples,'denoising':s.cycles.use_denoising,'threads':s.render.threads,'role':'conditional source hypothesis' if role=='source7' else 'artificial diagnostic only'})
json.dump(record,open(V/'qa/actual-render-states.json','w'),indent=2)
