import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Classroom_Textured.blend'));sc=bpy.context.scene;cam=bpy.data.objects['MATCH_C_Wide_01h11m24s']
# Manual source anchors are approximate, selected from the actual 1192x750 screenshot.
# Crop is 1190x669, origin (0,27), followed by uniform 16:9 resampling.
a=[('Board top left',(451,248),(1.9,.084,2.44)),('Board top right',(745,248),(-1.9,.084,2.44)),('Board bottom left',(451,368),(1.9,.084,.92)),('Board bottom right',(745,368),(-1.9,.084,.92)),('TV top left',(539,181),(.775,.21,3.26)),('TV top right',(655,181),(-.775,.21,3.26)),('TV bottom left',(539,239),(.775,.21,2.54)),('TV bottom right',(655,239),(-.775,.21,2.54)),('Clock centre',(737,224),(-1.82,.125,2.73))]
r=[]
for n,p,w in a:
 ref=(p[0]/1190*1280,(p[1]-27)/669*720);q=world_to_camera_view(sc,cam,Vector(w));ren=(q.x*1280,(1-q.y)*720);e=math.dist(ref,ren);r.append({'anchor':n,'source_xy':p,'reference_resampled_xy':ref,'render_xy':ren,'pixel_error':e})
result={'reference':'class_4284.jpg (requested 01:11:24, displayed 01:11:25)','camera':cam.name,'output_resolution':[1280,720],'method':'Manually selected approximate front-wall landmarks, no performer fitting and no local image warp. A diagnostic, not a survey or a pixel-perfect claim.','source_anchor_uncertainty_px':3,'mean_anchor_pixel_error':sum(x['pixel_error'] for x in r)/len(r),'max_anchor_pixel_error':max(x['pixel_error'] for x in r),'anchors':r}
json.dump(result,open(R/'qa/wide_camera_landmarks.json','w'),indent=2);print(json.dumps(result,indent=2))
