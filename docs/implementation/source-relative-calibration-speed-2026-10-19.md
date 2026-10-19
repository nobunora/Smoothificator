# Source-relative calibration speed — parent verification

Date2026-10-19. Authority: latest user speed instruction, accepted ADR0073 amendment,
SPEC_VALIDATED `../specs/source-relative-calibration-speed.md`. Branch remains
codex/calibration-matrix-library; prior uncommitted work is preserved.
Independent research/source review validated before separate native and UI owners
implemented. No new dependency or general printing-gate relaxation.

Native policy3 is a separate exact type; policy2/data identity and old prepared
outputs remain reproducible. Reference is reconstructed inside native code as
min(saved outer wall, actual base-top positive outer-wall command feed, conservative
saved machine X/Y limits). Actual source wall lines3367..3370 are F12000, saved
outer200mm/s and machine XY200, yielding200mm/s. New ratio columns.2/.4/.6/.8/1
emit40/80/120/160/200mm/s. F floors to.001mm/min, never rounds up. Actual maximum
sample flow.240047131mm3/s is below source cap21. Quantities are commanded feeds;
a10mm path does not guarantee the target speed is reached.

The parent independently checked all100 actual cells against separately stated
conditions:25 new feeds/ratios/reference speeds, unchanged E/XYZ and fixed values,
end/start treatment, source prefix/suffix and V1 raw identity. Independent reviewer
additionally rebuilt the new raw exactly, checked source/state/archive and503775
nominal pairs. Other3 cases remain byte-identical across all assets, not only raw.
No material finding remained. Detailed ownership tests: native35, architecture45;
UI30 focused/architecture; reviewer21 nearest.

Final ready-v6 bundle:
`a1f237a0a6f0c239955d5f925c2b9e481d9bde707f36fcf39b3d2403209b2599`.
Volume-speed raw:
`b2f00cde23101b1c7bf08c30e6f7df0f81f16a2bf70e42b4415ec53e745a18c4`.
Wheel0.3.1:
`1130b7e004a18f225a84935d6384636638dc4587ce34c70c31220a327d2d8e1e`.
Parent verified RECORD, package sources, locked bundle, isolated wheel-only imports,
all4 exact exports and selection reopen. Old absolute and new ratio requests were
independently replayed. Source guard, no-model capability and existing export
boundaries remain unchanged.

Browser review used the actual new page and bundle with a stub host bridge:
20..100percent columns, all25 E/commanded-speed cells, separate200reference and
omitted irrelevant fixed20 were visibly confirmed and screenshot reviewed.
Actual native Orca invocation/installation is not claimed. The user additionally
asked about accurate width/pitch preview: response explained true-coordinate
10mm lines/12mm pitch are straightforward, whereas measured bead width requires
calibration and must not be equated to volume divided by nozzle clearance.
No width/pitch rendering behavior was changed by this speed task.

Parent evidence: `artifacts/source-relative-speed-matrix-v1/` holds independent
commands, wheel and browser receipts and32 historical protected pins. The full
suite runs only after source/tests freeze; final result is appended below.
No G-code is submitted and no commit/push/merge is requested here.


Final full regression: 1111 tests PASS in 435.109s,
exit0. Source/test hashes remained unchanged and all32 protected historical files
remained byte-identical. LogSHA256 `8081fbdd1be4677c3db95d021cd09f1f14db18cf0aa91a0807192d4295c5bbf2`; receipt at
`artifacts/source-relative-speed-matrix-v1/full-regression-v1/receipt.json`.
`git diff --check` is the final whitespace check. Lint/type tools remain
NOT CONFIGURED; no additional dependencies were installed.
