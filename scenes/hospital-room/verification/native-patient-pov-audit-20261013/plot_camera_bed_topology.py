from pathlib import Path
import json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
R=Path(__file__).parent;J=json.load(open(R/'patient_camera_constraint.json'));old=json.load(open(R/'camera_candidates.json'));G=json.load(open(R/'frozen_d_world_geometry.json'))
a=np.array(G['objects']['Bed • mattress and sheet']['vertices']);b=np.array(G['objects']['Bed • observed endboard, consistent width']['vertices']);mn=a.min(0);mx=a.max(0);bn=b.min(0);bx=b.max(0)
fig,axs=plt.subplots(1,2,figsize=(16,8),dpi=120)
fig.patch.set_facecolor('#faf9f5')
for ax in axs:ax.set_facecolor('#faf9f5');ax.grid(alpha=.2);ax.set_aspect('equal',adjustable='box')
colors={'A':'#b53636','B':'#8b45a5','old_F':'#5e6670','constrained_A':'#d07917'}
points={k:np.array(v['position']) for k,v in J['semantic_audit_of_free_camera_and_D'].items() if k in ['A','B','old_F']};points['constrained_A']=np.array(J['cameras']['A']['location'])
for ax,dim,ylabel in [(axs[0],1,'D world Y'),(axs[1],2,'D world Z')]:
 ax.add_patch(Rectangle((mn[0],mn[dim]),mx[0]-mn[0],mx[dim]-mn[dim],facecolor='#bfd6c7',edgecolor='#376550',linewidth=2,label='Actual D mattress extent'))
 ax.add_patch(Rectangle((bn[0],bn[dim]),bx[0]-bn[0],bx[dim]-bn[dim],facecolor='#c4bdad',edgecolor='#6b6354',linewidth=2,label='Visible endboard in D'))
 for k,p in points.items():
  ax.scatter(p[0],p[dim],s=80,c=colors[k],zorder=4)
  labels={'A':'A free camera','B':'B free camera','old_F':'Existing F','constrained_A':'A bed-region test (at boundary)'}
  offset={'A':(-30,-23),'B':(-58,15),'old_F':(-5,-22),'constrained_A':(8,20)}[k]
  ax.annotate(labels[k],(p[0],p[dim]),xytext=offset,textcoords='offset points',fontsize=10,color=colors[k],weight='bold')
 ax.set_xlim(-2.6,2.65);ax.set_xlabel('D world X',fontsize=11);ax.set_ylabel(ylabel,fontsize=11)
axs[0].set_ylim(-3.85,-.8);axs[0].set_title('Top view: free cameras lie outside this D bed',loc='left',fontsize=13,weight='bold')
axs[1].set_ylim(-.2,1.8);axs[1].set_title('Side view: camera / mattress / endboard relation',loc='left',fontsize=13,weight='bold')
axs[0].legend(loc='upper left',fontsize=9);axs[1].axhline(mx[2],c='#376550',ls=':',lw=1)
fig.suptitle('D topology audit: image-fit cameras are not validated patient viewpoints',fontsize=18,weight='bold',y=.95)
fig.text(.055,.12,'User context: the camera is the patient lying on the hospital bed.\nThe mismatch may be in the free camera, D bed length/orientation, or the endboard interpretation.\nD scene units only; no physical measurements. Diagram uses actual D world coordinates. Geometry was not changed.',fontsize=12,linespacing=1.5)
plt.subplots_adjust(left=.055,right=.98,top=.85,bottom=.27,wspace=.16);fig.savefig(R/'D_bed_camera_topology_DIAGNOSTIC.png');plt.close(fig)
