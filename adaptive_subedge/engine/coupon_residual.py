"""Bounded, research-only comparison of nominal top against a proven planar mesh coupon."""
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable

from adaptive_subedge.domain.coupon_residual import CouponVerticalComparison, VerticalResidualInterval
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY

from .planar_cell_top import certify_planar_cell_top
from .support_cell import query_exact_nominal_top_cell, query_exact_nominal_top_point


_TARGET_REJECTION_REASONS = frozenset((
    "empty-mesh", "unused-vertex", "degenerate-bounds", "degenerate-triangle",
    "duplicate-triangle", "nonmanifold-edge", "inconsistent-winding",
    "disconnected-shell", "nonmanifold-vertex", "zero-signed-volume",
    "self-intersection", "no-top-facing-facet", "ambiguous-top-plane",
    "above-top-plane", "uncovered-top",
))


@dataclass(frozen=True, slots=True)
class _Leaf:
    cell: ExactTopCellXY
    depth: int
    baseline: VerticalResidualInterval | None
    augmented: VerticalResidualInterval | None


class _Outcome(Exception):
    def __init__(self, reason: str):
        self.reason = reason


def compare_planar_coupon_vertical_residual(
    mesh: IndexedTriangleMesh, rectangle: ExactTopCellXY,
    structural_sources: tuple[ExactNominalTopSegment, ...],
    candidate_sources: tuple[ExactNominalTopSegment, ...], *,
    source_mesh_id: str, baseline_slice_id: str,
    max_vertices: int, max_triangles: int, max_mesh_pair_checks: int,
    max_cell_vertices: int, max_centroid_tests: int, max_facet_clip_tests: int,
    max_sources: int, max_coordinate_bits: int, sqrt_fraction_bits: int,
    max_refinement_depth: int, max_leaf_cells: int,
    cancelled: Callable[[], bool],
) -> CouponVerticalComparison:
    """Return only certified bounds; identities remain unverified caller assertions."""
    budgets = (max_vertices, max_triangles, max_mesh_pair_checks, max_cell_vertices,
               max_centroid_tests, max_facet_clip_tests, max_sources,
               max_coordinate_bits, max_leaf_cells)
    if (any(type(v) is not int or v < 1 for v in budgets)
            or type(sqrt_fraction_bits) is not int or not 1 <= sqrt_fraction_bits <= 4096
            or type(max_refinement_depth) is not int or max_refinement_depth < 0
            or not callable(cancelled)):
        raise ContractError(ReasonCode.INVALID_SETTING, "invalid coupon comparison budgets")
    if (type(mesh) is not IndexedTriangleMesh or type(rectangle) is not ExactTopCellXY
            or type(structural_sources) is not tuple or type(candidate_sources) is not tuple
            or not candidate_sources or type(source_mesh_id) is not str or not source_mesh_id.strip()
            or type(baseline_slice_id) is not str or not baseline_slice_id.strip()):
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid coupon comparison inputs")

    def stopped() -> bool:
        answer = cancelled()
        if type(answer) is not bool:
            raise ContractError(ReasonCode.INVALID_SETTING, "cancellation callback must return exact bool")
        return answer

    def check() -> None:
        if stopped():
            raise _Outcome("cancelled")

    leaves: list[_Leaf] = []

    def publish(state: str, reason: str, baseline=None, augmented=None, plane=None):
        check()
        result = CouponVerticalComparison(state, reason, source_mesh_id, baseline_slice_id,
                                          rectangle if state == "complete" else None,
                                          plane if state == "complete" else None,
                                          baseline, augmented, len(leaves))
        check()
        return result

    try:
        check()
        if len(structural_sources) + len(candidate_sources) > max_sources:
            return publish("incomplete", "resource-limit")
        identifiers: set[str] = set()
        for source, kind in ((*((source, "structural") for source in structural_sources),
                              *((source, "candidate") for source in candidate_sources))):
            check()
            if (type(source) is not ExactNominalTopSegment or source.source_kind != kind
                    or source.segment_id in identifiers):
                raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid coupon source identity or kind")
            identifiers.add(source.segment_id)
        check()
        if any(v.bit_length() > max_coordinate_bits
               for coordinate in (rectangle.x_min_mm, rectangle.x_max_mm,
                                  rectangle.y_min_mm, rectangle.y_max_mm)
               for v in (coordinate.numerator, coordinate.denominator)):
            return publish("incomplete", "resource-limit")
        corners = ((rectangle.x_min_mm, rectangle.y_min_mm),
                   (rectangle.x_max_mm, rectangle.y_min_mm),
                   (rectangle.x_max_mm, rectangle.y_max_mm),
                   (rectangle.x_min_mm, rectangle.y_max_mm))
        certificate = certify_planar_cell_top(
            mesh, corners, algorithm_version="planar_cell_top_v1",
            max_vertices=max_vertices, max_triangles=max_triangles,
            max_mesh_pair_checks=max_mesh_pair_checks, max_cell_vertices=max_cell_vertices,
            max_centroid_tests=max_centroid_tests, max_facet_clip_tests=max_facet_clip_tests,
            cancelled=cancelled)
        check()
        if certificate.state == "incomplete":
            if certificate.reason not in ("cancelled", "resource-limit"):
                raise ContractError(ReasonCode.INVALID_GEOMETRY, "unknown top certificate failure")
            return publish("incomplete", certificate.reason)
        if certificate.state == "rejected":
            if certificate.reason not in _TARGET_REJECTION_REASONS:
                raise ContractError(ReasonCode.INVALID_GEOMETRY, "unknown top certificate rejection")
            return publish("rejected", "target-unresolved")
        if certificate.state != "complete" or certificate.reason != "planar-top-covered":
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "unknown top certificate outcome")
        plane = (certificate.plane_a, certificate.plane_b, certificate.plane_c_mm)
        baseline_sources = structural_sources
        augmented_sources = structural_sources + candidate_sources
        query_options = dict(max_sources=max_sources, max_coordinate_bits=max_coordinate_bits,
                             sqrt_fraction_bits=sqrt_fraction_bits, cancelled=cancelled)

        def top(query, *args):
            check()
            outcome = query(*args, **query_options)
            check()
            if outcome.state == "incomplete":
                if outcome.reason not in ("cancelled", "resource-limit"):
                    raise ContractError(ReasonCode.INVALID_GEOMETRY, "unknown nominal top failure")
                raise _Outcome(outcome.reason)
            if outcome.state not in ("full-bounded", "absent", "unresolved-partial"):
                raise ContractError(ReasonCode.INVALID_GEOMETRY, "unknown nominal top outcome")
            return outcome

        def residual(cell, sources):
            check()
            whole = top(query_exact_nominal_top_cell, cell, sources)
            if whole.state != "full-bounded":
                return None
            sample_xy = ((cell.x_min_mm, cell.y_min_mm),
                         (cell.x_max_mm, cell.y_min_mm),
                         (cell.x_max_mm, cell.y_max_mm),
                         (cell.x_min_mm, cell.y_max_mm),
                         ((cell.x_min_mm + cell.x_max_mm)/2,
                          (cell.y_min_mm + cell.y_max_mm)/2))
            heights = tuple(plane[0]*x + plane[1]*y + plane[2] for x, y in sample_xy)
            minimum, maximum = min(heights), max(heights)
            upper = max(abs(m-t) for m in (minimum, maximum)
                        for t in (whole.top_z_lower_mm, whole.top_z_upper_mm))
            lower = Fraction(0)
            for (x, y), target in zip(sample_xy, heights):
                check()
                point = top(query_exact_nominal_top_point, x, y, sources)
                if point.state != "full-bounded":
                    return None
                lower = max(lower, point.top_z_lower_mm-target,
                            target-point.top_z_upper_mm)
            if lower > upper:
                raise ContractError(ReasonCode.INVALID_GEOMETRY, "residual interval inverted")
            return VerticalResidualInterval(lower, upper)

        def evaluate(cell, depth):
            check()
            baseline = residual(cell, baseline_sources)
            augmented = residual(cell, augmented_sources)
            return _Leaf(cell, depth, baseline, augmented)

        leaves.append(evaluate(rectangle, 0))
        while True:
            check()
            if all(leaf.baseline is not None and leaf.augmented is not None for leaf in leaves):
                baseline = VerticalResidualInterval(
                    max(leaf.baseline.lower_mm for leaf in leaves),
                    max(leaf.baseline.upper_mm for leaf in leaves))
                augmented = VerticalResidualInterval(
                    max(leaf.augmented.lower_mm for leaf in leaves),
                    max(leaf.augmented.upper_mm for leaf in leaves))
                if augmented.upper_mm < baseline.lower_mm:
                    return publish("complete", "certified-reduction", baseline, augmented, plane)
                if augmented.lower_mm >= baseline.upper_mm:
                    return publish("complete", "certified-nonreduction", baseline, augmented, plane)
            def priority(leaf):
                cell = leaf.cell
                uncovered = leaf.baseline is None or leaf.augmented is None
                width = Fraction(0) if uncovered else max(
                    leaf.baseline.upper_mm-leaf.baseline.lower_mm,
                    leaf.augmented.upper_mm-leaf.augmented.lower_mm)
                return (not uncovered, -width, cell.x_min_mm, cell.y_min_mm,
                        cell.x_max_mm, cell.y_max_mm)
            chosen = min(leaves, key=priority)
            if chosen.depth >= max_refinement_depth or len(leaves)+3 > max_leaf_cells:
                if any(leaf.baseline is None or leaf.augmented is None for leaf in leaves):
                    return publish("incomplete", "coverage-unresolved")
                return publish("complete", "interval-overlap", baseline, augmented, plane)
            check()
            cell = chosen.cell
            middle_x = (cell.x_min_mm+cell.x_max_mm)/2
            middle_y = (cell.y_min_mm+cell.y_max_mm)/2
            children = (
                ExactTopCellXY(cell.x_min_mm, middle_x, cell.y_min_mm, middle_y),
                ExactTopCellXY(middle_x, cell.x_max_mm, cell.y_min_mm, middle_y),
                ExactTopCellXY(cell.x_min_mm, middle_x, middle_y, cell.y_max_mm),
                ExactTopCellXY(middle_x, cell.x_max_mm, middle_y, cell.y_max_mm),
            )
            new_leaves = []
            for child in children:
                check()
                new_leaves.append(evaluate(child, chosen.depth+1))
            leaves.remove(chosen)
            leaves.extend(new_leaves)
    except _Outcome as failure:
        reason = "cancelled" if stopped() else failure.reason
        result = CouponVerticalComparison("incomplete", reason, source_mesh_id,
                                          baseline_slice_id, None, None, None, None, len(leaves))
        if stopped() and reason != "cancelled":
            return CouponVerticalComparison("incomplete", "cancelled", source_mesh_id,
                                            baseline_slice_id, None, None, None, None, len(leaves))
        return result
