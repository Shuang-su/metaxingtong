import bpy,json,hashlib,sys
from pathlib import Path
P=Path(__file__).resolve().parent.parent;args=sys.argv[sys.argv.index('--')+1:];variant,view,samples=args;file=P/'export'/('roof-led-surface-v3'+('-white' if variant=='white' else '')+'.blend');bpy.ops.wm.open_mainfile(filepath=str(file));s=bpy.context.scene
record={'input_blend':str(file),'input_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'samples':int(samples),'variant':variant,'view':view}
if variant=='material':
 ob=bpy.data.objects['STAGE_OUTER LED front full circumference inferred'];mat=ob.data.materials[1];strength=mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value;recipe=json.loads((P/'textures-v2/pattern-recipe.json').read_text());assert abs(strength-recipe['candidate_strength_luminance_matched'])<1e-6;record['actual_strength']=strength
 for node in mat.node_tree.nodes:
  if node.type=='TEX_IMAGE':assert hashlib.sha256(bytes(node.image.packed_file.data)).hexdigest()==recipe['files'][Path(node.image.filepath).name]
s.camera=bpy.data.objects['DIAG outer LED surface close' if view=='close' else 'SOURCE11 conditional camera'];s.cycles.samples=int(samples);s.cycles.use_denoising=False;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;s.render.filepath=str(P/'renders'/f'v3-{variant}-{view}-{samples}s.png');bpy.ops.render.render(write_still=True);record['image_sha256']=hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest();(P/'renders'/f'v3-{variant}-{view}-{samples}s-recipe.json').write_text(json.dumps(record,indent=2))
