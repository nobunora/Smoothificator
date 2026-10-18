# Review and Convergence Process

Adaptive Sub-Edge modifies executable printer G-code and therefore uses stricter review than ordinary low-risk code.

## 1. Roles

### Specification / Adjudication
Owns:
- requirements;
- accepted ADR decisions;
- architecture/invariants;
- acceptance criteria;
- finding disposition.

### Repository / Implementation Lead
Owns:
- actual repository evidence;
- bounded implementation;
- checks/tests/builds;
- diff review;
- evidence report.

### Independent Blind Reviewer
Reconstructs behavior independently from specification/source without receiving primary-review conclusions.

## 2. Normal review loop

1. Validate specification against repository.
2. Adjudicate conflicts.
3. Implement a bounded step.
4. Run focused checks, then risk-appropriate broader checks.
5. Review final diff and affected execution paths.
6. Record material findings.
7. Adjudicate findings.
8. Fix and re-verify.
9. Repeat until convergence criteria are met.

A delegated implementation/review agent may not redefine requirements.

## 3. When blind review is mandatory

Blind review is mandatory before:
- enabling physical printer injection for the first time;
- changing G-code state restoration, execution-frame mapping, extrusion conversion, or safe-ceiling travel;
- relaxing an injection safety gate;
- supporting a new printer/firmware family;
- production/release readiness.

It is also required when:
- architecture/control flow changes materially;
- repeated review discovers new Critical/High issues;
- a root-cause hypothesis changes;
- implementation is substantially rewritten.

## 4. Blind-review independence

Before the blind report is complete, do not provide:
- primary review findings;
- suspected defect locations;
- prior root-cause hypotheses;
- proposed fixes;
- prior severities.

Allowed:
- authoritative specification/ADRs;
- implementation contract;
- current source/diff;
- tests/build/static-analysis results;
- necessary Orca/Bambu external contract evidence.

The blind reviewer should actively try to falsify important assumptions.

## 5. Required review dimensions

Where applicable inspect:
- specification compliance;
- parallel/stale implementations;
- control/data flow;
- ownership/lifetime;
- cancellation/cleanup;
- concurrency/ordering;
- min/max/zero/empty/malformed inputs;
- numeric units/conversions;
- G-code modal state and restoration;
- compatibility/profile gates;
- failure/atomicity/idempotence;
- regression outside changed lines;
- whether tests actually prove the claimed behavior.

## 6. Finding format

Every actionable finding:

- Severity: Critical | High | Medium | Low
- Location
- Affected behavior
- Evidence
- Violated requirement/invariant
- Concrete failure scenario
- Recommended remediation direction
- Confidence

Do not inflate severity.

## 7. Reconciliation

After both reports are complete classify findings:
- convergent;
- primary-only;
- blind-only.

Then assign disposition:
- confirmed;
- rejected;
- duplicate;
- superseded;
- accepted risk;
- requires further evidence.

Disagreement is resolved by specification, source, fixture, and execution evidence—not by majority vote.

## 8. Negative review

"No findings" is not sufficient.

A no-finding report must state:
- files/components inspected;
- execution paths traced;
- invariants checked;
- boundary/failure cases considered;
- validation evidence reviewed;
- residual uncertainty.

## 9. Convergence

Do not declare convergence until:
- no unresolved Critical/High findings;
- every confirmed finding has a disposition;
- normative docs are internally consistent;
- source and external contracts agree with the specification;
- required quality/test gates pass;
- no unexplained new warnings;
- material validation gaps are resolved or explicitly accepted;
- fixes were checked for secondary regressions;
- a fresh independent review finds no new material defect requiring redesign.

## 10. Review records

Store concise implementation/review evidence under docs/implementation/.

Milestone summaries may also be recorded under docs/records/.

For physical-print readiness, record exact:
- Orca version/commit;
- printer/process profile;
- fixture hash/path;
- plugin commit;
- checks passed;
- reviewer disposition;
- accepted residual risks.
