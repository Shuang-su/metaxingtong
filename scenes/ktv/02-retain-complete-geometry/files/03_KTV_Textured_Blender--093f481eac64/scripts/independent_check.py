import bpy,bmesh,json,hashlib,os
from mathutils import Vector
p='/workspace/scratch/fa58bfcf0425/ktv_fullroom/delivery/models/KTV_Complete_Open_Stage.blend'
bpy.ops.wm.open_mainfile(filepath=p)
D={'hash':hashlib.sha256(open(p,'rb').read()).hexdigest(),'objects':{},'degenerate':[],'negative':[],'nonmanifold':[],'animation':[],'inconsistent_shared_edge_winding':[]}
for o in bpy.context.scene.objects:
 if o.animation_data or o.constraints:D['animation'].append(o.name)
 if o.type!='MESH':continue
 ps=[o.matrix_world@v.co for v in o.data.vertices]
 bm=bmesh.new();bm.from_mesh(o.data)
 nd=sum(f.calc_area()<1e-12 for f in bm.faces); nm=sum(not e.is_manifold for e in bm.edges)
 iw=sum(e.is_manifold and not e.is_contiguous for e in bm.edges)
 if iw:D['inconsistent_shared_edge_winding'].append([o.name,iw])
 if nd:D['degenerate'].append([o.name,nd])
 if not nm and bm.calc_volume(signed=True)<-1e-8:D['negative'].append(o.name)
 if nm:D['nonmanifold'].append([o.name,nm])
 D['objects'][o.name]={'min':[min(p[i] for p in ps) for i in range(3)],'max':[max(p[i] for p in ps) for i in range(3)],'hidden':o.hide_render,'polygons':len(o.data.polygons),'materials':[m.name if m else '' for m in o.data.materials],'modifiers':[m.type for m in o.modifiers]}
 bm.free()
json.dump(D,open('/workspace/scratch/fa58bfcf0425/ktv_fullroom/independent_qa/check.json','w'),indent=2)
