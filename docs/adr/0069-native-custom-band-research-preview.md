# ADR-0069: Native Custom-role equal-band research preview

Status: Accepted
Date: 2026-10-17

## Scope and authorization

The user requests native Orca preview with Custom-classified generated lines,
explicit minimum/maximum widths, and multiple lines when one cannot span the
requested transverse interval. This is a separate unscored research mode, not
the full exposed-surface optimizer or an executable Plan. ADR-0068's original
read-only APIs and non-runnable research archive remain unchanged. This ADR
adopts a narrowly scoped exception allowing a newly generated viewer G-code
artifact in the separate preview distribution. No original G-code is read,
modified, appended, or replaced. No baseline-slice overlay is claimed.

The artifact is print-unvalidated, not guaranteed unprintable. No PlanStore,
postprocess hook, slicing hook, upload, device command, or physical output
authority is added. The existing isolated model-world snapshot restriction and
coordinate exception apply. Native Custom-only layer labels may differ from
the commanded Z; geometry and width must be verified in the actual viewer.

## Exact equal-band geometry contract

Owning modules remain domain/convex_chords.py and engine/convex_chords.py.
Existing public proposal APIs and DTOs retain their behavior.

```python
BandChordPreview(
    state: str, reason: str, section: MeshSectionLoop | None,
    proposals: tuple[ChordProposal, ...], width_mm: Fraction | None,
    command_z_mm: Fraction, axis: str,
    common_running_interval: tuple[Fraction, Fraction] | None,
)
propose_convex_band_preview(
    mesh: IndexedTriangleMesh, z_mm: float, *, axis: str,
    span_min_mm: float, span_max_mm: float,
    minimum_width_mm: float, maximum_width_mm: float,
    display_height_mm: float, end_trim_mm: float,
    algorithm_version: str, max_chords: int,
    max_vertices: int, max_triangles: int, max_mesh_pair_checks: int,
    max_section_segments: int, max_section_pair_checks: int,
    max_ray_directions: int, cancelled: Callable[[], bool],
) -> BandChordPreview
```

All arguments are required. Version is exactly convex_equal_bands_v1. Use the
existing proposal scalar policy (finite binary64 int/float, excluding bool,
normalized through float then exact Fraction), axis X/Y, exact positive integer
limits and callable cancellation with exact bool results. Invalid policy/limits
raise INVALID_SETTING; malformed geometry/scalars/results raise INVALID_GEOMETRY.
Require span_min < span_max, 0 < minimum_width <= maximum_width, positive height
and trim. No defaults or physical Settings are inferred. Callback exceptions
propagate. command_z_mm is an exact Fraction in every returned disposition.

Let S = span_max - span_min and m = max(minimum_width, display_height).
Compute exact integers n_min = ceil(S / maximum_width) and n_max = floor(S / m).
If n_min > n_max, reject width-span-infeasible; do not relax either width bound
or nominal height <= width. Otherwise choose n = n_min (fewest equal bands).
If n > max_chords, return incomplete/resource-limit before mesh work or allocating
position rows. Width w = S/n and centers span_min + (i+1/2)*w, i=0..n-1, are
exact Fractions. These closed adjacent transverse bands partition the requested
span exactly, with no gaps, zero widths or extension outside that span.

Fresh embedding and the exact symbolic section occur once in the same call,
sharing the current private geometry owners. Convexity and entire transverse
footprint halfplane clipping are exactly ADR-0005's rules. Pass Fraction centers,
width and trim directly to the shared private chord owner; never round through
the public binary64 interface. All positive centerlines receive the existing
same-call exact material-segment classification. All n rows must be proposed/
unscored. Any per-position rejection becomes global rejected/band-chord-rejected
with no rows. No partial collection can be rendered as a successful band set.

For the accepted running intervals [l_i,u_i], compute L=max(l_i), U=min(u_i).
Require L<U; otherwise reject no-common-running-span. The closed rectangle
[L,U] times [span_min,span_max] (axes swapped for Y) is covered by the union
of the nominal rectangular footprints. Return the original individual chord
endpoints, not silently shortened endpoints. Each original footprint remains
contained in the convex section. This is planar footprint coverage only: no
surface coverage, bead-volume containment, support, scoring, flow, improvement,
or physical feasibility is proved. Nominal display height is not measured h_eff.

Complete result is complete/bands-proposed with section, positive exact Fraction
width, nonempty proposed-only tuple and exact Fraction interval L<U. Enclosing
DTO validates exact types/state matrix, same-Z section, X/Y endpoint alignment,
strictly ascending unique centers with adjacent spacing equal to width, equal
width-band ordering and common interval exactly equal to endpoint intersection.
Constructor checks do not confer computation authority. Noncomplete results
have section=None, proposals=(), width_mm=None, common_running_interval=None.
Rejected reasons are all ADR-0005 global rejected reasons plus
width-span-infeasible, band-chord-rejected and no-common-running-span.
Incomplete reasons are resource-limit, cancelled, ray-directions-exhausted and
classification-inconsistent. Cancellation is checked after top-level validation,
before every expected return and at the existing mesh/section/chord checkpoints.
No counters or partially usable geometry survive failure/cancellation.

