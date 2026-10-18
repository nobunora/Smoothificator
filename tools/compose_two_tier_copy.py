"""Opt-in source-bound supported graph copy; no fictitious raised source walls."""
from dataclasses import dataclass, field
from hashlib import sha256
import os
from pathlib import Path
import tempfile

from orca_plugin.gcode.linear_trace import trace_linear_execution
from orca_plugin.gcode.source_profile import read_sliced_profile
from tools.conditional_nominal_body import fingerprint, interpret_nominal_body
from tools.conditional_nominal_copy import (
    ConditionalPathInput, DerivedPathAssociation, NominalBodyAnchorProposal, _anchor_from_trace, _context_identity,
    associate_derived_path, validate_profile_bound_policy,
)
from tools.conditional_preview_annotations import ConditionalPreviewAnnotationPolicy, annotate_conditional_cycle
from tools.prepare_two_tier_intents import FrozenTwoTierPlan, _supported_cycle_blocks
from tools.freeze_supplemental_emission import FrozenSupplementalEmission
from tools.supplemental_z_hop import HopPolicy


@dataclass(frozen=True)
class TwoTierCopyPolicy:
    max_source_bytes: int
    max_source_events: int
    max_insertions: int
    max_paths: int
    max_output_bytes: int

    def __post_init__(self):
        if any(type(getattr(self,n)) is not int or getattr(self,n)<1 for n in self.__dataclass_fields__):
            raise ValueError('finite positive exact copy limits required')


@dataclass(frozen=True)
class SupportedConditionalInsertion:
    anchor: NominalBodyAnchorProposal
    plan: FrozenTwoTierPlan
    emission_policy: HopPolicy
    original_floor_roots: tuple[ConditionalPathInput, ...]


@dataclass(frozen=True)
class SupportedInsertionSpan:
    source_byte_offset: int
    output_start: int
    output_end: int
    graph_identity: str
    execution_order: tuple[str, ...]
    root_association_identities: tuple[tuple[str,str], ...]
    child_support_identities: tuple[tuple[str,str,str], ...]
    preview_annotation_identities: tuple[str, ...]


@dataclass(frozen=True)
class TwoTierConditionalCopy:
    source_sha256: str
    project_sha256: str
    producer_sha256: str
    context_identity: str
    copy_policy: TwoTierCopyPolicy
    annotation_policy_identity: str | None
    output_bytes: bytes
    output_sha256: str
    insertion_spans: tuple[SupportedInsertionSpan, ...]
    physical_authority: bool = field(default=False, init=False)
    printable_authorized: bool = field(default=False, init=False)
    runtime_injection_authorized: bool = field(default=False, init=False)
    whole_original_job_interactions_complete: bool = field(default=False, init=False)


def _checkpoint(cancelled):
    answer=cancelled()
    if type(answer) is not bool or answer:
        raise ValueError('supported copy cancelled or invalid cancellation result')


