# ADR-0010: Match Orca filament flow ratio when converting candidate volume to E

Status: Superseded by ADR-0015
Date: 2026-09-30

## Context
Adaptive Sub-Edge candidate geometry is planned in volumetric units (mm3_per_mm).

A naive G-code emitter could convert volume to filament length as:

E = volume / filament_cross_section

Orca does not do only that.

Source audit of Extruder.cpp shows:
- m_e_per_mm3 = filament_flow_ratio / filament_crossection

and G-code extrusion uses the path volumetric flow multiplied by this conversion.

Ignoring filament_flow_ratio would make injected SubEdge extrusion disagree with surrounding Orca-generated extrusion whenever flow ratio is not exactly 1.0.

## Decision
v1 candidate extrusion conversion MUST match Orca's single-filament conversion:

filament_area = pi * filament_diameter^2 / 4

E_per_mm3 = filament_flow_ratio / filament_area

For a candidate segment of length L and volumetric line flow q:

E = L * q * E_per_mm3

filament_diameter and filament_flow_ratio used for the active v1 filament MUST be captured in immutable snapshot/plan execution metadata and validated against final G-code/profile fingerprints.

## Scope
This ADR covers the v1 single-tool / single-filament Bambu profile family.

Mixed filaments, per-variant dynamic mapping, tool changes, and pressure/flow features requiring a different config index remain unsupported.

## Alternatives considered
- Assume flow ratio 1.0: rejected.
- Infer E multiplier only from neighboring G-code: useful as a cross-check but rejected as the primary definition because it can be affected by ZAA/local compensation or other feature-specific flow logic.

## Safety impact
Prevents systematic under/over extrusion of injected candidate paths when user/profile flow ratio differs from 1.0.

## Test impact
Add:
- flow_ratio=1.0 reference;
- non-unity flow ratio reference;
- parity test against Orca Extruder::e_per_mm3() behavior;
- plan/profile mismatch rejection when filament flow ratio changes after planning.

Supersedes: none.


Supersession note: ADR-0015 retains the requirement to account for filament_flow_ratio but replaces this incomplete standalone formula with Orca's complete v1 external-wall flow-modifier chain.
