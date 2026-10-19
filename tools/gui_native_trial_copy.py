"""Explicit relative-E native trial cycles; legacy exact cycles stay unchanged."""
from dataclasses import asdict, dataclass, field, replace
from fractions import Fraction as F
from hashlib import sha256
import json

from orca_plugin.gcode.linear_trace import _advance, _words
from tools.conditional_nominal_body import fingerprint
from tools.conditional_nominal_copy import validate_profile_bound_policy
from tools.conditional_preview_annotations import annotate_conditional_cycle, ConditionalPreviewAnnotationPolicy
from tools.prepare_two_tier_intents import FrozenTwoTierPlan, _supported_cycle_blocks
from tools.supplemental_z_hop import HopPolicy, _text
from tools.native_smooth_dimensions import NativeSmoothDimensionTaper,resolve_tapered_root,emission_hop_for_taper,uses_distinct_emission_bounds
from tools.native_empirical_material import NativeEmpiricalMaterialCorrection, apply_empirical_material_correction
from tools.coupon_spatial_calibration import NativeCouponCalibration, coupon_emission_hop, resolve_coupon_path
from tools.coupon_profile_association import verify_coupon_profile
from tools.stepped_coupon_fixture import verify_stepped_coupon
from tools.native_supplement_end import NativeSupplementEndPolicy, apply_native_end_policy
from tools.gui_native_trial_trace import (
    NativeTrialContext, NativeTrialLimits, NativeTrialAnchor, interpret_native_trial,
    _anchor_from_native_trace, native_profile_caps, checkpoint,
)

STUDIO_NATIVE_METADATA_MARKER = b'; BambuStudio native metadata adapter; original producer OrcaSlicer; adapter Smoothificator'


@dataclass(frozen=True)
class NativeTrialCopyPolicy:
    max_insertions: int
    max_paths: int
    max_output_bytes: int
    max_block_bytes: int
    allow_saved_acceleration_wrapper: bool
    allow_strict_saved_layer_height: bool = False
    enable_studio_native_metadata: bool = False

    def __post_init__(self):
        if (any(type(v) is not int or v<1 for v in (self.max_insertions,self.max_paths,self.max_output_bytes,self.max_block_bytes))
                or type(self.allow_saved_acceleration_wrapper) is not bool
                or type(self.allow_strict_saved_layer_height) is not bool
                or type(self.enable_studio_native_metadata) is not bool):
            raise ValueError('explicit bounded native copy policy required')


@dataclass(frozen=True)
class NativeTrialInsertion:
    byte_offset: int
    plan: FrozenTwoTierPlan
    policy: HopPolicy
    original_floor_anchor_offset: int | None=None


@dataclass(frozen=True)
class NativeTrialInsertionSpan:
    source_byte_offset: int
    output_start: int
    output_end: int
    path_ids: tuple[str,...]
    symbolic_logical_e_delta_mm: F
    inherited_acceleration_mm_s2: F
    executed_acceleration_mm_s2: F


@dataclass(frozen=True)
class NativeTrialCopy:
    output_bytes: bytes
    output_sha256: str
    source_sha256: str
    project_sha256: str
    producer_sha256: str
    context_identity: str
    insertion_spans: tuple[NativeTrialInsertionSpan,...]
    added_path_bounds_mm: tuple[tuple[str,tuple[F,F,F],tuple[F,F,F]],...]
    added_motion_bounds_mm: tuple[tuple[F,F,F],tuple[F,F,F]]
    total_added_relative_e_mm: F
    body_end_counter_translation_candidates_mm: tuple[F,...]
    unresolved_premises: tuple[str,...]
    emission_policy_identity: str
    adapter_prefix: bytes
    physical_authority: bool = field(default=False,init=False)
    whole_original_job_complete: bool = field(default=False,init=False)
    printable_authorized: bool = field(default=False,init=False)


@dataclass(frozen=True)
class NativeTrialCopyRecipe:
    source_bytes: bytes
    project_bytes: bytes
    producer_bytes: bytes
    context: NativeTrialContext
    insertions: tuple[NativeTrialInsertion,...]
    limits: NativeTrialLimits
    copy_policy: NativeTrialCopyPolicy
    geometry_project_bytes: bytes
    annotation_policy: ConditionalPreviewAnnotationPolicy | None = None
    end_policy: NativeSupplementEndPolicy | None = None
    empirical_correction: NativeEmpiricalMaterialCorrection | None = None
    dimension_taper: NativeSmoothDimensionTaper | None = None
    coupon_calibration: NativeCouponCalibration | None = None


