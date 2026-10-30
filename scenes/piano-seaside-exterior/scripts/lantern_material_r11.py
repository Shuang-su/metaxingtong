"""Shared lamp-only correction. World, geometry, non-lamp materials and cameras stay fixed.
Panel area lights approximate luminous paper exitance in EEVEE, not extra fixtures.
"""
import bpy,math
from pathlib import Path
from mathutils import Vector
LAMP_IDS={'L01_lantern','L02_lantern'}
def apply_lanterns(core=8.0,panel_watts=1.4,variant='b'):
 s=bpy.context.scene
 # Reuse existing UV intensity, but separate its red-channel intensity from the
 # old sRGB orange tint. No texture files, source pixels or material UVs change.
 for m in bpy.data.materials:
  outer=m.name=='R09 warm paper bag - emission approximates translucency'
  inner=m.name.endswith('inferred lit interior paper')
  back=m.name.endswith('inferred back panel warm illumination')
  if not (outer or inner or back):continue
  b=m.node_tree.nodes.get('Principled BSDF');n=m.node_tree.nodes;l=m.node_tree.links
  if outer or inner:
   tex=next(nod for nod in n if nod.type=='TEX_IMAGE' and nod.image.name=='paper_emission.png')
   for link in list(b.inputs['Emission Color'].links):l.remove(link)
   if variant=='a':
    sep=n.new('ShaderNodeSeparateColor');sep.name='R11 existing radial intensity';sep.mode='RGB';l.new(tex.outputs['Color'],sep.inputs['Color'])
    gain=n.new('ShaderNodeMath');gain.name='R11 shared paper exitance';gain.operation='MULTIPLY';gain.inputs[1].default_value=core if outer else 4.0;l.new(sep.outputs['Red'],gain.inputs[0]);l.new(gain.outputs[0],b.inputs['Emission Strength'])
    b.inputs['Emission Color'].default_value=(1,.55,.12,1)
   else:
    new=n.new('ShaderNodeTexImage');new.name='R11 portable paper exitance';new.image=bpy.data.images.load(str(Path(__file__).resolve().parents[1]/'textures/r11'/('paper_exitance.png' if outer else 'paper_inner_exitance.png')),check_existing=True)
    l.new(new.outputs['Color'],b.inputs['Emission Color']);b.inputs['Emission Strength'].default_value=core if outer else 4.0
  else:b.inputs['Emission Color'].default_value=(1,.48,.09,1);b.inputs['Emission Strength'].default_value=4.0
  m['r11_scope']='lamp emission only; prior base color/roughness/normal/UV preserved'
 report=[]
 for id,(x,y,z),w in [('L01_lantern',(-.92,1.22,0),.25),('L02_lantern',(7.2,-5.5,-.08),.27)]:
  lamp=next(o for o in s.objects if o.type=='LIGHT' and o.get('evidence_id')==id)
  old=list(lamp.location);lamp.location.z+=.075;lamp.data.use_shadow=True
  # Four area lights represent outward flux through four paper panels. Same
  # rig for both instances, fixed in world space, shadows enabled throughout.
  added=[];d=w*.84;h=w*1.55
  for side,(nx,ny),dist,width in [('front',(0,-1),d/2,w),('back',(0,1),d/2,w),('left',(-1,0),w/2,d),('right',(1,0),w/2,d)]:
   data=bpy.data.lights.new(id+' R11 paper exitance '+side,'AREA');data.energy=panel_watts*(w/.25)**2;data.color=(1,.42,.09);data.shape='RECTANGLE';data.size=width*.80;data.size_y=h*.60;data.use_shadow=True
   o=bpy.data.objects.new(data.name,data);s.collection.objects.link(o);o.location=(x+nx*(dist+.008),y+ny*(dist+.008),z+.014+h*.40);o.rotation_euler=Vector((nx,ny,0 if variant=='c' else -.35)).to_track_quat('-Z','Y').to_euler();o['evidence_id']=id;o['camera_independent']=True;o['status']='inferred paper transmitted-light approximation; not a new physical lamp';added.append(o.name)
  report.append({'id':id,'point_before':old,'point_after':list(lamp.location),'point_energy_unchanged':lamp.data.energy,'shadow_enabled':True,'area_lights':added,'watts_per_panel':panel_watts*(w/.25)**2,'panel_light_purpose':'approximate transmitted paper flux; global fixed rig, not per-camera fill'})
 return {'variant':variant,'core_gain':core,'panel_watts_base':panel_watts,'lamps':report,'exposure_unchanged':s.view_settings.exposure,'time_state_binding':'none; identical lamp parameters for both existing world states'}
