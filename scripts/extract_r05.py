import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent.parent;src=P.parent/'cyber-roof-stage-20261105/models/roof-r05.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;objs=[o for o in s.objects if o.name.startswith('ROOF_MAIN')]
def proj(v,c):
 p=world_to_camera_view(s,c,Vector(v));return {'xy':[p.x*1192,(1-p.y)*671],'camera_depth':p.z,'inside_image':0<=p.x<=1 and 0<=p.y<=1 and p.z>0}
allv=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
res={'input':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'status':'read only; no model saved or altered','dimensions':[1192,671],'world_bounds':[[min(v[i] for v in allv),max(v[i] for v in allv)] for i in range(3)],'objects':[],'cameras':{},'landmarks':[]}
for o in objs:
 vs=[o.matrix_world@v.co for v in o.data.vertices];res['objects'].append({'name':o.name,'type':o.type,'matrix_world':[list(r) for r in o.matrix_world],'vertices':len(vs),'faces':len(o.data.polygons),'world_bounds':[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]})
cams=[bpy.data.objects[n] for n in ['SOURCE11 conditional camera','SOURCE10 auxiliary different state']]
for c in cams:res['cameras'][c.name]={'matrix_world':[list(r) for r in c.matrix_world],'location':list(c.location),'rotation_euler':list(c.rotation_euler),'lens':c.data.lens,'sensor_width':c.data.sensor_width,'sensor_height':c.data.sensor_height,'sensor_fit':c.data.sensor_fit,'shift_x':c.data.shift_x,'shift_y':c.data.shift_y,'render_percentage_saved':s.render.resolution_percentage,'pixel_aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y]}
# Authored centerline stations, not bbox corners. Exact generator equation is retained in scripts/build.py.
# Main roof center=(0,5.5); basez6, halfwidth11.4, halfdepth3, rise2.5.
for feature,t in [('ridge',0),('front_eave',-1),('back_eave_inferred',1)]:
 for u in [-1,-.75,-.5,-.25,0,.25,.5,.75,1]:
  x=u*11.4*(.74+.26*abs(t));y=5.5+t*3;z=6+2.5*(1-abs(t))**2+.8*abs(u)**7*abs(t)**2+.12
  co=[x,y,z];ob=bpy.data.objects['ROOF_MAIN gold '+('ridge' if t==0 else ('front eave' if t==-1 else 'back eave inferred'))]
  # Actual mesh nearest point distance validates that station lies on/inside a tubular trim, rather than asserting exact pixel edge.
  dist=min((ob.matrix_world@v.co-Vector(co)).length for v in ob.data.vertices)
  res['landmarks'].append({'id':feature+'_u'+str(u),'feature':feature,'u':u,'t':t,'world_centerline':co,'nearest_actual_mesh_vertex_distance':dist,'tube_radius':.085,'role':'authored trim centerline station; not a measured source edge or visible silhouette','projection':{c.name:proj(co,c) for c in cams}})
# Actual shell front/ridge stations are distinct from raised gold centerlines, preserving correspondences.
o=bpy.data.objects['ROOF_MAIN closed shell']
for feature,t,j in [('shell_ridge',0,16),('shell_front_edge',-1,0)]:
 for i in [0,8,16,24,32,40,48,56,64]:
  ix=j*65+i;v=o.matrix_world@o.data.vertices[ix].co
  res['landmarks'].append({'id':feature+'_vertex'+str(ix),'feature':feature,'mesh_object':o.name,'mesh_vertex':ix,'world_actual_vertex':list(v),'role':'actual saved mesh vertex, not ray-tested for source visibility','projection':{c.name:proj(v,c) for c in cams}})
(P/'results/r05-main-roof-projection.json').write_text(json.dumps(res,indent=2))
print('objects',len(objs),'world_bounds',res['world_bounds'],'landmarks',len(res['landmarks']))