@dataclass(frozen=True)
class NativeTrialEmissionPolicy:
    copy: NativeTrialCopyPolicy
    end: NativeSupplementEndPolicy | None
    annotation: ConditionalPreviewAnnotationPolicy | None
    studio_marker: str | None
    empirical_correction: NativeEmpiricalMaterialCorrection | None = None
    dimension_taper: NativeSmoothDimensionTaper | None = None


@dataclass(frozen=True)
class NativeCouponEmissionPolicy:
    native: NativeTrialEmissionPolicy
    calibration: NativeCouponCalibration
    schema: str = 'coupon-spatial-calibration-v1'


def rebuild_native_trial_copy(recipe, *, cancelled):
    from tools.native_prepared_matrix import NativePreparedMatrixRecipe,rebuild_prepared_matrix
    if type(recipe) is NativePreparedMatrixRecipe:
        return rebuild_prepared_matrix(recipe,cancelled=cancelled)
    from tools.native_microextrusion_matrix import NativeMicroextrusionMatrixRecipe,rebuild_microextrusion_matrix
    if type(recipe) is NativeMicroextrusionMatrixRecipe:
        return rebuild_microextrusion_matrix(recipe,cancelled=cancelled)
    if type(recipe) is not NativeTrialCopyRecipe:
        raise ValueError('immutable native copy recipe required')
    return compose_native_trial_copy(recipe.source_bytes,recipe.project_bytes,recipe.producer_bytes,recipe.context,
        recipe.insertions,limits=recipe.limits,copy_policy=recipe.copy_policy,cancelled=cancelled,
        annotation_policy=recipe.annotation_policy,geometry_project=recipe.geometry_project_bytes,end_policy=recipe.end_policy,empirical_correction=recipe.empirical_correction,dimension_taper=recipe.dimension_taper,coupon_calibration=recipe.coupon_calibration)


def _counter_translations(trace, spans):
    """Exact bounded translation alternatives for explicit source branch paths."""
    by_offset={span.source_byte_offset:span.symbolic_logical_e_delta_mm for span in spans}
    translations={F(0)}; stack=[]
    for event in trace.events:
        if event.byte_offset in by_offset:
            translations={number+by_offset[event.byte_offset] for number in translations}
        if event.command=='M622': stack.append(translations.copy())
        elif event.command=='M623': translations|=stack.pop()
        elif event.command=='G92': translations={F(0)}
        if len(translations)>len(spans)+1: raise ValueError('native symbolic counter state budget')
    if trace.events:
        boundary=trace.events[-1].byte_offset+len(trace.events[-1].raw)
        if boundary in by_offset: translations={number+by_offset[boundary] for number in translations}
    return tuple(sorted(translations))


def _validate_native_profile_policy(profile, policy, copy_policy):
    if not copy_policy.allow_strict_saved_layer_height:
        return validate_profile_bound_policy(profile,policy)
    saved_height=profile.setting('layer_height').number()
    maximum=F(str(policy.bounds.max_candidate_height_mm))
    if not 0<maximum<saved_height:
        raise ValueError('native candidate height must be strictly below saved layer height')
    # Adapt only the explicit native height permission. Legacy validation still
    # checks every inherited motion/flow field against the actual saved profile.
    legacy_bounds=replace(policy.bounds,max_candidate_height_mm=float(min(maximum,saved_height*F(9,10))))
    validate_profile_bound_policy(profile,replace(policy,bounds=legacy_bounds))


