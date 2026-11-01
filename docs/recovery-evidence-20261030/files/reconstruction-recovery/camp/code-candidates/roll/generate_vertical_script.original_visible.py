from pathlib import Path
p=Path('/workspace/shared/desert-camp-roll-audit-20261031');s=(p/'audit.py').read_text();s=s.replace("OUT=Path(__file__).resolve().parent","OUT=Path(__file__).resolve().parent/'with_vertical_segment';OUT.mkdir(exist_ok=True)")
insert='''
SEG_OBS=np.array([[185.,707.],[185.,731.]])
SEG_X=np.array([[-.45,0,0],[-.45,0,.456]])
def segment_check(p,f):
 xy,dep=project(SEG_X,p,f);a,b=xy;d=b-a;L=np.linalg.norm(d);v=SEG_OBS-a;t=(v@d)/(L*L);perp=(v[:,0]*d[1]-v[:,1]*d[0])/L;outside=(t-np.clip(t,0,1))*L
 return {'model_projected_full_edge':xy.tolist(),'observed_middle_samples':SEG_OBS.tolist(),'signed_perp_px':perp.tolist(),'outside_full_edge_px':outside.tolist(),'sample_fractions_on_model_edge':t.tolist(),'depths':dep.tolist()}
def segment_residual(p,f):
 q=segment_check(p,f);return np.r_[q['signed_perp_px'],q['outside_full_edge_px']]/4
'''
s=s.replace('def seed(q):',insert+'\ndef seed(q):')
s=s.replace("def fun(v):return ((project(X,v,f)[0]-UV)/sig[:,None]).ravel()","def fun(v):return np.r_[((project(X,v,f)[0]-UV)/sig[:,None]).ravel(),segment_residual(v,f)]")
s=s.replace("b['heldout_checks']=[]","b['heldout_checks']=[];b['vertical_segment_checks']=segment_check(p,f)")
s=s.replace("'fit_count':6","'fit_count':10,'active_data_note':'6 point coordinates + 2 signed line-sample distances; 2 additional finite-span penalties remain zero if samples lie within model edge. Endpoints are not mapped to model endpoints.'")
s=s.replace("'vertical_segment_added_to_fit':False","'vertical_segment_added_to_fit':True,'vertical_segment_training':{'samples':SEG_OBS.tolist(),'uncertainty_px':4,'model_edge':SEG_X.tolist(),'interpretation':'visible middle of nominal front-body left vertical line, not observed box-bottom/top endpoints; body near-orthogonality/inferred dimensions assumed'}")
s=s.replace("'fit_points':names","'fit_points':names,'extra_training_feature':'front_box_left_vertical_finite_middle_segment'")
(p/'audit_with_vertical_segment.py').write_text(s)
