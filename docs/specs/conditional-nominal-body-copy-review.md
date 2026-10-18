# Conditional nominal body execution and copy assembly

Disposition: parent repository validation approved for tools-only offline
execution experiments, 2026-10-18. Current SPEC24A-29 and accepted source-state,
clearance and phase-capability ADRs remain unchanged. This introduces no physical
anchor, enabled plugin capability, firmware support claim or print authorization.
The existing strict whole-source tracer/compositor must not become permissive.

The concrete branch-free experiment is documented in
implementation/branch-free-nominal-body-experiment-2026-10-18.md. Use that separately
identified derived source/project, whose saved time_lapse_gcode is empty. Record
the intentional loss of camera/head-wrap macros, unchanged manufacturer templates
and the fact that reslicing changed model F. Do not claim source/feed identity to
the earlier seam0 baseline. No additional removal or rewriting of source features
is approved here. Retain M624/M625 typed cancellation scopes, not no-op wrappers.

Implement a tools-owned conditional nominal-body interpreter and byte-preserving
copy assembler. Input source/project/producer hashes must match actual bytes and
embedded source. A pinned producer descriptor identifies exact startup/body/end
boundaries; M981 is outside the analyzed body and remains opaque. Caller provides
an immutable nominal entry MachineState and separately named declared assumptions
for manufacturer startup completion, frame/tool, linear relative-E semantics,
startup ordinary-retraction reference, live overrides and object-not-cancelled.
These are conditional premises, never measured evidence or validated real state.
No default debt, mode or object-execution assumptions are inferred from G92 or
marlin flavor. Partial/unknown state must remain unknown and cannot compose.

Repository review identified two missing explicit inputs, adjudicated here.
Require immutable NominalMotionEnvelope with source/project/profile identity,
active entry acceleration_mm_s2 and classic_jerk_xy_mm_s, resolved external-wall
acceleration/jerk caps and requested supplemental caps. Values are exact finite
rationals; acceleration positive, jerk nonnegative. Supplemental caps must not
exceed resolved external-wall caps; current inherited values must not exceed
supplemental caps. Entry provenance explicitly names the opaque prefix or saved
setting witness and declared firmware interpretation. Update acceleration only
from supported M204 S; body does not change jerk in this fixture. Rejection of
excessive inherited values is an anchor/composition eligibility check, not a ban
on interpreting ordinary original motion. A known positive entry acceleration
above the supplemental cap may be traced until an original M204 changes it;
no supplemental insertion is eligible while it is excessive. The actual startup
6000 followed by body500/2000/2500/5000 is such a fixture, not a new override.
Reject unknown
cornering dialects or missing entry fields. No new command overrides these caps.

Require a separately hashed DerivedPathAssociation naming original recipe/input
hashes, new actual source/project/producer hashes, exact frozen path/emission
identity and geometry comparison/recipe evidence. It declares geometry input to
the conditional experiment, not transfer of old source acceptance. All source
orders, contact/future/tool validation and source speed caps are recomputed against
the new baseline. Source/project/recipe disagreement rejects. Actual model XYZ/E
equality alone must not assert feed or byte-offset equality.

Interpret every body command, preserving exact bytes/offsets. Reuse the existing
strict linear tracer's arithmetic for supported G0/G1/modes/G92 rather than
copying a new extrusion/debt model. Add typed body events for exact supported
M204 S acceleration, M106 fan channels and producer M73/M991 notifications. Their
nominal effects contract is explicit and conditional on the descriptor's firmware
assumptions; there is no generic harmless-opcode skip. Reject unexpected parameters,
remaining runtime branches, unknown commands, malformed comments/payloads, tool
changes, unsupported modes, malformed/unmatched/nested or multiple-object scopes.
Retain the object predicate on material events, anchors and inserted blocks.

An immutable NominalBodyAnchorProposal names source/project/producer/entry-context
identities, exact complete-line byte boundary, reconstructed state, acceleration,
object scope, unresolved premises and conditional status. The assembler rebuilds
it from original inputs; caller-supplied booleans cannot establish an anchor.
Require the saved inherited acceleration and configured cornering bounds, an
eligible retracted position and complete state before using compose_retracted_cycle.
Every emitted cycle must replay to the exact prior nominal state; no new M204 or
jerk override. Insertions inherit the same object predicate and cannot depend on
material outside that premise. Preserve original source bytes, startup and end;
deleting inserted spans must reconstruct the source exactly. Maintain matching
newline format, sorted unique boundaries, source/entry fingerprints, deterministic
receipts, atomic separate output and no duplicate markers. This conditional
assembler is a distinct API and must not be accepted as SyntheticInsertionAnchor
or a production real-anchor token.

Implement the usable conditional copy flow on synthetic body fixtures and actual
derived source anchors, using immutable reviewed path intents. Do not gate parser
implementation on completion of all geometry groups; incomplete geometry prevents
whole-job authorization/output designation, not testing source execution. All
reports/output names explicitly UNVERIFIED with physical/runtime/print authority
false. Later full-group contact/support/material/tool validators remain required;
the copy assembler itself does not optimize or accept geometry.

Verification includes actual complete typed body event accounting; exact source
association and retained XYZ/E/F bytes; startup/end preservation; object scope
propagation; unknown debt surviving G92; malformed/stale/unknown-command rejection;
unretracted/unsafe acceleration rejection; exact round-trip state and byte
reconstruction; entry assumptions changed => identity/anchor invalidation. Existing
strict whole-source rejection and synthetic API behavior must remain intact.
Parent primary and independent blind reviews precede wider integration. No printer
connection, transmission or physical print is authorized by this handoff.