## Viewer-only artifact boundary

Preview v0.2 UI replaces manual position entry in its native-viewer mode with
span endpoints, minimum/maximum width, nominal height and trim. Show computed n,
width and guaranteed common rectangle separately from unverified physical claims.
UI examples width 0.3..0.6 mm and height 0.2 mm are labeled research examples,
require explicit Generate, and are not physical defaults or profile validation.
ADR-0068 resource/deadline limits remain, with max_chords=64. Infeasible intervals
are explicit rejection; no guessed fallback width. Worker cancellation, stale
generation/window suppression and bounded escaped HTML remain mandatory.

Only the preview adapter/application may write a unique exclusive-create ASCII
G-code file below plugin-owned storage. Never accept a user-supplied output path.
Bound output to 2,097,152 ASCII bytes before write; incomplete write is not
presented as an available artifact. Do not embed
model names or arbitrary newlines. No temperatures, homing, device connection,
printer start/end macros, or commands unrelated to viewer representation.
The content must clearly identify Smoothificator research and print-unvalidated
status. Expose the saved path and manual separate-viewer opening instructions.
No automatic executable launch, project replacement, upload or printing occurs.
Warn that opening G-code in the current modeling window may replace its project.

Pinned source evidence at 86905a8a20d5887f3b13017e66cd897766334bd3 shows Orca
producer recognition requires a sufficiently populated serialized config block;
a short forged producer header fails configuration extraction. UI-thread copies
of host full_config_keys/opt_serialize values may supply the viewer configuration.
Keys must match [A-Za-z][A-Za-z0-9_]* and values contain no raw CR/LF/NUL. Exclude
connection/authentication/URL/custom-script fields before storage and require
the source-verified minimum remaining config count. No hidden secrets or custom
scripts may be copied for convenience. Width/height metadata uses exact reserved
Orca tags; positive XY+E moves are viewer extrusions. Position the first G1 before
the Custom role tag per the pinned parser's first-layer handling. Do not insert
fake non-Custom reference extrusions. Appending generated commands to baseline
G-code is forbidden because layer IDs do not merge by equal Z.

No auto-launch contract is adopted. The renderer is a separate preview adapter,
never an engine G-code dependency. Its copied config/tag grammar follows the
source-verified Orca producer format, including both BBL and non-BBL reserved
tag spellings where needed. Require at least 80 retained valid serialized
settings; unavailable or insufficient config fails explicitly. Exclude any key
whose lowercase name contains host, api, password, token, secret, user, device,
url, gcode, notes or credential. Drop non-ASCII serialized values. Reject raw
CR/LF/NUL and keys outside [A-Za-z][A-Za-z0-9_]* rather than escaping them into
executable text. Never log serialized values or copy excluded values into HTML.
Require retained printer_model, filament_diameter and extruder_offset values;
validate needed numeric geometry and positive filament diameter. Positive E is
visualization-only, using nominal width/height cross-section and that diameter.
Missing/invalid required values fail explicitly. Select BBL/compatible reserved
tag spellings from printer_model according to the pinned processor evidence.

Use a 12-decimal-place grid. Choose the nearest representable width within the
exact requested minimum/maximum and >= display height (ties choose lower).
If that intersection contains no grid value, reject instead of relaxing bounds.
Round positions deterministically to 12 places (ties to even) and reject collapsed
extrusions; require finite positive feed rate and E for every extrusion.
Native coordinates/coverage are rounded display
approximations and must be labeled as such, not a new certified rectangle.
Generated extrusion moves use positive XY length and positive E. Native width/
height parsing requires pinned-source fixtures and actual runtime acceptance.
The only emitted command families are G21, G90, M83, G92 E0 and G1 plus comments;
G1 without extrusion is permitted for positioning. Native widget float32 display
tolerance is not physical proof. The nearest-grid displayed width can differ
from exact S/n, so its native bands must never be called exact certified coverage.

## Validation and pending review

Pinned Orca source/runtime configuration includes required_nozzle_HRC,
machine_max_force_Y and machine_bed_mass_Y. Their ASCII uppercase letters are
valid serialized key characters. The implementation lead approved this narrow
grammar correction; case-insensitive sensitive-key filtering and the existing
value delimiter guards remain unchanged.

Geometry fixtures: one band, exact min/max equality, height raises effective min,
infeasible width interval, resource precedence, rational S/n, X/Y symmetry,
triangle/sloped clipping, all-or-none rejection, positive common rectangle,
cancelled/unknown no partial output and unchanged v0.1 APIs. Example S=1,
min=1/4,max=2/5 gives n=3,w=1/3; S=1,min=3/5,max=4/5 is infeasible.

Native fixtures must test reserved tag/config parsing in the pinned runtime,
Custom classification, actual command coordinates and width, isolated project
lifecycle, exclusive paths, rejected secret/script/newline config, bounded output,
cancellation before publication and truthful print-unvalidated labeling. Static
source checks and unit tests alone do not prove an actual native viewer display.

The implementation lead independently reviewed the concrete geometry contract
and native config/format/manual-opening closure and accepted this bounded scope.
Actual target-runtime display remains a separate verification obligation.