def _native_cycle(anchor, plan, policy, acceleration_cap, *, trace, annotation_policy, cancelled,end_policy=None,empirical_correction=None):
    """Private zero-counter numeric adapter, never a claimed source counter."""
    if type(anchor) is not NativeTrialAnchor:
        raise ValueError('source-rebuilt native anchor required')
    zero_machine=replace(anchor.saved_state.machine,logical_e_mm=F(0))
    blocks=_supported_cycle_blocks(zero_machine,plan,policy,cancelled=cancelled)
    emitted=[]; delta=F(0); motion_points=[]
    for block,path_id in zip(blocks,plan.execution_order):
        checkpoint(cancelled)
        declared=b'G92 E'+_text(F(0),policy.e_places).encode('ascii')+b'\n'
        lines=block.splitlines(keepends=True)
        if lines.count(declared)!=1 or any(line.startswith(b'G92 ') and line!=declared for line in lines):
            raise ValueError('numeric formatter G92 contract drift')
        block=b''.join(line for line in lines if line!=declared)
        if end_policy is not None:
            frozen=next(p.local_support_numeric_adapter for p in plan.paths if p.intent.path_id==path_id)
            block=apply_native_end_policy(block,frozen,zero_machine,policy,end_policy)
        if annotation_policy is not None:
            frozen=next(p.local_support_numeric_adapter for p in plan.paths if p.intent.path_id==path_id)
            block=annotate_conditional_cycle(block,trace=trace,anchor_offset=anchor.byte_offset,
                frozen_paths=(frozen,),policy=annotation_policy).block
        frozen=next(p.local_support_numeric_adapter for p in plan.paths if p.intent.path_id==path_id)
        expected_amounts=frozen.relative_e_mm
        if empirical_correction is not None:
            block,expected_amounts=apply_empirical_material_correction(block,frozen,empirical_correction.for_path(path_id),policy.e_places,
                hop=policy,material_policy=empirical_correction.policy)
        machine=zero_machine
        for raw in block.splitlines():
            text=raw.split(b';',1)[0].strip().decode('ascii')
            if not text: continue
            command,words=_words(text)
            if command!='G1': raise ValueError('native numeric adapter command drift')
            machine,_=_advance(machine,command,words)
            motion_points.append(machine.xyz_mm)
        if replace(machine,logical_e_mm=F(0))!=zero_machine or machine.logical_e_mm is None:
            raise ValueError('native cycle physical restoration failed')
        expected=sum(expected_amounts,F(0))
        if machine.logical_e_mm!=expected:
            raise ValueError('native symbolic counter delta differs from frozen extrusion')
        delta+=expected; emitted.append(block)
    inherited=anchor.saved_state.acceleration_mm_s2
    executed=min(inherited,acceleration_cap)
    block=b''.join(emitted)
    if executed!=inherited:
        block=(f'M204 S{_text(executed,3)}\n'.encode('ascii')+block+
               f'M204 S{_text(inherited,3)}\n'.encode('ascii'))
    # Replay the complete wrapper, including its exact acceleration restoration.
    machine=zero_machine; acceleration=inherited
    for raw in block.splitlines():
        text=raw.split(b';',1)[0].strip().decode('ascii')
        if not text: continue
        command,words=_words(text)
        if command=='M204':
            if set(words)!={'S'}: raise ValueError('native acceleration wrapper drift')
            acceleration=words['S']
        else: machine,_=_advance(machine,command,words)
    if acceleration!=inherited or replace(machine,logical_e_mm=F(0))!=zero_machine or machine.logical_e_mm!=delta:
        raise ValueError('native wrapper/relative-counter replay failed')
    return block,delta,tuple(motion_points),executed


def _validate_posthop_floor_anchor(trace,context,insertion,anchor,acceleration_cap,jerk_cap,copy_policy,cancelled):
    offset=insertion.original_floor_anchor_offset
    if type(offset) is not int or not context.body_start_offset<=offset<insertion.byte_offset:
        raise ValueError('explicit earlier original-floor anchor required')
    former=_anchor_from_native_trace(trace,context,offset,
        acceleration_cap_mm_s2=acceleration_cap,jerk_cap_mm_s=jerk_cap)
    issues=set(former.eligibility_issues)
    if (copy_policy.allow_saved_acceleration_wrapper and type(former.saved_state.acceleration_mm_s2) is F
            and former.saved_state.acceleration_mm_s2>0):
        issues.discard('native-acceleration-cap-exceeded-or-unknown')
    floor=insertion.plan.original_source_floor_z_mm
    if issues or former.saved_state.machine.xyz_mm[2]!=floor:
        raise ValueError('ineligible original-floor witness')
    interval=tuple(e for e in trace.events if offset<=e.byte_offset<insertion.byte_offset)
    if (not interval or interval[-1].command!='G3' or interval[-1].byte_offset+len(interval[-1].raw)!=insertion.byte_offset
            or interval[-1].arc is None or sum(e.command=='G3' for e in interval)!=1):
        raise ValueError('raised anchor must immediately follow one actual native G3 hop')
    modes=('millimetres','absolute_xyz','relative_e','volumetric_disabled','speed_override_100','flow_override_100')
    debt=former.saved_state.machine.retraction_debt_mm
    for event in interval:
        checkpoint(cancelled)
        if (event.command not in ('','M625','M73','M991','M204','M624','G17','G3') or event.branch_depth
                or event.relative_e_mm!=0 or event.deposited_filament_mm not in (F(0),None)):
            raise ValueError('unsupported/depositing posthop source interval')
        for state in (event.before,event.after):
            if (state.machine.retraction_debt_mm!=debt or any(getattr(state.machine,k) is not True for k in modes)
                    or any(type(v) is not F for v in (*state.machine.xyz_mm,state.machine.feed_mm_min))):
                raise ValueError('posthop debt/modal/XYZ state not preserved')
    raised=anchor.saved_state.machine.xyz_mm[2]
    if (former.saved_state.xy_plane is not True or anchor.saved_state.xy_plane is not True
            or anchor.saved_state.object_token!=former.saved_state.object_token
            or raised!=insertion.plan.original_next_layer_z_mm+insertion.policy.z_hop_mm
            or raised>insertion.policy.printable_height_mm
            or any(raised<=p.intent.points_mm[0][2] for p in insertion.plan.paths)):
        raise ValueError('raised original hop differs from source-profile/candidate envelope')


