"""Post-hoc evidentiary binding. Does not alter or fabricate old execution logs."""
import pathlib,json,hashlib,subprocess
P=pathlib.Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def at(commit,path):return subprocess.check_output(['git','show',f'{commit}:{path}'],cwd=P)
freeze='2317e3dec04a7204e17a0a20eb381a5fe992af7f';source_outputs_commit='119d928c37fb7ddfdb4aefce73c5882fcb0194e1'
files=[]
for path in ['models/R04_material.blend','models/R04_white.blend','scripts/render_r04.py']:
 current=(P/path).read_bytes();frozen=at(freeze,path);files.append({'path':path,'freeze_commit':freeze,'frozen_sha256':sha(frozen),'current_sha256':sha(current),'current_bytes_equal_pre_render_freeze':current==frozen})
records=[]
for r in json.loads((P/'renders/R04_source/render-log.json').read_text()):
 path=pathlib.Path(r['file']).relative_to(P);b=(P/path).read_bytes();records.append({'path':str(path),'sha256_measured_now_posthoc':sha(b),'matches_first_tracked_output_bytes':b==at(source_outputs_commit,str(path)),'original_render_record_unchanged':r})
out={'measurement_timing':'POST-HOC after four R04 source images finished. The original source render log did NOT record an input-model hash during execution. This file does not retroactively add one.','sequence_evidence':['R04 models and render script were frozen in 2317e3d before the source render invocation.','Original source images and unmodified execution log were committed with R04D freeze 119d928.','Current bytes are compared against both earlier Git freezes; no assertion of a cryptographically attested running process is made.'],'original_log_sha256':sha((P/'renders/R04_source/render-log.json').read_bytes()),'input_and_script_bindings':files,'outputs':records,'R04D_reuse_evidence':'qa/independent-R04D/review.zh.md and accompanying exact diff prove geometry/UV/used materials/three source cameras/lights/World and rendering state unchanged. D does not relabel these as re-rendered.','D_formal_log_timing':'D per-image input_sha256 is read after each image render completes, not before loading. Compare each with pre-run 119d928 immutable model manifest and final frozen bytes.','source_acceptance':'FAILED for both report02 and report05'}
(P/'qa/R04-source-posthoc-binding.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('POSTHOC_BINDING_RECORDED',all(x['current_bytes_equal_pre_render_freeze'] for x in files),len(records))
