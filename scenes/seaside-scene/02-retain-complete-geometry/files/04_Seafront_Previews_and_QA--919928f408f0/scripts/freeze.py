import os,json,glob,zipfile,hashlib
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));D=R+'/frozen';os.makedirs(D,exist_ok=True)
readme=R+'/README_海滨开放场景_中文.txt'
sets=[('01_Seafront_White_Models.zip','libfile_48907d0ff4148191bec5276af793caa4',[R+'/models/Seafront_White.blend',R+'/models/Seafront_White.glb']),('02_Seafront_Textured_Blender.zip','libfile_59abbc70963481919a297d3a43dbdb73',[R+'/models/Seafront_Textured.blend']+glob.glob(R+'/source/textures/*')),('03_Seafront_Textured_GLB.zip','libfile_51408f34beb4819181506bddb63419f2',[R+'/models/Seafront_Textured.glb']),('04_Seafront_Previews_and_QA.zip','libfile_a6065e87011c81919243340c4d29dc84',glob.glob(R+'/previews/*.jpg')+glob.glob(R+'/qa/*.jpg')+glob.glob(R+'/qa/*.json')+glob.glob(R+'/qa/*.txt')+glob.glob(R+'/source_evidence/references/*')+glob.glob(R+'/scripts/*.py')+glob.glob(R+'/source_hd/*')+[R+'/independent_qa/'+n for n in ['独立最终核验报告_中文.txt','independent_audit.json','chains.json','contact_probe.json','support_contact_validation.json','audit.py','chains.py','contact_probe.py','supports.py','final_contact.jpg']]+[R+'/qa/section_diagnostic_only.blend'])]
manifest=[]
for name,ident,files in sets:
 path=D+'/'+name
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  z.write(readme,os.path.basename(readme))
  for f in files:
   arc=os.path.relpath(f,R).replace('source/textures/','textures/').replace('source_evidence/references/','references/')
   z.write(f,arc)
 size=os.path.getsize(path);assert size<18000000,(name,size)
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
 manifest.append({'filename':name,'path':path,'library_file_id':ident,'expected_current_version':0,'size_bytes':size,'sha256':hashlib.sha256(open(path,'rb').read()).hexdigest()})
json.dump({'packages':manifest,'models':[{ 'path':p,'size_bytes':os.path.getsize(p),'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest()} for p in glob.glob(R+'/models/*') if not p.endswith('.blend1')]},open(D+'/frozen_manifest.json','w'),indent=2)
print(json.dumps(manifest,indent=2))
