import bpy,bmesh,os,json
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));out={}
def measure(b):
 tris=b.calc_loop_triangles();ar=[((t[1].vert.co-t[0].vert.co).cross(t[2].vert.co-t[0].vert.co)).length/2 for t in tris];return {'zero':sum(a<1e-12 for a in ar),'area':sum(ar),'volume':b.calc_volume(signed=True),'nm':sum(not e.is_manifold for e in b.edges)}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=r+'/models/'+mode+'.blend');o=bpy.data.objects['SIGN_QQ炫舞_font_proxy'];base=bmesh.new();base.from_mesh(o.data);before=measure(base);bad=[f for f in base.faces if len(f.verts)==3 and ((f.verts[1].co-f.verts[0].co).cross(f.verts[2].co-f.verts[0].co)).length<2e-12][0];candidates=[]
 for e in bad.edges:
  others=[f for f in e.link_faces if f!=bad]
  if len(others)==1 and len(others[0].verts)==3 and abs(others[0].normal.y)>.99:candidates.append([tuple(v.co) for v in e.verts])
 trials=[];chosen=None
 for ec in candidates:
  for ccw in [False,True]:
   b=base.copy();e=next(e for e in b.edges if sorted(tuple(v.co) for v in e.verts)==sorted(ec))
   result=bmesh.ops.rotate_edges(b,edges=[e],use_ccw=ccw);bmesh.ops.recalc_face_normals(b,faces=list(b.faces));m=measure(b);good=m['zero']==0 and m['nm']==0 and abs(m['area']-before['area'])<1e-6 and abs(m['volume']-before['volume'])<1e-7;trials.append({'edge':ec,'ccw':ccw,'measure':m,'valid_limited':good})
   if good and chosen is None:chosen=b
   else:b.free()
 out[mode]={'before':before,'trials':trials,'applied':chosen is not None}
 if chosen:
  out[mode]['exact_vertex_multiset_equal']=sorted(tuple(v.co) for v in chosen.verts)==sorted(tuple(v.co) for v in base.verts);chosen.to_mesh(o.data);chosen.free();bpy.ops.wm.save_as_mainfile(filepath=r+'/models/'+mode+'.blend');bpy.ops.export_scene.gltf(filepath=r+'/models/'+mode+'.glb',export_format='GLB',export_cameras=True,export_lights=False)
 base.free()
json.dump(out,open(r+'/qa/sign-back-cap-retessellation-r03.json','w'),indent=2);print(out)
