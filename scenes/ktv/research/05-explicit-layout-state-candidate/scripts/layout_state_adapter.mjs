// No camera input. Loads exact verified shared GLB bytes; only explicit visibility targets may change.
const bindings = new WeakMap();
function targetNames(manifest) {
  const groups=[manifest.furnishing_group,...(manifest.inferred_attachment_groups||[])];
  if(groups.some(g=>g.objects.length!==g.expected_count))throw new Error('Invalid target group size');
  const names=groups.flatMap(g=>g.objects);
  if(new Set(names).size!==names.length)throw new Error('Duplicate visibility target');
  const dynamic=new Set(manifest.dynamic_groups.flatMap(g=>g.objects));
  if(names.some(n=>dynamic.has(n)))throw new Error('Dynamic/furnishing overlap');
  return names;
}
export function timelineState(manifest, seconds) {
  if(typeof seconds!=='number'||!Number.isFinite(seconds))return 'unknown';
  const [lo,hi]=manifest.timeline.ambiguous_transition_interval;
  if(seconds>=lo&&seconds<=hi)return 'unknown';
  for(const b of manifest.timeline.observed_intervals)if(seconds>=b.start&&seconds<=b.end)return b.state;
  return 'unknown';
}
export function chooseState(manifest,{state,sourceTime}={}) {
  if(sourceTime!==undefined&&(typeof sourceTime!=='number'||!Number.isFinite(sourceTime)))throw new Error('sourceTime must be finite or omitted');
  const inferred=timelineState(manifest,sourceTime);
  if(state===undefined){if(inferred==='unknown')throw new Error('Unknown source-time state');return {state:inferred,selection:{mode:'observed_timeline',sourceTime,timelineResult:inferred,manualOverride:false}};}
  if(!Object.hasOwn(manifest.states,state))throw new Error('Unknown explicit layout state');
  return {state,selection:{mode:'explicit_manual',sourceTime,timelineResult:inferred,manualOverride:sourceTime!==undefined&&inferred!==state}};
}
function checkNodeContract(json,manifest,contract) {
  if(!Array.isArray(json.nodes)||json.nodes.length!==contract.expected_node_count)throw new Error('GLB node count mismatch');
  const names=targetNames(manifest);
  if(names.length!==contract.expected_target_count)throw new Error('Target count mismatch');
  for(const name of names){
    const index=manifest.glb_node_indices[name];
    if(!Number.isInteger(index)||contract.target_node_names[index]!==name||json.nodes[index]?.name!==name)
      throw new Error('Original GLB node index/name mismatch');
  }
  if(new Set(names.map(n=>manifest.glb_node_indices[n])).size!==names.length)throw new Error('Duplicate node index');
}
export async function loadVerifiedSharedGlb(loader,inputBytes,manifest,contract) {
  if(contract.glb_sha256!==manifest.shared_glb.sha256)throw new Error('Binding contract / manifest SHA mismatch');
  const bytes=inputBytes instanceof Uint8Array?new Uint8Array(inputBytes):new Uint8Array(inputBytes.slice(0));
  const hash=Array.from(new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
  if(hash!==manifest.shared_glb.sha256)throw new Error('Exact shared GLB SHA mismatch');
  if(bytes.length<20)throw new Error('Truncated GLB');
  const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
  if(view.getUint32(0,true)!==0x46546c67||view.getUint32(4,true)!==2||view.getUint32(8,true)!==bytes.length)throw new Error('Invalid GLB header');
  const length=view.getUint32(12,true);
  if(view.getUint32(16,true)!==0x4e4f534a||20+length>bytes.length)throw new Error('Invalid GLB JSON chunk');
  const json=JSON.parse(new TextDecoder().decode(bytes.subarray(20,20+length)));
  checkNodeContract(json,manifest,contract);
  if(!loader||typeof loader.parseAsync!=='function')throw new Error('A GLTFLoader-compatible parseAsync loader is required');
  // The loader receives exactly the bytes just hashed, never a separate URL or mutable asset.
  const gltf=await loader.parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
  if(!gltf.scene||!gltf.parser?.associations||!gltf.parser.json)throw new Error('Loader result lacks source associations');
  checkNodeContract(gltf.parser.json,manifest,contract);
  const binding=Object.freeze({scene:gltf.scene,gltf,verifiedAsset:Object.freeze({sha256:hash,nodeCount:json.nodes.length})});
  bindings.set(binding,{root:gltf.scene,gltf,hash,contract:structuredClone(contract),targetMap:JSON.stringify(manifest.glb_node_indices)});
  return binding;
}
export function applyLayout(binding,manifest,choice) {
  const data=bindings.get(binding);
  if(!data)throw new Error('A verified shared-GLB binding is required');
  if(data.hash!==manifest.shared_glb.sha256||data.targetMap!==JSON.stringify(manifest.glb_node_indices))throw new Error('Asset or target mapping changed after verification');
  if(data.gltf.scene!==data.root)throw new Error('Loaded scene was replaced');
  checkNodeContract(data.gltf.parser.json,manifest,data.contract);
  if(!Object.hasOwn(manifest.states,choice.state))throw new Error('Unknown explicit layout state');
  const names=targetNames(manifest);const indexToName=new Map(names.map(n=>[manifest.glb_node_indices[n],n]));
  const targets=new Map(names.map(n=>[n,[]]));
  data.root.traverse(node=>{const i=data.gltf.parser.associations.get(node)?.nodes;if(indexToName.has(i))targets.get(indexToName.get(i)).push(node);});
  if([...targets.values()].some(a=>a.length!==1))throw new Error('Missing or duplicate sofa/attachment associations');
  const visible=manifest.states[choice.state].sofas_visible;const changes=[];
  for(const name of names){const node=targets.get(name)[0];changes.push({name,gltfNodeIndex:manifest.glb_node_indices[name],runtimeName:node.name,before:node.visible,after:visible});node.visible=visible;}
  return {state:choice.state,selection:choice.selection,verifiedGlbSha256:data.hash,targetCount:names.length,changes,dynamicObjectsModified:false,assetDuplicated:false};
}
