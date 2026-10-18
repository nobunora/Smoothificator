# Right-half V5 calibration comparison: parent audit

The user requested candidate minimum thickness to follow the configured 0.01 mm minimum, final equivalent-flow width 0.02 mm editable in the plugin, unchanged 25–30 degree volume per length, and supplementation only on the right half instead of fixed 5 mm end exclusions. Accepted V5 scope is recorded in ADR-0071 and the existing nonlinear dimension taper handoff specification.

## Policy and geometry

Candidate table minimum exposed thickness and original numeric minimum height now derive from the saved minimum height. The separate root contact analysis tolerance remains unchanged; it is not the candidate thickness parameter. Original admission width 0.21 mm and derived maximum angle 33.95770549 degrees remain unchanged.

The baseline uses the printed V4 retention formula, reference minimum width 0.1 mm and minimum height 0.01 mm. At or below 30 degrees, width and height targets are identical to V4. Above 30 degrees, u=(angle-30)/(maximum_angle-30), with default R(u)=1-(6u^5-15u^4+10u^3), and width=R(u)*baseline_width+(1-R(u))*0.02. Height remains the baseline height. The reference width, final minimum width, tail start and tail expression are normal saved V5 plugin parameters. Both expressions use the existing bounded polynomial evaluator; no eval/exec. Historical V1–V4 encoded policies retain their semantics and hashes.

The six calibrated 25–30 degree paths retain prior nominal families and actual resolved width/height, independently checked. Their changed length necessarily changes total E. Ordinary E rounding changes E per unit length by at most approximately 0.05% in this artifact, within the independently derived half-E-tick bound. No E multiplier or artificial rescaling is introduced.

The model X midpoint is 96.4920309 mm. Common added centerline range is 96.718–111.267 mm, inset by the maximum bead radius 0.225 mm to keep the full modeled footprint in the right half and inside the outer model boundary. Original G-code on both halves remains unchanged. There is no fixed 5 mm end exclusion.

## Candidate and endpoint recovery

The new 0.01 mm table was computed within existing budgets. At two floors (2.4/2.6 mm), both new retained families and the independently rechecked old family failed full-span contact. An explicit original-family candidate union alone did not recover those rows, so the failure must not be attributed solely to finite-cache pruning.

The accepted bounded prefix extension keeps the start, Y, support plane, source set and contact tolerance fixed. It uses fresh whole-segment contact proofs on the 0.001 mm X lattice, with at most 16 cached probes per path, seeded from the actual old path endpoint. Incomplete/cancelled/resource-limited results abort rather than mean unsupported. Contact is the search predicate; ordinary extrusion and all other gates run after clipping. Valid endpoint and next invalid grid tick certify a maximal supported prefix within this fixed modeled domain, not a physical optimum.

The final artifact recovers all six roots at the two floors: four right endpoints clip to 111.069 mm (three paths) or 110.847 mm (one path), while two reach 111.267 mm. Each uses at most 14 contact calls. All 24 eligible floors remain, totaling 39 paths. The calibrated six paths are unchanged by clipping. Independent synthetic cases cover full validity, unsupported seed/start, adjacent maximality, incomplete failure and exact query-budget exhaustion.

## Artifact, tests and installation

Final file: `artifacts/gui-angle0to45-right-half-v5-v1/trial-right-half-v5-v3/angle-0to45-RIGHT-HALF-calibrated-tail.gcode.3mf`.

- Package SHA256: `491e8dbd83d72c8451235968d77ea042c2da14108016555e9a81a95ada485925`.
- Raw G-code SHA256: `43191336f024d8ca888e444537cd738696715340ef47a363b3b59b2151ee0625`.
- Saved V5 policy SHA256: `41d60ff8b62ae06788f3f91e26aba04468f124293f11761dc31a7a0af2ff7420`.
- Plugin 0.2.7 installed with prior 0.2.6 entry/settings backed up; unrelated entries preserved. Actual host storage API save/readback verified and exact exported settings consumed by artifact generation. No actual plugin UI save is claimed.
- Independent source review: 70 focused tests passed after explicitly pinning historical V4 test fixtures to V4. Architecture: 45 tests passed.
- Parent authoritative Python 3.12.10 full suite: 1,047 tests passed in 501.153 seconds, exit 0. Source/tests unchanged throughout; protected historical artifacts and log_iotc.txt unchanged. Receipt: `artifacts/gui-angle0to45-right-half-v5-v1/final-tests-v1/receipt.json`; log SHA256 `e85dcd62b7a99df2eaaec4f7c9cb7de63bed45143c1ba48bf5544b7f2ab1f0d2`.

Final actual-artifact replay and fresh tool/material geometry audits completed successfully. Tool audit: 2,883 motions, 887,448 pairs, 39 forming prefixes and zero known issues (71.797 seconds). Material geometry audit: 39 paths, 24 groups, 30,729 future linear pairs and 741 candidate pairs (128.109 seconds). Independent review replayed all 156 tool certificates, 60 real contact clipping queries and two future material certificates/four projection queries; owner pins and source restoration match, with no findings. Evidence: final trial directory `independent-artifact-review.UNVERIFIED.json`, `tool-pinned.UNVERIFIED.json` and `geometry-derived-axes.UNVERIFIED.json`.

Bambu Studio was launched with the final v3 package. Accessibility confirms the exact new filename in its loading dialog, blocked by the settings information dialog. The UI API cannot click OK (`coordinate input geometry is unavailable`); manual dismissal was requested. Completed visual preview is not yet claimed. The unused file chooser in the previous Studio window was closed without changing that project.

Intermediate 22-floor/33-path packages are diagnostic only and are not delivered. Physical reproduction of 0.01 mm height or 0.02 mm equivalent-flow width is not established by these computational checks. Four inherited unknown material obligations and opaque original tool scope remain outside whole-job proof. No printing, merge or release was performed.
