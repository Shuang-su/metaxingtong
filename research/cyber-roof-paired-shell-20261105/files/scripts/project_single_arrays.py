dep=bpy.context.evaluated_depsgraph_get();ann=json.loads((P/'sources/annotations-v1.json').read_text())
cams={n:bpy.data.objects['SOURCE'+n+(' conditional camera' if n=='11' else ' auxiliary different state')] for n in ['10','11']}
mats={n:np.array(c.calc_matrix_camera(dep,x=1192,y=671,scale_x=1,scale_y=1)@c.matrix_world.inverted()) for n,c in cams.items()}
def proj(v,n):
 a=np.asarray(v);one=len(a.shape)==1
 if one:a=a[None,:]
 q=np.c_[a,np.ones(len(a))]@mats[n].T;xy=np.c_[(q[:,0]/q[:,3]+1)*596,(1-q[:,1]/q[:,3])*335.5]
 return (xy[0],q[0,3]) if one else (xy,q[:,3])
# Whole-group continuous x field. This is a numerical geometric hypothesis only; no object is changed.
roofobjs=[o for o in s.objects if o.name.startswith('ROOF_MAIN')];vertices={n:old[n] for n in main}
ridge=vertices['ROOF_MAIN gold ridge'];minx,maxx=ridge[:,0].min(),ridge[:,0].max();capix={'left':np.where(np.abs(ridge[:,0]-minx)<1e-5)[0],'right':np.where(np.abs(ridge[:,0]-maxx)<1e-5)[0]}
# Only shell+ribs for dark lower envelope; the artificial continuous gold beam is deliberately excluded.
geom=[];edges=[];metadata=[];offset=0
for o in roofobjs:
 if not(o.name=='ROOF_MAIN closed shell' or o.name.startswith('ROOF_MAIN rib')):continue
 v=vertices[o.name];o.data.calc_loop_triangles();ee=set()
 for t in o.data.loop_triangles:
  a,b,c=t.vertices
  for x,y in [(a,b),(b,c),(c,a)]:ee.add(tuple(sorted((x,y))))
 for a,b in sorted(ee):edges.append((offset+a,offset+b));metadata.append((o.name,int(a),int(b)))
 geom.extend(v);offset+=len(v)
geom=np.array(geom);edges=np.array(edges);shell=vertices['ROOF_MAIN closed shell']
sourcepoints={p['id']:p for p in ann['source11']['points']}
rows=[]
for h in [.74,.55]:
 tv={name:(old[name] if h==.74 else new[name]) for name in vertices};out={'h':h,'baseline':h==.74,'points':[],'lower_envelopes':{},'full_group_world_bounds':np.stack([np.concatenate(list(tv.values())).min(0),np.concatenate(list(tv.values())).max(0)],axis=1).tolist()}
 for side in ['left','right']:
  ix=capix[side];xy,z=proj(tv['ROOF_MAIN gold ridge'][ix],'11');j=int(np.argmin(xy[:,0]) if side=='left' else np.argmax(xy[:,0]));chosen=int(ix[j]);sid='RIDGE_'+('L' if side=='left' else 'R')+'_OUTER_CAP';ref=sourcepoints[sid]
  out['points'].append({'source_id':sid,'model_object':'ROOF_MAIN gold ridge','actual_vertex_index':chosen,'world':tv['ROOF_MAIN gold ridge'][chosen].tolist(),'projected':xy[j].tolist(),'source_xy':ref['xy'],'residual_xy':(xy[j]-np.array(ref['xy'])).tolist(),'semantic_caution':'model round tube-end extremum vs observed decorated cap; conditional, not homologous precise feature','entire_end_ring':[{'vertex':int(k),'projection':proj(tv['ROOF_MAIN gold ridge'][k],'11')[0].tolist()} for k in ix]})
 for side,ix in [('L',16*65),('R',16*65+64)]:
  sid='RIDGE_'+side+'_SLOPE_JUNCTION';xy,z=proj(tv['ROOF_MAIN closed shell'][ix],'11');ref=sourcepoints[sid]
  out['points'].append({'source_id':sid,'model_object':'ROOF_MAIN closed shell','actual_vertex_index':ix,'world':tv['ROOF_MAIN closed shell'][ix].tolist(),'projected':xy.tolist(),'source_xy':ref['xy'],'residual_xy':(xy-np.array(ref['xy'])).tolist(),'semantic_caution':'saved roof ridge-end vertex vs bar-under-slope junction; model has no separate extended end cap, correspondence conditional'})
 for label,co in [('front_candidate',[-11.4,2.5,6.9]),('back_candidate',[-11.4,8.5,6.9])]:
  wc=np.array(co);xy,z=proj(wc,'11');out['points'].append({'source_id':'LEFT_SWEPT_GOLD_TIP','candidate':label,'world_centerline':wc.tolist(),'projected':xy.tolist(),'source_xy':[84,98],'residual_xy':(xy-np.array([84,98])).tolist(),'use_fit':False,'reason':'front/back/side correspondence unresolved; neither selected by best loss'})
 vg=np.concatenate([tv[o.name] for o in roofobjs if o.name=='ROOF_MAIN closed shell' or o.name.startswith('ROOF_MAIN rib')])
 for n in ['10','11']:
  xy,depth=proj(vg,n);aa=xy[edges[:,0]];bb=xy[edges[:,1]];bands=[]
  for band in ann['source'+n]['segments']:
   if 'x_interval' not in band:continue
   xlo,xhi=band['x_interval'];ylo,yhi=band['y_interval'];samples=[]
   for x in [xlo,(xlo+xhi)/2,xhi]:
    mask=(np.minimum(aa[:,0],bb[:,0])<=x)&(np.maximum(aa[:,0],bb[:,0])>=x)&(np.abs(bb[:,0]-aa[:,0])>1e-10)
    ids=np.where(mask)[0];lam=(x-aa[ids,0])/(bb[ids,0]-aa[ids,0]);ys=aa[ids,1]+lam*(bb[ids,1]-aa[ids,1]);k=int(np.argmax(ys));eid=int(ids[k]);y=float(ys[k]);l=float(lam[k]);a,b=edges[eid];tw=l*depth[a]/((1-l)*depth[b]+l*depth[a]);world=vg[a]*(1-tw)+vg[b]*tw
    samples.append({'x':x,'y':y,'world_edge_intersection':world.tolist(),'edge_object_and_vertex_ids':metadata[eid],'signed_outside_band':y-yhi if y>yhi else (y-ylo if y<ylo else 0),'semantics':'max projected shell+rib triangle edge; gold beam excluded; not first-hit against other objects or exact source scallop correspondence'})
   bands.append({'source_band_id':band['id'],'source_x_interval':band['x_interval'],'source_y_interval':band['y_interval'],'three_samples':samples})
  out['lower_envelopes'][n]=bands
 rows.append(out)

(P/'results/single-a055-projections.json').write_text(json.dumps({'scope':'new pair translation + ring rigid rotation arrays, not old x field; full conditional source point and envelope sets; no first-hit or fit claim','nulls':{n:ann['source'+n]['nulls'] for n in ['10','11']},'rows':rows},indent=2))
