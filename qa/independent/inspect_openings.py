import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(sys.argv[sys.argv.index('--')+1]);dg=bpy.context.evaluated_depsgraph_get();names=['central red facade with real opening','left red screen','right red screen'];ts={};bs={}
for name in names:
 o=bpy.data.objects[name];ev=o.evaluated_get(dg);me=ev.to_mesh();v=[o.matrix_world@p.co for p in me.vertices];f=[list(p.vertices)for p in me.polygons];ts[name]=BVHTree.FromPolygons(v,f);bs[name]=[[min(p[i]for p in v)for i in range(3)],[max(p[i]for p in v)for i in range(3)]];ev.to_mesh_clear()
def probe(name,x,z,expected,label):
 b=bs[name];front=b[0][1]-.05;back=b[1][1]+.05;rs=[]
 for origin,dir in [((x,front,z),(0,1,0)),((x,back,z),(0,-1,0))]:
  loc,norm,index,dist=ts[name].ray_cast(Vector(origin),Vector(dir),back-front);rs.append({'hit':loc is not None,'location':list(loc)if loc is not None else None,'distance':dist,'origin':origin,'direction':dir,'ray_max_distance':back-front})
 return {'object':name,'label':label,'x':x,'z':z,'expected_wall_intersection':expected,'forward_reverse':rs,'passes':all(r['hit']==expected for r in rs)}
rows=[]
for x,z,e,label in [(0,.25,False,'bottom opening'),(0,2,False,'center opening'),(0,4.25,False,'upper opening'),(-1,2,False,'left center opening'),(1,2,False,'right center opening'),(-4.9,2,True,'left solid flank'),(4.9,2,True,'right solid flank'),(0,5.5,True,'solid lintel')]:rows.append(probe(names[0],x,z,e,label))
for sign,name in [(-1,'left red screen'),(1,'right red screen')]:
 for x,z,e,label in [(7.95,2.494,False,'center cutout'),(7.95,1.5,False,'lower cutout'),(7.95,3.5,False,'upper cutout'),(8.45,2.494,False,'cutout extends to panel outer edge'),(6.1,2.494,True,'inner solid panel'),(7.95,.3,True,'bottom solid panel'),(7.95,4.7,True,'upper solid panel')]:rows.append(probe(name,sign*x,z,e,label))
r={'blend':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'method':'Target-panel-only evaluated BVH; forward/reverse short rays from .05 in front/behind target slab bounds. Rear tunnel frames, wall and bay-return cannot be misclassified as blocking the portal. Probes establish selected open/solid regions, not source-confirmed aperture geometry. Side apertures are open-sided cutouts extending through panel outer edge, not fully enclosed oval holes.','bounds':bs,'probes':rows,'rays':2*len(rows),'failed':[x for x in rows if not x['passes']]};out.write_text(json.dumps(r,indent=2));print('OPENING_RAYS',r['rays'],'FAILED',r['failed'])
