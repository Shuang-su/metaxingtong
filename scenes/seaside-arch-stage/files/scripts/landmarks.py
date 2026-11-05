import bpy,os,json,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));bpy.ops.wm.open_mainfile(filepath=r+'/models/material.blend');s=bpy.context.scene
pts={'outer_apex':(0,4.1,5.88),'outer_left':(-5.5,4.1,.38),'outer_right':(5.5,4.1,.38),'middle_apex':(0,4.32,4.23),'inner_apex':(0,4.54,3.23),'round_left':(-1.85,3.55+.035*1.85**2-.18,2.2),'round_middle':(0,3.37,2.2),'round_right':(1.85,3.55+.035*1.85**2-.18,2.2),'upper_left':(-3.85,3.55+.035*3.85**2,2.97),'upper_right':(3.85,3.55+.035*3.85**2,2.97),'umbrella_apex':(6.4,1.15,4.25)}
src={'SOURCE03 conditional':{'outer_apex':[585,178],'outer_left':[279,449],'outer_right':[903,448],'middle_apex':[585,287],'inner_apex':None,'round_left':[484,415],'round_middle':[576,417],'round_right':[663,416],'upper_left':[368,371],'upper_right':[789,370],'umbrella_apex':None},'SOURCE04 conditional':{'outer_apex':None,'outer_left':[0,345],'outer_right':[904,344],'middle_apex':[465,78],'inner_apex':[464,186],'round_left':[321,301],'round_middle':[449,300],'round_right':[579,303],'upper_left':[130,230],'upper_right':[752,235],'umbrella_apex':None}}
for v in src.values():v['outer_left']=None;v['outer_right']=None
out={'status':'conditional approximate manual anchors; not calibrated; null=cropped/occluded unknown; no fit pass','cameras':{}}
for cam,sp in src.items():
 out['cameras'][cam]=[]
 for n,pt in pts.items():
  q=world_to_camera_view(s,bpy.data.objects[cam],Vector(pt));pred=[1192*q.x,671*(1-q.y)];obs=sp.get(n);out['cameras'][cam].append({'name':n,'source_pixel':obs,'model_world':pt,'render_pixel':pred,'camera_positive_depth':q.z>0,'camera_depth':q.z,'residual_pixels':math.dist(obs,pred) if obs else None})
json.dump(out,open(r+'/qa/landmarks.json','w'),indent=2)
