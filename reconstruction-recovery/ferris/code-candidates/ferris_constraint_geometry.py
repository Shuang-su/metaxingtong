import bpy,json
from mathutils import Vector
p='/workspace/shared/ferris-cabin-build-20261030/scenes/ferris-wheel-cabin/models/ferris_cabin_r07_material.blend';bpy.ops.wm.open_mainfile(filepath=p)
for name in ['cream_bezel_1_0','cream_bezel_2_0','cream_bezel_2_1','black_gasket_1_0','black_gasket_2_0','black_gasket_2_1','window_guard_2_0_1.06','window_guard_2_1_1.06','window_guard_2_1_1.97','bench_1_seat','bench_1_back']:
 o=bpy.data.objects.get(name)
 if not o:print('MISSING',name);continue
 vv=[o.matrix_world@v.co for v in o.data.vertices];print(name,[[round(min(v[i] for v in vv),6),round(max(v[i] for v in vv),6)] for i in range(3)])
