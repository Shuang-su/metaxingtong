import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {timelineState, chooseState, applyLayout} from './layout_state_adapter.mjs';
const dir=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const m=JSON.parse(fs.readFileSync(path.join(dir,'layout_state_manifest.json')));
const workspace=process.argv[2];
const bytes=fs.readFileSync(path.join(workspace,m.shared_glb.workspace_relative_path));
const gltf=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
const nodes=gltf.nodes.map(node=>({...structuredClone(node),visible:true}));
const root={traverse(fn){nodes.forEach(fn);}};
const associations=new Map(nodes.map((node,index)=>[node,{nodes:index}]));
const geometryBefore=JSON.stringify(nodes.map(({visible,...other})=>other));
const original=JSON.stringify(nodes);
const runs=[];
for (const state of ['furnished','unfurnished','furnished']) {
 runs.push(applyLayout(root,m,chooseState(m,{state}),associations));
 assert.equal(JSON.stringify(nodes.map(({visible,...other})=>other)),geometryBefore);
 for(const node of nodes) if(!m.furnishing_group.objects.includes(node.name))assert.equal(node.visible,true);
}
assert.equal(JSON.stringify(nodes),original);
for(const time of [6626.597822,6626.8,6627.31912,6627.396357,0,2117,4529,7000,7135]) {
 assert.equal(timelineState(m,time),'unknown');assert.throws(()=>chooseState(m,{sourceTime:time}));
}
assert.equal(timelineState(m,6620),'furnished');assert.equal(timelineState(m,6630),'unfurnished');
assert.equal(timelineState(m,7119),'unfurnished');
for(const time of [NaN,Infinity,true,'6620'])assert.throws(()=>chooseState(m,{state:'furnished',sourceTime:time}));
assert.equal(chooseState(m,{state:'unfurnished',sourceTime:7000}).selection.manualOverride,true);
assert.throws(()=>applyLayout(root,m,{state:'01_front'},associations));
assert.equal(JSON.stringify(nodes),original);
// Rename runtime nodes to reproduce a loader that does not preserve original names.
for (const node of nodes) node.name=node.name.replace(/[.\[\]:/]/g,'');
const renamedBefore=JSON.stringify(nodes);
applyLayout(root,m,chooseState(m,{state:'unfurnished'}),associations);
applyLayout(root,m,chooseState(m,{state:'furnished'}),associations);
assert.equal(JSON.stringify(nodes),renamedBefore);
assert.throws(()=>applyLayout(root,m,chooseState(m,{state:'unfurnished'})));
assert.equal(JSON.stringify(nodes),renamedBefore);
const incomplete=new Map(associations);incomplete.delete(nodes[m.glb_node_indices[m.furnishing_group.objects[0]]]);
assert.throws(()=>applyLayout(root,m,chooseState(m,{state:'unfurnished'}),incomplete));
assert.equal(JSON.stringify(nodes),renamedBefore);
const result={passed:true,runtimeRenamedNodesPass:true,missingAssociationNonmutating:true,source:'Actual shared GLB node JSON; mock traversal tests only, not a browser-render test',nodeCount:nodes.length,geometryMaterialsTransformsUnchanged:true,nonSofaVisibilityUnchanged:true,roundtripRestoresOriginal:true,closedUnknownIntervalTested:true,invalidTimesRejected:true,switches:runs};
fs.writeFileSync(path.join(dir,'qa/glb_consumer_adapter_tests.json'),JSON.stringify(result,null,2)+'\n');console.log('ADAPTER_TEST_PASS',nodes.length);
