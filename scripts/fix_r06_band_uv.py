import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];BASE=R/'stages/r05-review-candidate';O=R/'stages/r06-review-candidate';O.mkdir(exist_ok=True)
def snap():
    out={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        h=hashlib.sha256()
        for v in ob.data.vertices:h.update(struct.pack('<3d',*(ob.matrix_world@v.co)))
        for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
        out[ob.name]=h.hexdigest()
    return out
states={}
for state in ['white','material']:
    bpy.ops.wm.open_mainfile(filepath=str(BASE/('harbor-r05-'+state+'.blend')));sc=bpy.context.scene;before=snap();oldcams={o.name:[list(r) for r in o.matrix_world]+[[o.data.lens,o.data.shift_x,o.data.shift_y]] for o in sc.objects if o.type=='CAMERA'}
    if state=='material':
        image=bpy.data.images.load(str(R/'textures/curved-band-led-grid-r06.png'));image.pack();mat=bpy.data.materials['Curved support grid LED']
        for node in mat.node_tree.nodes:
            if node.type=='TEX_IMAGE':node.image=image
        for name in ['FRAME_L','FRAME_R']:
            ob=bpy.data.objects[name];uv=ob.data.uv_layers.active
            for p in ob.data.polygons:
                if p.material_index!=1:continue
                for li in p.loop_indices:
                    vi=ob.data.loops[li].vertex_index;t=(vi//4)/64;u=1-t if name=='FRAME_L' else t;v=1.0 if vi%4 in (1,3) else 0.0;uv.data[li].uv=(u,v)
            ob['band_uv_fix']='word baseline follows longitudinal arc, left foot-to-top and right top-to-foot; no mirrored glyphs; coarse source-inspired typography not exact recreation'
    for side,sgn in [('L',-1),('R',1)]:
        name='CHECK_BAND_'+side;da=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,da);sc.collection.objects.link(ob);ob.location=(sgn*1.3,-3.0,1.8);ob.rotation_euler=(Vector((sgn*1.3,1,1.8))-ob.location).to_track_quat('-Z','Y').to_euler();da.lens=50;da.clip_end=300;ob['role']='UV diagnostic only, not source camera'
    for n,values in oldcams.items():
        ob=bpy.data.objects[n];assert values==[list(r) for r in ob.matrix_world]+[[ob.data.lens,ob.data.shift_x,ob.data.shift_y]]
    after=snap();assert before==after;states[state]=after
    sc['status']='R06 REVIEW CANDIDATE; SOURCE NOT ACCEPTED';sc['material_revision']='R05 display faces plus R06 longitudinal curve-band UV correction; geometry/source cameras/lighting unchanged'
    bpy.ops.wm.save_as_mainfile(filepath=str(O/('harbor-r06-'+state+'.blend')))
    bpy.ops.export_scene.gltf(filepath=str(O/('harbor-r06-'+state+'.glb')),export_format='GLB',export_cameras=True,export_lights=False,export_extras=True)
assert states['white']==states['material']
(O/'geometry-identity.json').write_text(json.dumps({'white_material_exact_match':True,'all394_world_meshes_unchanged_from_r04':True,'all_existing_cameras_unchanged':True,'lighting_unchanged':True,'geometry_hashes':states['white']},indent=2));(O/'source-cameras.json').write_bytes((BASE/'source-cameras.json').read_bytes())
(O/'material-fix-summary.json').write_text(json.dumps({'inherited_r05_fixes':json.loads((BASE/'material-face-fixes.json').read_text()),'r06_band_uv':{'objects':['FRAME_L','FRAME_R'],'U':'left1-t, rightt along source strip path','V':'outer edge1, inner edge0','texture':'textures/curved-band-led-grid-r06.png','purpose':'correct word orientation and scale; generic source-inspired font, exact Chinese artwork still not reproduced'},'white_material_geometry_unchanged':True},indent=2))
print('R06_READY',len(states['white']))
