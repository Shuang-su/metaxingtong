#!/usr/bin/env python3
"""Record existing colors without assigning an official palette or recoloring."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json, shutil
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
PARAMS={
 '02-butterfly':{'frame':27,'version':'dynamic-candidate','head_crop':[40,120,370,410],
   'points':{'hair_base':(131,231),'bang_streak':(240,243),'iris':(203,329),'white_flower':(40,231),'dress_cream':(172,519),'bow_accent':(195,479)}},
 '03-awake':{'frame':17,'version':'dynamic-candidate-r1','head_crop':[390,140,760,450],
   'points':{'hair_base':(601,245),'bang_streak':(529,235),'iris':(575,375),'white_flower':(692,256),'dress_cream':(561,596),'bow_accent':(576,479)}}}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sample_path=Path('/workspace/emote-local-patch-review/color-reference-inputs/明前奶绿六式聊天表情包.png')
    refs=OUT/'references';refs.mkdir(exist_ok=True)
    imported=refs/'20261105-model-generated-style-sample.png'
    if not imported.exists():shutil.copy2(sample_path,imported)
    sample=Image.open(imported).convert('RGB')
    records=[];heads=[]
    for name,conf in PARAMS.items():
        b=ROOT/'emotes/sunburst/agent-emotes'/name/'versions/20261113-local-patch-review'
        original=Image.open(b/'original-decoded'/f"{conf['frame']:02d}.png").convert('RGB')
        gif_path=b/'v6-contour-and-motion'/conf['version']/'CANDIDATE-master-768.gif'
        with Image.open(gif_path) as gif:
            gif.seek(conf['frame']-1);candidate=gif.convert('RGB')
        heads.append((name,original.crop(conf['head_crop']),candidate.crop(conf['head_crop'])))
        sheet=Image.new('RGB',(1536,850),'white');sheet.paste(original,(0,25));sheet.paste(candidate,(768,25));d=ImageDraw.Draw(sheet)
        d.text((5,4),'ORIGINAL: generated artwork, not independent character reference',font=FONT,fill='black')
        d.text((773,4),'V6 CANDIDATE: same sampling locations',font=FONT,fill='black')
        for i,(part,(x,y)) in enumerate(conf['points'].items(),1):
            boxes=[]
            for j,im in enumerate([original,candidate]):
                patch=np.array(im)[y-2:y+3,x-2:x+3];rgb=np.median(patch.reshape(-1,3),axis=0).astype(int).tolist();boxes.append(rgb)
                d.rectangle((j*768+x-4,25+y-4,j*768+x+4,25+y+4),outline='red',width=2);d.text((j*768+x+6,25+y-12),str(i),font=FONT,fill='red')
            records.append({'emote':name,'frame':conf['frame'],'region':part,'sample_box':[x-2,y-2,x+3,y+3],
                'median_original_rgb':boxes[0],'median_v6_rgb':boxes[1],
                'sample_pixels_unchanged':bool(np.array_equal(np.array(original)[y-2:y+3,x-2:x+3],np.array(candidate)[y-2:y+3,x-2:x+3])),
                'caveat':'5x5 local sample; neither semantic segmentation nor official palette'})
            tx=(i-1)*255;d.rectangle((tx,800,tx+30,830),fill=tuple(boxes[0]));d.text((tx+35,801),f'{i} {part}',font=FONT,fill='black');d.text((tx+35,820),str(boxes[0]),font=FONT,fill='black')
        sheet.save(OUT/(name+'-region-sampling.png'))
    comparison=Image.new('RGB',(1200,750),'#eee');d=ImageDraw.Draw(comparison)
    d.text((6,5),'EARLIER GENERATED STYLE SAMPLE',font=FONT,fill='black')
    d.text((6,24),'Not an independent real character reference',font=FONT,fill='black')
    comparison.paste(sample.crop((80,45,490,375)).resize((410,330),Image.Resampling.LANCZOS),(5,50))
    for i,(name,original,candidate) in enumerate(heads):
        x=430+i*385;d.text((x,5),name+' original',font=FONT,fill='black');comparison.paste(original.resize((370,330),Image.Resampling.LANCZOS),(x,50))
        d.text((x,395),name+' v6 candidate',font=FONT,fill='black');comparison.paste(candidate.resize((370,330),Image.Resampling.LANCZOS),(x,420))
    d.text((5,405),'Color observations only. No recoloring applied.',font=FONT,fill='black')
    d.text((5,430),'Green bang, iris and leaf accents in the',font=FONT,fill='black')
    d.text((5,455),'generated sample do not establish official colors.',font=FONT,fill='black')
    comparison.save(OUT/'generated-style-vs-original-and-v6.png')
    (OUT/'region-sampling.json').write_text(json.dumps({'sampling_only':True,'no_recoloring_applied':True,'records':records},indent=2)+'\n')
    (OUT/'generated-sample-provenance.json').write_text(json.dumps({
      'library_file_id':'libfile_3101f67e5e5c8191856c049deb4321db','file_id':'file_00000000f44c82119f039c049149a84e',
      'original_name':'明前奶绿六式聊天表情包.png','source_date':'2026-11-05','model_generated':True,
      'classification_source':'Parent delegation explicitly reports the Library model_generated flag',
      'local_file':str(imported.relative_to(ROOT)),'sha256':sha(imported),'bytes':imported.stat().st_size,
      'independent_real_character_reference':False,'allowed_use':'Earlier project style/color comparison only'},ensure_ascii=False,indent=2)+'\n')
    print('Saved sampling and generated-style comparison; no colors changed.')

if __name__=='__main__':main()
