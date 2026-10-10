import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'));S=bpy.context.scene
old=bpy.data.objects.get('ARCH_Far_wall_arched_aperture');bpy.data.objects.remove(old,do_unlink=True)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,22.18,4.4));wall=bpy.context.object;wall.name='ARCH_Far_wall_arched_aperture';wall.dimensions=(14.72,.36,8.8);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
for c in list(wall.users_collection):c.objects.unlink(wall)
bpy.data.collections['10_Completed_Room_Shell'].objects.link(wall);wall.data.materials.append(bpy.data.materials['Plaster | original UV PBR']);wall['evidence']='Source-observed arched opening; structural thickness inferred. Boolean cutter outward normals verified.'
rad=3.075;spring=5.2;poly=[(-rad,-.1),(rad,-.1),(rad,spring)]+[(rad*math.cos(k*math.pi/64),spring+rad*math.sin(k*math.pi/64)) for k in range(1,65)];n=len(poly);vs=[(x,y,z) for y in (21.5,22.7) for x,z in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
me=bpy.data.meshes.new('ARCH_CUT');me.from_pydata(vs,[],fs);me.update();cut=bpy.data.objects.new('ARCH_CUT',me);S.collection.objects.link(cut)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0;bm.to_mesh(me);bm.free()
bpy.context.view_layer.objects.active=wall;m=wall.modifiers.new('Real arched aperture outward cutter','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
bm=bmesh.new();bm.from_mesh(wall.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));print('WALL_VOLUME',bm.calc_volume(signed=True),'BOUND',sum(e.is_boundary for e in bm.edges));bm.to_mesh(wall.data);bm.free()
# Assign stable world-space UVs after boolean so no spurious UV folding is inherited from primitive cube.
uv=wall.data.uv_layers.active or wall.data.uv_layers.new(name='UVMap')
for p in wall.data.polygons:
 ax=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=ax]
 for li in p.loop_indices:
  v=wall.matrix_world@wall.data.vertices[wall.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*.25,v[axes[1]]*.25)
# Semantic aperture rays must hit blue glazing and never plaster within the unobscured opening.
bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();hits={};unexpected=[]
for x in [-2.8,-2.2,-1.7,-.5,0,.5,1.7,2.2,2.8]:
 for z in [1.5,2.5,4,5.5,6,7,7.7]:
  if z>5.2 and x*x+(z-5.2)**2>(3.0)**2:continue
  hit,p,n,i,o,m=S.ray_cast(dep,Vector((x,21.995,z)),Vector((0,1,0)),distance=.5)
  name=o.name if hit else 'MISS';hits[name]=hits.get(name,0)+1
  if name!='ARCH_Central_arched_glazing_40mm':unexpected.append({'x':x,'z':z,'hit':name})
json.dump({'hits':hits,'unexpected':unexpected,'pass':not unexpected},open(R/'qa/semantic_aperture_validation.json','w'),indent=2);print('APERTURE',hits,'UNEXPECTED',unexpected)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'),compress=True)
S.render.resolution_percentage=50;S.cycles.samples=12;S.camera=bpy.data.objects['MATCH_A_45m15_empty_aisle'];S.render.filepath=str(R/'qa/arch_fixed_preview.png');bpy.ops.render.render(write_still=True)
