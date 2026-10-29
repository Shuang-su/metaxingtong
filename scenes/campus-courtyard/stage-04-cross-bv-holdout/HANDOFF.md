# Stage04 local handoff — earlier cross-BV camera diagnostic failed

Geometry base remains `87b37f98911f533605d5aebdd60756edb96fe951`. Source intake commit `006edc1`. Completed diagnostic content commit `a788ad15247638eecf2f3d48517c0cf120c6f27a`.

73 ordinary files were read back from the actual local commit/tree/blob with matching byte counts, SHA256 and Git blob SHA. No remote fetch/push or output Library save is claimed. Three original Stage03 model files remain byte-identical to the frozen commit. Detailed receipt: `qa/git_originals_readback.json`.

The new original source was successfully materialized and verified from Library. Output files remain local. No upload retry was made; previous prepared-upload HTTP401 failure remains outside this stage. No PR, push, public sharing, credential/security changes, installations or new ZIP.

Outcome: only six diagnostic cameras added. Geometry/material/light/visibility/old cameras verified after actual BLEND reload. None of the tested poses explains all fixed-object relations; no geometry was fitted to this frame. It is an earlier 2025-11-28 clip according to supplied provenance, not later-replay evidence. See `qa/REPORT.md` and `qa/independent_review.md` for limitations and next-stage proposal.

| File | Bytes | SHA256 | Git blob SHA |
|---|---:|---|---|
| frozen_model_diagnostic_cameras.blend | 3900811 | 7e4e345250f09f2e1dbe5c9653d2a90f83178cede954f38503ddbf09b62b12f4 | 43b4913781082accf41db8a687beef3c6a848c2b |
| renders/FORWARD_COURT_ORDER_F35.png | 4459972 | ae4f01d2dc3b4a2a9f6e85fb2cbc65a7ccd31407a748197d583a1abc4fef58ab | 2bf2f7eb3204bacc8b93752ce76f7e7f3bf51b91 |
| renders/REVERSE_TRACK_SIDE_F35.png | 4511023 | 236fc6d826738fd63a81f1d9021ef3298f749f2bd2becf57524de6c822fdd85a | 5607b8a5b116cd01d9651fa70acef3d8fa7b2be2 |
| comparisons/FORWARD_COURT_ORDER_F35_overlay50.png | 3293181 | a11c4d04e75e4f77c00fbbb4ca96fa68887c969ec686b7b4a599f881f71cae26 | 9c3973be427a8ff0c8758179c492cb0fed871070 |
| comparisons/REVERSE_TRACK_SIDE_F35_overlay50.png | 3350157 | 87cc62d3c61ba5e14239da2f4b8cab2ceda8b006dc156155397a3c5dc49230b6 | 6320aa2db9c72799aa5c1926393f22623e171017 |
| comparisons/HOLDOUT_source_render_overlay_contact_preview.jpg | 549569 | faf8e2f9177a5a5c9c980e3f37c4ad38fb8de012d3b3fda791429db2f638d41d | 942da29e88e80d7478f40862ef128a35e5c07a5d |
| comparisons/six_camera_trials_contact_preview.jpg | 390333 | ae3ae57a335e1294a1bb99a0c6c0a59e25c2b1c82d924312949286108815bfa5 | d4dd0e5bf2bc3f5c2226e124988e0c58ace51834 |

Display JPEG contact is 1920×792 (scaled preview), and six-camera sheet is 1920×1152 (scaled preview). Both below 900 KiB. Two individual render JPEGs are native 1920×1080 display copies; exact PNG originals/overlays remain unchanged. The normal presentation MAIN and eight inspection views remain Stage03 files, not replaced by these deliberately failed camera diagnostics.

Source identity and a later replay remain evidence gaps, not a pending software operation. Local diagnostics and verification completed; no render process remains active.
