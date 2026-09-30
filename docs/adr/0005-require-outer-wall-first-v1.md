# ADR-0005: Require outer-wall-first ordering for v1 injection

Status: Accepted
Date: 2026-09-30

## Context
Intermediate passes are emitted between structural layers. The upper structural layer still contains full-height inner walls/infill while the external wall is rewritten to a smaller remaining local height.

If Orca prints inner wall or infill before the rewritten outer wall, those full-height features may interact thermally/mechanically with the refined edge before the intended top external pass is established. This is not necessarily invalid, but it adds a major uncontrolled variable to the first physical proof.

## Decision
v1 physical injection requires:
- wall_sequence = outer wall / inner wall;
- infill-first disabled.

Intermediate passes are inserted before the upper structural layer, then the first relevant wall extrusion at the upper layer is the rewritten external wall.

Other wall sequences remain analysis-only until separately tested.

## Alternatives
- support all wall orders immediately: rejected for PoC isolation.
- reorder Orca G-code ourselves: rejected; too invasive.

## Safety/quality impact
Improves determinism and makes the refined exterior stack complete before coarse interior wall/infill execution.

## Test impact
Add gate tests and golden G-code fixture verifying expected wall/type order.

Supersedes: none.
