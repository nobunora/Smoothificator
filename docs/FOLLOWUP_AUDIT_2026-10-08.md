# Follow-up Risk and Implementation Audit — 2026-10-08

Status: COMPLETE for current specification review
Scope: post-design-review defect/risk sweep + current-Orca drift check

## 1. Executive result

No new Critical architectural contradiction was found.

The Phase 0.5 architecture remains implementable.

Four additional implementation-risk gaps were identified and resolved/documented:

1. High — printable v1 coordinate units/mode were not explicit enough.
   Resolution: ADR-0034 requires millimeter units + absolute XYZ + relative E.

2. High — one ModelPart did not guarantee one simple target loop.
   Resolution: ADR-0035 restricts each refined v1 region to one simple target outer boundary and rejects target holes/multiple islands/self-intersection.

3. High — firmware-side M220/M221 overrides were not part of the execution model.
   Resolution: ADR-0036 requires actual anchor M220=100% and M221=100% for printable v1.

4. Medium/High quality/reporting — postprocess insertion changes real time/material/thermal timing after Orca already computed cooling/progress/filament metadata.
   Resolution: ADR-0037 treats original metadata as pre-injection estimates, preserves it byte-for-byte, reports plugin-added estimates separately, and moves cooling/thermal effects into physical validation.

## 2. Current Orca drift

Original technical source audit baseline:
- OrcaSlicer main 789f848694b955d293ca6b277d1c8046aa6f7436 (2026-09-29)

Current OrcaSlicer main checked on 2026-10-08:
- 59fc97fb286e3748a1f34526a7862ca8a87cf72c
- 350 commits ahead of the original audit baseline.

Relevant core files have changed blob SHA since the baseline:
- src/libslic3r/GCode.cpp
- src/libslic3r/Print.cpp
- src/slic3r/GUI/PostProcessor.cpp
- SlicingPipelinePluginCapability.cpp

The current source still contains the core concepts used by the design:
- posSimplifyPath;
- psGCodePostProcess;
- path.z_contoured handling;
- print_flow_ratio / outer_wall_flow_ratio;
- filament adaptive volumetric speed logic;
- seam_gap;
- config_value in plugin/postprocess context.

However, this does NOT authorize treating 2026-10-08 main as production-compatible without a fresh exact-version fixture audit.

## 3. Firmware multiplier finding

Current Bambu common machine profile still emits startup resets:
- M220 S100
- M221 S100

These firmware multipliers are separate from slicer flow/speed configuration.

If changed later by custom/firmware G-code, they would alter actual execution without changing the immutable plan.

ADR-0036 therefore requires unity actual parsed state at injection anchors.

## 4. Coordinate mode / unit finding

The parser already planned to observe G90/G91 and actual XYZ, but printable-v1 semantics were not explicit.

Because execution-frame mapping and ToolClearance are defined in machine millimeters/absolute coordinates, v1 now explicitly requires:
- G21-equivalent millimeters;
- G90-equivalent absolute XYZ;
- M83 relative E.

Parser recognition of other modes is diagnostic only unless a later compatibility ADR implements them.

## 5. Multi-loop / hole finding

One ModelPart volume may produce multiple disjoint sections or holes.

Without an explicit gate, v1 could silently grow from the intended first simple-surface proof into:
- annular targets;
- multiple external loops;
- disconnected target islands.

ADR-0035 keeps the first printable target region to one simple external boundary.

## 6. Cooling/time/progress metadata finding

Orca runs cooling/layer-time processing before psGCodePostProcess.

Adaptive Sub-Edge then adds:
- travel;
- extrusion;
- elapsed time;
- material.

Therefore original Orca/Bambu:
- estimated time;
- progress;
- filament-used summaries;
- cooling/fan decisions

do not exactly describe the postprocessed print.

For v1:
- original bytes remain preserved;
- plugin calculates added estimates;
- original metadata is labeled pre-injection;
- thermal/cooling changes are measured during physical coupons.

No safety decision is allowed to depend on stale original estimates.

## 7. Additional residual risks found but not specification blockers

These remain later physical/compatibility test items:

### Flow transition / seam blob behavior
Segment-local q_cmd changes and temporary retract/unretract may create pressure transients or seam artifacts even with static PA.

Current handling:
- adaptive PA disabled;
- conservative speed;
- deterministic seam;
- physical coupon validation.

Potential future mitigation only if evidence requires:
- minimum segment length;
- flow-gradient limits;
- flow smoothing;
- explicit PA/acceleration policy.

### Cooling / fan inheritance
Injected candidates inherit the current machine thermal/fan environment rather than receiving Orca role-specific thermal planning.

This may affect quality but is not a logical motion-safety contradiction.

### Progress / printer UI
Printer/display progress or remaining-time estimates may be inaccurate after injection.

This is explicitly not a v1 correctness signal.

### API drift
SlicingPipeline remains experimental. Every production-supported Orca version must be re-audited and fixture-pinned.

## 8. Current readiness

Phase 0.5 architecture skeleton:
- remains READY after manifest restamp/revalidation.

Full injector:
- still staged behind parser/matcher/fixture gates.

Physical injection:
- still NOT READY.

No newly found issue requires discarding the current architecture.
