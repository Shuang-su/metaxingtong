"""Load the frozen BLEND; add cameras only; retain failed camera renders.
Run with Blender 4.3.2. No transform, material, visibility, or light edits.
"""
import bpy,json,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
D=Path(__file__).resolve().parents[1];R=D.parent;BASE=R/'stage-03-contact-qa'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def value(v):
    if isinstance(v,(str,int,float,bool)):return v
    try:return list(v)
    except:return str(v)
def snapshot():
    s=bpy.context.scene;geometry={};assignment={};materials={};textures={}
    for o in s.objects:
        if o.type!='MESH':continue
        m=o.data;vv=np.array([tuple(o.matrix_world@v.co) for v in m.vertices],dtype=np.float64)
        geometry[o.name]=hashlib.sha256(vv.tobytes()+str([tuple(p.vertices) for p in m.polygons]).encode()).hexdigest()
        assignment[o.name]={'slots':[m.name if m else None for m in o.data.materials],'indices_sha256':sha([p.material_index for p in m.polygons])}
    for m in sorted(bpy.data.materials,key=lambda m:m.name):
        nodes=[]
        if m.use_nodes:
            for n in sorted(m.node_tree.nodes,key=lambda n:n.name):
                node={'name':n.name,'type':n.type,'inputs':{p.name:value(p.default_value) for p in n.inputs if hasattr(p,'default_value')}}
                if n.type=='TEX_IMAGE' and n.image:node['image']={'name':n.image.name,'size':list(n.image.size),'packed':bool(n.image.packed_file)}
                nodes.append(node)
        materials[m.name]={'diffuse_color':list(m.diffuse_color),'nodes':nodes,'links':sorted([f'{l.from_node.name}:{l.from_socket.name}->{l.to_node.name}:{l.to_socket.name}' for l in m.node_tree.links]) if m.use_nodes else []}
    for im in bpy.data.images:
        if im.type=='IMAGE' and im.size[0]:textures[im.name]={'size':list(im.size),'packed':bool(im.packed_file),'pixel_sha256':hashlib.sha256(np.array(im.pixels[:],dtype=np.float32).tobytes()).hexdigest()}
    lighting={'world_background_color':list(s.world.node_tree.nodes['Background'].inputs[0].default_value),'world_strength':s.world.node_tree.nodes['Background'].inputs[1].default_value,'lights':{o.name:{'type':o.data.type,'matrix':[list(r) for r in o.matrix_world],'energy':o.data.energy,'color':list(o.data.color),'angle':getattr(o.data,'angle',None)} for o in s.objects if o.type=='LIGHT'},'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma}
    visibility={o.name:[o.hide_render,o.hide_viewport] for o in s.objects if not o.name.startswith('HOLDOUT_')}
    cameras={o.name:{'matrix':[list(r) for r in o.matrix_world],'lens_mm':o.data.lens,'sensor_width_mm':o.data.sensor_width,'sensor_fit':o.data.sensor_fit,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y} for o in s.objects if o.type=='CAMERA' and o.name.startswith('SRC')}
    all_cameras={o.name:{'matrix':[list(r) for r in o.matrix_world],'data':{k:value(getattr(o.data,k)) for k in ['lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end','type']}} for o in s.objects if o.type=='CAMERA' and not o.name.startswith('HOLDOUT_')}
    return {'geometry_sha256':sha(geometry),'material_nodes_sha256':sha(materials),'material_assignments_sha256':sha(assignment),'texture_pixels_sha256':sha(textures),'lighting_sha256':sha(lighting),'visibility_sha256':sha(visibility),'source_cameras_sha256':sha(cameras),'all_existing_cameras_sha256':sha(all_cameras),'mesh_count':len(geometry),'mesh_geometry_hashes':geometry}
bpy.ops.wm.open_mainfile(filepath=str(BASE/'campus-courtyard_material.blend'))
s=bpy.context.scene;before=snapshot();frozen=json.loads((BASE/'qa/frozen_invariants.json').read_text())
historical={k:before[k]==frozen[k] for k in before if k.endswith('sha256') and k in frozen}
assert all(historical.values()),historical
fit=json.loads((D/'qa/camera_fit.json').read_text())['hypotheses']
for name,c in fit.items():
    d=bpy.data.cameras.new('HOLDOUT_'+name);o=bpy.data.objects.new('HOLDOUT_'+name,d);s.collection.objects.link(o)
    o.location=c['location'];o.rotation_euler=(Vector(c['target'])-o.location).to_track_quat('-Z','Y').to_euler();d.lens=c['lens_mm'];d.sensor_width=36;d.clip_end=250
    o['role']='unaccepted camera-only earlier cross-BV holdout diagnostic';o['geometry_base_commit']='87b37f98911f533605d5aebdd60756edb96fe951'
s.camera=bpy.data.objects['HOLDOUT_FORWARD_COURT_ORDER_F35'];s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
bpy.context.view_layer.update();after=snapshot();assert before==after
bpy.ops.wm.save_as_mainfile(filepath=str(D/'frozen_model_diagnostic_cameras.blend'),compress=True)
# Reload the actual new file, then verify all frozen object state a second time.
bpy.ops.wm.open_mainfile(filepath=str(D/'frozen_model_diagnostic_cameras.blend'));s=bpy.context.scene
reloaded=snapshot();assert reloaded==before
report={'base_commit':'87b37f98911f533605d5aebdd60756edb96fe951','comparison_to_historical_frozen_hashes':historical,'before':before,'after_add_cameras':after,'actual_saved_blend_reloaded':reloaded,'all_existing_state_equal':before==after==reloaded,'only_new_objects':sorted(o.name for o in s.objects if o.name.startswith('HOLDOUT_')),'scope':'Actual world vertex/topology hashes, material nodes/assignments, decoded texture pixels, world/light/color management, existing object visibility and all existing cameras. Active camera and output filename/resolution may differ. No geometry/light/material/state fits.'}
(D/'qa/frozen_state_verification.json').write_text(json.dumps(report,indent=2))
projection={};deps=bpy.context.evaluated_depsgraph_get()
def project(cam,xyz):
    q=world_to_camera_view(s,cam,Vector(xyz));return [q.x*1920,(1-q.y)*1080,q.z]
for name,c in fit.items():
    cam=bpy.data.objects['HOLDOUT_'+name];points=[]
    for r in c['fitting_points']:
        xyz=Vector(r['world']);q=project(cam,xyz);v=xyz-cam.location;hit,loc,nor,idx,obj,mat=s.ray_cast(deps,cam.location,v.normalized(),distance=v.length-.01)
        points.append({**r,'blender_projection':q,'numpy_blender_delta_px':math.dist(q[:2],r['projection_xy']),'occluder_before_target':obj.name if hit else None,'occluder_world':list(loc) if hit else None})
    bounds={}
    for o in s.objects:
        if o.type!='MESH' or not o.name.startswith(('HOOP','STAIR','LAMP','BENCH','GOAL','COURT','TRACK','LAWN','BLD-')):continue
        pp=np.array([project(cam,o.matrix_world@v.co) for v in o.data.vertices]);front=pp[:,2]>.01
        bounds[o.name]={'vertices_in_front':int(front.sum()),'vertices_total':len(pp),'all_in_front':bool(front.all()),'projected_bounds_if_all_in_front':[pp[:,:2].min(0).tolist(),pp[:,:2].max(0).tolist()] if front.all() else None}
    projection[name]={'fit_points':points,'object_projection_bounds':bounds,'warning':'Projection bounds do not mean visibility; point rays and actual full-scene render are separate checks.'}
(D/'qa/blender_projections_and_occlusion.json').write_text(json.dumps(projection,indent=2))
s.render.threads_mode='FIXED';s.render.threads=4
# Same frozen Cycles sample count (32) and lighting/material settings; smaller images are previews.
for name in fit:
    full=name.endswith('_F35');s.camera=bpy.data.objects['HOLDOUT_'+name]
    s.render.resolution_x=1920 if full else 960;s.render.resolution_y=1080 if full else 540;s.render.resolution_percentage=100
    s.render.filepath=str(D/('renders' if full else 'trials')/(name+('' if full else '_960x540_preview')+'.png'))
    print('DIAGNOSTIC_RENDER_START',name,s.render.resolution_x,s.render.resolution_y,flush=True)
    bpy.ops.render.render(write_still=True)
    print('DIAGNOSTIC_RENDER_DONE',name,flush=True)
print('DIAGNOSTIC_ALL_DONE',flush=True)
