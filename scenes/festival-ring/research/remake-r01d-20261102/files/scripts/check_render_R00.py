import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];out=r/'versions/R00';bpy.ops.wm.open_mainfile(filepath=str(out/'ring-remake-R00-platforms.blend'));s=bpy.context.scene
rows=[]
for o in s.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);rows.append({'name':o.name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True),'zero_faces':sum(f.calc_area()<1e-12 for f in bm.faces)});bm.free()
ray=[];dg=bpy.context.evaluated_depsgraph_get()
for rad in [5.2,7,9.5]:
 for i in range(48):
  a=2*math.pi*i/48;hit,loc,normal,index,obj,m=s.ray_cast(dg,Vector((rad*math.cos(a),rad*math.sin(a),2)),Vector((0,0,-1)));ray.append({'r':rad,'angle_i':i,'hit':obj.name if hit else None,'z':loc.z if hit else None})
(r/'qa/R00-mesh-and-floor-check.json').write_text(json.dumps({'topology':rows,'outer_floor_limited_first_hits':ray,'limits':'First hits only, not exhaustive coplanar overlap or whole-scene collision proof'},indent=2))
# Actual fresh import, compare names and world-space bounds, not a material-equivalence certificate.
orig={o.name:[[min((o.matrix_world@Vector(v))[j] for v in o.bound_box) for j in range(3)],[max((o.matrix_world@Vector(v))[j] for v in o.bound_box) for j in range(3)]] for o in s.objects if o.type=='MESH'}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out/'ring-remake-R00-platforms.glb'));new={o.name:[[min((o.matrix_world@Vector(v))[j] for v in o.bound_box) for j in range(3)],[max((o.matrix_world@Vector(v))[j] for v in o.bound_box) for j in range(3)]] for o in bpy.context.scene.objects if o.type=='MESH'}
missing=sorted(set(orig)-set(new));errors=[abs(orig[n][i][j]-new[n][i][j]) for n in orig if n in new for i in range(2) for j in range(3)]
(r/'qa/R00-actual-glb-reimport.json').write_text(json.dumps({'original_meshes':len(orig),'imported_meshes':len(new),'missing':missing,'max_bounds_difference':max(errors),'limits':'Actual fresh GLB import and world bounds only, not source or visual equivalence'},indent=2))
bpy.ops.wm.open_mainfile(filepath=str(out/'ring-remake-R00-platforms.blend'));s=bpy.context.scene;s.render.filepath=str(out/'R00-platform-only-material-960.png');bpy.ops.render.render(write_still=True);s.view_layers[0].material_override=bpy.data.materials['shared white diagnostic'];s.render.filepath=str(out/'R00-platform-only-white-960.png');bpy.ops.render.render(write_still=True)
