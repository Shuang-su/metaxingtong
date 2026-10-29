# Cross-BV holdout diagnostic — geometry frozen

2026-10-29 correspondence correction: the original four frames support a high-confidence near-hoop / three-ball rack / doorway-steps / exterior-stair chain. The earlier frame lacks co-visible rack, same doorway and large round tree planter bridging that chain; its foreground hoop cannot uniquely be assigned to the original near hoop. No unambiguous 2025/2026 instance match is established. “Reverse view” is only a pending hypothesis; existing FORWARD/REVERSE camera labels are experiment names. See `qa/correspondence_correction_2026-10-29.md`. Keep the candidate frozen and do not automatically add cameras or renders pending the parent's full relation table.

Base: `87b37f98911f533605d5aebdd60756edb96fe951`, stage-03-contact-qa. This stage may add diagnostic cameras only. Mesh coordinates/topology, material nodes/assignments/texture pixels, lighting, existing cameras and object visibility must remain unchanged. All original files are retained.

New original: BV1fwSEBqEPJ, 96.994858 s, 1920×1080, 3,352,659 bytes. The materialized PNG was decoded, SHA256 verified and visually inspected. Acquisition provenance is the complete parent-supplied CROSS_REPLAY_CHECK.md, preserved unchanged. The local worker did not itself watch this clip.

This is an earlier, unofficial 2025-11-28 episode slice according to the supplied description. It is not a later replay and does not establish identical assets, real-time rendering or hospital connectivity. Dynamic people, captions, heart overlays and watermark remain in the original and are excluded from hard-anchor measurements. Tree planter identity is unresolved.

Completed: six camera-only hypotheses; two native 1920×1080 source/render/direct-50%-overlay groups; six native crop groups for each; failed numeric and rendered trials; saved/reopened frozen-state verification; independent read-only pixel review. None of the tested hypotheses passes. See `qa/REPORT.md` for four fixed-object groups, conflicts and limits; `comparisons/HOLDOUT_source_render_overlay_contact_preview.jpg` for a reduced display preview. Any future geometry edit must start a separate stage and re-run all four base source views plus this view, explicitly giving up this frame's held-out status.

Local only. No push, PR or Library upload attempted in this stage.
