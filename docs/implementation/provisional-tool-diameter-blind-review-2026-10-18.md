# Provisional tool diameter — independent blind review, 2026-10-18

## Independence and result

Read docs/specs/provisional-tool-diameter-review.md before implementation inspection and checked consistency with canonical SPECIFICATION27/29/30. After ready notification, independently inspected tools/provisional_tool_geometry.py, tools/review_supplemental_hops.py, tests/unit/test_provisional_tool_geometry.py, both actual diameter JSON reports and generation-receipt.json. No parent/research/implementation findings consulted for this stage. No code/test edits, artifact overwrite, slicing, printer operations or subagents; only this report written.

No actionable material defect identified within this tools-only planar-disc diagnostic contract. No physical/complete-head/clearance authority is established.

## Coverage and invariants

- ProvisionalPlanarTip is frozen and accepts only exact positive Fraction diameter. Default0.4 derives radius0.2, not0.4. Nonexact floats/strings/bools, nonfinite float inputs and zero/negative inputs reject. Fraction normalization ensures mathematically equivalent rationals have identical geometry identity. Explicit model/version participates in the deterministic identity.
- Segment sweep bounds use both actual endpoints, expand X/Y by the radius, and retain endpoint min/max Z without fabricated axial height or uncertainty margin. Pure Z, oblique/negative XY and exact touching extents are directly tested.
- Full polyline envelopes union every consecutive sweep, retaining interior extrema, point count, geometry identity and all path IDs. Closed rings remain complete; the AABB is explicitly a broad-phase envelope, not internal ring clearance.
- Hop review quantizes path XY/Z and bridge start/end with the existing XYZ3 quantizer. Three legs correspond to raise, ceiling XY and descent commands. Diameter is numerically consumed by these54 leg bounds and30 full-path bounds, while command strings, ordering, source identities, extrusion intent and profile Z-hop remain invariant.
- Review identity combines source/project/manifest hashes, geometry identity, review version and XYZ/E precision. Saved nozzle diameter is separate, with assumption mismatch diagnostic and explicit note that it is a different quantity. The assumption neither rewrites saved settings nor impersonates a physical ToolClearanceProfile.
- CLI exposes --assumed-tool-diameter-mm through exact Fraction parsing and the same validation. Output flags printable_authorized, physical_print_authorized, complete_head_verified and tool_clearance_verified stay false. No obstacle query or hidden measured/head-height evidence is claimed; source insertion anchors and entry/exit remain unverified.

## Executed evidence

Exact repository Python3.12.10, verified earlier in this independent session.

`.\.venv\Scripts\python.exe -m unittest tests.unit.test_provisional_tool_geometry -v` → exit0, all5 tests pass (0.014 seconds). Includes default/alternate/equivalent diameter, frozen state, invalid inputs, pure-Z and oblique bounds, complete-polyline interior extreme, quantized command agreement, source preservation and all authority flags.

Additional read-only `@' ... '@ | .\.venv\Scripts\python.exe -` → exit0:

- Regenerated both0.4/0.6 actual reports in memory through review_hops and compared complete JSON structures to saved artifacts: exact agreement.
- Independently invoked both real CLI commands with stdout capture only and compared complete output to saved artifacts: exact agreement; no file output was written.
- Reconstructed endpoint updates from every bridge command's XYZ words and verified all54 leg start/end coordinates equal the diagnostic endpoints; independently recomputed their exact min/max±radius bounds.
- Verified increasing diameter0.4→0.6 expands X/Y bounds by exactly0.1 per side, for every bridge leg and all30 path envelopes, with Z unchanged.
- Verified path IDs, quantized-centerline hashes, bridge commands, batch order and safe Z remain unchanged; all source/project/manifest before/after receipt hashes match current inputs.
- Verified both recorded review identities reproduce and differ:0.4=`e499fe0103aece9b3c54ca696d5381f6d3d5c542f6487a40acd51bbedb6fe2a3`;0.6=`736cf55503ac05e172d4bad1d00c90aac55becfa605ba4776dae7097f91deadc`.

## Residuals

A planar tip-disc AABB is deliberately incomplete whole-head geometry. It cannot establish internal ring clearance, obstacle contact, axial hotend clearance, physical printer support, downstream safety or real insertion-anchor eligibility. The report is associated with the original research source/project, not the separate restored manufacturer's baseline; that association is preserved explicitly. Existing hop-review ring construction/manifest validation and original fixed-height limitations are unchanged and are not recast as executable approval. A deterministic review hash is a review artifact identity, not canonical PlanStore or print certification. Parent owns full regression/architecture gates beyond these focused checks. No findings require disposition; no production or physical convergence declared.

## Reconciled default-owner finding — independent fix check, 2026-10-18

After the first blind report was complete, parent supplied its Low default-ownership finding: repeated literal0.4 defaults could drift. Reviewed the ready shared-default delta: DEFAULT_ASSUMED_TOOL_DIAMETER_MM is now the single immutable Fraction owner in provisional_tool_geometry.py, reused by model, API and CLI; help derives its displayed default from that constant. No geometry/command/identity algorithm change identified. Finding disposition: confirmed, fixed, independently verified.

`.\.venv\Scripts\python.exe -m unittest tests.unit.test_provisional_tool_geometry -q` → exit0, all5 cases pass (0.013 seconds), exact repository Python3.12.10. Additional independent read-only API/subprocess CLI probes exited0: omitted-diameter API and CLI equal the stored0.4 report completely; explicit0.4 and0.6 API/CLI outputs equal their respective existing artifacts completely. CLI --help reports default0.4 from the shared owner. Actual geometry, command bytes represented in JSON, source hashes and review identities remain unchanged. No artifact overwrite or printer operation occurred; previous negative-review coverage and physical/runtime limitations remain valid. No new material defect found.
