import bpy,bmesh,json,hashlib,math,struct
from pathlib import Path
from collections import Counter
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import numpy as np
R=Path(__file__).resolve().parents[2];D=R/'stage-03-contact-qa';Q=D/'qa';Q.mkdir(exist_ok=True)
def geometry():
    result={};verts={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        m=o.data;m.calc_loop_triangles();vv=np.array([tuple(o.matrix_world@v.co) for v in m.vertices],dtype=np.float64)
        h=hashlib.sha256(vv.tobytes()+str([tuple(p.vertices) for p in m.polygons]).encode()).hexdigest()
        edge=Counter()
        for p in m.polygons:
            v=list(p.vertices)
            for a,b in zip(v,v[1:]+v[:1]):edge[tuple(sorted((a,b)))]+=1
        result[o.name]={'vertices':len(m.vertices),'faces':len(m.polygons),'triangles':len(m.loop_triangles),'geometry_sha256':h,'finite':bool(np.isfinite(vv).all()),'bounds':[vv.min(axis=0).tolist(),vv.max(axis=0).tolist()],'zero_area_polygons':sum(p.area<1e-9 for p in m.polygons),'edges_not_two_faces':sum(c!=2 for c in edge.values()),'materials':len(m.materials)}
        verts[o.name]=vv
    return result,verts
bpy.ops.wm.open_mainfile(filepath=str(D/'campus-courtyard_material.blend'))
def image_report():
    out={}
    for im in bpy.data.images:
        if im.type!='IMAGE' or im.size[0]==0:continue
        p=np.array(im.pixels[:],dtype=np.float32)
        out[im.name]={'size':list(im.size),'packed':bool(im.packed_file),'pixel_sha256':hashlib.sha256(p.tobytes()).hexdigest()}
    return out
source_images=image_report()
g,vertices=geometry();np.savez_compressed(Q/'original_world_vertices.npz',**vertices)
(Q/'material_geometry.json').write_text(json.dumps(g,indent=2))
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
# Dense ground coverage rays: only ground slab, not a claim of unobstructed global circulation.
floor=bpy.data.objects['SITE-PAVERS'];floor_rays=[]
for x in np.linspace(-34.8,30.8,120):
 for y in np.linspace(-19.8,31.8,96):
    hit,loc,norm,idx=floor.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),distance=2)
    floor_rays.append([float(x),float(y),bool(hit),float(loc.z) if hit else None])
(Q/'ground_dense_rays.json').write_text(json.dumps(floor_rays))
ap=[]
for prefix,origin,axis,bays,pitch in [('BLD-A',(-5.6,28),(1,0),7,3.65),('BLD-B',(20,28),(0,-1),12,3.8)]:
    dx,dy=axis;nx,ny=-dy,dx;wall=bpy.data.objects[prefix+'-SHELL']
    for row in range(4):
      for c in range(bays):
        for du in [-.7,0,.7]:
          for dz in [.2,.9,1.7]:
            u=(c+.5)*pitch+du;z=row*3.18+.52+dz;start=Vector((origin[0]+u*dx-nx,origin[1]+u*dy-ny,z));direction=Vector((nx,ny,0))
            hit,loc,norm,idx=wall.ray_cast(start,direction,distance=8)
            dist=(loc-start).length if hit else None
            ap.append({'building':prefix,'row':row+1,'bay':c+1,'du':du,'z':z,'hit':bool(hit),'distance':dist,'front_shell_blocks_opening':bool(hit and dist<1.40)})
(Q/'window_aperture_rays.json').write_text(json.dumps(ap,indent=2))
walk=[]
for x in np.linspace(-.6,.6,7):
 for y in np.linspace(-18,-8,41):
    hit,loc,norm,idx,obj,mat=scene.ray_cast(deps,Vector((x,y,1.7)),Vector((0,0,-1)),distance=1.48)
    walk.append({'x':float(x),'y':float(y),'hit_above_0_22':bool(hit),'object':obj.name if hit else None})
