import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;S=R.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(S/'models/car_passenger_cabin_material.blend'))
s=bpy.context.scene
def point(obj,desired):
 o=bpy.data.objects[obj];return list(min((o.matrix_world@v.co for v in o.data.vertices),key=lambda p:(p-Vector(desired)).length))
geometry=[]
for o in sorted([o for o in s.objects if o.type=='MESH'],key=lambda x:x.name):geometry.append([o.name,[[float(c) for c in v.co] for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]])
report={'geometry_vertex_topology_sha256':hashlib.sha256(json.dumps(geometry,separators=(',',':')).encode()).hexdigest(),'states':{},'cameras':{}}
for frame in [1,2]:
 s.frame_set(frame);bpy.context.view_layer.update();hinge=bpy.data.objects['STATE_passenger_door_hinge']
 def door(p):return list(hinge.matrix_world@hinge.matrix_parent_inverse@Vector((p[0]-.99,p[1]-.93,p[2])))
 # Parent has origin (.99,.93,0); child model coordinates at frame1 are world coordinates.
 def door(p):
  angle=0 if frame==1 else math.radians(54);x,y,z=p;dx=x-.99;dy=y-.93
  return [.99+dx*math.cos(angle)-dy*math.sin(angle),.93+dx*math.sin(angle)+dy*math.cos(angle),z]
 report['states'][str(frame)]={
  'vent_center':[.8,.6135,.77],
  'vent_rim':[[.8+.117*math.cos(a*2*math.pi/160),.6135,.77+.117*math.sin(a*2*math.pi/160)] for a in range(160)],
  'dash_top_corner':point('D01_dashboard_top',(1.015,.65,1.022)),
  'dash_bottom_corner':point('D01_dashboard_top',(1.015,.65,.947)),
  'a_foot':point('A01_fixed_A_pillar',(.87,.93,.97)),
  'a_inner_edge':[[.87,.93,.97],[.87,.23,1.66]],
  'door_belt_line':[door([.90,.75,.98]),door([.90,-.82,.98])],
  'roof_lower_line':[[.87,.15,1.615],[.87,-.8,1.615]],
  'mirror_center':door([1.11,.628,1.20])
 }
for id in ['S01','S02','S03']:
 c=bpy.data.objects['SRC_'+id+('_open' if id=='S02' else '_closed')];forward=c.matrix_world.to_quaternion()@Vector((0,0,-1));yaw=math.atan2(forward.y,forward.x);pitch=math.asin(forward.z)
 report['cameras'][id]={'position':list(c.location),'yaw_pitch_roll':[yaw,pitch,0],'lens':c.data.lens,'state':2 if id=='S02' else 1}
(R/'shared_geometry.json').write_text(json.dumps(report,indent=2)+'\n')
