from pathlib import Path
import runpy,json,contextlib,io
R=Path(__file__).resolve().parents[2]
with contextlib.redirect_stdout(io.StringIO()):m=runpy.run_path(str(R/'c28/scripts/fit_spacing.py'))
out={}
for k,x,ys in [('H',900,[195,171,147,124,100,76,53,30,6]),('G',300,[242,216,190,165,140,115,90,65,41,15]),('N642',550,[157,131,105,81,57,33,9])]:
 vals={}
 for tag,s in [('C27',1),('C28',m['scale'])]:
  allvals=[{'slat':i+1,'y':float(m['bottom'](k,i,s,[x])[0])} for i in range(1,26)]
  vals[tag]=[a for a in allvals if 0<=a['y']<=max(ys)+6]
 out[k]={'fixed_native_x':x,'source_ridge_y_bottom_to_top':ys,'source_visible_ridges':len(ys),'source_method':'native grayscale contrast ridge peaks at fixed x, visually checked ordering; no parameter fit on upper additions','projected':vals}
out['665']={'max_projected_y_C27':max(float(m['uv']('665',i,1)[:,1].max()) for i in range(1,26)),'max_projected_y_C28':max(float(m['uv']('665',i,m['scale'])[:,1].max()) for i in range(1,26)),'status':'bank1 remains wholly above frame; geometry projection only, not shadow verification'}
(R/'c28/top_frame_count_check.json').write_text(json.dumps(out,indent=2))
