# Indexed source-mesh topology prerequisite

Validated ADR-0030 / phase1b-mesh-topology.md was imported at fa63ab0 before
production edits. The implementation introduces immutable indexed mesh/topology
values and a bounded exact evaluator in domain/mesh_topology.py and
engine/mesh_topology.py. It preserves source IDs/coordinates, rejects invalid
elements and local winding, checks closed edges, connected faces and single-cycle
vertex links, and records exact signed volume with a non-mutating global reversal.

Positive volume is an orientation convention, not embeddedness or material-side
proof. Coincident nonlocal geometry, mesh self-intersection, inside/outside,
source-frame parity and actual Orca manifold evidence remain separate gates.
No Plan identity registration or printer authorization is introduced.

## Verification

Windows isolated Python 3.12.10, commands exited zero:

- `.venv/Scripts/python -m compileall -q adaptive_subedge tools tests`: PASS.
- `.venv/Scripts/python -m unittest discover -s tests/architecture -p 'test_*.py' -q`: 41 PASS.
- `.venv/Scripts/python -m unittest tests.unit.test_mesh_topology -v`: 17 PASS, authored/executed independently.
- `.venv/Scripts/python -m unittest discover -s tests -p 'test_*.py' -q`: 421 PASS.

Independent review found no actionable findings. Separate checks covered exact
tetrahedron volume, translation by 2**40, mirrored/global reversal, incidence,
local winding, malformed oversized tuple budget precedence and mid-scan
cancellation. The focused suite additionally covers a connected pinched vertex,
zero-volume closed topology, 1,024-face iterative traversal, subnormal/huge
coordinates and cancellation at every observed checkpoint. Cancellation never
publishes partial topology. Lint/type tooling remains NOT CONFIGURED.

Windows CI adds handoff integrity; archive build imports the new module from a
clean extraction. Exact committed build and CI receipts belong to Draft PR #8.
No screen capture, desktop input, physical printing, original G-code changes or
security changes were used. Unrelated untracked log_iotc.txt was preserved.

## Next dependency

Topology-aware sections will consume these canonical source vertex/edge IDs.
Sections, material-side checks, candidate paths and optimization are still needed
before the requested actual improvement preview and safe output can work.
The existing saved Orca coupon/export remain fixtures, not new runtime proof.
