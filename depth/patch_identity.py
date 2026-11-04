from pathlib import Path
import json,hashlib,shutil
p=Path(__file__).resolve().parent;d=Path('/workspace/shared/depth-corridor-report-20261104');root=p.parent;identity=json.loads((root/'corridor-identity-20261104/identity.json').read_text());source=json.loads((root/'stardream-corridor-20261105/sources/manifest.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
old=json.loads((d/'manifest.json').read_text());before={f['path']:f['sha256'] for f in old if f['path'].endswith(('.png','.npy'))};(p/'provenance/pre-identity-manifest.json').write_text(json.dumps(old,indent=2))
for n in ['008','023','026']:
 entry=next(x for x in source['files'] if x['article_number_1based']==int(n));assert sha(d/f'sources/{n}.png')==entry['sha256']
 update={'official_replay':identity['official_replay']['url'],'official_clip':identity['official_clip']['url'],'official_identity_evidence':'sources/official-identity.json, public page metadata only; no playback/decode','image_url':entry['url'],'verified_article_source':entry,'same_state_validation':'NOT VERIFIED; fixture count/layout and lighting may differ','subsequent_date_reuse':'NOT VERIFIED; no independent pixel evidence','video_time_seconds':None,'decode_size':None,'login_quality_verified':False}
 for base in [p,d]:
  rp=base/f'report-image-{n}/report.json';r=json.loads(rp.read_text());r['source'].update(update);rp.write_text(json.dumps(r,ensure_ascii=False,indent=2))
  mp=base/f'provenance/{n}-metadata.json';m=json.loads(mp.read_text());m.update(update);mp.write_text(json.dumps(m,ensure_ascii=False,indent=2))
shutil.copy2(root/'corridor-identity-20261104/identity.json',d/'sources/official-identity.json');shutil.copy2(root/'stardream-corridor-20261105/sources/manifest.json',d/'sources/production-source-manifest.json');shutil.copy2(p/'provenance/pre-identity-manifest.json',d/'provenance/pre-identity-manifest.json');shutil.copy2(p/'patch_identity.py',d/'patch_identity.py')
f=d/'analysis.zh.md';text=f.read_text().replace('本分析未独立核对官方BV、时间连续性或新场景排重，不能作为这些条件完成的证明。','官方身份现由来源负责人公页核验补入：完整回放BV11E4m1R716、单曲BV1NT421r72q均关联2024-08-03演出。仅身份关联，不代表实际播放、时序连续或原生像素验收。有限排重由独立任务负责，本深度结果不证明排重。');text+='\n## 来源补件（仅metadata，未重跑深度）\n精确三图URL/SHA/尺寸已与生产来源表逐项一致。official-identity及production-source-manifest保留在sources。官方clip页面OG的3840×2160仅元数据，不是实际解码或原生4K证据。008/023/026时刻、最高画质、同一几何状态仍未知；不同日期复用无像素证据。此前所有PNG/NPY重新回读与补件前哈希完全一致。\n';f.write_text(text)
for path,h in before.items():assert sha(d/path)==h
files=[{'path':str(f.relative_to(d)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(d.rglob('*')) if f.is_file() and f.name!='manifest.json'];(d/'manifest.json').write_text(json.dumps(files,indent=2))
for f in files:assert sha(d/f['path'])==f['sha256']
print('FROZEN',len(files),sum(x['bytes'] for x in files),'bytes; unchanged numerical/image artifacts',len(before),'manifest SHA',sha(d/'manifest.json'))
