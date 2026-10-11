// Adapter for an already loaded Three.js-compatible graph. It does not load or duplicate assets.
// Only sofa node.visible changes. Camera, geometry, materials, transforms, dynamic objects stay untouched.
export function timelineState(manifest, seconds) {
  if (typeof seconds !== 'number' || !Number.isFinite(seconds)) return 'unknown';
  const [lo, hi] = manifest.timeline.ambiguous_transition_interval;
  if (seconds >= lo && seconds <= hi) return 'unknown';
  for (const band of manifest.timeline.observed_intervals)
    if (seconds >= band.start && seconds <= band.end) return band.state;
  return 'unknown';
}
export function chooseState(manifest, {state, sourceTime} = {}) {
  if (sourceTime !== undefined && (typeof sourceTime !== 'number' || !Number.isFinite(sourceTime)))
    throw new Error('sourceTime must be a finite number or omitted');
  const inferred = timelineState(manifest, sourceTime);
  if (state === undefined) {
    if (inferred === 'unknown') throw new Error('Unknown source-time state; explicit manual diagnostic state required');
    return {state: inferred, selection: {mode: 'observed_timeline', sourceTime, timelineResult: inferred, manualOverride: false}};
  }
  if (!Object.hasOwn(manifest.states, state)) throw new Error('Unknown explicit layout state');
  return {state, selection: {mode: 'explicit_manual', sourceTime, timelineResult: inferred,
    manualOverride: sourceTime !== undefined && inferred !== state}};
}
export function applyLayout(root, manifest, choice, associations) {
  if (!Object.hasOwn(manifest.states, choice.state)) throw new Error('Unknown explicit layout state');
  const names = manifest.furnishing_group.objects;
  if (new Set(names).size !== names.length || names.length !== manifest.furnishing_group.expected_count)
    throw new Error('Invalid furnishing allowlist');
  const dynamic = new Set(manifest.dynamic_groups.flatMap(group => group.objects));
  if (names.some(name => dynamic.has(name))) throw new Error('Dynamic/furnishing overlap');
  // GLTFLoader can sanitize/deduplicate Object3D names. Resolve by original node index,
  // using gltf.parser.associations, never by the mutable/sanitized runtime display name.
  if (!associations || typeof associations.get !== 'function') throw new Error('GLTF node associations required');
  const indices = names.map(name => manifest.glb_node_indices[name]);
  if (indices.some(index => !Number.isInteger(index) || index < 0) || new Set(indices).size !== names.length)
    throw new Error('Invalid glTF node-index mapping');
  const indexToName = new Map(names.map(name => [manifest.glb_node_indices[name], name]));
  const nodes = new Map(names.map(name => [name, []]));
  root.traverse(node => {
    const index = associations.get(node)?.nodes;
    if (indexToName.has(index)) nodes.get(indexToName.get(index)).push(node);
  });
  // Validate complete and unambiguous targets before mutating any node.
  if ([...nodes.values()].some(list => list.length !== 1)) throw new Error('Missing or duplicate sofa node associations');
  const visible = manifest.states[choice.state].sofas_visible;
  const changes = [];
  for (const name of names) {
    const node = nodes.get(name)[0];
    changes.push({name, gltfNodeIndex: manifest.glb_node_indices[name], runtimeName: node.name, before: node.visible, after: visible});
    node.visible = visible;
  }
  return {state: choice.state, selection: choice.selection, targetCount: names.length,
    changes, dynamicObjectsModified: false, assetDuplicated: false};
}
