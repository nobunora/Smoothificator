# Phase 0.5 — delegated specification-owner decisions

Date: 2026-10-15
Status: DESIGN DECISIONS APPROVED BY DELEGATION; NOT independent review, source/fixture validation, implementation completion, or merge authorization.

The project requester explicitly delegated the remaining *specification* decisions. Previous S1–S9 and D1–D10 policy directions are approved. The decisions here resolve engineering design choices to the *schema* extent stated. Accepted ADRs 0037/0043/0044/0045/0047/0049/0050/0058/0059/0062/0063/0064/0065 have priority. PR #5 is the integration review surface; old PR #3/#4 are historical alternatives.

## A. ADR-0066 — approved Settings v2 design

The exact approved text is now owned by [`ADR-0066`](../adr/0066-plugin-settings-fingerprint-schema-versioning-proposal.md#normative-schema-decision--consolidated-2026-10-16). The decision record at revision `515c2a97fd51dd9590be93678524337d63447731` is retained in Git history as approval provenance. It is not a second normative owner.

## B. ADR-0067 — approved immutable Domain/Attempt schema principles

The exact approved text is now owned by [`ADR-0067`](../adr/0067-phase05-domain-dto-and-attempt-snapshot-contract-proposal.md#normative-schema-decision--consolidated-2026-10-16). The decision record at revision `515c2a97fd51dd9590be93678524337d63447731` is retained in Git history as approval provenance. It is not a second normative owner.

## Dispositions and non-waivable gates

| Question | Delegated specification decision | Separate implementation/external gate |
| --- | --- | --- |
| X1 weights conflict | APPROVED exploration-only p95 heuristic | bounded-search queue/equivalence tests |
| X2 unavailable time | APPROVED disjoint typed evidence, rank-incomplete analysis | v2 DTO/golden/error tests and machine time model |
| X3 complexity/time/material | APPROVED planned-intent counts and exact lex rank | canonical segment equivalence fixtures, motion/time and commanded E proof |
| X4 motion precedence | APPROVED separate plugin and resolved caps, fail closed | firmware profile fixture/Orca config parity |
| S3 support policy | APPROVED typed mm tolerance, no numerical default | conservative numeric proof and calibration |
| surface/loop references | APPROVED typed immutable refs/frame | mesh topology, orientation and matcher tests |
| Attempt | APPROVED typed evidence/history/snapshot provenance | verifier/TOCTOU integration tests |
| v1 identity | INVIOLABLE: no changes | independent exact SHA/byte vectors |
| injection | NOT APPROVED | later exact G-code/Orca fixture and blind review |

**Governance:** The user delegated specification-owner choices, NOT independent review or test/physical certification. These decisions can be incorporated as accepted *schema decisions* while PR #5 stays Draft until (1) a single consistent normative ADR/Spec/Implementation revision, (2) updated audit manifest + handoff, (3) independent review where required and a review-only REPOSITORY_REVIEW disposition validated, (4) exact-HEAD implementation tests, (5) Implementation Review. The decision record itself never claims those latter gates passed.
