import bpy,json,pathlib,itertools
P=pathlib.Path('/workspace/scratch/fa58bfcf0425');Q=P/'independent-backstage-tabletop-qa-20261104';bpy.ops.wm.open_mainfile(filepath=str(P/'backstage-local-study-20261105/models/R10_material.blend'));names=[n for n in bpy.data.objects.keys() if n.startswith('DEVICE_front_')];B={}
for n in names:
 o=bpy.data.objects[n];vs=[o.matrix_world@v.co for v in o.data.vertices];B[n]=[[min(v[i]for v in vs),max(v[i]for v in vs)]for i in range(3)]
R=[]
for a,b in itertools.combinations(B,2):
 x,y=B[a],B[b];ov=[min(x[i][1],y[i][1])-max(x[i][0],y[i][0])for i in range(3)]
 if min(ov)>0:R.append({'objects':[a,b],'world_bounds':[x,y],'overlap_xyz':ov,'front_y_equal':x[1][0]==y[1][0],'front_xz_overlap_area':ov[0]*ov[2]})
(Q/'R10-coplanar-front-check.json').write_text(json.dumps(R,indent=2));print(R)
