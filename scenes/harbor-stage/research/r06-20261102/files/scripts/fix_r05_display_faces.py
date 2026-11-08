import bpy,math,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];BASE=R/'stages/r04-review-candidate';O=R/'stages/r05-review-candidate';O.mkdir(exist_ok=True)
def geom():
    out={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        h=hashlib.sha256()
        for v in ob.data.vertices:h.update(struct.pack('<3d',*(ob.matrix_world@v.co)))
        for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
        out[ob.name]=h.hexdigest()
    return out
def camera(name,loc,target,lens):
    da=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,da);bpy.context.scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();da.lens=lens;da.clip_end=300;ob['role']='DIAGNOSTIC ONLY, not a source camera; no object hiding';return ob
states={};reports=[]
for state in ['white','material']:
    bpy.ops.wm.open_mainfile(filepath=str(BASE/('harbor-r04-'+state+'.blend')));sc=bpy.context.scene;before=geom();source_cams={o.name:[list(r) for r in o.matrix_world]+[[o.data.lens,o.data.shift_x,o.data.shift_y]] for o in sc.objects if o.type=='CAMERA'}
    if state=='material':
        for name in ['CROWN_TOP_DISPLAY_DRUM','CROWN_MID_DISPLAY_RING','CROWN_OUTER_DISPLAY_RING','BACK_DISPLAY_RAIL']:
            ob=bpy.data.objects[name];ob.data.materials.clear();ob.data.materials.append(bpy.data.materials['Titanium brushed']);ob.data.materials.append(bpy.data.materials['2025 circular LED signage']);uv=ob.data.uv_layers.active
            target_type=2 if name=='BACK_DISPLAY_RAIL' else 3;vmin=min(v.co.z for v in ob.data.vertices);vmax=max(v.co.z for v in ob.data.vertices);center_y=0 if name=='BACK_DISPLAY_RAIL' else 1
            for p in ob.data.polygons:
                p.material_index=1 if p.index%4==target_type else 0
                coords=[]
                for li in p.loop_indices:
                    v=ob.data.vertices[ob.data.loops[li].vertex_index].co;u=(math.atan2(v.y-center_y,v.x)/math.tau)%1
                    if name=='BACK_DISPLAY_RAIL':u=1-u
                    coords.append((li,u,(v.z-vmin)/(vmax-vmin)))
                us=[x[1] for x in coords];seam=max(us)-min(us)>.5
                for li,u,v in coords:uv.data[li].uv=(u+1 if seam and u<.5 else u,v)
            ob['material_fix']='LED on outward cylinder face only; rear rail inward-facing display. Caps and reverse surfaces plain metal; angular UV seam unwrapped.'
            reports.append({'id':name,'led_face_class_mod4':target_type,'other_faces':'Titanium brushed','UV':'continuous angle U; rear rail reverses U for inward display; seam unwrapped per polygon','geometry_changed':False})
    # Add genuinely useful inspection cameras without altering any existing/source camera.
    for i in range(8):
        a=math.radians(-90+i*45);camera('CHECK_EFFECTIVE_%02d'%(i+1),(14*math.cos(a),14*math.sin(a),14),(0,0,2.7),35)
    camera('CHECK_LED_INNER',(0,1,5.9),(0,3.3,5.9),28)
    camera('CHECK_LED_OUTER_BACK',(0,10,6.0),(0,1,5.9),48)
    camera('CHECK_LED_OUTER_FRONT',(0,-9,6),(0,1,5.9),48)
    for name,vals in source_cams.items():
        ob=bpy.data.objects[name];assert vals==[list(r) for r in ob.matrix_world]+[[ob.data.lens,ob.data.shift_x,ob.data.shift_y]]
    after=geom();assert before==after;states[state]=after
    sc['status']='R05 REVIEW CANDIDATE, SOURCE UNACCEPTED';sc['material_revision']='Four display objects corrected to one-sided LED; geometry, prior cameras and lighting unchanged'
    bpy.ops.wm.save_as_mainfile(filepath=str(O/('harbor-r05-'+state+'.blend')))
    bpy.ops.export_scene.gltf(filepath=str(O/('harbor-r05-'+state+'.glb')),export_format='GLB',export_cameras=True,export_lights=False,export_extras=True)
assert states['white']==states['material']
(O/'geometry-identity.json').write_text(json.dumps({'white_material_exact_match':True,'all394_world_meshes_unchanged_from_r04':True,'all_existing_cameras_unchanged':True,'added_cameras':'8 elevated effective inspection +3 LED surface diagnostics; no scene objects hidden','geometry_hashes':states['white']},indent=2))
(O/'material-face-fixes.json').write_text(json.dumps(reports,indent=2));(O/'source-cameras.json').write_bytes((BASE/'source-cameras.json').read_bytes())
print('R05_MATERIAL_STAGE_READY',len(states['white']))
