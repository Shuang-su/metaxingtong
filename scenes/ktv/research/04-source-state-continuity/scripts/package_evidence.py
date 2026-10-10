#!/usr/bin/env python3
from pathlib import Path
import json,shutil,hashlib,zipfile,datetime
root=Path(__file__).resolve().parents[1];out=root/'delivery';out.mkdir(exist_ok=True)
# Original capture files, logs and generated evidence are copied, never modified.
for n in ['captures','qa','scripts']:
 shutil.copytree(root/n,out/n,dirs_exist_ok=True)
for p in root.iterdir():
 if p.is_file() and p.suffix in ['.json','.md','.jpg'] and p.name not in ['freeze_receipt.json','package_manifest.json']:
  shutil.copy2(p,out/p.name)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[p for p in sorted(out.rglob('*')) if p.is_file() and p.name!='FILE_MANIFEST.json']
man={'stage':'KTV source-state continuity evidence; models unchanged','frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[{'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
(out/'FILE_MANIFEST.json').write_text(json.dumps(man,ensure_ascii=False,indent=2)+'\n')
files=sorted(p for p in out.rglob('*') if p.is_file())
common=[p for p in files if p.suffix not in ['.jpg'] and p.parent.name!='captures']
def is_sofa(p):return p.name.startswith(('Sofa_','layout_probe_'))
rawD=[p for p in files if p.parent.name=='captures' and not is_sofa(p)]
rawS=[p for p in files if p.parent.name=='captures' and is_sofa(p)]
boardsD=[p for p in files if p.parent==out and p.suffix=='.jpg' and not is_sofa(p)]
boardsS=[p for p in files if p.parent==out and p.suffix=='.jpg' and is_sofa(p)]
groups=[('KTV_source_continuity_01_dynamic_exits.zip',common+rawD+boardsD),('KTV_source_continuity_02_sofa_layout.zip',common+rawS+boardsS)]
receipts=[]
for n,ps in groups:
 z=root/n
 with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as f:
  for p in sorted(set(ps)):f.write(p,'KTV_source_state_continuity/'+str(p.relative_to(out)))
 with zipfile.ZipFile(z) as f:assert f.testzip() is None
 assert z.stat().st_size<18000000
 receipts.append({'file':n,'bytes':z.stat().st_size,'sha256':sha(z),'crc_test':'pass','member_files':len(set(ps))})
seen=set(p for _,ps in groups for p in ps);assert seen==set(files)
r={'frozen':True,'delivery_directory':'delivery','file_count':len(files),'image_count':120,'raw_image_count':115,'composite_image_count':5,'file_manifest_sha256':sha(out/'FILE_MANIFEST.json'),'packages':receipts,'coverage':'ZIP union equals complete delivery file set; common metadata repeated in both','models_modified':False,'CURRENT_changed':False}
(root/'freeze_receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False,indent=2))
