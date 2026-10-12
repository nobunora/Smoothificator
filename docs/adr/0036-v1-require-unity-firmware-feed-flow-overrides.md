# ADR-0036: Require unity firmware feed/flow overrides for printable v1

Status: Accepted
Date: 2026-10-08

## Context

Bambu/Orca start G-code commonly emits:
- M220 S100 — reset firmware feedrate override;
- M221 S100 — reset firmware flow override.

These firmware-side multipliers are distinct from slicer settings such as print_flow_ratio / filament_flow_ratio.

If custom G-code or another mechanism changes M220/M221 later, then:
- actual motion speed can differ from the plugin's resolved F/speed limits;
- actual extrusion can differ from the plugin's commanded E/material model.

The current v1 plan/execution model does not intentionally compensate for non-unity firmware multipliers.

## Decision

The G-code parser tracks supported M220/M221 semantics.

Printable v1 requires at every injection anchor:
- firmware feedrate override = 100%;
- firmware flow override = 100%.

These values must remain unity throughout every plugin-generated block.

A non-unity or unknown override at the anchor, or an unsupported override change inside the relevant chronological clearance/validation horizon, causes PluginResult.Skipped.

The plugin MUST NOT emit M220/M221 solely to force the file into a supported state and MUST NOT alter the user's firmware override policy in v1.

## Requirements / invariants introduced

- speed limits in the plan/execution model correspond to actual firmware feed scaling;
- commanded E/material assumptions correspond to actual firmware flow scaling;
- parser SavedMachineState includes firmware feed/flow override state for the supported dialect;
- final state restoration preserves the original unity override state without adding override commands.

## Test impact

Add:
- M220 S100 / M221 S100 accepted;
- M220 != 100 rejected;
- M221 != 100 rejected;
- unknown/malformed override rejected;
- custom override restored to 100 before anchor accepted only if parser proves actual anchor state is unity;
- downstream relevant override change rejected unless explicitly modeled by a future compatibility contract.

## Safety impact

High for actual speed/material parity.

## Supersedes

Any implication that slicer-level flow/speed settings alone determine actual machine execution.
