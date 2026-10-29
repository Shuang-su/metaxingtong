"""Clarify glazing metadata without changing any mesh, transform, camera or material."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for f in ['car_passenger_cabin_white.blend','car_passenger_cabin_material.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(R/'models'/f))
 o=bpy.data.objects['P12_side_window_glass'];o['evidence_class']='observed-aperture_inferred-glazing';o['limitations']='Window aperture observed; whether glass is raised, thickness and IOR inferred'
 bpy.ops.wm.save_as_mainfile(filepath=str(R/'models'/f))
