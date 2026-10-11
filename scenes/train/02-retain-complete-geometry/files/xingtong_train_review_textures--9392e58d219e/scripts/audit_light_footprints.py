import bpy,json,math
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'deliverables/01_train_material.blend'));S=bpy.context.scene
D={'scope':'Full luminous area boundaries, not only light centers. Saved carriage lights only; temporary exterior QA lamps are intentionally outside the carriage.','unit_convention':'Inferred model units, not measured metres.','lights':[]}
for o in S.objects:
 if o.type!='LIGHT':continue
 d=o.data
 if d.type!='AREA':D['lights'].append({'name':o.name,'type':d.type,'classification':'non-area'});continue
 if d.shape in ['DISK','ELLIPSE']:
  ry=(d.size_y if d.shape=='ELLIPSE' else d.size)/2;pts=[(d.size/2*math.cos(a*math.pi/180),ry*math.sin(a*math.pi/180),0) for a in range(360)]
 else:
  hx=d.size/2;hy=(d.size_y if d.shape=='RECTANGLE' else d.size)/2;pts=[]
  corners=[(-hx,-hy,0),(hx,-hy,0),(hx,hy,0),(-hx,hy,0)]
  for i in range(4):
   for j in range(65):pts.append(tuple(corners[i][k]+(corners[(i+1)%4][k]-corners[i][k])*j/64 for k in range(3)))
 wp=[o.matrix_world@Vector(p) for p in pts];bad=[];margins=[]
 for p in wp:
  roof=2.575 if abs(p.x)<=.58 else min(2.575,2.60-(abs(p.x)-.58)*(.24/.92))
  margin=min(1.49-abs(p.x),5.43-abs(p.y),p.z,roof-p.z);margins.append(margin)
  if margin<0:bad.append(list(p))
 D['lights'].append({'name':o.name,'shape':d.shape,'size':d.size,'size_y':d.size_y,'boundary_points':len(wp),'corners_or_boundary_bounds':[[min(p[i] for p in wp) for i in range(3)],[max(p[i] for p in wp) for i in range(3)]],'minimum_conservative_room_margin':min(margins),'outside_enclosure_points':bad,'pass':not bad})
D['area_lights']=len(D['lights']);D['boundary_samples']=sum(o.get('boundary_points',0) for o in D['lights']);D['pass']=all(o.get('pass',True) for o in D['lights']);D['note']='The exterior inspection render uses additional large-area lamps outside the hull on purpose. Their roof highlights are explicit diagnostic lighting, not saved interior emitters leaking through the hull.'
(R/'analysis/light_footprint_qa.json').write_text(json.dumps(D,indent=2));print(json.dumps(D,indent=2))
