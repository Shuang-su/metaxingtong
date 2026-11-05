import bpy,bmesh,os,json
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));bpy.ops.wm.open_mainfile(filepath=r+'/models/material.blend');o=bpy.data.objects['SIGN_QQ炫舞_font_proxy'];out=[]
for mode in ['limit','iterate']:
 b=bmesh.new();b.from_mesh(o.data);steps=[]
 for k in range(6):
  if mode=='limit':bmesh.ops.dissolve_limit(b,angle_limit=1e-5,use_dissolve_boundaries=False,verts=list(b.verts),edges=list(b.edges),delimit={'NORMAL'})
  else:bmesh.ops.dissolve_faces(b,faces=[f for f in b.faces if f.calc_area()<1e-12],use_verts=True)
  bmesh.ops.dissolve_degenerate(b,dist=1e-7,edges=list(b.edges));bmesh.ops.recalc_face_normals(b,faces=list(b.faces));steps.append({'v':len(b.verts),'f':len(b.faces),'nm':sum(not e.is_manifold for e in b.edges),'deg':sum(f.calc_area()<1e-12 for f in b.faces),'volume':b.calc_volume(signed=True)})
 out.append({'method':mode,'steps':steps});b.free()
json.dump(out,open(r+'/qa/text-dissolve-tests.json','w'),indent=2);print(out)
