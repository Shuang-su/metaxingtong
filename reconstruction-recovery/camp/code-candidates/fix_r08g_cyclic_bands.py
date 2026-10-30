import bpy,bmesh,math,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];out=r/'qa/R08_trial';bpy.ops.wm.open_mainfile(filepath=str(r/'models/R08f_partial_geometry.blend'));s=bpy.context.scene;p=.55
sp=lambda x:math.copysign(abs(x)**p,x)
for x in [-.78,.78]:
 name='P02_vertical_band_'+str(x);old=bpy.data.objects[name];mat=old.data.materials[0];bpy.data.objects.remove(old,do_unlink=True);c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=.022;c.bevel_resolution=2;c.use_fill_caps=False;sl=c.splines.new('POLY');sl.points.add(63);sl.use_cyclic_u=True;factor=(1-(abs(x)/1.25)**(2/p))**(p/2)
 for k,pt in enumerate(sl.points):q=math.tau*k/64;pt.co=(-.55+x,6.65+(.36*factor+.006)*sp(math.cos(q)),max(.022,.59-.025+.59*factor*sp(math.sin(q))),1)
 o=bpy.data.objects.new(name,c);s.collection.objects.link(o);c.materials.append(mat);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
 for v in o.data.vertices:v.co.x-=.45*max(0,min(1,(v.co.x+.55)/1.25))**1.2
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(r/'models/R08g_partial_geometry.blend'));(out/'R08g_report.json').write_text(json.dumps({'fix':'two closed loop bands reconstructed as genuinely cyclic curves without end caps, then converted/welded; removes internal seam caps, not extra fake caps','shape':'R08f retained, no camera/roof/body changes','unaccepted':True},indent=2));print('R08G_DONE')
