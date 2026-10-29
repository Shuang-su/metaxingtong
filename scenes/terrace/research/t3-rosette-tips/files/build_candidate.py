import bpy, math, json, hashlib, os
from mathutils import Vector
ROOT='/workspace/scratch/fa58bfcf0425/terrace_table_candidate_v2'
remove=['Table_small_cup','Planter.003']+[f'Plant_{k}.{i:03d}' for k in ['leaf','stem'] for i in range(36,48)]
def snapshot(o):
 import array
 h=hashlib.sha256()
 d={'matrix':[list(r) for r in o.matrix_world], 'hide':[o.hide_render,o.hide_viewport], 'data':o.data.name if o.data else None,'mods':[(m.name,m.type) for m in o.modifiers]}
 if o.type=='MESH':
  d['materials']=[m.name if m else None for m in o.data.materials]
  for coll,prop,count,typ in [(o.data.vertices,'co',len(o.data.vertices)*3,'f'),(o.data.loops,'vertex_index',len(o.data.loops),'i'),(o.data.polygons,'loop_total',len(o.data.polygons),'i')]:
   ar=array.array(typ,[0])*count;coll.foreach_get(prop,ar);h.update(ar.tobytes())
  for l in o.data.uv_layers:
   ar=array.array('f',[0])*(len(l.data)*2);l.data.foreach_get('uv',ar);h.update(ar.tobytes())
 if o.type in ['CAMERA','LIGHT']: d['parameters']={p.identifier:str(getattr(o.data,p.identifier)) for p in o.data.bl_rna.properties if p.type not in ['COLLECTION','POINTER']}
 h.update(json.dumps(d,sort_keys=True).encode());return h.hexdigest()
print('BEGIN_FREEZE',flush=True)
before={o.name:snapshot(o) for o in bpy.data.objects if o.name not in remove}
print('BASELINE_HASHED',len(before),flush=True)
for n in remove:
 assert n in bpy.data.objects,n
 bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
coll=bpy.data.collections.new('T2_Visible_Table_Decor_CANDIDATE');bpy.context.scene.collection.children.link(coll)
def mat(n,c,rough=.65):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;return m
charcoal=mat('T2_Left_Charcoal_Ceramic',(.065,.057,.054));gray=mat('T2_Right_WarmGray_Ceramic',(.14,.132,.125));soil=mat('T2_Dark_Soil',(.025,.018,.014));purple=mat('T2_Purple_Rosette',(.20,.10,.13));green=mat('T2_Green_Rosette',(.085,.14,.105));white=mat('T2_White_Deer_Approximation',(.65,.65,.61))
def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);coll.objects.link(o);o.data.materials.append(m)
 for p in d.polygons:p.use_smooth=True
 o['evidence']='5586.011739 front projection only; hidden depth inferred'
 return o
def lathe(n,x,y,z,prof,m):
 v=[];f=[];N=64
 for r,h in prof:
  for j in range(N):a=2*math.pi*j/N;v.append((x+r*math.cos(a),y+r*math.sin(a),z+h))
 for i in range(len(prof)):
  ni=(i+1)%len(prof)
  for j in range(N):f.append((i*N+j,i*N+(j+1)%N,ni*N+(j+1)%N,ni*N+j))
 return mesh(n,v,f,m)
def pot(n,x,y,h,r,m):
 z=.734;lathe(n,x,y,z,[(.002,0),(r*.84,0),(r*.90,.018),(r,h-.012),(r*.99,h),(r*.88,h),(r*.86,h-.025),(.002,h-.025)],m)
 lathe(n+'_Soil',x,y,z,[(.002,h-.028),(r*.85,h-.028),(r*.85,h-.025),(.002,h-.025)],soil)
 return z+h
# Leaves are closed lenticular pointed meshes, with layered radial rosette rather than vertical oval paddles.
def rosette(n,x,y,z,rise,rad,m):
 for tier,(count,L,W,lift) in enumerate([(11,rad,rad*.36,rise*.3),(9,rad*.79,rad*.32,rise*.65),(7,rad*.52,rad*.25,rise)]):
  for j in range(count):
   a=2*math.pi*(j/count+.07*tier); ca,sa=math.cos(a),math.sin(a);v=[];f=[];N=10;K=12
   # closed rings along leaf; endpoint caps with single vertices
   v.append((x+ca*.012,y+sa*.012,z+.008*tier))
   for i in range(1,N):
    t=i/N; rr=.012+L*t;ww=W*math.sin(math.pi*t)**.8; hh=.012*math.sin(math.pi*t); zz=z+.008*tier+lift*t+.022*math.sin(math.pi*t)
    for k in range(K):
     q=2*math.pi*k/K; v.append((x+ca*rr-sa*ww*math.cos(q),y+sa*rr+ca*ww*math.cos(q),zz+hh*math.sin(q)))
   tip=len(v);v.append((x+ca*(.012+L),y+sa*(.012+L),z+.008*tier+lift))
   for k in range(K):f.append((0,1+(k+1)%K,1+k))
   for i in range(N-2):
    for k in range(K):b=1+i*K;c=1+(i+1)*K;f.append((b+k,b+(k+1)%K,c+(k+1)%K,c+k))
   for k in range(K):b=1+(N-2)*K;f.append((b+k,b+(k+1)%K,tip))
   mesh(f'{n}_leaf_{tier}_{j:02}',v,f,m)
x1,y1=3.32,2.86;x2,y2=3.66,2.90
z1=pot('T2_Left_Decorated_Pot',x1,y1,.235,.120,charcoal);z2=pot('T2_Right_Tall_Gray_Pot',x2,y2,.315,.128,gray)
rosette('T2_Left_Purple',x1,y1,z1-.015,.12,.145,purple);rosette('T2_Right_Green',x2,y2,z2-.015,.055,.162,green)
# Front visible white deer-like motif is an explicitly approximate flat ceramic marking, not an identification of the product.
outline=[(-.065,.025),(.044,.025),(.025,.045),(.004,.060),(-.012,.090),(-.020,.130),(.035,.160),(.048,.182),(.018,.177),(.010,.192),(-.001,.178),(-.020,.179),(-.025,.199),(-.036,.179),(-.050,.170),(-.062,.173),(-.049,.158),(-.044,.140),(-.061,.110),(-.048,.077)]
v=[]
for xx,zz in outline:
 rr=.120*(.9+.1*(zz/.235));v.append((x1+xx,y1-math.sqrt(max(.0001,rr*rr-xx*xx))-.0015,.734+zz))
mesh('T2_Left_White_Motif_APPROXIMATE',v,[tuple(range(len(v)-1,-1,-1))],white)
print('DECOR_BUILT',flush=True)
after={n:snapshot(bpy.data.objects[n]) for n in before};assert before==after
json.dump({'unchanged_object_count':len(before),'unchanged_hashes':before,'removed_decor_names':remove,'new_names':[o.name for o in coll.objects],'scope':'Two pots and rosettes only. Table tray ribs white inner object unchanged. Back surfaces and plant depth inferred.'},open(ROOT+'/freeze_audit.json','w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/Terrace_T2_TwoPots_Candidate.blend')
s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=32;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.cycles.seed=0;s.render.use_compositing=False;s.render.threads_mode='FIXED';s.render.threads=4
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.filepath=ROOT+'/T2_material_raw.png'
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1430/1920;s.render.border_max_x=1650/1920;s.render.border_min_y=1-845/1080;s.render.border_max_y=1-580/1080;s.render.filepath=ROOT+'/T2_preview_crop.png';bpy.ops.render.render(write_still=True)
