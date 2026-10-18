# Settings v2 implementation and review

Scope: validated Settings-only handoff `docs/specs/phase05-settings-v2.md`;
canonical prerequisite `02f745568b74d21ffefcd96b356f0f54ca841d6b`, imported in
`69044804d132bcbb58d37c550546347ca19da027`. No existing PR was merged.

## Behavior and ownership

Added frozen `domain/settings_v2.py` with all 17 required fields and six new
policy/motion/weight DTOs. Existing fragment DTOs are reused unchanged. Required
explicit values, closed versions, exact nested types, nonfinite/bool/overflow
rejection and physical=false are enforced. Time model is explicitly unavailable;
no time predictor or ranking engine was implemented.

Application serialization remains the one projection owner. It explicitly
registers every v2 field, normalizes float constructor inputs and validates
projected v2 trees against the closed DTO schema. Only plugin-settings accepts
root schema 2; payload marker 2 is required. Typed identities reject mixed
versions. The v1 Plan still rejects a v2 Settings identity.

V1 DTOs, field lists, encoding grammar, hash domains and golden fixtures are
unchanged. ADR architecture coverage advances from 65 to 67 because the reviewed
prerequisite adds ADR-0066/0067; uniqueness remains enforced.

## Verification

Windows isolated Python 3.12.10, no dependency additions. code-quality-audit
procedure follows QUALITY_GATES; independent lint/type analyzers NOT CONFIGURED.

- `python -m compileall -q adaptive_subedge orca_plugin diagnostics tools tests`: PASS.
- `python -m unittest discover -s tests/architecture -p 'test_*.py' -q`: 41 PASS.
- `python -m unittest tests.unit.test_settings_v2 -q`: 9 PASS.
- `python -m unittest discover -s tests -p 'test_*.py' -q`: 281 PASS.
- Build tool: ZIP CRC, source-byte checks and clean extracted `-I` imports PASS.
- `git diff --check`: PASS.

Tests independently enumerate fields and encode a complete canonical vector,
perturb every synthetic Settings leaf, reject fixed unknown versions, separate
constructor normalization from canonical-root tokens, and exercise wrong/missing
DTOs, bounds, physical=true, v1 identity/Plan isolation. Existing v1 golden tests
were executed without changes. Six manifest-gate tests are included in 281.

## Independent implementation review

A separate reviewer inspected new DTOs, serializer/hashing changes, architecture
adjustment and tests against the approved handoff without primary findings.
One Medium finding was confirmed: projected float fields accepted integer tokens
and reconstructed a normalized DTO without enforcing normalized input bytes.
Fixed by requiring exact float tokens in projected roots while retaining integer
constructor normalization. Added a regression. Reviewer independently reproduced
the rejection and ran v2 plus v1 golden tests (11 PASS at that revision), returning
PASS with no remaining finding in this bounded scope. Subsequent added boundary
tests brought the complete suite to 281; no later production behavior edits.

## Limits and next scope

This completes the Settings v2 DTO/fingerprint slice only. Plan v2's complete
semantic projection and geometry reference tags remain an independently confirmed
schema gap. SurfaceBand, loop/anchor augmentation, Attempt proof/history and
their integration require subsequent reviewed contracts. No geometry algorithm,
Orca adapter, G-code writer, physical injection or Release is introduced.

The previously installed diagnostic plugin is unchanged and was not re-certified
as a geometry analyzer. Its existing real-Orca evidence remains separately dated.
The research ZIP is not an installable production plugin. Removal of this bounded
patch restores v1-only acceptance without changing saved v1 identities; no implicit
migration, machine setting or external-state mutation requires rollback.
