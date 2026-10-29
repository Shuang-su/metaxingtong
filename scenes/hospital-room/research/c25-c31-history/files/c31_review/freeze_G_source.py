from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
P=Path(__file__).resolve().parent;s=P.parent/'inputs/hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png'
d={'source':str(s.relative_to(P.parent)),'sha256':hashlib.sha256(s.read_bytes()).hexdigest(),'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_seen_at_freeze':False,'classification':'Previously seen fixed-view projection check, not blind test','method':'Native visual context plus mean RGB over x±2 columns; Gaussian sigma1 and vertical-gradient extrema. Lip outer boundary uses entrance/exit gradient of dark lip; inner uses reverse-sign transition. These are appearance edges, not exact mesh vertices.','slot':{'x':1900,'outer_top':818,'outer_bottom':885,'inner_top_transition':823,'inner_bottom_transition':881,'outer_height':67,'outer_center_y':851.5,'inner_transition_height':58,'inner_transition_center_y':852,'boundary_uncertainty_px':3,'flat_face_approx_y':[828,877],'flat_face_boundary_uncertainty_px':4},'left_hole':{'x':1700,'aperture_top':822,'aperture_bottom':880,'height':58,'center_y':851,'boundary_uncertainty_px':3},'limitations':['Appearance-gradient inner transition is not identical to the approximately flat cream interior extent; both definitions are recorded.','Slot complete width and true object center are offscreen.','Vertical source readings vary with x due to perspective; do not infer world center from this one scanline.','Source endboard lower edge near x1900 around y993 is bedding-adjacent/soft; lower margin approx108px ±6, not a mechanical clearance.']}
json.dump(d,open(P/'G_source_frozen.json','w'),indent=2)
im=Image.open(s).convert('RGB');dr=ImageDraw.Draw(im)
for y,c in [(818,'red'),(885,'red'),(823,'yellow'),(881,'yellow')]:dr.line((1880,y,1919,y),fill=c,width=1)
for y in [822,880]:dr.line((1680,y,1720,y),fill='cyan',width=1)
im.save(P/'G_source_annotated_native1x.png')
