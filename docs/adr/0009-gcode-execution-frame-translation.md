# ADR-0009: Derive and validate print-space to G-code-space translation at injection

Status: Accepted
Date: 2026-09-30

## Context
The geometry analyzer operates in Orca PrintObject / print-space coordinates.

Orca GCode.cpp does not emit those XY values verbatim:
- GCode::point_to_gcode() adds the current instance origin (`m_origin`) and subtracts extruder XY offset.
- `m_origin` is set from the selected PrintInstance `shift`.
- structural machine Z is emitted as `print_z + z_offset`.
- ZAA point offsets are then added to that nominal machine Z.

Therefore a SubEdgePlan expressed in print-space mm cannot safely be emitted directly as machine G-code coordinates.

v1 has exactly one printable instance and one tool, so within the target print the mapping is expected to be a constant translation after all model rotation/scale has already been applied in sliced path geometry.

## Decision
Keep all domain/preview geometry in **print-space mm**.

At psGCodePostProcess, the PlanMatcher MUST derive a validated execution-frame translation:

Gx = Px + dx
Gy = Py + dy
Gz = Pz + dz

where:
- P is plan print-space coordinate;
- G is final G-code machine coordinate;
- dx/dy include PrintInstance origin and active-extruder offset effects;
- dz includes printer z_offset and any validated constant machine-Z offset.

The translation is inferred from existing Orca-generated structural geometry and layer boundaries in the final G-code, not guessed from profile defaults.

## Validation
Before injection:
1. match the planned baseline structural outer path/layer to final G-code;
2. derive dx/dy from multiple corresponding XY points/segments;
3. derive dz from structural layer Z tags/motion versus Layer.print_z;
4. require the inferred translation to be constant within configured tolerance across all sampled anchors;
5. reject if correspondence is ambiguous or translation is inconsistent.

No rotation, scale, shear, or non-constant mapping is accepted in v1.

## Emission
Only the G-code adapter applies the validated translation.

The domain/engine/preview MUST never store or work in machine G-code coordinates.

The safe-ceiling Z in ADR-0007 is a **machine-coordinate Z**, computed after applying the validated dz.

## Alternatives considered
- Read instance shift/extruder offset and recreate Orca point_to_gcode in the analyzer: rejected for v1 because it duplicates more Orca export semantics and may miss profile/runtime offsets.
- Assume Bambu offsets are zero: rejected as unsafe.
- Store plan directly in G-code coordinates: rejected because it couples geometry optimization to one export instance/profile.

## Safety impact
Critical positive impact. Prevents otherwise plausible XY/Z coordinate-offset printing errors.

## Compatibility impact
v1 remains one-instance/one-tool. Multi-instance/tool support requires a mapping per execution context and a future ADR.

## Test impact
Add:
- translated object fixture;
- non-zero extruder-offset synthetic fixture or parser-level mapping fixture;
- non-zero z_offset fixture;
- constant-translation acceptance;
- inconsistent/ambiguous transform rejection;
- emitter test proving Plan coordinates are unchanged and only G-code adapter applies transform.

Supersedes: none.
