"""Local contact-risk samples against exact vertices of the unchanged R04/R06 water recipe.
No lake mesh or forest is rebuilt; no source/physical contact truth is asserted.
"""
import bpy,pathlib,sys,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from leaf_local_warp import Parameters,forward
R=pathlib.Path(__file__).resolve().parents[1]
model=R/'models/leaf-only-r06-nonexact-diagnostic-replay.blend'
bpy.ops.wm.open_mainfile(filepath=str(model));o=bpy.data.objects['LEAF_001_ThinConcaveShell']
baseline=[v.co.copy() for v in o.data.vertices];inv=o.matrix_world.inverted();rows=[]
for name,p in [('baseline',Parameters()),('belly_up_008',Parameters(belly_dz=.08)),('belly_down_008',Parameters(belly_dz=-.08)),
    ('shoulder_wider_008',Parameters(shoulder_fraction=.08)),('belly_down_002_limited_probe',Parameters(belly_dz=-.02))]:
    for v,co in zip(o.data.vertices,baseline):v.co=inv@Vector(forward(o.matrix_world@co,p))
    o.data.update();vs=[o.matrix_world@v.co for v in o.data.vertices]
    tree=BVHTree.FromPolygons(vs,[list(f.vertices) for f in o.data.polygons]);samples=[]
    for i in [64,65,66]:
        for j in [64,65,66]:
            x=-38+76*i/130;y=-38+76*j/130
            water=.018*math.sin(x*2.7+y*1.1)+.009*math.sin(y*4.8-x*1.6)
            # Match Mesh.from_pydata's float32 storage for these actual grid vertices.
            stored=Vector((x,y,water));x,y,water=stored.x,stored.y,stored.z
            hit,normal,index,d=tree.ray_cast(Vector((x,y,8)),Vector((0,0,-1)),20);assert hit is not None
            gap=hit.z-water
            samples.append(dict(water_grid_indices=[i,j],x=x,y=y,water_vertex_z=water,leaf_upper_hit_z=hit.z,
                leaf_upper_surface_minus_water_z=gap,water_above_upper_leaf=gap<0))
    rows.append(dict(trial=name,parameters=p.__dict__,sample_count=len(samples),water_above_leaf_count=sum(t['water_above_upper_leaf'] for t in samples),samples=samples))
report=dict(scope='Nine actual grid-coordinate samples from the fixed R04/R06 modeled water recipe against the nonexact leaf subset replay. Not source or physics truth; not a full triangle-contact sweep.',
    input_subset_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),water_recipe_source='upstream/scripts/build_lakeleaf_r04.py',water_grid_N=130,
    water_vertex_storage='Formula computed in Python double then cast to float32 exactly as original Mesh.from_pydata input storage; no claim about interpolated positions between these vertices.',
    production_model_loaded=False,model_files_modified=False,rendered_images=0,rows=rows)
(R/'qa/fixed-water-grid-contact-probes.json').write_text(json.dumps(report,indent=2)+'\n')
for r in rows:
    mid=next(t for t in r['samples'] if t['water_grid_indices']==[65,65])
    print(r['trial'],'water-above-leaf',r['water_above_leaf_count'],'of 9; center gap',mid['leaf_upper_surface_minus_water_z'])
