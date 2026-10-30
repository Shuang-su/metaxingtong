"""Technical projection diagrams over untouched sources, not reconstructed renders."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from diagnose import HERE, ROOT, CFG, G, T0, FRONT, OBLIQUE, EMPTY_RECT, project, table_corners, table_feet, table_stats

cam=json.loads((HERE/'camera-only-results.json').read_text())
table=json.loads((HERE/'shared-table-results.json').read_text())
out=HERE/'figures';out.mkdir(exist_ok=True)
def trial(kind):
    a=[a for a in table['r05']['optimization_trials'] if a['objective']==kind and a['success']]
    return min(a,key=lambda a:a['cost'])
cases=[('r05','R05 baseline; no changed geometry',T0,CFG['front'],CFG['oblique']),
       ('camera-only','Camera-only diagnostic; static anchor gate FAILED',T0,cam['front']['best']['parameters'],cam['oblique']['best']['parameters']),
       ('less-oblique-table','Shared table: minimize oblique intrusion, front RMS <= 6 px; REJECTED',trial('min_top_intrusion_front6')['parameters'],CFG['front'],CFG['oblique']),
       ('lower-front-feet','Shared table: minimize front foot deficit, front RMS <= 6 px; REJECTED',trial('min_foot_deficit_front6')['parameters'],CFG['front'],CFG['oblique'])]
source_paths={'front':ROOT/'sources/BV14ioLBAEDt_1283.813032_front.png','oblique':ROOT/'sources/BV14ioLBAEDt_1505.632497_oblique.png'}
saved=[]
for slug,label,t,cf,co in cases:
    stats=table_stats(np.array(t),np.array(cf),np.array(co))
    for view,c in [('front',np.array(cf)),('oblique',np.array(co))]:
        source=np.asarray(Image.open(source_paths[view]).convert('RGB'))
        fig=plt.figure(figsize=(19.2,11.6),dpi=100,facecolor='#10151b')
        ax=fig.add_axes([0,0,1,1080/1160])
        ax.imshow(source,extent=(0,1920,1080,0),interpolation='none')
        ax.set(xlim=(0,1920),ylim=(1080,0));ax.axis('off')
        uv=project(table_corners(t),c)
        ax.plot(uv[[0,1,3,2,0],0],uv[[0,1,3,2,0],1],color='#00e6ff',lw=3)
        foot=table_feet(t);legtop=foot.copy();legtop[:,2]=G['table_z']-.028
        for p,q in zip(project(legtop,c),project(foot,c)):
            ax.plot([p[0],q[0]],[p[1],q[1]],color='#00e6ff',lw=3)
            ax.plot(q[0],q[1],'o',color='#00e6ff',ms=7)
        anchors=FRONT if view=='front' else OBLIQUE
        src=np.array([a['source_px'] for a in anchors]);pred=project([a['world'] for a in anchors],c)
        ax.plot(src[:,0],src[:,1],'+',color='#1dff30',ms=11,mew=2)
        ax.plot(pred[:,0],pred[:,1],'x',color='#f938db',ms=9,mew=2)
        if view=='front':
            ax.plot([546,1353,488,1407],[712,712,750,750],'+',color='#ffeb00',ms=12,mew=2)
            score=f"corner RMS {stats['front_corner_rms_px']:.2f}px; foot lower-bound deficits {stats['front_feet_bottom_deficit_px'][0]:.1f}/{stats['front_feet_bottom_deficit_px'][1]:.1f}px"
        else:
            x0,y0,x1,y1=EMPTY_RECT;ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fill=False,edgecolor='#ff8d00',lw=4))
            score=f"wrong table samples in observed clear rectangle: {stats['oblique_wrong_table_fraction']:.1%}"
        fig.text(.012,.975,f'{label} | {view} | {score}',fontsize=15,color='white',va='top')
        fig.text(.012,.946,'PROJECTION DIAGNOSTIC ONLY — not a Blender render. Cyan: modeled table. Green: source anchors. Magenta: projected anchors.',fontsize=13,color='white',va='top')
        dest=out/f'{slug}-{view}.png';fig.savefig(dest,dpi=100);plt.close(fig);saved.append(dest)
contact=Image.new('RGB',(1920,4*580),(16,21,27))
for i,p in enumerate(saved):
    im=Image.open(p).convert('RGB');im=im.resize((960,580),Image.Resampling.LANCZOS)
    contact.paste(im,((i%2)*960,(i//2)*580))
contact.save(out/'diagnostic-contact.jpg',quality=84,subsampling=0,optimize=True)
print('saved',len(saved),'native-coordinate diagnostic PNGs; contact bytes',(out/'diagnostic-contact.jpg').stat().st_size)
