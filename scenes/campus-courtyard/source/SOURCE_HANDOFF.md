# Campus courtyard — native source handoff

Acquired 2026-10-29. Source https://www.bilibili.com/video/BV1GqXMByE1s/ ; 星瞳_Official; title 【直播回放】【3D】进来治臆症！2026年03月27日19点场. Upload UI 2026-03-27 23:31:38; duration 1:51:13. Real-time rendering versus prerecorded footage is unknown.

Four unmodified Chromium Save video frame as PNGs, not UI screenshots. All 1920×1080; media DOM currentTime below, paused=true and readyState=4 recorded at native export. Selected quality 1080P 高清; higher 1080P 高码率 entry marked 大会员. No entitlement change attempted. Source sharpening, chromatic aberration and motion blur retained. Every PNG opened locally, byte count and SHA256 validated. Shared paths `/workspace/shared/campus-source/<filename>`; Library IDs portable to child tasks.

## Valid references

1. `BV1GqXMByE1s_t3368.109825_native.png` — time 3368.109825; 4,118,719 bytes; SHA256 `74bdf120b0878582cb0a85b7e2934f768f1fa621d5fa389df5d73be7bd81f07f`; Library `libfile_c0cdef075f28819184fe5049fbcc983e`; file `file_00000000238481fbb2c8af5f01b84d7a`. Wide frontal paved plaza, large tree/raised planter, curved red running track, green field/goals, school facade, curved streetlights, bench and flowerbed. Character obscures center.
2. `BV1GqXMByE1s_t3356.842934_native.png` — time 3356.842934; 3,797,239 bytes; SHA256 `bb55737d1d0203f927c27080dec5aeb5d30c5a61f3b6532e97ccb771ebddf803`; Library `libfile_b3e8ee44bf588191b371613f0b854b66`; file `file_00000000f05c81fb92c20fde96183815`. Oblique right courtyard, tree planter, black-post basketball hoop, green court/red border, brown three-ball rack, facade doors/steps, rear net/bench/flowerbeds. Source character-arm blur retained.
3. `BV1GqXMByE1s_t3426.097342_native.png` — time 3426.097342; 3,474,895 bytes; SHA256 `725a026c7fd7a4001d3daa8e6327f4990549f742cb37fc31d1d311e7dbe1af62`; Library `libfile_0d5598ed61bc8191a197fb0a176b2f8d`; file `file_00000000464c81f5aeae90e6cb7957fe`. Side building direction: hoop left, window grid, door/steps, trees, brown metal exterior zigzag stair tower right. Large character occlusion.
4. `BV1GqXMByE1s_t3610.834976_native.png` — time 3610.834976; 3,632,159 bytes; SHA256 `d1a33a292223d8ce37fb6ba485d41e3275abe795044c6cbc329b48602b5c273e`; Library `libfile_205f2c4ceeb48191b33bd4ae0188fa7a`; file `file_00000000b50881f5abb42b5c04d2e8d1`. Near tree and character close view; simultaneously shows left curved track, central planter edge, right half-court markings/hoop, facade door/steps and distant hoop/net court/bench. Useful co-visible spatial anchors despite central occlusion.

## Scope and limits

Limited campus courtyard / sports-edge scene, not a complete measured basketball court. These views provide genuine changed spatial directions, not four duplicate timestamps. Whole perimeter, full court extents, hidden facades, exact dimensions and complete circulation remain unverified. Source worker reported continuous camera parallax around 3336–3345; that report is not an additional native reference. Do not infer hidden adjacency or full 360-degree coverage. Four valid files above are the acquisition deliverable.

## Supported native-download workflow and recovery

1. Read current CUA docs (`await cua.rewriteDocumentation()`). Bind an actual tab in current browser context. On takeover the old campus tab was visible to Sky but CUA listTabs returned empty and getTab failed Tab not found in browser 1. Its old UUID was not readable. Do not invent a tab binding.
2. Created own supported tab via `var ownedCourtTab=await cua.createBrowserTab("cdp","https://www.bilibili.com/video/BV1GqXMByE1s/?t=3345")`; returned tab 6. IMPORTANT: it opened in background. Activated its tab using Sky; verified foreground URL and rendered image matched ownedCourtTab. A background/foreground mismatch is an observed hazard; attributing the previous failure solely to this is inference, not established cause.
3. Use source UI to play/seek/pause. Read only DOM properties via `ownedCourtTab.playwright.evaluate(()=>Array.from(document.querySelectorAll("video")).map(v=>({time:v.currentTime,paused:v.paused,readyState:v.readyState,width:v.videoWidth,height:v.videoHeight})))`. Inspect settled screenshot after clicks; seek keys can resume. No JS seeking or network extraction.
4. Capture full Sky desktop; verify foreground tab. First right-click video opens Bili custom menu; second right-click elsewhere inside video outside that popup opens Chromium native VIDEO menu. Visually inspect Save video frame as (将视频帧另存为…), not Save video as. Coordinates are transient, not reusable without fresh screenshot.
5. In SAME CUA call, arm observer BEFORE menu action and await after action:

```js
var pending = ownedCourtTab.playwright.waitForEvent("download", {timeoutMs:20000})
  .then(d => d.path({timeoutMs:20000}))
  .catch(e => ({error:String(e)}));
await sky.move({x:352,y:560}); // observed Save frame row in this desktop only
await sky.press_key({key:"Return"});
nodeRepl.write(await pending);
```

6. This returned immediately readable native files for all four captures under `/opt/codex/downloads/45f173a7-5919-4c5c-996d-a15feb62cb29/`: respectively `9e2732c6-4f17-495e-b299-2f539253c7b9`, `a8e10c86-a2ee-4150-8df7-c0a679f729dc`, `63c02e05-5b74-4a64-af43-1f4ad864904b`, `d7c28410-3261-4765-9edb-e21c28946a28`. Record media state again; copy exact bytes, validate PNG/dimensions/hash and visually inspect actual image, then Library upload and returned xattrs. Do not guess download paths from UI UUIDs.
7. Earlier worker's UI-only completed 3.3 MB download UUID `624f694b-3926-4ff8-9af4-d5718f1f9cee` at 3345.774469 had timed-out observer and no readable bytes. It is NOT a validated asset, not counted among four, not an extra angle. The new first frame is a different actual timestamp, not a recovered copy of that missing file.

No certificate/access warning bypass, no credential reading or login change, no image alteration. Browser ownership released to parent after fourth export; tab 6 left paused at 3610.834976. No Git or model edits.
