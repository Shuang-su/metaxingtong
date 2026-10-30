"""Direct 50% blends/crops only; native images are never changed or warped."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,csv,hashlib
from scipy.spatial import cKDTree
R=Path(__file__).resolve().parents[1];D=R/'stage-02-material-candidate';Q=R/'qa'
original=np.load(Q/'original_world_vertices.npz');reimport=np.load(Q/'glb_reimport_world_vertices.npz');vertices=[]
for k in original.files:
    a,b=original[k],reimport[k];dist=max(cKDTree(b).query(a)[0].max(),cKDTree(a).query(b)[0].max());vertices.append({'id':k,'original_vertices':len(a),'imported_vertices':len(b),'symmetric_max_distance_model_units':float(dist),'within_1e-5':bool(dist<1e-5)})
(Q/'glb_vertex_correspondence.json').write_text(json.dumps(vertices,indent=2))
meta=json.loads((R/'source/acquisition.json').read_text());byid={x['id']:x for x in meta['frames']};comp=D/'comparison';comp.mkdir(exist_ok=True)
comparisons=[]
for cid,f in byid.items():
    src=Image.open(R/'source'/f['file']).convert('RGB');ren=Image.open(D/'renders'/(cid+'.png')).convert('RGB')
    assert src.size==ren.size==(1920,1080)
    blend=Image.blend(src,ren,.5);path=comp/(cid+'_overlay50.png');blend.save(path)
    strip=Image.new('RGB',(1920,390),(25,31,38));dr=ImageDraw.Draw(strip)
    for i,(im,title) in enumerate([(src,'SOURCE native 1920x1080'),(ren,'RENDER conditional camera'),(blend,'DIRECT 50% blend, no warp')]):
        strip.paste(im.resize((640,360)),(i*640,30));dr.text((i*640+12,8),cid+' | '+title,fill='white')
    strip.save(comp/(cid+'_source_render_overlay_strip.png'))
    comparisons.append({'source_id':cid,'source_file':f['file'],'source_sha256':f['sha256'],'render_file':'renders/'+cid+'.png','overlay_file':'comparison/'+path.name,'dimensions':[1920,1080],'operation':'PIL.Image.blend(source RGB, render RGB, alpha=0.5); floor rounding per Pillow; no transforms','strip_display_scale':'640/1920 = 1/3, clearly labelled; original comparison files unscaled','status':'conditional camera diagnostic; not acceptance'})
(comp/'comparison_manifest.json').write_text(json.dumps(comparisons,indent=2))
regions=[('CROP01-facade','SRC01',(720,50,1280,575)),('CROP02-treebed','SRC01',(1110,650,1575,820)),('CROP03-lamps','SRC01',(920,0,1220,640)),('CROP04-goals','SRC01',(390,470,670,700)),('CROP05-door','SRC02',(1250,260,1550,565)),('CROP06-bench','SRC02',(90,440,250,560)),('CROP07-rack','SRC02',(1040,440,1245,620)),('CROP08-hoop','SRC03',(560,400,960,1060)),('CROP09-stair','SRC03',(1430,0,1920,1080)),('CROP10-track','SRC02',(0,520,520,865))]
cropdir=comp/'crops';cropdir.mkdir(exist_ok=True)
for name,cid,box in regions:
    src=Image.open(R/'source'/byid[cid]['file']).convert('RGB');ren=Image.open(D/'renders'/(cid+'.png')).convert('RGB');overlay=Image.blend(src,ren,.5)
    for role,im in [('source',src),('render',ren),('overlay50',overlay)]:im.crop(box).save(cropdir/(name+'_'+role+'.png'))
(comp/'crop_regions.json').write_text(json.dumps([{'id':n,'source_id':c,'original_xyxy':b,'display_scale':1,'independent_source_view':False,'conditional_camera':True} for n,c,b in regions],indent=2))
checks=sorted((D/'renders').glob('CHECK*.png'));sheet=Image.new('RGB',(1920,620),(25,31,38));dr=ImageDraw.Draw(sheet)
for i,p in enumerate(checks):
    im=Image.open(p).convert('RGB');x=(i%4)*480;y=(i//4)*310;dr.text((x+10,y+10),p.stem+' | internal inspection',fill='white');im.thumbnail((480,270));sheet.paste(im,(x,y+35))
sheet.save(D/'inspection_contact_sheet.png')
geom=json.loads((D/'object_manifest.json').read_text());p=Q/'object_evidence.csv';rows=list(csv.DictReader(p.open()));mapping={r['stable_id']:r for r in rows}
for o in geom:
    if o['id'] in mapping:mapping[o['id']]['position_model_units']=json.dumps([round(sum(v[i] for v in o['world_bounds'])/8,4) for i in range(3)])
with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
summary=json.loads((Q/'blender_qa_summary.json').read_text());summary['glb_bidirectional_vertices_match']=all(v['within_1e-5'] for v in vertices);summary['glb_vertex_max_distance_model_units']=max(v['symmetric_max_distance_model_units'] for v in vertices);summary['source_views_compared']=len(comparisons);summary['internal_check_views']=len(checks);summary['source_acceptance']='NOT PASSED';summary['later_other_replay']='missing';summary['user_acceptance']='not received';(Q/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
