from pathlib import Path
import hashlib,urllib.request,json
p=Path(__file__).resolve().parent;rev='5426e4f0f36572d16453bbda7a8389317b1bef99';repo='depth-anything/Depth-Anything-V2-Small-hf';expected={'README.md':'319566441daaac0c5ed83e75a8fd19bae0863f3275e23f147c06fe0906edf6fb','config.json':'c56698d3643dde1f83ea2212759e6b31a22b8f827246a36dd007ee8a22b3ff75','model.safetensors':'3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70','preprocessor_config.json':'d41175c0d889477ca8fc67191e540faef14baf6275157b3fdecf78469e6bbf84'};out=[]
for name,sha in expected.items():
 url=f'https://huggingface.co/{repo}/resolve/{rev}/{name}';f=p/'model'/name
 with urllib.request.urlopen(url,timeout=120) as r:f.write_bytes(r.read())
 assert hashlib.sha256(f.read_bytes()).hexdigest()==sha
 out.append({'path':name,'bytes':f.stat().st_size,'sha256':sha,'url':url});print(name,'verified',flush=True)
(p/'provenance/model-manifest.json').write_text(json.dumps({'repo':repo,'revision':rev,'artifacts':out},indent=2))
