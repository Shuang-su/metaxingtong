"""Render the actual independently empty-scene imported GLB + restored sidecar.
No geometry/material/environment repair performed here.
"""
import bpy,pathlib,json,hashlib,time
P=pathlib.Path(__file__).resolve().parents[1]
inp=P/'qa/independent-R04D/restored/R04D_material_restored.blend';assert inp.exists()
bpy.ops.wm.open_mainfile(filepath=str(inp));s=bpy.context.scene
assert s.camera and s.camera.name=='SOURCE02_conditional_front'
s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=96;s.cycles.use_denoising=False;s.render.resolution_percentage=100
out=P/'qa/R04D-roundtrip-render';out.mkdir(exist_ok=True);s.render.filepath=str(out/'material_SOURCE02_glb_sidecar.png')
t=time.time();bpy.ops.render.render(write_still=True)
(out/'render-provenance.json').write_text(json.dumps({'actual_input':str(inp.relative_to(P)),'input_sha256':hashlib.sha256(inp.read_bytes()).hexdigest(),'camera':s.camera.name,'samples':96,'resolution':[s.render.resolution_x,s.render.resolution_y],'seconds':time.time()-t,'geometry_material_environment_modified_for_probe':False,'expected_original':'renders/R04_source/material_SOURCE02_conditional_front.png','status':'Actual GLB plus sidecar roundtrip probe, NOT native GLB environmental parity and NOT source fidelity proof'},indent=2))
