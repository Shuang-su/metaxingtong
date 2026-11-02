import bpy,bmesh,os,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[-2:]))
D=Path(__file__).resolve().parents[1];fits=json.loads((D/'models/R04-camera-fit.json').read_text())
# SOURCE1 visible top-of-sidewall contour, original 1920x1080. ±10px soft visual samples.
left=[(0,920),(100,931),(250,913),(400,875),(550,830),(700,785),(771,763)]
right=[(1140,764),(1280,830),(1450,883),(1650,894),(1810,882),(1885,858),(1907,826)]
# Inferred connections are deliberately identified; frame intersection is NOT real endpoint.
pixelpoly=[(-150,790),(960,635),(2080,790)]+list(reversed(right))+[(1400,1250),(500,1250)]+list(reversed(left))+[(-150,920)]
p=fits['SOURCE_P1_45'];C=Vector(p['location']);r=Vector(p['right']);u=Vector(p['up']);f=Vector(p['forward']);fp=p['lens_mm']/36*1920
poly=[]
for x,y in pixelpoly:
 ray=f+(x-960)/fp*r+(540-y)/fp*u;t=(.24-C.z)/ray.z;P=C+t*ray;poly.append((P.x,P.y))
(D/'models/R04-stage-conditional-protocol.json').write_text(json.dumps({'source':'BV1DZ4y1U71V P1 t45.013436 native1920x1080','observed_left_top_edge_px':left,'observed_right_top_edge_px':right,'uncertainty_px':10,'inferred_pixel_connections':[[-150,790],[960,635],[2080,790],[1400,1250],[500,1250],[-150,920]],'method':'Ray intersect z=.24 conditional working plane under R04 camera; model-space contour, never warp source or per-camera shape','plane_top':.24,'plane_bottom':0,'world_polygon':poly,'limits':'Boundary pixel samples soft and some thin light edge identification uncertain. End closures extended beyond source1 image; no physical full-front evidence. All other sources must regress, SOURCE1 contour fit not acceptance.'},indent=2))
for mode in['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R03_{mode}.blend'));s=bpy.context.scene;s.render.threads=2;s.cycles.use_denoising=False
 for name,p in fits.items():
  o=bpy.data.objects[name];o.location=p['location'];o.rotation_euler=Matrix((p['right'],p['up'],[-v for v in p['forward']])).transposed().to_euler();o.data.lens=p['lens_mm'];o['fit_status']=p['status']
 old=bpy.data.objects['STAGE_shared_rounded_lobes'];m=old.data.materials[0];bpy.data.objects.remove(old,do_unlink=True)
 for o in list(s.objects):
  if o.name.startswith('STAGE_edge'):bpy.data.objects.remove(o,do_unlink=True)
 N=len(poly);vs=[(x,y,z) for z in[0,.24] for x,y in poly];faces=[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)]
 pts=[Vector((x,y,0))for x,y in poly];lookup={tuple(v):i for i,v in enumerate(pts)}
 for tri in tessellate_polygon([pts]):
  ids=[v if isinstance(v,int) else lookup[tuple(v)]for v in tri];faces += [tuple(reversed(ids)),tuple(v+N for v in ids)]
 me=bpy.data.meshes.new('R04_stage');me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new('STAGE_shared_rounded_lobes',me);s.collection.objects.link(o);o.data.materials.append(m);o['evidence']='SOURCE1 soft planar contour conditional, foreground closure inferred beyond frame; all-camera same geometry'
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 # Retain a narrow border as separate actual material strip by a thin curve on top, conditional width.
 curve=bpy.data.curves.new('Stage top border','CURVE');curve.dimensions='3D';curve.bevel_depth=.012;curve.bevel_resolution=2;curve.use_fill_caps=True;sp=curve.splines.new('POLY');sp.points.add(N-1)
 for pt,(x,y) in zip(sp.points,poly):pt.co=(x*.99,y*.99,.243,1)
 sp.use_cyclic_u=True;ob=bpy.data.objects.new('STAGE_shared_border',curve);s.collection.objects.link(ob);curve.materials.append(bpy.data.materials['White diagnostic' if mode=='white' else 'Warm architectural white'])
 bpy.data.objects['UMBRELLA_RIG'].location.z-=.012;bpy.data.objects['UMBRELLA_RIG']['R04_ground_hypothesis']='Engineering tangent to actual ground mesh upper plane z=0, NOT observed source contact'
 s['R04_limit']='All 3 sources trained. Camera distance prior, planar stage backprojection, rim engineering contact are explicit assumptions; no source acceptance.'
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R04_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/R04_{mode}.glb'),export_format='GLB',export_cameras=True,export_lights=False)
print('R04_SAVED')
