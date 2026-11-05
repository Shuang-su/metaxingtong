import bpy,json,pathlib,hashlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/cyber-roof-stage-20261105');Q=pathlib.Path(__file__).parent
states=[]
for stage in ['r04','r05']:
 bpy.ops.wm.open_mainfile(filepath=str(P/f'models/roof-{stage}.blend'));s=bpy.context.scene
 states.append({'mesh':{o.name:{'points':sorted(set(tuple(o.matrix_world@v.co)for v in o.data.vertices)),'faces':len(o.data.polygons),'mat':[m.name if m else None for m in o.data.materials],'visibility':[o.hide_render,o.hide_viewport]}for o in s.objects if o.type=='MESH'},'cam':{o.name:{'matrix':[list(r)for r in o.matrix_world],'lens':o.data.lens,'fit':o.data.sensor_fit}for o in s.objects if o.type=='CAMERA'},'lights':{o.name:{'matrix':[list(r)for r in o.matrix_world],'energy':o.data.energy,'color':list(o.data.color)}for o in s.objects if o.type=='LIGHT'}})
a,b=states
out={'mesh_name_equal':a['mesh'].keys()==b['mesh'].keys(),'points_exact':{n:a['mesh'][n]['points']==b['mesh'][n]['points'] for n in a['mesh']},'face_counts':{n:[a['mesh'][n]['faces'],b['mesh'][n]['faces']]for n in a['mesh'] if a['mesh'][n]['faces']!=b['mesh'][n]['faces']},'mat_assignments_equal':all(a['mesh'][n]['mat']==b['mesh'][n]['mat'] for n in a['mesh']),'visibility_equal':all(a['mesh'][n]['visibility']==b['mesh'][n]['visibility']for n in a['mesh']),'camera_equal':a['cam']==b['cam'],'lights_equal':a['lights']==b['lights']}
(Q/'diff.json').write_text(json.dumps(out,indent=2));print('DONE')
