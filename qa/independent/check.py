import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
O=Path(__file__).resolve().parent;R=O.parent/'seaside-arch-feature-semantics-20261105';P=O.parent/'independent-seaside-r03-images-20261105/frozen/models/material.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;c=bpy.data.objects['SOURCE04 conditional'];bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();src=json.loads((R/'qa/features.json').read_text());out={'model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'candidates':[],'probes':[]}
def test(item):
 v=Vector(item['world']);q=world_to_camera_view(s,c,v);px=[q.x*1192,(1-q.y)*671];ray=v-c.matrix_world.translation;hit,loc,_,_,ob,_=s.ray_cast(dep,c.matrix_world.translation,ray.normalized(),distance=ray.length+.01)
 row={'label':item['label'],'object':item['object'],'vertex':item['mesh_vertex_index'],'pixel':px,'pixel_diff':max(abs(a-b) for a,b in zip(px,item['projected_pixel'])),'depth':q.z,'residual':math.dist(px,item['source_pixel_unchanged']),'first_hit':ob.name if hit else None,'first_hit_matches':(ob.name if hit else None)==item['first_hit']}
 if item['object']:
  o=bpy.data.objects[item['object']];vs=[o.matrix_world@x.co for x in o.data.vertices]
  if item['mesh_vertex_index'] is not None: row['actual_mesh_world_diff']=(vs[item['mesh_vertex_index']]-v).length
  else:
   my=min(x.y for x in vs);cap=[x for x in vs if abs(x.y-my)<1e-5];center=sum(cap,Vector())/len(cap);row['actual_cap_count']=len(cap);row['actual_cap_center_diff']=(center-v).length
 out['candidates'].append(row)
for f in src['features']:
 test(f['old_world_under_current_camera'])
 for item in f['actual_mesh_candidates']:test(item)
test(src['additional_source_feature_not_in_old_fit'])
for p in json.loads((R/'qa/adjacent-face-probes.json').read_text())['probes']:
 o=bpy.data.objects[p['object']];v=o.data.vertices[p['candidate_vertex_index']].co;poly=o.data.polygons[p['adjacent_polygon']];assert p['candidate_vertex_index'] in poly.vertices;q=o.matrix_world@(v*.99+poly.center*.01);ray=q-c.matrix_world.translation
 hit,loc,_,face,ob,_=s.ray_cast(dep,c.matrix_world.translation,ray.normalized(),distance=ray.length+.002);dist=(loc-c.matrix_world.translation).length if hit else None;vis=bool(hit and abs(dist-ray.length)<1e-4)
 out['probes'].append({'object':o.name,'vertex':p['candidate_vertex_index'],'polygon':poly.index,'world_diff':(q-Vector(p['probe_world'])).length,'first_hit':ob.name if hit else None,'target_distance':ray.length,'hit_distance':dist,'visible':vis,'classification_matches':vis==p['target_point_visible_within_0_0001']})
out['old_six_preserved']=src['old_source_and_world_records_verbatim']==json.loads((R/'source/old-fit04-unchanged.json').read_text())['source_points']
(O/'check.json').write_text(json.dumps(out,indent=2));print('DONE',len(out['candidates']),len(out['probes']),max(x['pixel_diff'] for x in out['candidates']),all(x['classification_matches'] for x in out['probes']))
