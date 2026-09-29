# Development Roadmap

## Phase 0 — specification
- preserve upstream Smoothificator
- ZAA-first residual-error architecture
- stock-Orca posContouring + psGCodePostProcess architecture
- immutable plan/preview/injection contract
- parser safety and all-or-nothing requirements

## Phase 0.5 — architecture skeleton and contract tests
Before algorithms:
- create package/module skeleton from ARCHITECTURE.md
- frozen domain dataclasses and typed errors
- settings validation boundary
- canonical plan serializer/hash
- import-boundary tests
- PlanStore interface tests
- no Orca/G-code implementation yet

Exit: dependency-boundary tests pass and later phases can implement behind stable interfaces.

## Phase 1 — standalone reference engine
Implement analytic/mesh error model, finite bead model, arbitrary multi-sub-edge optimization, deterministic SubEdgePlan and tests.

## Phase 2 — Stock Orca analyzer
Wheel/plugin:
- posContouring
- copy post-ZAA geometry
- compute residual error
- compute plan
- store deterministic immutable plan
- no G-code mutation yet

## Phase 3 — Plugin preview
UI-safe Script capability:
- post-ZAA reference
- sub-edge plan
- error heatmap
- metrics
- plan hash/status

## Phase 4 — Safe G-code parser/injector
- parser/state machine
- anchor/fingerprint validation
- extrusion conversion
- lower-Z-first emitter
- idempotent markers
- atomic all-or-nothing write
- golden fixtures

## Phase 5 — First stock-Orca printable PoC
Single-tool 0.4 mm PLA, simple outward slopes only. Compare planned path with emitted G-code and verify printer behavior.

## Phase 6 — Adaptive hybrid benchmark
Compare normal / fine layer / ZAA-only / ZAA+SubEdge on fixed-angle and smooth coupons. Measure error, roughness, time and material.

## Phase 7 — Calibration/generalization
Calibrate bead model/min spacing, expand supported Orca profiles/firmware dialects and geometry classes.

## Phase 8 — Production plugin
Pinned compatibility, wheel packaging, quality/tolerance UI, performance, regression corpus, safe analysis-only fallback.

## Optional future native integration
Only after plugin evidence justifies it, propose Orca native path-insertion/preview integration. It is not required for community testing or v1 printing.
