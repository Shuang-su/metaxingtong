from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/metaxingtong-matplotlib')
import json, math, hashlib, numpy as np
from PIL import Image,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
P=Path(__file__).resolve().parent
r=json.load(open(P/'sun_path_audit.json'));a=json.load(open(P/'structural_audit.json'))
points=[v['hit_world'] for v in r['probes'] if v['role']=='shadow_band_candidate'];z=4.769845962524414
ratios=[max((-.489-v[1])/(z-v[2]) for v in points),min((3.749-v[1])/(z-v[2]) for v in points)]
r['direction_only_necessary_envelope_condition']={'test_count':len(points),'sun_to_source_y_over_z_current':r['ray_direction_to_sun'][1]/r['ray_direction_to_sun'][2],'y_over_z_interval_to_intersect_all_six_grid_y_bounding_envelopes':ratios,'not_sufficient_for_actual_bars':True,'rear_fascia_front_normal':[0,-1,0],'conflict':'Positive sun-ray Y required by the current grid Y envelope and six selected shadow-band candidates places the rear fascia front on the non-sunlit side. This rules out a small single-sun adjustment as a demonstrated complete repair; multi-light or different shared depth remains unverified.'}
(P/'sun_path_audit.json').write_text(json.dumps(r,indent=2))
# Diagnostic line-offset measurement, not a fit and not a global fidelity score.
sp=P/'source/native/terrace/frames/terrace-main-front-BV1g64y1P7VV-t5586.011739-native.png';rp=P/'renders/main/render_raw.png'
found={}
for label,path in [('source',sp),('render',rp)]:
 im=np.array(Image.open(path).convert('RGB'),dtype=float);g=np.linalg.norm(im[1:]-im[:-1],axis=2);found[label]=[int(g[40:75,x-2:x+3].mean(1).argmax()+40) for x in [900,950,1000,1050,1100,1140]]
metrics={'resolution':[1920,1080],'scope':'Main view, lower outer fascia boundary against unobstructed sky only. No repeated interior beam correspondence is assumed.','measurement':'Max adjacent-row RGB difference averaged over a 5-pixel strip in y=40..74; coordinates are between rows, no subpixel fit.','x_samples':[900,950,1000,1050,1100,1140],'source_edge_y':found['source'],'render_edge_y':found['render'],'render_minus_source_y':[x-y for x,y in zip(found['render'],found['source'])],'uncertainty_pixels':2,'interpretation':'A fixed-baseline image-space residual. Does not identify whether camera, mesh dimensions or surface boundary causes it. No camera or geometry updated.'}
(P/'edge_diagnostic.json').write_text(json.dumps(metrics,indent=2))
# Read-only light-path geometry illustration.
fig,axs=plt.subplots(1,2,figsize=(15,6),dpi=130)
ax=axs[0];ax.add_patch(Rectangle((-.489,4.769846),4.238,.18,facecolor='#507caa',label='Existing open grid Y/Z envelope'))
ax.add_patch(Rectangle((3.5403,4.654846),.16,.565154,facecolor='#b46b51',label='Rear fascia'))
ax.plot([-9,5],[0,0],color='#80674a',lw=3,label='Deck top Z=0')
for i,p in enumerate([p for p in r['probes'] if p['role']=='shadow_band_candidate']):
 q=p['hit_world'];e=p['ray_at_grid_bottom_height'];ax.plot([q[1],e[1]],[q[2],e[2]],color='#dba126',alpha=.55,lw=1.2);ax.plot(q[1],q[2],'o',color='#804f16',ms=3)
ax.plot([-8.05,-.475],[4.86,4.86],'--',color='#999',lw=2,label='Historical OPTIONAL envelope (OFF)')
ax.set(xlim=(-9,5),ylim=(-.4,5.6),xlabel='World Y (front / camera side is left)',ylabel='World Z',title='Frozen sun: foreground rays miss current roof')
ax.legend(loc='lower left',fontsize=8);ax.grid(alpha=.15)
ax=axs[1];vs=np.array(a['grid_vertices_world'])
for e in a['grid_edges']:ax.plot(vs[e,0],vs[e,1],color='#507caa',lw=.8)
ax.add_patch(Rectangle((-4.0875,-8.05),5.4625,7.575,fill=False,ls='--',color='#999',lw=1.2,label='Historical optional extent (OFF)'))
for p in [p for p in r['probes'] if p['role']=='shadow_band_candidate']:
 q=p['hit_world'];e=p['ray_at_grid_bottom_height'];ax.plot([q[0],e[0]],[q[1],e[1]],color='#dba126',lw=1);ax.plot(q[0],q[1],'o',color='#804f16',ms=3);ax.plot(e[0],e[1],'x',color='#c33',ms=6)
ax.set(xlim=(-4.7,2),ylim=(-8.7,4.4),xlabel='World X',ylabel='World Y',title='Plan: red crosses at grid-bottom height')
ax.set_aspect('equal');ax.legend(loc='upper right',fontsize=8);ax.grid(alpha=.15)
fig.suptitle('Physical diagnostic only. No geometry, lighting or visibility change. Model units are not surveyed metres.',fontsize=10)
fig.tight_layout();fig.savefig(P/'sun_path_diagram.png');plt.close(fig)
im=Image.open(sp).convert('RGB');d=ImageDraw.Draw(im)
for i,p in enumerate(r['probes'],1):
 x,y=p['source_pixel'];d.ellipse((x-10,y-10,x+10,y+10),outline='red' if p['role']=='shadow_band_candidate' else 'cyan',width=3);d.text((x+13,y-8),str(i),fill='red' if p['role']=='shadow_band_candidate' else 'cyan',stroke_width=1,stroke_fill='white')
im.save(P/'source_floor_probe_guide.jpg',quality=94,subsampling=0)
print(json.dumps(metrics));print('necessary y/z',ratios)
