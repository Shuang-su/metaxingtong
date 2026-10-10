import bpy,json,hashlib,time,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent/'castle_hall_fullroom/models/Xingtong_Castle_Hall_FullRoom.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene
s.render.resolution_x=1180;s.render.resolution_y=664;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=24;s.cycles.use_denoising=False;s.render.image_settings.file_format='PNG'
s.camera=bpy.data.objects['MATCH_A_45m15_empty_aisle']
out=R/'renders/baseline_A_1180_raw.png';s.render.filepath=str(out);bpy.ops.render.render(write_still=True)
(R/'qa/baseline_A_provenance.json').write_text(json.dumps(dict(model_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),camera=s.camera.name,location=list(s.camera.location),rotation=list(s.camera.rotation_euler),lens=s.camera.data.lens,shift=[s.camera.data.shift_x,s.camera.data.shift_y],geometry_changes='None',material_changes='None',samples=s.cycles.samples,denoising=False,pixels=[1180,664],source='hall_A_2712_paused_core.png',reference_warp=False,status='Baseline comparison, old camera approximate, not full-scene pass'),indent=2))
