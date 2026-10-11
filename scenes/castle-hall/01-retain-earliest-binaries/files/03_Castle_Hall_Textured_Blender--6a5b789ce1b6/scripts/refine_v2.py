import bpy,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_Textured.blend'));S=bpy.context.scene
# Denser octagon/diamond pattern traced against the empty-aisle image.
for name,diamond in [('Octagonal polished ivory floor tiles',False),('Dark marble diamond inlay',True)]:
 o=bpy.data.objects[name];vs=[];fs=[];pitch=.84;cut=.185;h=pitch/2-.002
 for i in range(-8,9):
  for j in range(-6,27):
   x=i*pitch;y=j*pitch
   pts=[(-h+cut,-h),(h-cut,-h),(h,-h+cut),(h,h-cut),(h-cut,h),(-h+cut,h),(-h,h-cut),(-h,-h+cut)] if not diamond else [(-cut+.004,0),(0,-cut+.004),(cut-.004,0),(0,cut-.004)]
   a=len(vs);vs.extend([(x+xx+(pitch/2 if diamond else 0),y+yy+(pitch/2 if diamond else 0),.004 if diamond else .003) for xx,yy in pts]);fs.append(tuple(range(a,len(vs))))
 old=o.data;me=bpy.data.meshes.new(name+'_dense');me.from_pydata(vs,[],fs);me.update();me.materials.append(old.materials[0]);uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  for li in p.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.6,v.y*.6)
 o.data=me
# Near cakes on aisle-facing end of buffet; flower arrangement on outer end.
for o in S.objects:
 if o.type!='MESH' or not o.data.vertices:continue
 xs=[v.co.x for v in o.data.vertices];ys=[v.co.y for v in o.data.vertices];cx=sum(xs)/len(xs);cy=sum(ys)/len(ys)
 if abs(cx)>2.4 and cy<1.3:
  if any(t in o.name.lower() for t in ['cake','icing','candle flame']):
   for v in o.data.vertices:v.co.x-=1.2 if cx>0 else -1.2
  elif any(c.name[:2]=='06' for c in o.users_collection):
   for v in o.data.vertices:v.co.x+=1.2 if cx>0 else -1.2
# Color-correct authored stone toward the reference's pale muted mauve.
for im in bpy.data.images:
 if im.name.startswith('RoseStone_BaseColor'):
  im.filepath=str(R/'textures/RoseStone_BaseColor.png');im.reload();im.pack()
# Slightly broader framing maintains the far-window alignment while revealing buffet edges.
c=bpy.data.objects['MATCH_A_45m15_empty_aisle'];c.data.lens=41;c.data.shift_y=-.043
S.render.resolution_percentage=65;S.cycles.samples=28;S.camera=c;S.render.filepath=str(R/'renders/refined_v2_MATCH_A.png');bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/04_refined_v2.blend'),compress=True);bpy.ops.render.render(write_still=True)
