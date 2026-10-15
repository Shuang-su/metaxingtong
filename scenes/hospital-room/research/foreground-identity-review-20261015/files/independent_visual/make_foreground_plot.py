import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import json
from pathlib import Path
out=Path('/workspace/scratch/fa58bfcf0425/hospital_bed_context_review_20261015/independent_visual')
rows=json.loads((out/'foreground_identity_points.json').read_text())['points']
fig,axes=plt.subplots(5,1,figsize=(16,12.5),layout='constrained')
for ax,key,limits in zip(axes,['N665','N640','H','G','T1'],[(1100,1920,1080,760),(1100,1920,1080,930),(1350,1920,1080,970),(1200,1920,1080,950),(420,1150,650,430)]):
 pts=[p for p in rows if p['source_id']==key];im=Image.open(pts[0]['source_path'])
 ax.imshow(im);ax.set_xlim(limits[:2]);ax.set_ylim(limits[2:]);ax.set_aspect('equal')
 for p in pts:
  ax.scatter([p['x']],[p['y']],c='#00ffff',edgecolors='black',s=60,zorder=3)
  ax.annotate(p['id']+f" ({p['x']},{p['y']})",(p['x'],p['y']),xytext=(-100,-15),textcoords='offset points',color='#00ffff',fontsize=10,fontweight='bold',bbox=dict(facecolor='black',alpha=.78,pad=2),arrowprops=dict(arrowstyle='-',color='#00ffff'))
 title='NATIVE 1920x1080' if pts[0]['coordinate_space'].startswith('native') else 'VIEWPORT 1180x757 (not native; never scale for native raycast)'
 ax.set_title(key+' | '+title+' | '+pts[0]['source_surface_identity'],loc='left',fontsize=11)
 ax.set_ylabel('source y');ax.set_xlabel('source x')
fig.suptitle('Foreground identity evidence: original-pixel coordinates, partial visual crops\nCyan markers are surface-interior observations, not calibrated residual anchors.',fontsize=15)
fig.savefig(out/'foreground_identity_evidence.png',dpi=150)
print(out/'foreground_identity_evidence.png')
