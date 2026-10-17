# Exact planar-cell top coverage: implementation result

Disposition: bounded research primitive PASS. This is not a certified
exposed band, candidate-path score, Orca same-plan comparison, Plan or
printability claim.

Authority: `docs/specs/phase1b-planar-cell-top-coverage-draft.md` at spec
commit `3366162` (`SPEC_VALIDATED`), accepted ADR-0005/0030/0059. Independent
read-only repository review against MAIN `c2110d5` returned `validated`.
The existing two-height section difference supplies no continuous surface
proof, so this API validates the mesh afresh and proves only the supplied
convex XY cell's highest upward-facing surface is one plane.

The domain receipt admits only exact Fraction coordinates/area and a closed
state/reason matrix. The engine checks strict convexity, self-intersection,
orientation and topology, selects the highest upward plane at the cell's
interior centroid, then clips each oriented facet once against the closed
vertical prism. Any facet above that plane, including boundary-only contact,
rejects. Exact coplanar upward-facet area must cover the whole cell. Resource
and cancellation exits publish no partial plane. No external dependency,
settings default, Orca callback or G-code path changed.

Independent implementation review requested valid closed-manifold fixtures
for a recessed pocket and a higher feature touching only the cell boundary.
Both were added and return `uncovered-top` and `above-top-plane` respectively.
It also requested a degenerate prism-clip bound test; the tested vertical and
corner contacts stay within the specified `k+3` vertex bound. Final reviewer
found no remaining material blocker. This is bounded test evidence, not a
formal proof for arbitrary future geometry.

Validation on Windows with `.venv/Scripts/python.exe` (Python 3.12.10):

- `-m compileall -q adaptive_subedge tests tools`: PASS.
- Architecture/import-boundary suite: 43 PASS.
- Planar-cell and section-difference focused suite: 21 PASS.
- Full `unittest discover -s tests -p test_*.py -q`: 593 PASS.
- Lint/type analyzers: NOT CONFIGURED; no dependency was added.

Package/source build evidence is recorded after the exact commit. Remaining:
the caller-supplied cell is not proven to originate from an exposed model
band. A separate specification must close interval nesting, finite-bead
candidate footprints and same-domain baseline/candidate error before any
improvement claim. The native same-slice Orca overlay and safe G-code export
remain separate unresolved gates. No printer operation occurred.
