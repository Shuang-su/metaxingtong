import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent.parent;rows=[]
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r06b-experiment.blend'));s=bpy.context.scene
body=bpy.data.objects['CLOUD_2 continuous shallow relief proxy'];bm=bmesh.new();bm.from_mesh(body.data);bvh=BVHTree.FromBMesh(bm);bm.free()
for o in s.objects:
 if not o.name.startswith('CLOUD_2') or o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);rows.append({'name':o.name,'verts':len(bm.verts),'faces':len(bm.faces),'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True),'bounds_y':[min(v.co.y for v in bm.verts),max(v.co.y for v in bm.verts)]});bm.free()
 if o==body:continue
 hits=miss=0;depth=[]
 for v in o.data.vertices:
  loc,normal,idx,dist=bvh.ray_cast(Vector((v.co.x,3.8,v.co.z)),Vector((0,1,0)),1)
  if loc is None:miss+=1
  else:hits+=1;depth.append(v.co.y-loc.y)
 rows[-1]['front_rays']={'hits':hits,'miss':miss,'vertex_y_minus_front_range':[min(depth),max(depth)] if depth else None,'note':'positive means embedded behind front; both signs needed. All cross sections must separately be inspected.'}
(P/'research-r06/cloud-r06b-topology-contact.json').write_text(json.dumps(rows,indent=2))
for version in ['06b-experiment','06b-white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/('roof-r'+version+'.blend')));s=bpy.context.scene;s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_percentage=100
 for name in ['SOURCE11 conditional camera','SOURCE10 auxiliary different state']:
  s.camera=bpy.data.objects[name];s.render.resolution_x=1192;s.render.resolution_y=671;s.render.filepath=str(P/'research-r06'/('r'+version+'-'+name.split()[0]+'.png'));bpy.ops.render.render(write_still=True)
 for label,loc in [('front-close',(4.1,-1,4.7)),('oblique-close',(6.5,.8,5.8))]:
  bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.rotation_euler=(Vector((4.1,4.3,4.7))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=3.2;s.camera=c;s.render.resolution_x=796;s.render.resolution_y=448;s.render.filepath=str(P/'research-r06'/('r'+version+'-'+label+'.png'));bpy.ops.render.render(write_still=True)
