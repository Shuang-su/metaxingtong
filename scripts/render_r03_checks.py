import bpy,math,json
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r03.blend'))
s=bpy.context.scene;s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_percentage=100
records=[]
def render(n,c,x=1192,y=671):
 s.camera=c;s.render.resolution_x=x;s.render.resolution_y=y;s.render.filepath=str(P/'renders'/n);bpy.ops.render.render(write_still=True)
 records.append({'file':n,'camera':c.name,'location':list(c.location),'rotation':list(c.rotation_euler),'lens':c.data.lens,'sensor_width':c.data.sensor_width,'sensor_fit':c.data.sensor_fit,'pixel_aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y],'resolution':[x,y],'percentage':100,'state':'same fixed 11 DJ geometry; 10 different-source-state diagnostic only'})
render('source11-r03.png',bpy.data.objects['SOURCE11 conditional camera'])
render('source10-auxiliary-r03.png',bpy.data.objects['SOURCE10 auxiliary different state'])
# These are inspection cameras, never count as observed source baselines.
configs=[('01-front-oblique',(-21,-25,14),(0,2,3)),('02-right-oblique',(23,-21,12),(0,2,3)),('03-left-profile',(-29,1,7),(0,2,3)),('04-right-profile',(29,1,7),(0,2,3)),('05-rear-roof-hypothesis',(0,27,13),(0,3,4)),('06-top-layout',(0,0,35),(0,1,0)),('07-low-thickness',(16,-25,2),(0,1,2)),('08-underside-unknown-support',(0,-22,-5),(0,2,3))]
for n,loc,tar in configs:
 bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.name='CHECK '+n;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=35
 render('check-'+n+'.png',c,796,448)
(P/'qa/render-cameras.json').write_text(json.dumps(records,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r03-white.blend'));s=bpy.context.scene;s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_percentage=100;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.filepath=str(P/'renders/source11-white-r03.png');bpy.ops.render.render(write_still=True)
