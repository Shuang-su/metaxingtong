import bpy,json,bmesh,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path('/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010/six_bay_candidate/qa');s=bpy.context.scene
def active(o):
 def walk(c,on=True):
  on=on and not c.hide_render
  return (on and o.name in c.objects) or any(walk(k,on) for k in c.children)
 return not o.hide_render and walk(s.collection)
def bounds(o):
 a=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(v[i] for v in a) for i in range(3)],[max(v[i] for v in a) for i in range(3)]]
# Wall-side geometry only: exterior city/vegetation and interior furnishing are not architecture blockers.
wall=[];panes=[]
for o in s.objects:
 if o.type!='MESH' or not active(o):continue
 lo,hi=bounds(o);n=o.name.lower()
 if lo[0]<3.85 or hi[0]>4.7:continue
 if any(t in n for t in ['city','foliage','tree','grade']):continue
 if 'transparent front glass' in n or 'extended front glass' in n or 'transparent rear glass' in n:panes.append(o)
 elif any(t in n for t in ['wall','masonry','spandrel','upright','horizontal','sill','return','sash']):
  if not('glass'in n or'glazing'in n):wall.append(o)
verts=[];faces=[];owners=[]
for o in wall:
 offset=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
 for f in o.data.polygons:faces.append(tuple(offset+i for i in f.vertices));owners.append(o.name)
bv=BVHTree.FromPolygons(verts,faces);checks=[]
for o in panes:
 lo,hi=bounds(o);hits=[]
 for u in [.2,.5,.8]:
  for v in [.2,.5,.8]:
   y=lo[1]+u*(hi[1]-lo[1]);z=lo[2]+v*(hi[2]-lo[2]);h=bv.ray_cast(Vector((3.8,y,z)),Vector((1,0,0)),.9)
   if h[2] is not None:hits.append({'yz':[y,z],'opaque_object':owners[h[2]]})
 checks.append({'pane':o.name,'samples':9,'opaque_blocks':hits})
solid=[]
for y in [4.4,4.55,7.8,8.5,9.5,10.5,11.25]:
 for z in [.3,1.5,2.5]:
  h=bv.ray_cast(Vector((3.8,y,z)),Vector((1,0,0)),.9);solid.append({'yz':[y,z],'hit':owners[h[2]] if h[2] is not None else None})
# Changes are all beyondY3.69 or are removals/end-shortening; entire window leaf sweep remains near front hinges.
param=json.loads(Path('/workspace/scratch/fa58bfcf0425/classroom_hd_alignment_20261010/old_evidence/参数/共享窗扇.json').read_text());sweep_ymax=max(param['hinge_front_y']+param['right_leaf_width'],param['hinge_rear_y']+param['left_leaf_width'])+.05
changed=json.loads((p/'shared_changes.json').read_text())['changes'];intrusions=[]
for c in changed:
 if c['operation'].startswith('remove'):continue
 name=c['object'];lo,hi=bounds(bpy.data.objects[name])
 # Shortening existing rails only removes far material; it cannot add material to the near sweep.
 if c['operation'].startswith('resize') and all(c['after'][0][i]>=c['before'][0][i]-1e-5 and c['after'][1][i]<=c['before'][1][i]+1e-5 for i in range(3)):continue
 if lo[1]<=sweep_ymax:intrusions.append(name)
mesh=[]
for c in changed:
 o=bpy.data.objects.get(c['object'])
 if not o or o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);mesh.append({'name':o.name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_world':bm.calc_volume(signed=True)*o.matrix_world.to_3x3().determinant()});bm.free()
result={'fixed_glass_panes':len(panes),'glass_aperture_samples':sum(c['samples']for c in checks),'opaque_block_count':sum(len(c['opaque_blocks'])for c in checks),'pane_checks':checks,'solid_pier_and_rear_fill_probes':solid,'uncovered_solid_probes':sum(c['hit'] is None for c in solid),'changed_mesh_checks':mesh,'changed_bad_solid_meshes':[r for r in mesh if r['nonmanifold_edges']or r['signed_volume_world']<=0],'opening_sash_path':{'unchanged_leaf_dimensions_hinges_angles':True,'conservative_full_y_sweep_max':sweep_ymax,'new_or_moved_geometry_intruding_near_sweep':intrusions,'scope':'Conservative separation from changed wall geometry for whole hinge-radius envelope. Existing original sash-frame self-clearance is inherited, not newly proven.'},'interpretation':'Numerical sampled rays, not watertight theorem; hidden enlarged rear solid remains inferred. Material/transmission and exterior parallax require visual review.'};(p/'window_aperture_sash_normal_checks.json').write_text(json.dumps(result,indent=2));print('WINDOW_QA',len(panes),result['opaque_block_count'],result['uncovered_solid_probes'],len(result['changed_bad_solid_meshes']),intrusions)
