# Settings v2 readiness and independent review

## Baselines and scope

Specification PR #5: `515c2a97fd51dd9590be93678524337d63447731`.
Implementation PR #2: `01cc65a632f5b14755a5d90f0b54771e8e45cb86`.
Diagnostic PR #6: `cc96452b81d810ff1825d3a3442a8a26c0fbe38f`.
All were fetched/read on 2026-10-16; no PR was merged.

This record validates only docs/specs/phase05-settings-v2.md. Plan v2 and Attempt
are excluded. Physical/G-code/geometry/time-predictor work remains prohibited.

## Independent schema review

A separate agent received authoritative docs/source contracts without primary
findings or proposed fixes for its initial review. It inspected ADR-0066/0067,
the delegated owner contract, relevant ADR-0037/0045/0049/0058/0059/0062/0064/0065,
SPECIFICATION settings/optimizer sections and IMPLEMENTATION DTO/identity sections.
It checked units, version identity, unknown inputs, proof ownership, immutability,
unavailable time, chronological references and runtime/semantic separation.

Initial findings at the specification baseline:

1. Medium, confirmed/open for Plan v2: exact closed payload, reference tags and
   support/travel metadata placement are missing. ADR-0064 requires declared
   semantic bytes; choosing these in code would silently define schema 2.
2. Medium, confirmed/resolved for Settings: recognized version IDs had no
   registry. Added an explicit schema/research-only registry, including
   unavailable_v1; no numeric predictor or printer parameters invented.
3. Follow-up precision issue, resolved: moved exact 17-field type/range contract
   into normative ADR text, required weights and exact motion DTOs, and stated
   legacy finite-binary64 normalization explicitly.

The independent final review returned **validated for bounded Settings-only
schema**, with no remaining material finding in that scope. This is an AI
independent review, not a human approval or physical certification. Plan finding
1 remains open and does not authorize an improvised Plan projection.

## Canonical reconciliation

Approved A1–A5/B1–B6 text was moved verbatim from the delegated record into its
owning ADR; the record now links to those owners. Earlier proposal text is
explicitly historical. The Settings registry/field table are engineering
codifications of the delegated decisions, independently reviewed above.
The new JSON manifest pins all 83 original normative/evidence paths including
ADR-0066/0067. Handoff and manifest exclude each other from the enumerated set;
handoff pins the manifest's Git blob. Historical manifests remain unchanged.

## Repository review — validated for Settings only

Trace: caller constructs domain Settings -> application semantic_tree's exact
DTO field whitelist and float normalization -> identity_root -> canonical tagged
bytes -> domain-separated SHA-256 -> typed IdentityReference. Existing v1 Plan
creation separately enforces v1 reference schemas.

Inspected source: domain/settings.py, domain/numeric.py, domain/plan.py identity
definition, application/serialization.py and hashing.py; architecture DTO-owner
test and existing research/v1 Settings identity tests. Settings fragments already
exist and will be reused. No Orca object or raw config enters this path. The
serializer is the existing projection owner; no second serializer is needed.
IdentityReference itself allows version vocabulary; application functions must
gate schema 2 only for plugin-settings and retain v1 Plan rejection.

Disposition: **validated**. Minimal edits: a version-specific domain Settings
module, explicit application registry entries, narrow version-aware identity
operations and focused tests. No v1 class/field/golden changes; no added library.
Tests must cover every leaf, wrong root/payload versions, unknown policies,
malformed nested DTOs, numeric boundaries, physical=true and v1 Plan isolation.

## Checks before implementation

Existing Python 3.12.10 environment, no dependency changes. Quality audit order:
syntax/import -> integrity/structural checks -> focused gate tests. Lint/type
analyzers remain NOT CONFIGURED under QUALITY_GATES.

- `python -m compileall -q tools tests`: PASS.
- `python -m unittest discover -s tests -p test_canonical_manifest.py -v`: 6 PASS.
- `python tools/check_canonical_manifest.py`: 83 Git blobs PASS.
- `git diff --check`: PASS.

Manifest tests exercise changed bytes, stale handoff hash, omitted ADR, unsafe/
duplicate/self references and attempts to mislabel integrity as approval.
Integrity CI is separate from substantive schema review. Later source commits
must run architecture, focused identity tests, full suite/build and independent
implementation review before being described as complete.