def compose_two_tier_copy(inputs, insertions, *, copy_policy, cancelled, annotation_policy=None):
    if (type(inputs) is not tuple or len(inputs)!=6 or type(copy_policy) is not TwoTierCopyPolicy
            or not callable(cancelled) or type(insertions) is not tuple
            or not 0<len(insertions)<=copy_policy.max_insertions
            or any(type(i) is not SupportedConditionalInsertion for i in insertions)
            or annotation_policy is not None and type(annotation_policy) is not ConditionalPreviewAnnotationPolicy):
        raise ValueError('exact bounded supported-copy inputs required')
    _checkpoint(cancelled)
    source,project,producer,descriptor,entry,motion=inputs
    if (type(source) is not bytes or len(source)>copy_policy.max_source_bytes
            or len(source.splitlines())>copy_policy.max_source_events):
        raise ValueError('supported source byte/event budget exceeded')
    if any(marker in source for marker in (b'SUPPLEMENTAL_CYCLE_',b'TWO_TIER_UNVERIFIED',b'ADAPTIVE_SUBEDGE_',b'CONDITIONAL_NOMINAL_')):
        raise ValueError('existing insertion marker rejects repeated supported copy')
    trace=interpret_nominal_body(*inputs)
    if len(trace.events)>copy_policy.max_source_events:
        raise ValueError('interpreted supported source event budget exceeded')
    context=_context_identity(trace)
    profile=read_sliced_profile(project,source,include_motion_caps=True)
    previous=-1
    path_ids=set()
    blocks=[]
    annotation_count=0
    for insertion in insertions:
        _checkpoint(cancelled)
        if (type(insertion.plan) is not FrozenTwoTierPlan or type(insertion.anchor) is not NominalBodyAnchorProposal
                or type(insertion.emission_policy) is not HopPolicy):
            raise ValueError('exact supported graph/anchor required')
        plan,anchor,policy=insertion.plan,insertion.anchor,insertion.emission_policy
        validate_profile_bound_policy(profile,policy)
        if any(p.intent.physical_height_mm>profile.setting('layer_height').number()*9/10 for p in plan.paths):
            raise ValueError('supported physical height exceeds90% saved source layer height')
        rebuilt=_anchor_from_trace(descriptor,trace,entry,motion,anchor.byte_offset)
        if rebuilt!=anchor or anchor.eligibility_issues or anchor.byte_offset<=previous:
            raise ValueError('ineligible/stale/unordered supported anchor')
        previous=anchor.byte_offset
        if plan.source_context_identity!=context:
            raise ValueError('foreign/stale supported graph source context')
        future_material=tuple(e for e in trace.events if e.byte_offset>=anchor.byte_offset
            and e.deposited_filament_mm is not None and e.deposited_filament_mm>0
            and e.before.xyz_mm[:2]!=e.after.xyz_mm[:2])
        if (not future_material or future_material[0].before.xyz_mm[2]!=future_material[0].after.xyz_mm[2]
                or future_material[0].after.xyz_mm[2]!=plan.original_next_layer_z_mm
                or plan.original_next_layer_z_mm<=plan.original_source_floor_z_mm):
            raise ValueError('supported original next layer is not the first actual future material plane')
        if type(insertion.original_floor_roots) is not tuple or any(type(p) is not ConditionalPathInput for p in insertion.original_floor_roots):
            raise ValueError('exact original-floor root associations required')
        if any(type(p.frozen_emission) is not FrozenSupplementalEmission or type(p.association) is not DerivedPathAssociation
               for p in insertion.original_floor_roots):
            raise ValueError('exact frozen root and original source association types required')
        roots={p.frozen_emission.path.path_id:p for p in insertion.original_floor_roots}
        expected_roots={p.intent.path_id for p in plan.paths if p.intent.parent_path_id is None}
        if len(roots)!=len(insertion.original_floor_roots) or set(roots)!=expected_roots:
            raise ValueError('complete unique original-floor root associations required')
        root_ids={}
        by_id={p.intent.path_id:p for p in plan.paths}
        for name,root in roots.items():
            frozen=by_id[name].local_support_numeric_adapter
            if root.frozen_emission!=frozen:
                raise ValueError('root association/frozen numeric intent differs')
            association=associate_derived_path(trace,descriptor,frozen,original_recipe=root.original_recipe,
                original_inputs=root.original_inputs,geometry_evidence=root.geometry_evidence,
                matched_source_lines=root.association.matched_source_lines)
            if (association!=root.association or association.object_token!=anchor.object_scope.object_token
                    or policy.candidate_speed_mm_s>association.source_speed_cap_mm_s):
                raise ValueError('stale/foreign root association or excessive source-floor speed')
            by_line={e.line_number:e for e in trace.events}
            if any(by_line[line].byte_offset>=anchor.byte_offset for line in association.matched_source_lines):
                raise ValueError('root source material must strictly precede supported insertion')
            root_ids[name]=fingerprint(association)
        if path_ids.intersection(by_id) or len(path_ids)+len(by_id)>copy_policy.max_paths:
            raise ValueError('duplicate supported path or whole-copy path budget')
        path_ids.update(by_id)
        raw_blocks=_supported_cycle_blocks(anchor.saved_state,plan,policy,cancelled=cancelled)
        line_ending=b'\r\n' if source[:anchor.byte_offset].splitlines(keepends=True)[-1].endswith(b'\r\n') else b'\n'
        cycle_blocks=[]
        annotation_ids=[]
        for name,block in zip(plan.execution_order,raw_blocks):
            if line_ending==b'\r\n':
                block=block.replace(b'\n',b'\r\n')
            if annotation_policy is not None:
                annotated=annotate_conditional_cycle(block,trace=trace,anchor_offset=anchor.byte_offset,
                    frozen_paths=(by_id[name].local_support_numeric_adapter,),policy=annotation_policy)
                annotation_count+=len(annotated.generated_line_indices)
                if annotation_count>annotation_policy.max_generated_comments:
                    raise ValueError('supported whole-copy annotation budget exceeded')
                block=annotated.block
                annotation_ids.append(annotated.identity)
            cycle_blocks.append(block)
        block=b'; TWO_TIER_UNVERIFIED explicit immediate support graph'+line_ending+b''.join(cycle_blocks)
        replay=trace_linear_execution(block,initial_state=anchor.saved_state)
        if replay.failure is not None or replay.final_state!=anchor.saved_state:
            raise ValueError('supported source state restoration failed')
        child_ids=tuple((p.intent.path_id,p.parent_frozen_identity,root_ids[p.intent.parent_path_id])
                        for p in plan.paths if p.intent.parent_path_id is not None)
        blocks.append((anchor.byte_offset,block,fingerprint(plan),plan.execution_order,tuple(sorted(root_ids.items())),child_ids,tuple(annotation_ids)))
    chunks,spans=[],[]
    cursor=output_offset=0
    for offset,block,graph_identity,order,root_ids,child_ids,annotation_ids in blocks:
        untouched=source[cursor:offset]
        chunks.extend((untouched,block))
        output_offset+=len(untouched)
        spans.append(SupportedInsertionSpan(offset,output_offset,output_offset+len(block),graph_identity,order,root_ids,child_ids,annotation_ids))
        output_offset+=len(block)
        cursor=offset
        if output_offset>copy_policy.max_output_bytes:
            raise ValueError('supported output byte budget exceeded')
    chunks.append(source[cursor:])
    output=b''.join(chunks)
    if len(output)>copy_policy.max_output_bytes:
        raise ValueError('supported output byte budget exceeded')
    return TwoTierConditionalCopy(descriptor.source_sha256,descriptor.project_sha256,descriptor.producer_sha256,context,
        copy_policy,fingerprint(annotation_policy) if annotation_policy is not None else None,
        output,sha256(output).hexdigest(),tuple(spans))


