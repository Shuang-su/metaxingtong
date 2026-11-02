import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa/front-camera-diagnostic';bpy.ops.wm.open_mainfile(filepath=str(R/'models/ferris_remake_R04_material.blend'))
# Find actual un-beveled rear leaf outer-face corner vertices, not image round tangencies.
pts={}
for name,x,z in [('bl',-.505,.05),('br',.505,.05),('tl',-.505,2.56),('tr',.505,2.56)]:
 ob=bpy.data.objects['door_4_bottom' if z<1 else 'door_4_top'];vv=[ob.matrix_world@v.co for v in ob.data.vertices];target=Vector((x,1.79,z));p=min(vv,key=lambda v:(v-target).length);assert (p-target).length<1e-6;pts[name]=list(p)
train={'left':[pts['bl'],pts['tl']],'right':[pts['br'],pts['tr']],'top':[pts['tl'],pts['tr']],'bottom':[pts['bl'],pts['br']]}
hold=[]
for name,pixels,external in [('cream_bezel_4_1',[[[337,350],[338,600]],[[678,350],[677,600]]],False),('cream_bezel_4_0',[[[1031,350],[1030,600]],[[1352,350],[1351,600]]],False),('cream_bezel_0_1',[[[1262,350],[1263,780]],[[1788,350],[1787,780]]],True)]:
 o=bpy.data.objects[name];n=len(o.data.vertices)//4;loop=[o.matrix_world@v.co for v in o.data.vertices[(2*n if external else 0):(3*n if external else n)]]
 for i,xx in enumerate([min(v.x for v in loop),max(v.x for v in loop)]):
  vv=[v for v in loop if abs(v.x-xx)<1e-6];lo=min(vv,key=lambda v:v.z);hi=max(vv,key=lambda v:v.z);hold.append({'name':name+('_source_left' if i==0 else '_source_right'),'edge_world':[list(lo),list(hi)],'source_subsegment':pixels[i],'identity':'conditional visible fixed frame instance, not blind holdout','source_uncertainty_px':8 if external else 6})
c=bpy.data.objects['SRC_front'];(Q/'actual-mesh-edges.json').write_text(json.dumps({'training_edges_world':train,'rear_leaf_face_y':1.79,'heldout_edges':hold,'heldout_lamp':{'world':[0,0,2.555],'source':[854,44],'uncertainty_px':12},'baseline_camera':{'location':list(c.location),'matrix_world':[list(r) for r in c.matrix_world],'lens_mm':c.data.lens,'sensor_width':c.data.sensor_width},'proof':'train endpoint positions located in actual door top/bottom mesh vertices to1e-6; source subsegment endpoints are NOT mapped to these 3D endpoints; fitting uses finite projected edges'},indent=2))
print('EXPORTED_ACTUAL_EDGES')
