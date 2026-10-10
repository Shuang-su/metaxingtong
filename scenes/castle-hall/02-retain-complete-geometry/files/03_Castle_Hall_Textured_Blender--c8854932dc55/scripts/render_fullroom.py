import bpy,sys,os,json,bmesh,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'));S=bpy.context.scene
S.render.threads=int(os.environ.get('QA_THREADS','3'));S.cycles.samples=int(os.environ.get('QA_SAMPLES','32'));S.cycles.use_denoising=False;S.render.resolution_percentage=int(os.environ.get('QA_RES','100'));prefix=os.environ.get('QA_PREFIX','');model_sha=hashlib.sha256((R/'models/Xingtong_Castle_Hall_FullRoom.blend').read_bytes()).hexdigest()
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['ALL']
views={'Match_A':'MATCH_A_45m15_empty_aisle','Match_B':'MATCH_B_75m07_oblique','Match_C':'MATCH_C_73m44_arch_crosscheck','Entry':'QA_ENTRY_COMPLETE','Reverse':'QA_REVERSE_COMPLETE','Side':'QA_SIDE_COMPLETE','Ceiling':'QA_CEILING_COMPLETE','Exterior':'QA_EXTERIOR_COMPLETE','Cutaway':'QA_CUTAWAY_COMPLETE'}
for label,cam in views.items():
 if 'ALL' not in args and label not in args:continue
 if label=='Cutaway':
  # A disposable physical section, never a source-alignment change or a hidden part of the final asset.
  for o in list(S.objects):
   if o.type!='MESH':continue
   bm=bmesh.new();bm.from_mesh(o.data)
   for no,co in [((0,0,1),(0,0,8.3)),((0,-1,0),(0,-11.8,0)),((1,0,0),(6.7,0,0))]:
    if not bm.verts:break
    r=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=Vector(co),plane_no=Vector(no),clear_outer=True,clear_inner=False)
    edges=[e for e in r['geom_cut'] if isinstance(e,bmesh.types.BMEdge) and e.is_boundary]
    if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
   if bm.faces:bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
   bm.to_mesh(o.data);bm.free()
 if label in ('Exterior','Cutaway'):
  S.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.61,.72,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.7
  d=bpy.data.lights.new('Inspection exterior sun','SUN');d.energy=2.4;o=bpy.data.objects.new('Inspection exterior sun',d);S.collection.objects.link(o);o.rotation_euler=(.4,-.3,-.4)
 S.camera=bpy.data.objects[cam];S.render.filepath=str(R/'renders'/f'{prefix}FullRoom_{label}.png');bpy.ops.render.render(write_still=True);json.dump({'model_sha256':model_sha,'camera':cam,'samples':S.cycles.samples,'resolution_percentage':S.render.resolution_percentage,'mesh_changes':'Physical diagnostic cut only' if label=='Cutaway' else 'None'},open(R/'qa'/f'render_provenance_{prefix}{label}.json','w'),indent=2);print('RENDER_DONE',label,flush=True)
