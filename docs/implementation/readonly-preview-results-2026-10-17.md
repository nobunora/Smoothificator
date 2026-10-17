# Read-only candidate preview implementation

Scope: accepted ADR-0068 and orca-readonly-chord-preview handoff. Parent repository
review validated the separate model-world frame, shared exact section/proposal
owner, bounded UI-thread copy, worker cancellation and Script-only distribution.
Fixed-source API evidence confirms matrix access needs NumPy. No PlanStore or
G-code capability is introduced. This is not the printable improvement plugin.

Owners: engine/domain convex_chords; smoothificator_preview adapters, application,
UI and entrypoint; separate wheel builder. Existing research archive remains
non-runnable. Tests target transform order/count bounds, exact section identity,
rejections, cancellation/stale jobs, escaped HTML and wheel metadata/contents.

## Actual Orca result

PASS for this bounded milestone: installed the separate wheel using Plugin Manager,
activated its Script, opened the HTML window and generated three X-directed and
three Y-directed chords from the loaded offline-coupon.3mf model. Blue source
section and orange centerlines appeared together: complete/proposals-evaluated.
The existing placed coupon has nontrivial Z bounds; this is not independent runtime
proof of every rotation/scale combination.

Inputs: Z=1.522544393 mm, width=0.25 mm, end trim=0.25 mm,
positions=87.4611717775,90,92.5388282225. Final Y display bounds:
X=85..95 mm; Y=84.971873609..95.028126391 mm. Three proposed/unscored rows.
Width zero rejected with invalid-numeric-input and cleared old geometry. Restoring
width regenerated successfully. Cancel cleared the completed display; Generate
afterwards completed. In-flight cancellation/deadline/stale callbacks are unit-test
evidence, not inferred from this fast GUI coupon.

Runtime: Orca 2.5.0-dev build 86905a8a, embedded Python 3.12.13, NumPy 2.2.6.
The official NumPy cp312 Windows wheel was installed only in the dedicated portable
runtime. Orca's Python open-audit prompt was granted for this authorized local plugin;
no OS security setting changed. No export/Send/Print action occurred.

Built and installed wheel SHA256 match:
001b459dbe49c935fdee506b633cd4e59b862e50a679b5eda3233eff7163aff9.
Ignored local screenshots: artifacts/preview-candidates-x.png,
preview-candidates-y.png, preview-invalid-input.png, preview-cancelled.png and
preview-candidates-final.png. Final screenshot SHA256:
236b673402e4e8768824ba947285492aad7e14ce9f84dc2d690c26dc569a9984.
The result window remains open. No ongoing capture/control process is retained.
Computer Use failed twice with SetIsBorderRequired/0x80004002 and was reset;
the previously proven task-local pywinauto/Pillow fallback performed the operations.

## Executed checks

Development interpreter: isolated Python 3.12.10. Commands below use
.venv/Scripts/python, all exit zero:
- -m compileall -q adaptive_subedge smoothificator_preview tools tests
- -m unittest discover -s tests/architecture -p 'test_*.py' -q: 43 PASS
- -m unittest tests.unit.test_readonly_preview tests.unit.test_preview_package -q:
  initial 22 PASS; final readonly-only file 19 PASS after the busy-race regression
- -m unittest discover -s tests -p 'test_*.py' -q: final 541 PASS
- tools/check_canonical_manifest.py --handoff docs/specs/orca-readonly-chord-preview.md:
  84 canonical blobs PASS
- tools/build_preview_plugin.py: separate deterministic wheel PASS
- tools/build_validation_artifacts.py: non-runnable archive boundary and clean
  extracted geometry imports PASS
- git diff --check: PASS

Static lint/type/dependency analyzers: NOT CONFIGURED; no tooling dependencies added.
Independent review found matrix shape/index coercion, stale window/cancel callbacks
and a Cancel/busy disabled-button race. All were fixed and regression-tested; no
unresolved material finding remained in the bounded implementation review.

## Limits

One object/one printable instance/one ModelPart; at most 512 vertices/512 triangles;
convex simple cross sections only. Model-world coordinates are not centered
PrintObject or final G-code coordinates. No improvement score, finite-bead support,
clearance proof, executable Plan or safe G-code output. The complete production
plugin remains unfinished. Next: exposed-surface evaluation/support/error scoring,
then same-plan preview/output integration. Disable this Script capability to disable
the preview; original model/slice/G-code are untouched.
