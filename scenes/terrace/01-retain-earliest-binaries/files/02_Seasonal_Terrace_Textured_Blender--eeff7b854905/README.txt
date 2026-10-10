XINGTONG SEASONAL ROOFTOP TERRACE — autumn reconstruction v1

Source: https://www.bilibili.com/video/BV1g64y1P7VV/
Livestream replay: 你和我的季节限定, January 19 2024.
Primary front reference 29:46; unobstructed floor 31:57;
independent low-oblique geometry/pergola confirmation 45:27.

Open models/Xingtong_Seasonal_Terrace_Textured.blend or White.blend in Blender 4.3+.
GLB versions are portable mesh + material exports. Cameras/lights stay in BLEND.
10 editable collections distinguish deck/gravel, fence, suspended chair, autumn
tree, easel, feature wall, moon/table, arch, generic distant backdrop and cameras.
All visible assets are mesh geometry, including chair ribs/chain, tree branches,
individual lobed leaves, gravel, pergola, boards, and arch opening. No screenshot
billboards or character cutouts. White and textured versions share the same mesh
geometry. UV PBR albedo/roughness/normal texture PNGs are supplied and packed.

What is inferred or simplified:
- Relative proportions from low-resolution video; absolute metre scale is assumed.
- This is the visible terrace zone, not an entire apartment or whole roof.
- No hidden home interior, unseen opposite boundary, or full roof perimeter.
- The arch is open; its thickness/reverse closures are approximated.
- Tree branching/leaf placement, wicker weave, plants and moon markings are
  procedural approximations, not exact original assets. Plants are simplified.
- Easel canvas artwork is left blank because it cannot be reconstructed reliably.
- Distant city masses are explicitly labelled generic approximations, editable in
  their own collection. They are not surveyed skyline reconstruction.
- Source character, UI, subtitles, foreground occluders and moving effects omitted.
- Winter (10:55) and green-season (1:33:06) share the same terrace architecture;
  their trees/snowmen/gifts/balloons are alternate dressing, not extra spaces.
  This release models autumn only. Variant references are included as evidence.
- Primary camera is manually fitted, not calibrated. Comparison overlays expose
  remaining discrepancies; no claim of pixel-exact or survey-grade reconstruction.

Review: renders/Final_*_Wide_clean.png = clean level wide view;
Final_*_Oblique_clean.png = normal oblique geometry view;
qa/Reference_White_Textured.jpg and qa/Final_Overlay.png = same-camera comparison.
qa/Iteration_Comparison.jpg documents the sparse initial blockout, pergola/tree
proportion correction, dense canopy refinement and final source camera/light pass.
Final wide-view QA also repaired deck extent and pergola support/chain connections.
qa/roundtrip_validation.json records native and GLB geometry comparisons.

Reproducible scripts: textures.py, build.py, refine.py, polish.py, finalize.py,
validate_roundtrip.py, denoise.py, package.py. Renders use Cycles; clean previews
use Open Image Denoise as image postprocessing, with raw PNGs retained separately.