def compose_native_trial_copy(source,project,producer_bytes,context,insertions,*,geometry_project,limits,copy_policy,cancelled,annotation_policy=None,end_policy=None,empirical_correction=None,dimension_taper=None,coupon_calibration=None):
    if type(copy_policy) is not NativeTrialCopyPolicy or type(limits) is not NativeTrialLimits or type(context) is not NativeTrialContext:
        raise ValueError('immutable native copy context and limits required')
    if annotation_policy is not None and type(annotation_policy) is not ConditionalPreviewAnnotationPolicy:
        raise ValueError('immutable native preview annotation policy required')
    if empirical_correction is not None and type(empirical_correction) is not NativeEmpiricalMaterialCorrection:
        raise ValueError('immutable native empirical correction required')
    if empirical_correction is not None and (end_policy is None
            or end_policy.retract_mm!=empirical_correction.policy.retract_mm
            or end_policy.wipe_mm!=empirical_correction.policy.wipe_mm):
        raise ValueError('empirical saved end policy mismatch')
    if dimension_taper is not None and (type(dimension_taper) is not NativeSmoothDimensionTaper or empirical_correction is not None):
        raise ValueError('distinct immutable dimension taper cannot combine empirical E correction')
    if coupon_calibration is not None and (type(coupon_calibration) is not NativeCouponCalibration or dimension_taper is not None or empirical_correction is not None):
        raise ValueError('distinct immutable specimen calibration required')
    if coupon_calibration is not None and coupon_calibration.geometry_sha256!=context.geometry_project_sha256:
        raise ValueError('specimen profile geometry identity differs from source context')
    if coupon_calibration is not None:
        if coupon_calibration.stepped_fixture is None:verify_coupon_profile(geometry_project,coupon_calibration.placed_profile)
        else:verify_stepped_coupon(geometry_project,coupon_calibration.placed_profile,coupon_calibration.stepped_fixture)
    if copy_policy.enable_studio_native_metadata:
        if annotation_policy is None or b'; generated by OrcaSlicer ' not in source[:512]:
            raise ValueError('Studio metadata adapter requires frozen annotations and actual OrcaSlicer provenance')
    if STUDIO_NATIVE_METADATA_MARKER in source:
        raise ValueError('existing Studio metadata adapter rejects repeated composition')
    if (type(insertions) is not tuple or not insertions or len(insertions)>copy_policy.max_insertions
            or any(type(i) is not NativeTrialInsertion for i in insertions)):
        raise ValueError('bounded immutable native insertion tuple required')
    if any(marker in source for marker in (b'SUPPLEMENTAL_CYCLE_',b'ADAPTIVE_SUBEDGE_',b'NATIVE_TRIAL_')):
        raise ValueError('already supplemented native source')
    trace=interpret_native_trial(source,project,producer_bytes,context,geometry_project=geometry_project,limits=limits,cancelled=cancelled)
    profile,acceleration_cap,jerk_cap=native_profile_caps(source,project,geometry_project,limits,cancelled=cancelled)
    adapter_prefix=STUDIO_NATIVE_METADATA_MARKER+b'\n' if copy_policy.enable_studio_native_metadata else b''
    output=[adapter_prefix]; spans=[]; path_bounds=[]; motion_points=[]; previous=0; total=len(adapter_prefix); counter=F(0); ids=set()
    for insertion in insertions:
        checkpoint(cancelled)
        if type(insertion.byte_offset) is not int or insertion.byte_offset<=previous:
            raise ValueError('strictly increasing native insertion offsets required')
        if type(insertion.plan) is not FrozenTwoTierPlan or insertion.plan.source_context_identity!=trace.context_identity:
            raise ValueError('native plan not bound to current source context')
        _validate_native_profile_policy(profile,insertion.policy,copy_policy)
        if coupon_calibration is not None:
            if coupon_calibration.reference_taper.policy.admission_layer_height_mm!=profile.setting('layer_height').number():
                raise ValueError('specimen reference differs from saved global layer height')
            for path in insertion.plan.paths:
                original=coupon_calibration.for_path(path.intent.path_id)
                _validate_native_profile_policy(profile,original.admission_hop,copy_policy)
                if coupon_emission_hop(original.admission_hop,coupon_calibration.policy)!=insertion.policy:
                    raise ValueError('specimen emission differs from two-minimum bounds adapter')
                if original.reference_intent.source_context_identity!=trace.context_identity:
                    raise ValueError('specimen original source context differs')
                transformed,_=resolve_coupon_path(original,coupon_calibration)
                if transformed!=path.intent:raise ValueError('specimen intent differs from authoritative geometry transform')
        if dimension_taper is not None:
            if dimension_taper.policy.admission_layer_height_mm!=profile.setting('layer_height').number():
                raise ValueError('dimension taper admission differs from saved profile/plan bounds')
            for path in insertion.plan.paths:
                original=dimension_taper.for_path(path.intent.path_id)
                admission_hop=original.admission_hop if uses_distinct_emission_bounds(dimension_taper.policy) else insertion.policy
                _validate_native_profile_policy(profile,admission_hop,copy_policy)
                if emission_hop_for_taper(admission_hop,dimension_taper.policy)!=insertion.policy:
                    raise ValueError('dimension emission policy differs from original bounds-only adapter')
                if original.original_intent.source_context_identity!=trace.context_identity:
                    raise ValueError('dimension taper original source context differs')
                decision=resolve_tapered_root(original,admission_hop,dimension_taper.policy)
                if decision.resolved_intent!=path.intent:
                    raise ValueError('dimension taper intent differs from authoritative mapping/refreeze')
        if empirical_correction is not None and (empirical_correction.policy.admission_layer_height_mm!=profile.setting('layer_height').number()
                or empirical_correction.policy.admission_minimum_width_mm!=F(str(insertion.policy.bounds.min_candidate_width_mm))):
            raise ValueError('empirical admission policy differs from saved profile/nominal bounds')
        if empirical_correction is not None and empirical_correction.policy.minimum_modeled_thickness_mm is not None and empirical_correction.policy.minimum_modeled_thickness_mm!=F(str(insertion.policy.bounds.min_candidate_height_mm)):
            raise ValueError('empirical minimum thickness differs from nominal plan bound')
        anchor=_anchor_from_native_trace(trace,context,insertion.byte_offset,
            acceleration_cap_mm_s2=acceleration_cap,jerk_cap_mm_s=jerk_cap)
        issues=set(anchor.eligibility_issues)
        if (copy_policy.allow_saved_acceleration_wrapper and type(anchor.saved_state.acceleration_mm_s2) is F
                and anchor.saved_state.acceleration_mm_s2>0):
            issues.discard('native-acceleration-cap-exceeded-or-unknown')
        if issues: raise ValueError('ineligible native anchor: '+','.join(sorted(issues)))
        if anchor.saved_state.xy_plane is not True: raise ValueError('known native XY arc plane required')
        floor=insertion.plan.original_source_floor_z_mm
        if insertion.original_floor_anchor_offset is None:
            if floor!=anchor.saved_state.machine.xyz_mm[2]: raise ValueError('native plan floor differs from saved source Z')
        else:
            _validate_posthop_floor_anchor(trace,context,insertion,anchor,acceleration_cap,jerk_cap,copy_policy,cancelled)
        future=[]
        for event in trace.events:
            if event.byte_offset<insertion.byte_offset or event.relative_e_mm<=0: continue
            if event.deposited_filament_mm is None:
                raise ValueError('unknown future deposited material cannot establish completed original floor')
            if event.deposited_filament_mm>0: future.append(event)
        if not future or any(any(type(z) is not F or z<=floor for z in
                (e.before.machine.xyz_mm[2],e.after.machine.xyz_mm[2])) for e in future):
            raise ValueError('native anchor must follow all deposition on its original floor')
        if future[0].after.machine.xyz_mm[2]!=insertion.plan.original_next_layer_z_mm:
            raise ValueError('native plan next layer differs from actual future deposition')
        wall=[e.after.machine.feed_mm_min for e in trace.events if e.byte_offset<insertion.byte_offset
              and e.feature=='Outer wall' and e.deposited_filament_mm is not None and e.deposited_filament_mm>0
              and (e.arc is not None or e.before.machine.xyz_mm[:2]!=e.after.machine.xyz_mm[:2])
              and e.after.machine.xyz_mm[2]==floor]
        if not wall or any(type(v) is not F or v<=0 for v in wall) or insertion.policy.candidate_speed_mm_s>min(wall)/60:
            raise ValueError('native candidate speed exceeds complete original-floor outer-wall cap')
        for path in insertion.plan.paths:
            if path.intent.path_id in ids: raise ValueError('duplicate native path ID')
            ids.add(path.intent.path_id)
            if len(ids)>copy_policy.max_paths: raise ValueError('native path budget')
            points=path.local_support_numeric_adapter.path.points_mm
            radius=F(str(path.local_support_numeric_adapter.physical_width_mm[0]))/2
            path_bounds.append((path.intent.path_id,(min(p[0] for p in points)-radius,min(p[1] for p in points)-radius,
                points[0][2]-path.intent.physical_height_mm),(max(p[0] for p in points)+radius,
                max(p[1] for p in points)+radius,points[0][2])))
        block,delta,points,executed=_native_cycle(anchor,insertion.plan,insertion.policy,acceleration_cap,
            trace=trace,annotation_policy=annotation_policy,cancelled=cancelled,end_policy=end_policy,empirical_correction=empirical_correction)
        if len(block)>copy_policy.max_block_bytes: raise ValueError('native block byte budget')
        unchanged=source[previous:insertion.byte_offset]
        output.extend((unchanged,block)); total+=len(unchanged)
        spans.append(NativeTrialInsertionSpan(insertion.byte_offset,total,total+len(block),insertion.plan.execution_order,
            delta,anchor.saved_state.acceleration_mm_s2,executed))
        total+=len(block)
        if total+len(source)-insertion.byte_offset>copy_policy.max_output_bytes: raise ValueError('native output byte budget')
        previous=insertion.byte_offset; counter+=delta; motion_points.extend(points)
    if empirical_correction is not None and {p.path_id for p in empirical_correction.paths}!=ids:
        raise ValueError('empirical correction coverage differs from inserted paths')
    if dimension_taper is not None and {p.original_intent.path_id for p in dimension_taper.paths}!=ids:
        raise ValueError('dimension taper coverage differs from inserted paths')
    if coupon_calibration is not None and {p.reference_intent.path_id for p in coupon_calibration.paths}!=ids:
        raise ValueError('specimen calibration coverage differs from inserted paths')
    output.append(source[previous:]); content=b''.join(output)
    checkpoint(cancelled)
    bounds=tuple(tuple(operation(p[i] for p in motion_points) for i in range(3)) for operation in (min,max))
    emission_policy=NativeTrialEmissionPolicy(copy_policy,end_policy,annotation_policy,
        STUDIO_NATIVE_METADATA_MARKER.decode('ascii') if copy_policy.enable_studio_native_metadata else None,empirical_correction,dimension_taper)
    if coupon_calibration is None:emission_identity=fingerprint(emission_policy)
    else:
        specimen=NativeCouponEmissionPolicy(emission_policy,coupon_calibration)
        if coupon_calibration.policy.schema_version<3:
            legacy=asdict(specimen);legacy['calibration'].pop('stepped_fixture');legacy['calibration']['policy'].pop('reference_geometry_sha256')
            if coupon_calibration.policy.schema_version==1:legacy['calibration']['policy'].pop('coordinate')
            emission_identity=sha256(json.dumps(legacy,sort_keys=True,separators=(',',':'),default=str).encode('ascii')).hexdigest()
        else:emission_identity=fingerprint(specimen)
    return NativeTrialCopy(content,sha256(content).hexdigest(),context.source_sha256,context.project_sha256,context.producer_sha256,
        trace.context_identity,tuple(spans),tuple(path_bounds),bounds,counter,_counter_translations(trace,spans),context.unresolved_premises+
        ('logical-counter-translation-until-executed-original-G92','opaque-prefix-and-suffix-unverified','source-and-candidate-geometry-requires-separate-audit'),
        emission_identity,adapter_prefix)
