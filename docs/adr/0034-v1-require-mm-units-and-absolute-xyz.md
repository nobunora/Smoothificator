# ADR-0034: Require millimeter units and absolute XYZ positioning for printable v1

Status: Accepted
Date: 2026-10-08

## Context

The G-code parser tracks G90/G91 and actual XYZ, but the printable-v1 contract did not explicitly require a coordinate mode/unit at the injection anchor.

Execution-frame translation and immutable plan serialization are expressed in machine millimeters. Emitting those coordinates while the machine is in relative XYZ mode, or after a G20 inches switch, would be unsafe unless the injector temporarily changes/restores those modes perfectly.

The initial Bambu/Orca fixture family normally uses millimeters and absolute XYZ, so supporting other modes in v1 adds complexity without research value.

## Decision

Printable v1 requires, at every injection anchor and throughout the plugin-emitted block:
- millimeter units (G21-equivalent semantics);
- absolute XYZ positioning (G90-equivalent semantics);
- relative E (M83), as already required.

The parser may understand/observe G20/G21 and G90/G91 for diagnostics, but:
- saved anchor state other than mm + absolute XYZ => Skipped;
- unsupported unit/mode transition inside the validated downstream-clearance horizon => Skipped unless the parser can prove and model it under a later compatibility contract.

The plugin MUST NOT switch G20/G21 or G90/G91 merely to make an otherwise unsupported file injectable in v1.

## Requirements / invariants introduced

- execution-frame translation is interpreted in mm absolute XYZ;
- ToolClearance and structural matching use one unit system;
- final emitted plan coordinates are never interpreted in relative XYZ mode.

## Test impact

Add:
- G21+G90 accepted fixture;
- G91 anchor rejected;
- G20 anchor rejected;
- temporary custom-code G91 that restores before anchor is acceptable only if actual saved anchor state is G90;
- mode/unit change inside relevant validation window either correctly parsed under the compatibility contract or rejected.

## Safety impact

High.

## Supersedes

Any implication that parser support for G90/G91 alone means printable v1 supports relative XYZ.
