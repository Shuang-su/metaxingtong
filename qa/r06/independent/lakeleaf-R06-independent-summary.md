# Leafboat R06 independent technical review

Independent Blender4.3.2 one-thread read-only checks of frozen R06 files. Production commit reported86eb68f2d48683da5b1d13f1f16e543d173bb423; exact checked file hashes below are controlling evidence.

Material and white each have2704 mesh objects and13 cameras. Evaluated world geometry matches exactly between material/white, as do cameras and lights. Every one of the1370 preexisting R05 evaluated mesh hashes is unchanged;1334 new finite west-bank instances were added. No conclusion of a closed complete lake follows from adding a finite bank sector.

Both material and white GLBs were actually imported. All2704 mesh node names and13 cameras retained, with zero missing/extra mesh names. Largest bidirectional nearest world vertex difference1.573e-5 model units, occurring in transformed west-bank instances; this is export precision, not measured world accuracy. glTF uses1370 unique mesh payloads with multiple nodes, not2704 unique geometry payloads. White original assignments use only WHITE_R06_DiagnosticOnly.

Original mesh inspection: zero zero-area faces and zero hidden objects.518 meshes have open/nonmanifold edges, including modeled thin foliage, water and finite shoreline surfaces. Therefore do not claim the entire scene is watertight. Main leaf shell is closed/positive under the performed mesh test. These checks do not prove all-object intersections/contact-free geometry, finite-radius vein margin, physical buoyancy or source fidelity.

Raw GLB camera limitation independently reproduced: top source camera frame-ray-slope disagreement0.01841862 due to off-axis shift loss. Other twelve cameras differ only at floating-point precision (<2.7e-8). Opening the actual sidecar-restored GLB check blend yields zero camera-frame disagreement for all13, with matrix errors<2.4e-7. Thus camera restoration works, but standalone raw GLB does not retain that top projection. Raw imported material scene has one light; original AREA/world lighting is not represented fully. No cross-engine render equivalence claim.

Texture/dependency check: three GLB embedded images (leaf albedo, water normal, lake color) are byte-identical to corresponding external PNGs. Roughness is repacked from grayscale into glTF metallic-roughness RGB: G equals original gray exactly; R/B are255 and metallicFactor0. All required texture-coordinate attributes, including water normal TEXCOORD_1, exist. Four original image dependencies are relative external files and are NOT packed in blend; include the textures directory with original models. They are procedural appearance hypotheses, not source photographs or recovered lake depth.

Final R06 image suite/source geometry acceptance remains pending at this report time. Earlier R04 actual source views failed leaf curvature/tip, forest-instance, shoreline and water appearance, with severely missing rear shoreline. R06 finite bank addition is not accepted merely by passing file checks. R05 vein repair removed a spike, but does not itself validate source shape. Exact source-object identities, later replay and complete hidden structures remain unverified.

Exact hashes:
- lakeleaf-r06-material.blend: 4af868869ee7f7eebf0c8569b16cef356143c5425c888e98a4f56dee25449a12
- lakeleaf-r06-white.blend: 0c3a7d8d3addd27a81a38600686fec7b7fa6320a13fa7182947e20aaa4fc1086
- lakeleaf-r06.glb: 2eff1ebd1e9b3d96dc3788a6f0c3c75e082b8ab126d4c6cd0b84575be81b4fa7
- lakeleaf-r06-white.glb: 8806f40bc9e0dce7103fdecf4e5eb2f05393fc1341af20f1d80ac3baf4a68b19

Evidence: lakeleaf-R06-independent-technical.json, lakeleaf-R06-white-camera-check.json, lakeleaf-R06-texture-check.json. No production model or Git state modified.
