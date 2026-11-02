import pathlib,json,hashlib
import numpy as np
from PIL import Image
R=pathlib.Path('/workspace/scratch/fa58bfcf0425/metaxingtong-harbor-candidate-20261102');S=R/'stages/r06-review-candidate';O=pathlib.Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();array=lambda p:np.array(Image.open(p).convert('RGB'))
n=read(O/'independent-native.json');renders=read(S/'render-manifest.json');camchecks=[]
for r in renders:
 state='white' if r['input'].endswith('-white.blend') else 'material';c=n['states'][state]['cameras'][r['camera']]
 camchecks.append({'output':r['output'],'native_recorded_matrix_lens_shifts_exact':c['matrix_world']==r['camera_matrix_world'] and c['lens']==r['lens'] and [c['shift_x'],c['shift_y']]==r['shift']})
crops=[]
for c in read(S/'object-crops-manifest.json'):
 x0,y0,x1,y1=c['crop_xyxy'];src=array(R/c['source']);cfg=next(x for x in read(S/'source-cameras.json') if x['file']==c['source']);v={'id':c['id'],'source_crop_all_pixels_exact':np.array_equal(array(R/c['source_crop']),src[y0:y1,x0:x1]),'source_crop_sha_match':sha(R/c['source_crop'])==c['source_crop_sha256']}
 for state in ['white','material']:
  render=array(S/f"source-renders/{cfg['id']}/{state}.png");crop=array(R/c[state]['render_crop']);overlay=array(R/c[state]['overlay']);expected=((src[y0:y1,x0:x1].astype(np.uint16)+render[y0:y1,x0:x1].astype(np.uint16))//2).astype(np.uint8)
  v[state]={'render_crop_all_pixels_exact':np.array_equal(crop,render[y0:y1,x0:x1]),'overlay_all_pixels_exact_floorhalf':np.array_equal(overlay,expected),'all_hashes_exact':sha(R/c[state]['render_crop'])==c[state]['render_crop_sha256'] and sha(R/c[state]['overlay'])==c[state]['overlay_sha256']}
 crops.append(v)
p=S/'qa/glb-render';a=array(p/'native-same-rig.png');b=array(p/'actual-glb-import-same-rig.png');d=np.abs(a.astype(np.int16)-b.astype(np.int16));rep=read(p/'report.json');diff={'dimensions':list(a.shape[1::-1]),'mean_absolute_channel_0_255':float(d.mean()),'p99_absolute_channel_0_255':float(np.percentile(d,99)),'max_absolute_channel_0_255':int(d.max()),'fraction_pixels_any_channel_above_8':float((d.max(axis=2)>8).mean()),'report_output_hashes_match':all(sha(p/x['file'])==x['sha256'] for x in rep['outputs'])}
borrowed={}
for fn in ['all-object-topology.json','dense-floor-rays-and-feet.json','core-assembly-contacts.json','portal-rays.json']:
 t=read(S/'qa'/fn);z={'sha256':sha(S/'qa'/fn),'note':'Builder-provided log contents examined, not independently recomputed.'}
 if fn.startswith('all-object'):z.update({'rows':len(t),'boundary_edge_sum':sum(x['boundary_edges'] for x in t),'nonmanifold_edge_sum':sum(x['nonmanifold_edges'] for x in t),'zero_area_face_sum':sum(x['zero_area_faces'] for x in t),'nonpositive_volumes':sum(x['signed_world_volume']<=0 for x in t)})
 elif fn.startswith('dense'):z.update({'floor_ray_count':t['floor_ray_count'],'misses':len(t['misses']),'max_abs_floor_height_error':t['max_abs_floor_height_error']})
 elif fn.startswith('core'):z.update({'core_objects':t['core_objects'],'candidate_pairs':len(t['candidate_pairs']),'method':t['method'],'not_proof_of_zero_intersections':True})
 else:z.update({'ray_count':t['ray_count'],'rows':len(t['rays'])})
 borrowed[fn]=z
files=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size} for p in R.rglob('*') if p.is_file() and '.git' not in p.parts]
report={'actual_native_vs_manifest_cameras':camchecks,'crop_groups':crops,'glb_native_same_rig_pixel_diff_independent':diff,'builder_logs_reviewed_not_recomputed':borrowed,'largest_worktree_files':sorted(files,key=lambda x:x['bytes'],reverse=True)[:10],'worktree_files_at_or_above_100MiB':[x for x in files if x['bytes']>=100*1024*1024]}
(O/'independent-supplement.json').write_text(json.dumps(report,indent=2));print('Native camera records exact',len(camchecks),all(x['native_recorded_matrix_lens_shifts_exact'] for x in camchecks));print('8 crop groups',crops);print('GLB diff',diff);print('worktree largest',report['largest_worktree_files'][0]);print('borrowed logs',borrowed)