(Q/'limited_foreground_clearance_rays.json').write_text(json.dumps(walk,indent=2))
# Explicit source landmark diagnostic, measured manually in native image coordinates.
# Neither these image picks nor the cameras are a solved calibration.
anchors={
 'treebed_near_rim':(3.9,-5.34,.39),
 'bench01_ground':(3.6,8.8,0),
 'hoop03_base':(17,-5.1,.07),
 'ballrack_base':(14.3,2.1,0),
 'door_B_bottom':(20,3.3,.40),
 'hoop03_board_centre':(17,-6,7.43),
}
picks={
 'SRC01':{'treebed_near_rim':[1340,788],'bench01_ground':[1165,643]},
 'SRC02':{'treebed_near_rim':[741,710],'bench01_ground':[166,542],'hoop03_base':[1508,590],'ballrack_base':[1140,608],'door_B_bottom':[1405,493]},
 'SRC03':{'hoop03_board_centre':[825,520],'ballrack_base':[160,1060],'door_B_bottom':[350,1005]},
 'SRC04':{'treebed_near_rim':[558,688],'bench01_ground':[250,450],'hoop03_base':[1190,507],'door_B_bottom':[1100,412]}
}
projection=[]
for cid,pick in picks.items():
    cam=bpy.data.objects[cid]
    for name,xy in pick.items():
        p=world_to_camera_view(scene,cam,Vector(anchors[name]));uv=[p.x*1920,(1-p.y)*1080]
        projection.append({'camera':cid,'anchor':name,'model_xyz':anchors[name],'source_xy_approx':xy,'render_xy':uv,'error_px':math.dist(xy,uv),'status':'conditional manual landmark; not accepted calibration'})
(Q/'source_landmark_residuals.json').write_text(json.dumps(projection,indent=2))
baseline={'meshes':len(g),'all_finite':all(v['finite'] for v in g.values()),'zero_area_polygons':sum(v['zero_area_polygons'] for v in g.values()),'closed_solid_edges_not_two_faces':sum(v['edges_not_two_faces'] for k,v in g.items() if k!='COURT-E-PAINT'),'intentional_flat_paint_open_edges':g.get('COURT-E-PAINT',{}).get('edges_not_two_faces',0),'ground_rays':len(floor_rays),'ground_misses':sum(not v[2] for v in floor_rays),'window_rays':len(ap),'window_front_blocked':sum(v['front_shell_blocks_opening'] for v in ap),'clearance_rays':len(walk),'clearance_hits':sum(v['hit_above_0_22'] for v in walk),'scope':'limited checks; intersections at assembled parts are not boolean-unioned; no structural or real-scale certification'}
bpy.ops.wm.open_mainfile(filepath=str(D/'campus-courtyard_white.blend'))
w,_=geometry();baseline['material_white_equal']=g.keys()==w.keys() and all(g[k]['geometry_sha256']==w[k]['geometry_sha256'] for k in g)
(Q/'white_geometry.json').write_text(json.dumps(w,indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(D/'campus-courtyard.glb'))
import_images=image_report()
(Q/'texture_roundtrip.json').write_text(json.dumps({'original':source_images,'glb_reimport':import_images,'pixel_hash_sets_equal':sorted(x['pixel_sha256'] for x in source_images.values())==sorted(x['pixel_sha256'] for x in import_images.values())},indent=2))
ig,iv=geometry();np.savez_compressed(Q/'glb_reimport_world_vertices.npz',**iv)
(Q/'glb_reimport_geometry.json').write_text(json.dumps(ig,indent=2))
baseline['glb_reimport_meshes']=len(ig);baseline['glb_mesh_names_equal']=g.keys()==ig.keys();baseline['glb_triangle_count_equal']=all(k in ig and g[k]['triangles']==ig[k]['triangles'] for k in g)
bpy.ops.wm.save_as_mainfile(filepath=str(Q/'glb_actual_reimport.blend'),compress=True)
(Q/'blender_qa_summary.json').write_text(json.dumps(baseline,indent=2))
print('QA_COMPLETE',json.dumps(baseline),flush=True)
