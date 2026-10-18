# ADR-0070: Export empirical supplemental-material settings from the research UI

Status: Accepted
Date: 2026-10-18

## Context

The user requests configurable supplemental material correction, linearly decreasing from100 percent at zero angle to50 percent at the configured admission maximum, together with doubled supplemental retraction/wipe. The existing `smoothificator_preview` Script capability is a separate unscored chord preview, and its wheel does not contain the tools-owned native trial emitter. ADR-0068/0069 prohibit silently turning this capability into an original-file injector.

The parent task adjudicated the bounded experimental specification in `docs/specs/supplemental-empirical-material-correction-research.md`. This decision adds a settings-export bridge; it does not grant print execution or establish a calibrated physical bead model.

## Decision

Extend the existing pinned Script UI with a separate panel labeled `補完試験出力用設定`. It loads and saves validated policy JSON exclusively under plugin-owned storage and displays effective settings. It must preserve the existing chord preview behavior. It neither reads original G-code nor injects, slices, uploads, sends, or automatically opens a file. Existing window-generation/lifecycle guards apply to settings operations.

A pure immutable domain DTO owns structural and range validation. Pure engine arithmetic owns derived admission angle and interpolation. A pure application codec owns strict JSON, derived-field verification, canonical serialization and fingerprint, composing domain and engine without a domain-to-engine dependency. A preview adapter owns filesystem persistence. The UI may import these pure package modules; neither UI nor engine/domain imports the tools-owned native emitter. `tools/build_preview_plugin.py` continues to package the preview and pure application/domain/engine code without bundling tools. No canonical printable Settings or saved printer/filament/process preset is mutated.

The tools-owned native trial builder explicitly consumes the saved policy, verifies its fingerprint, and records the exact effective policy in emission provenance. It rejects admission height/minimum-width disagreement with its pinned table. It cannot claim UI settings were applied without a matching consumed policy identity. Policy export is not native runtime/UI validation; actual UI read-back and generated-artifact consumption must be verified separately.

## Material semantics

The policy exposes start/end percentages with `0 < end <= start <= 100`, default100/50; nominal layer height and minimum width used for the admission endpoint; and supplemental retract/wipe settings default1.6/1.0 mm. The maximum angle is derived from the configured conservative short-base admission rule, `degrees(atan(H/(sqrt(2)*minimum_width)))`, not from the coupon maximum or largest selected path. The endpoint is approximately33.95770549 degrees for H=.2/minwidth=.21.

Quantize actual section angle and derived maximum to decimal degrees with8 places, round-half-even, using one pure owner. Clamp their ratio to0..1 and interpolate percentages using exact Fraction arithmetic. Round only the final corrected deposition E to the established command lattice. Persist exact factor representation and angle strings for replay.

The opt-in native adapter scales only positive moving supplemental deposition E. Original source commands, source debt/unretraction, retraction/wipe E, debt reconciliation, E resets, nominal XYZ/width/height, admission and geometry optimization remain unchanged. M220/M221 stay unity as required by ADR-0036. The original full-volume design freeze remains reference provenance; corrected emitted-volume/state/rate checks are separate. Nominal width bounds must not be relabeled as actual E-implied physical-width guarantees after correction. Corrected material shape, contact and coverage are explicitly uncalibrated; nominal geometry certificates are reference-model evidence only.

Retraction doubles only the supplemental cycle total from.8 to1.6 mm and requested reverse wipe from.5 to1.0 mm, retaining staged fraction/speed caps, segment clipping and reconciliation to the original source debt. Its changed travel requires fresh motion verification.

## Consequences and verification

This is a scoped extension to ADR-0068/0069's UI responsibility. All unrelated restrictions remain. It adds no native injector to the plugin and no physical-print authority. Tests must cover strict policy input/ranges/identity, exact formula boundaries, storage roundtrip and lifecycle, package dependency boundaries, builder policy consumption, unchanged nominal geometry/source recovery, corrected positive E only, and exact physical state restoration. Actual pinned Orca UI read-back and actual Studio artifact loading are separate evidence gates.


## Accepted amendment: corrected-volume minimum-thickness gate

The later user request changes the new-policy default endpoint from50 to25 percent and explicitly authorizes supplemental path removal after volume correction. This supersedes this ADR's earlier unchanged-admission statement for the new opt-in policy only. Historical explicit50-percent policies remain unchanged. Schema v2 explicitly includes identity-bound minimum modeled thickness (current pinned trial.08mm); v1 compatibility preserves historical values and no-filter behavior, while new filtered trial generation requires an explicit v2 policy.

The pure engine compares final rounded corrected E-derived geometric area `E*pi*d²/(4*L*M)` against same frozen nominal-width stadium area `w*h_min-(1-pi/4)*h_min²`, with exact units mm³/mm and saved slicer multiplier M. It does not approximate corrected thickness as nominal height times factor. Threshold must equal the pinned plan minimum height. Rational pi enclosure and sign-aware comparison admit only proven greater-or-equal area, with no positive under-threshold tolerance. Unresolved or unsupported numerical inputs fail closed. Original full-volume design freeze remains separate reference provenance.

Filter before final supported-graph freeze, cascade removal through parent references, omit empty groups, preserve original source state/order and define an original-preserving all-empty outcome. Recompute identities/spans/package and fresh motion proof for the survivor set. These modeled thickness results remain empirical same-width proxies, not measured physical shape/contact evidence. Detailed bounded contract and source review are in the accepted amendment to `docs/specs/supplemental-empirical-material-correction-research.md`.

Post-filter removal can reduce coverage and error improvement. Original table objective/epsilon certificates remain provenance for the pre-filter selection only; the subset is not a new optimum and filtered union/error is diagnostic. Existing root-contact, spill and motion hard gates remain required for survivors. No geometry reoptimization is added.
