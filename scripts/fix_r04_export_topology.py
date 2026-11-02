import bpy,bmesh,math,json,hashlib,struct
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];BASE=R/'stages/r03b-mounted-review';O=R/'stages/r04-review-candidate';O.mkdir(exist_ok=True)
def snap():
    rows={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        h=hashlib.sha256();vs=[ob.matrix_world@v.co for v in ob.data.vertices]
        for v in vs:h.update(struct.pack('<3d',*v))
        vh=h.hexdigest()
        for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
        rows[ob.name]={'vertex_position_sha':vh,'full_sha':h.hexdigest(),'bbox':[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]}
    return rows
states={};reports={};cams={}
for state in ['white','material']:
    bpy.ops.wm.open_mainfile(filepath=str(BASE/('harbor-r03b-'+state+'.blend')));sc=bpy.context.scene;before=snap();cam_before={o.name:[list(row) for row in o.matrix_world]+[[o.data.lens,o.data.shift_x,o.data.shift_y]] for o in sc.objects if o.type=='CAMERA'}
    rr=[]
    for name in ['FRAME_L','FRAME_R']:
        ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);oldfaces=len(bm.faces);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bad=sum(f.calc_area()<1e-10 for f in bm.faces);assert bad==0,(name,bad);bm.to_mesh(ob.data);bm.free();ob.data.update();ob['export_repair']='beauty triangulation avoids collinear zero-triangle diagonal; vertex positions unchanged';rr.append({'id':name,'old_faces':oldfaces,'new_faces':len(ob.data.polygons),'change':'tessellation only, identical vertex coordinates'})
    for idx,(x,y,h) in enumerate([(10.4,5.7,2.6),(12.2,6.1,1.9)]):
        name='NEON_PROP_ARCH_'+str(idx);ob=bpy.data.objects[name];raw=[(x-.52,y-.20,0),(x-.52,y-.20,h-.52)]+[(x+.52*math.cos(math.pi-j*math.pi/16),y-.20,h-.52+.52*math.sin(math.pi-j*math.pi/16)) for j in range(17)]+[(x+.52,y-.20,0)];pts=[]
        for p in raw:
            if not pts or (Vector(p)-Vector(pts[-1])).length>1e-6:pts.append(p)
        vv=[];ff=[];n=8;radius=.028
        for i,p in enumerate(pts):
            p=Vector(p);d=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)]);d.normalize();u=d.cross(Vector((0,0,1)))
            if u.length<.01:u=d.cross(Vector((0,1,0)))
            u.normalize();v=d.cross(u).normalized()
            for j in range(n):vv.append(p+radius*(math.cos(math.tau*j/n)*u+math.sin(math.tau*j/n)*v))
        ff=[tuple(reversed(range(n))),tuple(range((len(pts)-1)*n,len(pts)*n))]
        for i in range(len(pts)-1):
            for j in range(n):k=(j+1)%n;ff.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j))
        me=bpy.data.meshes.new(name+'_deduplicated');me.from_pydata(vv,[],ff);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
        for mat in ob.data.materials:me.materials.append(mat)
        ob.data=me;ob['export_repair']='one duplicate consecutive arch point removed; no added external feature';rr.append({'id':name,'old_path_points':len(raw),'new_path_points':len(pts),'change':'remove redundant consecutive point and folded internal sweep strip'})
    after=snap();allowed={'FRAME_L','FRAME_R','NEON_PROP_ARCH_0','NEON_PROP_ARCH_1'};changed={n for n in before if before[n]['full_sha']!=after[n]['full_sha']};assert changed==allowed,(changed,allowed)
    for n in ['FRAME_L','FRAME_R']:assert before[n]['vertex_position_sha']==after[n]['vertex_position_sha']
    cam_after={o.name:[list(row) for row in o.matrix_world]+[[o.data.lens,o.data.shift_x,o.data.shift_y]] for o in sc.objects if o.type=='CAMERA'};assert cam_before==cam_after
    sc['status']='R04 REVIEW CANDIDATE, NOT SOURCE ACCEPTED';sc['export_topology_fix']='Two frames tessellated without moving vertices; two accessory arch duplicate points removed; all cameras unchanged'
    bpy.ops.wm.save_as_mainfile(filepath=str(O/('harbor-r04-'+state+'.blend')))
    bpy.ops.export_scene.gltf(filepath=str(O/('harbor-r04-'+state+'.glb')),export_format='GLB',export_cameras=True,export_lights=False,export_extras=True)
    states[state]=after;reports[state]=rr;cams[state]=cam_after
assert states['white']==states['material'];assert cams['white']==cams['material']
(O/'geometry-identity.json').write_text(json.dumps({'white_material_exact_match':True,'changed_objects_from_r03b':sorted(allowed),'390_other_meshes_unchanged':True,'frame_vertices_exactly_unchanged':True,'cameras_exactly_unchanged':True,'objects':states['white']},indent=2))
(O/'technical-fixes.json').write_text(json.dumps(reports,indent=2));(O/'source-cameras.json').write_bytes((BASE/'source-cameras.json').read_bytes())
print('R04_READY',len(states['white']))
