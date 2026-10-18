"""Root-only nonlinear dimension mapping and bounded numeric representation."""
from dataclasses import dataclass,replace
from fractions import Fraction as F
import re

from adaptive_subedge.domain.smooth_dimensions import SmoothDimensionPolicy, SmoothDimensionTargets
from adaptive_subedge.engine.smooth_dimensions import validate_resolved_policy,target_dimensions_for_section
from tools.prepare_two_tier_intents import SupportedPathIntent
from tools.freeze_supplemental_emission import freeze_numeric_emission
from tools.supplemental_z_hop import SupplementalPath,HopPolicy


def uses_distinct_emission_bounds(policy):
    validate_resolved_policy(policy)
    return policy.research_endpoint_envelope or policy.schema_version>=4


@dataclass(frozen=True)
class NativeSmoothDimensionSourcePath:
    original_intent: SupportedPathIntent
    section_base_mm: F
    section_rise_mm: F
    original_plan_identity: str
    admission_hop: HopPolicy | None = None

    def __post_init__(self):
        if (type(self.original_intent) is not SupportedPathIntent
                or any(type(v) is not F or v<0 or max(v.numerator.bit_length(),v.denominator.bit_length())>256
                       for v in (self.section_base_mm,self.section_rise_mm)) or self.section_base_mm<=0
                or type(self.original_plan_identity) is not str or re.fullmatch('[0-9a-f]{64}',self.original_plan_identity) is None
                or self.admission_hop is not None and type(self.admission_hop) is not HopPolicy):
            raise ValueError('immutable bounded dimension taper source path required')


@dataclass(frozen=True)
class NativeSmoothDimensionTaper:
    policy: SmoothDimensionPolicy
    original_plans_sha256: str
    paths: tuple[NativeSmoothDimensionSourcePath,...]

    def __post_init__(self):
        validate_resolved_policy(self.policy)
        if (type(self.original_plans_sha256) is not str or re.fullmatch('[0-9a-f]{64}',self.original_plans_sha256) is None
                or type(self.paths) is not tuple or not 0<len(self.paths)<=1000
                or any(type(p) is not NativeSmoothDimensionSourcePath for p in self.paths)
                or len({p.original_intent.path_id for p in self.paths})!=len(self.paths)):
            raise ValueError('unique bounded immutable dimension taper paths required')
        if any((p.admission_hop is not None)!=uses_distinct_emission_bounds(self.policy) for p in self.paths):
            raise ValueError('version-bound original admission policy required for separate endpoints')

    def for_path(self,path_id):
        matches=tuple(p for p in self.paths if p.original_intent.path_id==path_id)
        if len(matches)!=1:raise ValueError('missing original dimension taper path')
        return matches[0]


@dataclass(frozen=True)
class NativeSmoothDimensionDecision:
    path_id: str
    targets: SmoothDimensionTargets
    resolved_intent: SupportedPathIntent | None
    width_attempts_mm: tuple[F,...]
    reason: str
    width_expansion_mm: F = F(0)


def emission_hop_for_taper(admission_hop,policy):
    """Explicit V3 research envelope; every non-minimum field remains unchanged."""
    validate_resolved_policy(policy)
    if type(admission_hop) is not HopPolicy:
        raise ValueError('immutable original admission HopPolicy required')
    if policy.admission_minimum_width_mm!=F(str(admission_hop.bounds.min_candidate_width_mm)):
        raise ValueError('dimension source admission width differs from original policy')
    if not uses_distinct_emission_bounds(policy):
        return admission_hop
    bounds=replace(admission_hop.bounds,min_candidate_height_mm=float(policy.minimum_height_mm),
        min_candidate_width_mm=float(policy.minimum_width_mm))
    return replace(admission_hop,bounds=bounds)


