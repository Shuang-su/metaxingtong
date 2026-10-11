import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/scratch/fa58bfcf0425/castle_garden_fullscene';bpy.ops.wm.open_mainfile(filepath=R+'/delivery/models/Garden_Complete_Textured.blend');obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];bv={o.name:BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons]) for o in obs};out=[]
for o in obs:
 axis=1;sign=1;targets=[]
 if o.name.startswith('Turned_stone_baluster'):axis=2;targets=[x for x in obs if x.name.startswith('Stone_balustrade_rail') and min((x.matrix_world@v.co).z for v in x.data.vertices)>.9]
 elif o.name.startswith('Classical_flower_urn'):axis=2;sign=-1;targets=[x for x in obs if x.name.startswith('Pedestal_cap')]
 elif o.name.startswith(('Pilaster_edge_flute','Gothic_door_frame','Window_pointed_stone_border','Door_raised','Door_central','Window_dark_mullion','Window_sill')):targets=[x for x in obs if x.name.startswith(('Visible_violet','Pointed_double','Tall_cyan','Stone_vertical'))]
 if not targets:continue
 vv=[o.matrix_world@v.co for v in o.data.vertices];ax=[i for i in range(3) if i!=axis];bounds=[(min(v[i] for v in vv),max(v[i] for v in vv)) for i in ax];d=Vector();d[axis]=sign;n=contact=0;gaps=[]
 for i in range(13):
  for j in range(37):
   p=Vector();p[axis]=-sign*10;p[ax[0]]=bounds[0][0]+(bounds[0][1]-bounds[0][0])*(i+.5)/13;p[ax[1]]=bounds[1][0]+(bounds[1][1]-bounds[1][0])*(j+.5)/37
   a=bv[o.name].ray_cast(p,d)[0]
   if a is None:continue
   # Get rear-most intersection with own solid by backwards cast.
   pback=p+d*20;b=bv[o.name].ray_cast(pback,-d)[0]
   ts=[bv[t.name].ray_cast(p,d)[0] for t in targets];ts=[t for t in ts if t is not None]
   if not ts:continue
   t=min(ts,key=lambda v:(v-p).length);gap=(t-b).dot(d);gaps.append(gap);n+=1;contact+=int(gap<=1e-4)
 out.append({'name':o.name,'sample_rays':13*37,'covered_pairs':n,'contact_or_overlap_rays':contact,'min_gap':min(gaps) if gaps else None,'max_gap':max(gaps) if gaps else None})
json.dump(out,open(R+'/independent_qa/dense_contacts.json','w'),ensure_ascii=False,indent=2);print('objects',len(out),'rays',sum(x['sample_rays'] for x in out),'zero_contact',[x for x in out if not x['contact_or_overlap_rays']]);print('partial',[x for x in out if x['contact_or_overlap_rays']<x['covered_pairs']])