def write_two_tier_copy(copy,target:Path,*,source_path:Path,project_path:Path,producer,descriptor,entry,motion,
                        insertions,cancelled,annotation_policy=None):
    if type(copy) is not TwoTierConditionalCopy or target.exists() or 'UNVERIFIED_VIEW_ONLY' not in target.name:
        raise ValueError('new explicitly view-only supported copy target required')
    for original,digest in ((source_path,copy.source_sha256),(project_path,copy.project_sha256)):
        if target.resolve()==original.resolve() or sha256(original.read_bytes()).hexdigest()!=digest:
            raise ValueError('aliased/stale supported source inputs')
    rebuilt=compose_two_tier_copy((source_path.read_bytes(),project_path.read_bytes(),producer,descriptor,entry,motion),insertions,
        copy_policy=copy.copy_policy,cancelled=cancelled,annotation_policy=annotation_policy)
    if rebuilt!=copy:
        raise ValueError('stale/forged supported copy receipt')
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(prefix='.supported-UNVERIFIED-',dir=target.parent,delete=False) as stream:
            temporary=Path(stream.name)
            stream.write(copy.output_bytes);stream.flush();os.fsync(stream.fileno())
        _checkpoint(cancelled)
        os.link(temporary,target)
    finally:
        if temporary is not None:
            temporary.unlink()
    return copy.output_sha256
