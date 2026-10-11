import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {timelineState,chooseState,loadVerifiedSharedGlb,applyLayout} from './layout_state_adapter.mjs';
const dir=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const m=JSON.parse(fs.readFileSync(path.join(dir,'layout_state_manifest.json')));
const contract=JSON.parse(fs.readFileSync(path.join(dir,'glb_binding_contract.json')));
const bytes=fs.readFileSync(path.join(process.argv[2],m.shared_glb.workspace_relative_path));
let parses=0;let nodes;
const loader={async parseAsync(buffer){parses++;const b=Buffer.from(buffer);assert.deepEqual(b,bytes);const json=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)).toString());nodes=json.nodes.map((n,i)=>({...structuredClone(n),name:'runtime_renamed_'+i,visible:i%3!==0}));const associations=new Map(nodes.map((n,i)=>[n,{nodes:i}]));return {scene:{traverse(fn){nodes.forEach(fn);}},parser:{json,associations}};}};
const binding=await loadVerifiedSharedGlb(loader,bytes,m,contract);assert.equal(parses,1);
const original=structuredClone(nodes);const targets=new Set(Object.values(m.glb_node_indices));const runs=[];
const geometry=()=>JSON.stringify(nodes.map(({visible,...rest})=>rest));const geometryBefore=geometry();
let furnishedSnapshot;
for(const state of ['furnished','unfurnished','furnished']){runs.push(applyLayout(binding,m,chooseState(m,{state})));if(runs.length===1)furnishedSnapshot=structuredClone(nodes);assert.equal(geometry(),geometryBefore);for(let i=0;i<nodes.length;i++)assert.equal(nodes[i].visible,targets.has(i)?state==='furnished':original[i].visible);}
assert.deepEqual(nodes,furnishedSnapshot);
// Explicit restoration of captured target values proves adapter does not alter any non-target state.
for(const i of targets)nodes[i].visible=original[i].visible;assert.deepEqual(nodes,original);
const failureTests=[];
async function expectPreflightFailure(label,alteredBytes,manifest=m,c=contract){const count=parses;await assert.rejects(()=>loadVerifiedSharedGlb(loader,alteredBytes,manifest,c));assert.equal(parses,count);assert.deepEqual(nodes,original);failureTests.push(label);}
const changed=Buffer.from(bytes);changed[changed.length-1]^=1;await expectPreflightFailure('replaced_or_modified_glb_bytes',changed);
await expectPreflightFailure('incorrect_expected_node_count',bytes,m,{...contract,expected_node_count:373});
const wrongName=structuredClone(contract);wrongName.target_node_names[m.glb_node_indices[m.furnishing_group.objects[0]]]='NOT_THE_SOFA';await expectPreflightFailure('original_node_name_mismatch',bytes,m,wrongName);
await expectPreflightFailure('binding_manifest_SHA_mismatch',bytes,m,{...contract,glb_sha256:'0'.repeat(64)});
assert.throws(()=>applyLayout({scene:binding.scene},m,chooseState(m,{state:'unfurnished'})));failureTests.push('unverified_forged_binding');
const changedManifest=structuredClone(m);changedManifest.shared_glb.sha256='0'.repeat(64);assert.throws(()=>applyLayout(binding,changedManifest,chooseState(m,{state:'unfurnished'})));failureTests.push('asset_changed_after_binding');
const index=m.glb_node_indices[m.furnishing_group.objects[0]];const n=binding.gltf.parser.json.nodes[index];const oldName=n.name;n.name='WRONG_LOADED_NODE';assert.throws(()=>applyLayout(binding,m,chooseState(m,{state:'unfurnished'})));n.name=oldName;failureTests.push('loaded_parser_name_changed');
const obj=nodes[index];const assoc=binding.gltf.parser.associations.get(obj);binding.gltf.parser.associations.delete(obj);assert.throws(()=>applyLayout(binding,m,chooseState(m,{state:'unfurnished'})));binding.gltf.parser.associations.set(obj,assoc);failureTests.push('missing_node_association');assert.deepEqual(nodes,original);
const other=nodes[0];const oldOther=binding.gltf.parser.associations.get(other);binding.gltf.parser.associations.set(other,{nodes:index});assert.throws(()=>applyLayout(binding,m,chooseState(m,{state:'unfurnished'})));binding.gltf.parser.associations.set(other,oldOther);failureTests.push('duplicate_target_association');
const popped=binding.gltf.parser.json.nodes.pop();assert.throws(()=>applyLayout(binding,m,chooseState(m,{state:'unfurnished'})));binding.gltf.parser.json.nodes.push(popped);failureTests.push('loaded_parser_node_count_changed');assert.deepEqual(nodes,original);
for(const time of [6626.597822,6626.8,6627.31912,6627.396357,0,2117,4529,7000,7135]){assert.equal(timelineState(m,time),'unknown');assert.throws(()=>chooseState(m,{sourceTime:time}));}
assert.equal(timelineState(m,6620),'furnished');assert.equal(timelineState(m,6630),'unfurnished');assert.equal(timelineState(m,7119),'unfurnished');
for(const t of [NaN,Infinity,true,'6620'])assert.throws(()=>chooseState(m,{state:'furnished',sourceTime:t}));
const result={passed:true,verification:'Exact actual GLB bytes hashed with Web Crypto; actual JSON parsed by mock loader receiving those same bytes. Not a real browser/GLTFLoader render test.',verifiedGlbSha256:binding.verifiedAsset.sha256,nodeCount:nodes.length,targetCount:targets.size,runtimeRenamingSafe:true,furnishedStateRoundtripRestored:true,mixedNonTargetVisibilityPreserved:true,geometryMaterialsTransformsUnchanged:true,failureTests,failuresAreNonmutating:true,switches:runs};
fs.writeFileSync(path.join(dir,'qa/glb_consumer_adapter_tests.json'),JSON.stringify(result,null,2)+'\n');console.log('VERIFIED_ADAPTER_PASS',nodes.length,targets.size,failureTests);
