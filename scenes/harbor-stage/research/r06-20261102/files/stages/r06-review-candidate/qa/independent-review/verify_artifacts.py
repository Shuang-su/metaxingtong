import pathlib,json,hashlib,struct,io,subprocess,collections
import numpy as np
from PIL import Image
R=pathlib.Path('/workspace/scratch/fa58bfcf0425/metaxingtong-harbor-candidate-20261102')
S=R/'stages/r06-review-candidate'
O=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def git(*a):return subprocess.check_output(['git','-C',str(R),*a])
checks={'head_at_check':git('rev-parse','HEAD').decode().strip(),'scope':'Independent pixel, file-byte, GLB-container and ordinary Git inspection; not a repeat rendering or source identity acquisition.'}
cs=read(S/'source-cameras.json');rm=read(S/'render-manifest.json');om=read(S/'overlay-manifest.json')
checks['sources']=[]
for c in cs:
 p=R/c['file'];im=Image.open(p);im.load();checks['sources'].append({'id':c['id'],'dimensions':list(im.size),'dimensions_match':list(im.size)==c['size'],'sha256':sha(p),'sha_match':sha(p)==c['source_sha256'],'bytes_match':p.stat().st_size==c['source_bytes'],'split':c['split']})
checks['renders']=[]
for r in rm:
 p=S/r['output'];im=Image.open(p);im.load();checks['renders'].append({'path':r['output'],'dimensions':list(im.size),'dimensions_match':list(im.size)==r['dimensions'],'sha256':sha(p),'sha_match':sha(p)==r['sha256'],'bytes_match':p.stat().st_size==r['bytes'],'input_sha_match':sha(R/r['input'])==r['input_sha256']})
checks['overlays']=[]
for r in om:
 a=np.array(Image.open(R/r['source']).convert('RGB'),dtype=np.uint16);b=np.array(Image.open(R/r['render']).convert('RGB'),dtype=np.uint16);c=np.array(Image.open(R/r['overlay']).convert('RGB'),dtype=np.int16);d=c-((a+b)//2).astype(np.int16)
 checks['overlays'].append({'id':r['id'],'state':r['state'],'shape':list(c.shape),'full_pixel_channel_count':int(c.size),'mismatch_channels':int(np.count_nonzero(d)),'max_abs_channel_error':int(np.max(np.abs(d))),'all_three_file_hashes_match':all(sha(R/r[k])==r[k+'_sha256'] for k in ['source','render','overlay']),'overlay_bytes_match':(R/r['overlay']).stat().st_size==r['bytes']})
checks['camera_pairs']=[]
for c in cs:
 rows=[next(r for r in rm if r['output']==f"source-renders/{c['id']}/{state}.png") for state in ['white','material']]
 checks['camera_pairs'].append({'id':c['id'],'all_camera_fields_exact':all(rows[0][k]==rows[1][k] for k in ['camera','camera_matrix_world','lens','shift','dimensions']),'camera_id_matches_binding':all(r['camera']==c['camera'] for r in rows)})
checks['glb']=[]
for state in ['white','material']:
 p=S/f'harbor-r06-{state}.glb';raw=p.read_bytes();magic,version,total=struct.unpack_from('<4sII',raw);pos=12;chunks=[];binary=None;doc=None
 while pos<len(raw):
  n,t=struct.unpack_from('<I4s',raw,pos);payload=raw[pos+8:pos+8+n];chunks.append({'type':t.decode('ascii','replace'),'bytes':n});pos+=n+8
  if t==b'JSON':doc=json.loads(payload)
  elif t==b'BIN\0':binary=payload
 images=[]
 for im in doc.get('images',[]):
  assert 'bufferView' in im and 'uri' not in im
  bv=doc['bufferViews'][im['bufferView']];offset=bv.get('byteOffset',0);data=binary[offset:offset+bv['byteLength']];pic=Image.open(io.BytesIO(data));pic.load();images.append({'name':im.get('name'),'bytes':len(data),'dimensions':list(pic.size),'sha256':hashlib.sha256(data).hexdigest(),'embedded_buffer':bv['buffer']})
 checks['glb'].append({'state':state,'sha256':sha(p),'bytes':len(raw),'header_valid':magic==b'glTF' and version==2 and total==len(raw) and pos==len(raw),'chunks':chunks,'mesh_count':len(doc.get('meshes',[])),'mesh_node_count':sum('mesh' in n for n in doc.get('nodes',[])),'images':images,'external_uris':[x['uri'] for k in ['buffers','images'] for x in doc.get(k,[]) if 'uri' in x and not x['uri'].startswith('data:')],'buffer_lengths':[b['byteLength'] for b in doc.get('buffers',[])],'extensionsUsed':doc.get('extensionsUsed',[])})
# Ordinary Git: all reachable object sizes; scan all small blobs for actual LFS pointer header.
objs=git('rev-list','--objects','--all').decode().splitlines();paths={l.split(' ',1)[0]:l.split(' ',1)[1] if ' ' in l else '' for l in objs}
meta=subprocess.check_output(['git','-C',str(R),'cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize)'],input=('\n'.join(paths)+'\n').encode()).decode().splitlines();blobs=[];pointers=[]
for l in meta:
 oid,kind,size=l.split();size=int(size)
 if kind!='blob':continue
 blobs.append({'oid':oid,'bytes':size,'path':paths[oid]})
 if size<1024 and git('cat-file','blob',oid).startswith(b'version https://git-lfs.github.com/spec/v1'):pointers.append({'oid':oid,'path':paths[oid]})
checks['git']={'reachable_blob_count':len(blobs),'largest_10_blobs':sorted(blobs,key=lambda b:b['bytes'],reverse=True)[:10],'blobs_at_or_above_100MiB':[b for b in blobs if b['bytes']>=100*1024*1024],'lfs_pointer_blobs':pointers,'working_tree_status':git('status','--short').decode(),'fsck_full':subprocess.run(['git','-C',str(R),'fsck','--full'],capture_output=True,text=True).__dict__ if False else None}
f=subprocess.run(['git','-C',str(R),'fsck','--full'],capture_output=True,text=True);checks['git']['fsck_full']={'returncode':f.returncode,'stdout':f.stdout,'stderr':f.stderr}
checks['summary']={'source_count':len(cs),'render_count':len(rm),'overlay_count':len(om),'overlay_all_pixels_exact_floor_half':all(x['mismatch_channels']==0 for x in checks['overlays']),'source_render_and_file_checks_pass':all(all(v for k,v in x.items() if k.endswith('_match')) for x in checks['sources']+checks['renders']),'camera_pairs_exact':all(x['all_camera_fields_exact'] for x in checks['camera_pairs'])}
(O/'independent-artifacts.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print(json.dumps(checks['summary'],indent=2));print(json.dumps(checks['glb'],indent=2));print('git largest',checks['git']['largest_10_blobs'][0]);print('lfs',len(pointers),'fsck',f.returncode)