def resolve_tapered_root(source_path,hop,policy):
    """Preserve root floor/XY; use first bounded width with ordinary full-E freeze."""
    validate_resolved_policy(policy)
    if policy.maximum_extra_width_ticks*policy.dimension_grid_mm>F('.001'):
        raise ValueError('dimension width exception exceeds absolute representation cap')
    admission_hop=source_path.admission_hop if uses_distinct_emission_bounds(policy) else hop
    numeric_hop=emission_hop_for_taper(admission_hop,policy)
    if hop not in (admission_hop,numeric_hop):
        raise ValueError('dimension emission policy differs from bounds-only adapter')
    hop=numeric_hop
    original=source_path.original_intent
    if (original.parent_path_id is not None or original.support_plane_z_mm!=original.original_source_floor_z_mm
            or original.remaining_height_mm!=original.physical_height_mm
            or any(p[2]!=original.support_plane_z_mm+original.physical_height_mm for p in original.points_mm)):
        raise ValueError('dimension taper requires original zero-overlap roots')
    if (policy.admission_minimum_width_mm!=F(str(admission_hop.bounds.min_candidate_width_mm))
            or policy.minimum_height_mm<F(str(hop.bounds.min_candidate_height_mm))
            or policy.minimum_width_mm<F(str(hop.bounds.min_candidate_width_mm))):
        raise ValueError('dimension taper minima differ from allowed numeric bounds')
    if uses_distinct_emission_bounds(policy):
        if original.points_mm[0][2]>=original.original_next_layer_z_mm:
            raise ValueError('original research source candidate reaches next layer')
        freeze_numeric_emission(SupplementalPath(original.path_id,original.support_plane_z_mm,original.width_mm,
            original.physical_height_mm,original.points_mm),admission_hop)
    targets=target_dimensions_for_section(source_path.section_base_mm,source_path.section_rise_mm,
        original.width_mm,original.physical_height_mm,policy)
    if targets.angle_degrees>policy.maximum_angle_degrees:
        raise ValueError('dimension source section exceeds existing admission maximum')
    if targets.retention==1:
        height=original.physical_height_mm;widths=(original.width_mm,)
    else:
        grid=policy.dimension_grid_mm
        quotient=targets.target_height_mm/grid
        height=max(policy.minimum_height_mm,min(original.physical_height_mm,
            F(quotient.numerator//quotient.denominator)*grid))
        quotient=targets.target_width_mm/grid
        first=F(-(-quotient.numerator//quotient.denominator))*grid
        widths=[];width=first
        while width<=original.width_mm:
            widths.append(width)
            if len(widths)>policy.maximum_width_ticks:raise ValueError('dimension width representation budget')
            width+=grid
        if original.width_mm not in widths:widths.append(original.width_mm)
        if len(widths)>policy.maximum_width_ticks:raise ValueError('dimension width representation budget')
        widths=tuple(widths)
    if targets.retention<1 and policy.maximum_extra_width_ticks:
        extra=original.width_mm+policy.dimension_grid_mm
        if extra<=F(str(hop.bounds.max_candidate_width_mm)):
            widths=tuple(widths)+(extra,)
        if len(widths)>policy.maximum_width_ticks:raise ValueError('dimension width representation budget')
    tried=[]
    for width in widths:
        if not targets.target_width_mm<=width<=original.width_mm+policy.dimension_grid_mm*policy.maximum_extra_width_ticks:
            raise ValueError('dimension representation exceeds width exception policy')
        transformed=replace(original,width_mm=width,physical_height_mm=height,remaining_height_mm=height,
            points_mm=tuple((x,y,original.support_plane_z_mm+height) for x,y,z in original.points_mm))
        tried.append(width)
        try:
            freeze_numeric_emission(SupplementalPath(transformed.path_id,transformed.support_plane_z_mm,
                width,height,transformed.points_mm),hop)
        except ValueError as failure:
            if str(failure)!='nearest E implies width outside bounds':raise
            continue
        return NativeSmoothDimensionDecision(original.path_id,targets,transformed,tuple(tried),
            'standard-numeric-freeze-passed' if width<=original.width_mm else 'standard-numeric-freeze-passed-one-width-tick-expansion',
            max(F(0),width-original.width_mm))
    return NativeSmoothDimensionDecision(original.path_id,targets,None,tuple(tried),'width-unrepresentable-within-representation-policy')

