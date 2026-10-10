XINGTONG CASTLE GARDEN ENTRANCE — editable reference-based reconstruction

Source: https://www.bilibili.com/video/BV1aw411T7ws/
Primary garden frames: 00:21:59 and 00:25:11. Secondary frames: 00:11:06, 00:15:06, 00:20:09, 00:26:39, 00:27:43, 00:28:41. The supplied evidence manifest records the capture history; excluded_stale images were never used.

Deliverables
01: White clay BLEND + GLB.
02: Textured self-contained GLB.
03: Textured BLEND with packed PBR images, external PNG textures and editable scripts.
04: Normal wide/oblique renders, camera-matched renders, 50% overlays, source references and QA.

What is supported
A straight purple-dark paved axis; paired dense flowerbeds with low pale stone edges; balustrades and urns; nearby climbing-rose uprights; a farther flower-covered arch with a small center dip; purple-gray masonry facade; pointed dark double door; tall cyan windows with dominant dark vertical divisions. Meshes model the visible scene rather than displaying source frames on image planes. The livestream character and UI are not reconstructed.

What remains approximate
This is a scene reconstruction from compressed livestream images, not recovered production assets or a photogrammetric scan. Relative dimensions and camera solutions are approximate. Ornamental door panels, urn profiles, individual flowers, exact masonry/paving patterns and fine surface appearance are simplified procedural interpretations. Visible window vertical divisions are retained; unsupported repeated diamond lattice was removed. Dense planting is represented by editable petal and leaf surfaces, grouped into material batches. Some fine plant surfaces are two-sided, zero-thickness sheets. Matching camera views preserve the same world model; lighting differences and the occluding character limit direct comparison.

Explicitly omitted / inferred
The building roof, upper silhouette, complete castle footprint, hidden garden perimeter, reverse view, surrounding landscape, interior and hall connection are not observed and are not invented. The facade is a finite visible patch. The thin support slab, unseen backs, clipping edges and metric scale are construction conveniences. Wide and oblique views intentionally reveal those limits.

Version improvements
V1 to V2: compressed excessive garden depth, increased facade/door presence, corrected flower arch center sag, aligned foreground bed ends, and oriented climbing leaves and roses toward the viewer.
V2 to V3: corrected world-scale masonry UVs; added dark marbled and bordered paving; muted excessive blue/white flower brightness; removed unsupported diamond leading; increased floral density. Final overlay fit widened path and far arch and adjusted matched camera framing. Comparison files retain honest residual differences.

Textures / interoperability
Procedurally generated basecolor, roughness and normal PNG sets: violet masonry, aged limestone, purple paving, dark wood, cyan glass and foliage. Other flower/stem materials use explicit PBR color constants. No livestream frames were baked into textures. BLEND has packed textures; GLB embeds them. White and textured variants use identical geometry, UVs and cameras; only surface materials/light settings differ. Open the BLEND normally in Blender or import the GLB into a glTF-compatible editor. Units are arbitrary metre-scaled working proportions, not surveyed measurements.

QA
qa/roundtrip_validation.json records source meshes, imported GLB geometry, embedded texture checks and coordinate tolerances. qa/variant_uv_validation.json verifies native geometry and UV identity. Standard overview cameras show the complete reconstructed patch. Overlays are diagnostic 50/50 blends, not an assertion of pixel-perfect correspondence.

Lighting note
Final matching views use a darker nighttime setup and low-emission blue glazing. Normal textured overview renders receive a 1.5x area-light boost solely for legibility. White-clay versions use neutral inspection lighting. These are rendering differences, not geometric differences.
