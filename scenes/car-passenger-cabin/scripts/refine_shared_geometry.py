"""Repair initial geometric defects and improve the common camera trial, preserving failed stage in Git."""
import bpy,bmesh,json,math
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/car_passenger_cabin_white.blend'))
s=bpy.context.scene;s.frame_set(1)
repairs=[]
for o in s.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);before=sum(not e.is_manifold for e in bm.edges)
 # Converted curve caps have coincident but split boundary vertices.
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
 bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges))
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 bm.to_mesh(o.data);bm.free();o.data.update()
 if before:repairs.append({'object':o.name,'repair':'weld coincident curve cap vertices, recompute exterior normals','before_nonmanifold_edges':before})
 # Existing synthetic UVs are added later after geometry fixes.
# Lower sill so the door bottom clears the fixed threshold.
o=bpy.data.objects['B02_sill_fixed'];o.location.z=.10;o.scale.z=.43
bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False)
repairs.append({'object':o.name,'repair':'Reduce threshold top to .1301, below door lower boundary .14; no swept collision acceptance claim'})
# Reposition the external mirror forward/above the door waist; keep attached to hinge.
for name in ['P15_mirror_stem','P16_mirror_housing','P17_mirror_glass']:
 o=bpy.data.objects[name];o.location.y-=.09;o.location.z+=.06
repairs.append({'objects':['P15_mirror_stem','P16_mirror_housing','P17_mirror_glass'],'repair':'Shared exterior mirror placement trial; not calibrated'})
# More horizontal source-like framing; same geometry for all cameras.
cam_specs={
 'SRC_S01_closed':((-.37,-.17,1.12),(.96,.02,1.055),24),
 'SRC_S02_open':((-.39,-.20,1.12),(.97,.04,1.035),24),
 'SRC_S03_closed':((-.57,-.19,1.13),(.95,.03,1.055),25),
 'MAIN_passenger_local':((-1.75,-1.53,1.34),(.62,.06,.95),37)
}
for name,(loc,target,lens) in cam_specs.items():
 c=bpy.data.objects[name];c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
# Fixed studio lighting kept identical in all source views; prevent fixture silhouettes in window.
for o in s.objects:
 if o.type=='LIGHT':o.visible_glossy=False;o.visible_transmission=False
s.cycles.use_denoising=False;s.cycles.samples=96
s['revision']='r02 repairs: welded caps, outward normals, degenerate bevel cleanup, sill clearance, common mirror shift, camera trial'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/car_passenger_cabin_white.blend'))
(R/'qa/shared-geometry-repairs.json').write_text(json.dumps(repairs,indent=2)+'\n')
