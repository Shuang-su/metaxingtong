# Candidate novelty review — 2026-11-03

Result: the proposed city-window-bedroom-stage is visually distinct from the existing bedroom (#8), and from four other potentially confusable interior/night/bar scenes sampled below. This is not a claim that every frame of every archived scene was inspected.

Candidate pixels inspected: /workspace/shared/20261103-source/cityroom-native-1352.177747.png (1920×1080, source BV1ic12BMEk6). Visible identifiers: gold nested-arch bed headboard at left, enormous curtained city-night window with curved surrounding opening, red rounded bar at right, white hourglass stool centrally.

## Existing bedroom #8
Actual native source frame inspected through the GitHub connector, not inferred from the issue title:
https://github.com/Shuang-su/metaxingtong/blob/c34616238a0a9d1846ab07b8025ba07bdd4cd503/scenes/bedroom/verification/native-hd-source-recapture-20261011/frames/bedroom-headboard-BV1mx4y1z7oY-t3018.693709-native.png
Visible identifiers: continuous vertical padded white headboard, black-and-white checkered pillows/bedding, beige rectangular wall mouldings, large red cartoon picture, right white bedside cabinet and orange mushroom lamp. These are structurally different from the candidate, not merely altered lighting or camera position.
The old empty-wide PNG is over 1 MiB; fetch_file returned empty content and fetch_blob failed UTF-8 decoding. Its pixels were NOT inspected. The smaller 877,394-byte headboard native PNG was fetched as base64 and actually viewed.

## Other actual reference pixels inspected
- Issue #6: Neon dance studio: purple PERFECT pillars, dance-arrow floor and exposed lit ceiling; not the candidate.
https://github.com/Shuang-su/metaxingtong/blob/e88b6f2563b8240f24ba6c43e19a4098866f93f9/scenes%2Fdance-studio%2F01-retain-earliest-binaries%2Ffiles%2FXingtong_Dance_Studio_Neon_3D--0e5ea27297d7%2Freferences%2FReference_A_crop.jpg
- Issue #9: KTV: metallic blue rounded seats, star cushion and large red balloon-dog against city skyline; not the candidate.
https://github.com/Shuang-su/metaxingtong/blob/c594bb05bb97e46755be1bc0697a8298706276a3/scenes%2Fktv%2F01-retain-earliest-binaries%2Ffiles%2F04_KTV_Views_and_QA--d765f32402e5%2Freferences%2Fframe_2117_crop.png
- Issue #10: Seaside bar: sea horizon, wooden counter, books and bottles; not the candidate's red curved bar/bedroom.
https://github.com/Shuang-su/metaxingtong/blob/c1fd29d5e1e2a6e4ba7df3019329de809bf4ab03/scenes%2Fseaside-bar%2F02-retain-complete-geometry%2Ffiles%2F04_Seaside_Bar_PBR_and_QA--9aeb9f449ce0%2Freferences%2Fbar_22min_before_exact_crop.png
- Issue #16: Dark-cell: floor-to-ceiling black bars and bare dark enclosure; not the candidate.
https://github.com/Shuang-su/metaxingtong/blob/8bf040f5874748412c5a59ddabe4da81d2b2b84e/scenes%2Fdark-cell%2F01-retain-first-verifiable-release%2Ffiles%2F02_%E6%9A%97%E8%89%B2%E9%93%81%E6%A0%8F%E5%B8%83%E6%99%AF_%E6%9D%A5%E6%BA%90%E4%B8%8E%E4%B8%AD%E6%96%87%E6%A0%B8%E9%AA%8C--7bd7ce771c88%2Freferences%2Fbars_932s52.png

## Scope and limitations
Reviewed producer preflight issue inventory covering original 16 scenes plus later candidates. The five image comparisons above address nearest semantic confusion risks; other listed outdoor/vehicle/campus/arcade/festival scenes were not each re-downloaded pixel-by-pixel in this review. No repo, issue, branch, or source pixels were modified. This novelty finding does not establish geometric reconstruction quality, camera matching, later-replay same-scene validation, or user acceptance.
