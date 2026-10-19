# Prepared calibration matrix library

Status: SPEC_VALIDATED; independent repository review validated ADR0073 and this bounded contract on 2026-10-19.
Date: 2026-10-19. Authority: latest user request, ADR0072/0073. Canonical base revision f620b1ef5df2bf4a7ea883bd359a63936d7c465a; this task adds the explicitly scoped Script-library exception to the canonical summaries. Branch:codex/calibration-matrix-library.

## Exact finite trials

Reuse the original genuine0.8mm-flat-base/one0.2mm-number-layer64mm source from ADR0072. Each case contains25numbered10mm lines, no reslicing and no omitted cells. Preserve V1 rawSHAeba3727f0c32d05ad4d03f681c06c46ae376232b16087c4589be822a5c5154f3, historical reference packages, saved settings and log_iotc.txt.

| ID | Rows | Columns |
| --- | --- | --- |
| h_volume | clearance .010/.015/.020/.030/.040mm | final-volume/length .000075/.000150/.000300/.000600/.001200mm3/mm |
| retract_wipe | end retract .4/.7/1.0/1.3/1.6mm | reverse wipe .25/.5/1.0/1.5/2.0mm |
| startup_extra_speed | first2mm EXTRA filament E 0/.00005/.00010/.00015/.00020mm | initial debt-recovery speed6/12/18/24/30mm/s |
| volume_speed | final-volume/length .000075/.000150/.000300/.000600/.001200mm3/mm | drawing speed5/10/20/30/40mm/s |

Except each case's two axes, fix h=.020mm, final-volume/length=.000300mm3/mm, drawing speed20mm/s, end retract1.6mm/wipe1mm, end retraction speed30mm/s, start debt-recovery speed30mm/s, and ceiling debt reconciliation speed30mm/s. These are `provisional_not_selected`, not an inferred user winner. Source profile caps remain mandatory and no clipping may silently change the finite axes. Ordinary source/hop/known-state and numeric limits remain. Add a distinct versioned experiment representation without reinterpreting V1.

For startup_extra_speed, round the baseline total10mm E once, round the baseline first2mm E, assign the remainder to8mm so zero extra retains the total baseline dose, then add exactly the configured extra E to the first2mm XY command. No stationary positive deposition is permitted. Report requested/actual startup quantity and rounding error separately; the existing whole10mm2% baseline tolerance does not imply a2% per-segment tolerance at very small E. Check emitted E/F/rate caps per segment. Vary only the initial saved-debt recovery speed; return/ceiling debt reconciliation stays fixed30mm/s. Central baseline region and fixed end handling must remain unchanged.

All cases use the exact original source and post-label anchor, current nominal.45x.2 sample envelopes, scoped current forming/wipe/vertical-retreat experimental premise, Zhop, source restoration and inherited opaque OEM limitations of ADR0072. Run fresh bounded actual numeric/state/source/archive/nominal-motion audits for each new case. Assert only the quantity varied by an axis; metadata display width.45 does not claim an actual physical width.

## Offline owner and assets

Provide a repeatable offline preparation entrypoint using immutable inputs (actual source G-code, genuine saved source archive, producer/runtime identity and geometry-only baseline settings project). Prepare all four rawG-code outputs with their frozen manifests, decimal conditions CSVs, labeled overview PNGs and optional sliced3MF archives. Primary delivery is always `.gcode`. Emit a closed portable resource catalog and per-file hashes/source/profile/policy identities. Include the geometry-only original configured source3MF for baseline settings, not an ordinary-source sliced3MF disguised as a no-G-code project.

Coordinate a closed manifest schema between offline and plugin owners. Asset roles: raw_gcode, conditions_csv, plot_png, frozen_manifest_json required per case; source_project_3mf required and must contain no `.gcode`; optional gcode_3mf. Include25 unique numbered cells and exact axes/units, fixed settings/baseline_status, request_sha256=null for initial prepared cases, source/policy/raw identities and exact required profile-key hashes. Reject duplicates/path escapes/symlinks/unknown roles/cases or fields, oversized/unbounded content, stale or forged hashes, mismatched raw/CSV/frozen-case identities, malformed finite inputs and any missing required assets. No host credentials or live configuration values may enter UI status/logs; expected macro hashes only, not raw macro values.

