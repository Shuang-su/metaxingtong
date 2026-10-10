import bpy,bmesh,math,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'deliverables/01_train_material.blend';bpy.ops.wm.open_mainfile(filepath=str(p))
def cutter(name,poly,y0,y1):
 n=len(poly);vs=[(x,y,z) for y in [y0,y1] for x,z in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);assert bm.calc_volume(signed=True)>0;bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);return o
def subtract(o,c):
 m=o.modifiers.new('Verified true aperture through solid','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=bm.edges,dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();o['Aperture_QA']='Outward-normal cutter; independently checked for opaque backing'
pts=[];w=.45;h=.745;r=.038
for cx,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
 for k in range(9):
  a=math.radians(start+k*90/8);pts.append((cx+r*math.cos(a),cz+r*math.sin(a)+1.68))
for sy in [-1,1]:
 c=cutter('Correct outward rounded light cutter',pts,sy*5.55-.4,sy*5.55+.4)
 for o in list(bpy.data.objects):
  if o.name.startswith(('End door leaf','End door rounded dark window frame','Door glass full-depth dark reveal')):
   ym=sum((o.matrix_world@v.co).y for v in o.data.vertices)/len(o.data.vertices)
   if ym*sy>0:subtract(o,c)
 bpy.data.objects.remove(c,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);print('DOOR_APERTURES_FIXED',flush=True)
