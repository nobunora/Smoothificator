# Zero physical downshift and same-family 0..45-degree trial

Status: SPEC_VALIDATED by parent adjudication2026-10-18. Implementation authorized within the following bounded delta.
Extends angle-table-trial-review.md and its tapered-stack/user0.08gap amendments; canonical revision and tools-only restrictions unchanged. No print/send/device action. Preserve all original source/settings/projects/log_iotc.

## Physical placement versus analysis query

Current30percent overlap physically sets root bottom floor-0.30*h (0.036..0.057mm for h0.12..0.19). Independently root support-gap tolerance0.08 changes only the queried source-support plane; it does not command a physical Z shift. User now requires actual downshift0: default overlap_percent=0. Every root physical bottom equals its saved original terrace floor; each child physical bottom equals its completed declared parent top. Rootgap tolerance stays explicitly0.08 as a separately fingerprinted analysis premise unless parent adjudicates otherwise. OriginalsourceZ/layerheight are never lowered/changed. Zero-overlap parent contact must still pass the existing exact public contact gate; no assumed contact or suppressed collision.

## Bounded generic table

Keep width0.21..0.45, exposedminimum0.08, physicalheight strictlybelow actualsavedH, outputgrid0.001 and tapered stacktopology2 (strict narrower latticechild, no taller than parent, frozen containment,max2tiers). New fingerprinted physical_height_step_mm=0.01 declares the finite height family; include the largest strict-H grid endpoint if otherwise valid. At H0.2/overlap0 this gives0.08,0.09,...,0.19,0.199, all exactly grid-valid. Existing explicit overlap30 remains supported and yields its previous0.12..0.19 legal family. This avoids accidental unbounded quadratic enumeration of every0.001height combination. Table/search budgets and cancellation remain explicit. New policy/cache identity invalidates oldtrialtableassociation.

## Same coupon family expanded to45degrees

Retain X30mm,Y20mm,flat bottom0,baseheight2mm,256Ypanels and9decimal meshserialization. General family theta(y)=theta_max*y/20; z(y)=2-(20/theta_max)*ln(cos(theta(y))). Previous theta_max=pi/6; new theta_max=pi/4, hence z=2-(80/pi)*ln cos(pi*y/80). This changes only maximum angle within the current curvedcoupon family. Do not substitute old fixture shapes. Preserve genuine savedsettings/placement and replace only geometry in an explicitly geometry-only project, then obtain genuine GUI slicing/export. Never associate oldsourceGcode with newmesh. Freshplacedgeometry/source/archive hashes, source-step catalog, usedmaterialprofile, nativecontext and posthopanchors are mandatory.

Generic slope0..1 covers0..45 and the existing short-base rejection should now appear within the coupon (minimumwidth0.21,H0.2 configured conservative admission cutoff~33.96degrees; this is not a necessary physical feasibility bound). Actual finite-table quality/height/format/contact gates determine selected/skipped source steps and must be reported. Rebuild all retained-member feasibility/epsilon rankings and all source/state/preview/material/tool/package gates for freshslice. No model-specific per-location optimization.

## Acceptance

Tests verify defaultzero overlap physicalbottoms exactly supportplanes, strictH endpoint0.199, exposedminimum, explicit30percent compatibility, taperedhierarchy, cachekey changes and finite lattice preflight. Actualjob audit reports every emitted physical bottom minus its declared supportplane is0, rootqueryplane lowerby0.08 only foranalysis, and new45coupon contains a bounded unsupplemented steepregion. A clean table test is not genuine slicing/physicalproof. The pinned geometry source has onebuilditem/onecomponent. Preserve that onecoupon placement; WITH/WITHOUT derive from the same genuine new slice.

Parent explicitly retains the earlier user-requested base<sqrt(2)*minimumwidth exclusion. Counterexamples can satisfy triangle-spill/error without passing this conservative family policy; excluded rows must therefore be labeled configured-policy-excluded, never physically impossible.

## Exact actual-section admission guard amendment

Parent-adjudicated boundary correction: the configured sqrt(2)*minimumwidth exclusion applies to each actual section before selecting its lower representative bin. A slope0.675 section must not bypass its actualbase exclusion via the eligible0.67bin. Add a constant-time exact base_squared<2*minimumwidth_squared guard in lookup before bin arithmetic; return stable strict-short-base. This is enforcement of the existing user admission policy, not a new physical impossibility claim or optimizer expansion. Focused regressions cover actual slopes just below/above the configured boundary and the reported0.675 case. Parent restarts full-suite evidence for this final source revision.


## Genuine trailing empty nominal planes

Parent validated native material-profile extension against the new actual GUI
export and independent Orca source evidence. Header printed-layer count can be
smaller than the consistent layer-progress denominator because terminal nominal
planes contain no printable paths. Admit an extended contiguous EMPTY terminal
range starting exactly at printed count only when all progress numerators are
exactly 1..printed count, all denominators agree and are bounded, CHANGE_LAYER
count agrees with printed count, and exact source max_z_height divided by the
source/saved uniform layer_height agrees with that nominal denominator. Its end
must be exactly nominal count minus one. Used-material ranges remain restricted
to printed indices with the one actual material. Preserve legacy accepted cases;
reject gaps, duplicate ranges, nonempty tails, forged/missing counts, fractional
nominal grids, mismatched saved/source height and unreasonable numeric/count
bounds. Do not rewrite archive metadata to satisfy the gate.
