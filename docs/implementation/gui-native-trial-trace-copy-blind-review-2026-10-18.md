# GUI native-trial trace/copy independent blind review — 2026-10-18

Initial disposition: **one Medium finding, NTC-1**. This is a separate pure-owner scope from the preceding packaging review. No parent trace/copy findings were supplied. Reviewed the complete frozen trace/copy owners and direct tests against `docs/specs/gui-native-paired-trial-review.md`, its required native-arc/context research and targeted existing arithmetic/profile/formatting/graph contracts. No source/test edit, GUI, network or printer operation.

Frozen manifest `artifacts/gui-angle0to30-trial-v1/native-pure-freeze-v1.json`: trace `e54b5d6a7c5a6e9bab6ed1676b30b23d25af86dcfa51f90e65f62a14a520e896`; copy `2942da498303aa8741056da8e21630548976c25f8d5ec0715ec90ce76e286fd5`; tests `f4e7d42a13e5f1b17fee5c0adceafcabf16fe03ef82bba541abbe48f2e85e423` / `7376a202b9fdad620ca88305a99ab78ee351d63726b8708452c9625f70137e51`. All four hashes match after the probes. New GUI re-slice identities are not silently substituted for this frozen review.

## NTC-1 — Medium — Anchor admission omits later stationary source deposition

Location: `tools/gui_native_trial_copy.py`, `compose_native_trial_copy`, the `future` positive-material comprehension and following original-floor completion check.

The compositor considers a future positive command only when it is an arc or changesXY. An original stationary positive-E command with known deposited material is excluded. Thus it can admit an insertion before original material is still deposited on that same source layer, contrary to the explicit anchor-after-every-original-deposition requirement. Vertical-only positive deposition is excluded by the same predicate.

Concrete independently executed counterexample uses the freshly pinned supported fixture `recipe_fixture(reset_after=b'G1 E1.0 F1800\nG1 E-.8 F1800\n')`. Its selected insertion is after the first retraction and before these added commands. Fresh trace proves line69 deposits exactly1/5mm filament at unchanged XYZ(2,2,3), the original floor. Later moving material is atZ3.2. `rebuild_native_trial_copy` nevertheless succeeds because the same-floor stationary deposit is missing from `future`; output SHA `20b60300cb881a85ffb819e1a37a9bab80b5553b6928c398fbc048ec9abed79f`. Context/project/source/graph identities are freshly rebuilt by the fixture; no source file was modified.

Invariant: an anchor must follow **all** original deposition on its source layer; a positive material event cannot be silently classified as irrelevant because it lacksXY extent. This finding concerns the admission/state boundary, not a claim to have modeled a stationary blob. Whole-job/physical flags remaining false limits severity but does not make the anchor condition true.

Remediation direction: include every known-positive deposited-material event in completion/chronology admission and reject unknown material placement that cannot be discharged. Distinguish zero-deposition ordinary unretract from true stationary/vertical deposition using the fresh debt ledger; do not invent geometry or a blob radius. Add the specific same-floor stationary counterexample and a vertical-only case. Confidence high; disposition pending reconciliation.

## Checks and negative coverage

Command `.\.venv\Scripts\python.exe -m unittest tests.unit.test_gui_native_trial_trace tests.unit.test_gui_native_trial_copy -v` — PASS,10 tests,.189 seconds, Python3.12.10. These execute the new opt-in branch/arc/state/counter/M204 paths, not just legacy regression.

Independent branch probe separately interpreted skip and execute paths for a conditional XYZ/F/G92 sequence, checked that every retained joined field agrees with both paths or is unknown, and confirmed subsequent unconditional XYZ/F/M204 reconvergence. Physical debt remains0.8 despite conditional logicalG92. The interpreter bounds byte/event/branch/archive/numeric inputs, rejects unknown commands/unsupported words/absoluteE and records raw opaque/arc provenance. Exact source/project/producer hashes and typed immutable context fields are validated before interpretation.

Arc endpoint state reuses explicit linear relative-E arithmetic only for endpoint/counter/debt effects. Geometry is a separately retained full-circle XY envelope with outward rational radius covering both rounded endpoint radii, full min/maxZ and handedness/P1. It never marks an arc as straight support. Firmware/IJ/rounding and hidden OEM effects remain unresolved premises; this report does not promote nominal disk bounds to measured firmware trajectories.

Copy entry rebuilds its actual native trace, validates top-level known physical state and plane, saved source-owned motion/flow policy, floor/next-layer and source-floor wall feed caps. Unknown/excessive jerk rejects. The opted-in acceleration wrapper uses saved outer cap and restores the exact inherited value; already eligible anchors need no wrapper. Replayed wrappers/one-path blocks preserve physical XYZ/F/debt/modes and acceleration, remove only the exact declared zero-adapter G92, and prove net relative-E equal to frozen extrusion. Legacy exact-counter owners were not changed.

Symbolic counter alternatives track executed original G92 reset versus skipped branches. Tests verify an unconditional reset yields zero translation, a conditional reset retains both zero and supplemental translation, and unknown initial numeric logicalE is not fabricated as a known source counter. The private zero-counter formatting adapter is explicit and is not a firmware-state claim.

Fresh graph reconstruction rejects stale/forged ordering/geometry; root/child world-Z ordering and local support identities remain separate from original-floor semantics. Formatted E/F parity, safe ceiling, output/block/path/insertion limits, source-byte recovery and annotation comment-only behavior are exercised. Annotation generated-comment admission is currently applied per one-path formatting block, with total output additionally bounded by copy limits; whole-copy aggregate comment-budget semantics were not established here.

The copy explicitly declares source/candidate geometry requires a separate audit. This pure review does not certify actual roots, all arc/stationary material exclusions, continuous contact, intended/unrelated material or causal tool clearance, CAD diagnostics, GUI delivery, the subsequent re-slice, or physical printing. The packaging findings remain independently applicable until reconciled. No second material pure-owner defect established within this bounded review; all owner authority flags remain false.

## NTC-1 and derived arc-budget correction verification

Frozen v2 trace/copy hashes `ddf8130903a28d71d3a0f9b01f41835adf6a53c92324e58244f82d13d785bccf` / `83d3942e03c6b08e3433ec875fb17d518fe7e40fda92ae3efa450c21264facee`, tests `944336589b139903aa9d754852312745008afdd033d3cb06f3293b4eff4cb750` / `bb64c340f636398c428b9c8f69083b37bff5dfba48e1e3c70a9176fc37ac9983`, verified against the freeze manifest after probes.

The original stationary1/5mm deposition counterexample now rejects, as does a vertical-only positive-deposition variant. Fresh unknown future deposited material rejects; known positive events are checked using both before/afterZ, so a layer-crossing event cannot be hidden by its ending plane. Ordinary zero-deposition unretraction remains distinct. Disposition: **NTC-1 confirmed, fixed and independently verified**.

Implementation's separate derived-arc bit-budget correction was also inspected: center, squared radius, turns, outward radius and all bound coordinates now receive exact bit-limit validation. New focused regression passes. The combined30-test command recorded in the package follow-up passes, including12 trace/copy tests. No additional material fix-delta defect established. Actual source/material resolver, new GUI slice and trial printing remain separate stages.
