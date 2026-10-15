# Phase 0.5 unified Settings/Plan contract review

**SPEC_REVIEW; Proposed, not Accepted; no production implementation.**

Baseline: PR #3 `20d38c46fc18f6efd81ada0d9fac479adcb963d8` and PR #4 `cc1562715c616c7284aa52cf2773deeedd212a49` were both Draft and both changed `docs/SPECIFICATION.md` and `docs/IMPLEMENTATION.md` independently. This branch combines their existing draft edits without changing v1 identity or any executable source. Existing Accepted ADR-0037/0047/0062/0065 and their precedence remain authoritative.


## 2026-10-15 consolidated X1/X2 design adjudication candidate (for reviewer approval)

**Scope:** this addresses the previously identified conflict between requester-approved S5 directional weights and S6's strict quality-gated lexicographic objective, and the v1 Plan's inability to encode unknown time. These decisions are **candidate type/algorithm rules**, not an Accepted ADR or production source implementation.

### X1: Directional weights have one explicit search-only owner

- \`DirectionalErrorWeights\` retains two separately configured nonnegative finite IEEE-754 binary64 fields \`pred_to_src_weight\` and \`src_to_pred_weight\`. Reject both zero, bool, NaN, Inf, negative and undeclared fields.
- The **hard feasibility check** always independently requires \`E_max_pred_to_src_mm <= tolerance_mm\` and \`E_max_src_to_pred_mm <= tolerance_mm\` with both bounds numerically converged. Weights MUST NOT change either threshold, the conservative support gate, or the final comparator.
- An approved *bounded candidate search* MAY use the two weights to prioritize **which already evaluable candidate branches to expand**, based on converged directional p95 errors. Define a *single* exploration priority:
  \`H(P) = (w_pred * E_p95_pred_to_src_mm(P) + w_src * E_p95_src_to_pred_mm(P)) / (w_pred+w_src)\`.
  All four numeric values are finite, nonnegative, and evidence-backed; each input binary64 is interpreted as an **exact rational** for mathematical comparison. Normalize by the positive exact rational sum; do not require a binary64 sum that might overflow. Implementations may use a faster equivalent comparison only after parity tests demonstrate identical ordering for all supported inputs. Ascending \`H\` is exploration priority; exact ties use canonical candidate semantics and bounded-search versioned policy, never Python object identity.
- **No residual-error term is inserted into S6's final tuple.** The final feasible-plan comparator remains \`(complexity, estimated_added_time_s, commanded_added_volume_mm3, canonical_semantic_bytes)\`. Changing directional weights may change *which plans a bounded search explores* and therefore may change which feasible candidates are found; the search budget/coverage must be included in the proposal's model/version identity and the result must never claim an exhaustive/global optimum. When candidate enumeration is exhaustive, the final selected plan MUST be independent of weights (unless an exact tie in all final keys cannot be distinguished, in which case semantically equal results are equivalent).
- If no search algorithm consuming \`H\` has been reviewed, retain the field's versioned semantic presence as **unimplemented research-only**; do not advertise it as a working optimizer feature or inject a hidden weighted objective.

**Why this resolves X1:** the weights have a defined, reproducible influence only on search ordering under a bounded exploration algorithm. The user-approved quality gate and lexicographic final ranking remain unchanged. No v1 schema or golden hash is modified.

### X2: unknown time is distinct from a numerical zero

- New v2 \`AddedTimeEvidence\` is a tagged **sum type**, with \`AVAILABLE(estimated_added_time_s: finite binary64 >=0, predictor_version: nonempty version ID, resolved_execution_config: exact typed IdentityReference, provenance: immutable evidence reference)\` OR \`UNAVAILABLE(reason: stable reason code, missing_dependency_ids: immutable nonempty tuple of explicit identifiers)\`. Reject simultaneously supplied available/unavailable variants, unknown tags and missing provenance. \`AVAILABLE(0.0)\` means a valid zero estimate only when a real model supports it; it never means unknown.
- A \`PlanSemanticContentV2\` or an immutable v2 analysis result must include the above discriminated time evidence **without mutating v1 \`PlanSemanticContent.estimated_added_time_s\`**. Exact owner/version placement is a joint ADR-0066/0067 schema review decision: never put mutable runtime status into the Plan hash.
- Distinguish two sets: \`F_geometry\` contains candidates that passed all decidable geometric/support/clearance/error hard checks; \`F_ranked\` contains the subset with all finite, validated rank metrics and applicable target-specific motion/time evidence. A candidate in \`F_geometry - F_ranked\` remains a *research-only geometry result*, not an eligible printable selection and never takes a numeric sentinel value in sorting.
- If \`F_geometry\` is empty, return a stable no-feasible-geometry result; if \`F_geometry\` is nonempty and *any* required time evidence is UNAVAILABLE, return **RANKING_INCOMPLETE / ANALYSIS_ONLY** with best-known ranking explicitly labeled as incomplete, and do not declare a lexicographic optimum across the full \`F_geometry\`. Without a valid model, do not claim an optimal physical plan or set \`injectable=True\`. If all full metrics are available, select by exact lexicographic tuple over \`F_geometry\`, but physical-mode authorization remains separately gated by runtime/fixture/atomic writer checks in later phases.
- No numerical time predictor may be synthesized solely from structural complexity or \`path_length/requested_speed\`; target machine acceleration, corner behavior, travel and restart policy are model inputs with explicit versioned provenance. Plugin-owned caps remain separate from resolved Orca execution configuration.

### Example reviewer fixtures (input -> expected)

| Fixture | Expected result |
| --- | --- |
| both weights zero; either weight NaN/Inf | INVALID_SETTING |
| w=(1,0), converged p95=(0.2,0.3) vs (0.4,0.1) | exploration prefers first candidate; both hard E_max gates still required |
| same feasible completed candidate set, weights exchanged | identical *final* lex-selected canonical plan |
| error under tolerance, fewer paths but greater time | fewer paths wins under S6 (as approved); no unapproved weight blending |
| valid geometric evidence; no time-model provenance | ANALYSIS_ONLY / RANKING_INCOMPLETE; never zero time, never physical injection |
| equal complexity/time/material, two distinct canonical byte projections | choose lex smaller canonical bytes; hash digest collision cannot be treated as semantic equality |
| exhaustive search vs bounded search | report scoped-optimum vs globally proven only with formal completeness evidence |

**Remaining reviews:** agreement on exact canonical complexity counting, time-estimator implementation/evidence, and typed plan/analysis result placement is required. Requester's S1–S9 and D1–D10 approvals fix the policy direction, not these source/fixture-dependent implementation contracts.

## Exact remaining completion gates

1. Review and approve or amend the newly proposed X1/X2 semantics; cite source-backed distinction between immutable Plan identity and runtime evidence.
2. Resolve X3/X4 versioned motion/time/complexity semantics and exact S3 support-query soundness proof, with machine-dialect adapters still outside Phase 0.5.
3. Review ADR-0067 geometry reference closure, path split/insertion anchor semantics and immutable attempt evidence history/retention; explicit v2 Plan identity root and goldens required.
4. Reconcile one final canonical `SPECIFICATION.md` and `IMPLEMENTATION.md`, accepted ADRs, handoff and audited blob manifest with non-self-referential hashes; run review-only `validated` gate.
5. Only then implement v2 DTOs/identity/attempt evidence on Draft PR #2 and run exact-commit CI/normal implementation review; no G-code modification or physical injection.