Current-config guard uses exact original source CONFIG_BLOCK opt_serialize strings for a finite explicit allowlist of available machine/material/bed/frame/temperatures/flow/retraction/speeds/caps/fan/pressure/sequence and macro keys. Source-header absent optional overrides stay explicitly unverified rather than guessed. Required keys are frozen in the validated manifest and are not arbitrarily selected by a UI caller. Exact host opt_serialize format is the contract; unknown or nonstring values reject, no numeric/whitespace normalization to force a match. The guard's scope must be visible; these are prebuilt FROZEN-profile cases, not newly generated from current presets.

## Plugin and distribution

Add a dedicated Script capability named for calibration matrices, with no active-model/NumPy-copy precondition. Preserve existing preview behavior and runtime pin. UI selects the four families, shows5x5 numbered conditions and row/column units, fixed provisional values and commanded E/dose. Explain constant nominal viewer width and unknown actual deposited width. Validate all prepared resource hashes and current required-config hashes immediately before exporting exact bytes to a new directory under plugin.storage. Reject path/symlink escapes, overwrite/alias, cancellation/stale window/epoch and output read-back mismatch. Do not auto-open other applications or print.

Allow geometry-only baseline-project export independently of current mismatch. When raw export is unavailable, give a clear missing-data/mismatch reason and baseline settings route; never pretend files were generated. Show actual directG-code path and condition-table path after export. The plugin must not import tools or mutate G-code; no unverified live slicing capability, subprocess or arbitrary path API.

Persist selection (case+cell01..25+symptom) with source/policy/trial IDs; no forced winner. Persist next-range PROPOSAL request only, with a clearly separate status from a generated prepared trial. For interior selection, transform clearance linearly and positive volume logarithmically; define bounds at adjacent midpoints, then use [lo,(lo+s)/2,s,(s+hi)/2,hi], keeping the selected point for nonuniform axes. At boundary, propose bounded expansion rather than wrongly narrowing; zero-startup-E axes use a linear coordinate. Quantize only by a stated request rule, reject duplicate/unrepresentable grids and require offline revalidation before any new output. Symptom routing may suggest end/start/speed stages; do not silently apply these suggestions to ordinary print settings.

Build version0.3.0 with explicit optional `--calibration-bundle` input; validate locked resources before wheel construction and include their hashes in provenance/RECORD. Default unbundled wheel must still build/import and clearly report no prepared data, with no fake working export. The delivered wheel includes all four validated cases. Bundle assets are generated local artifacts, not automatically committed user model/profile data.

## Verification and ownership

Emission owner: finite experiment policy/formatter, offline preparation CLI, case assets and frozen bundle. UI owner: resource/host-config adapters, dedicated Script/UI lifecycle, selection/request persistence, wheel builder/version and their tests. Parent: ADR/canonical documentation and architecture ADR inventory; no conflicting edits. Independent reviewer checks both boundaries, numeric/state restoration, bundle identity/export/cancellation and honest statuses. Test typed/zero/nonfinite/duplicate/unknown/modified inputs, exact legacy V1 bytes, per-cell caps and unchanged axis invariants, guarded baseline/raw export, no model requirement, same prepared resource bytes, missing bundle, escaped UI values and stale window requests. Run focused checks/architecture first, final complete suite after core freeze, and build/read back the actual calibration wheel. Browser tests are UI evidence only; actual Orca menu invocation must be attempted where the current Windows API permits, and any limitation reported accurately. No printing or merge/release is requested by this task.

Refinement requests use closed per-axis decimal quantization: .001mm clearance,
retraction and wipe; .000001mm3/mm volume; .00001mm extra E; .001mm/s speed.
Use Decimal precision50 and ROUND_HALF_EVEN, preserve the selected point, and
respect the validated stage caps. Requests are proposals, not prepared outputs.

Independent-review adjudication: at an approved endpoint, a narrowed inward grid
must not be presented as range expansion. Save the selected cell and an explicit
`offline_range_expansion_review_required` request. If a finer grid cannot preserve
five distinct values on the stated lattice, save
`resolution_limit_offline_range_review_required` instead of invented axes.
Neither status produces G-code or changes approved bounds.
