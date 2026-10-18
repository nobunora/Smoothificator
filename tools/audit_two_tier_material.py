"""Account each candidate pair; only proven immediate-support slabs are allowed."""
from dataclasses import dataclass, field, replace

from tools.audit_nominal_bead_overlap import BeadOverlapPolicy, BeadOverlapReport, audit_nominal_bead_overlap
from tools.prepare_two_tier_intents import (
    FrozenTwoTierPlan, ImmediateSupportSlab, freeze_supported_graph, supported_bead,
)


@dataclass(frozen=True)
class TwoTierMaterialPolicy:
    max_pairs: int
    max_queries: int
    pair: BeadOverlapPolicy

    def __post_init__(self):
        if (type(self.max_pairs) is not int or self.max_pairs<1 or type(self.max_queries) is not int
                or self.max_queries<1 or type(self.pair) is not BeadOverlapPolicy):
            raise ValueError('explicit finite material-pair budgets required')


@dataclass(frozen=True)
class SupportedMaterialPair:
    first_path_id: str
    second_path_id: str
    state: str
    intended_slab: ImmediateSupportSlab | None
    unrelated_pair_audit: BeadOverlapReport | None


@dataclass(frozen=True)
class TwoTierMaterialReport:
    state: str
    reason: str
    pairs: tuple[SupportedMaterialPair,...]
    kernel_queries: int
    all_candidate_pairs_accounted: bool
    physical_authority: bool=field(default=False,init=False)


def audit_two_tier_material(plan,emission_policy,*,policy,cancelled):
    if type(plan) is not FrozenTwoTierPlan or type(policy) is not TwoTierMaterialPolicy or not callable(cancelled):
        raise ValueError('exact supported plan/material policy required')
    if freeze_supported_graph(tuple(p.intent for p in plan.paths),source_context_identity=plan.source_context_identity,
            policy=emission_policy,graph_policy=plan.graph_policy,cancelled=cancelled)!=plan:
        raise ValueError('stale/forged supported material graph')
    slabs={frozenset((s.parent_path_id,s.child_path_id)):s for s in plan.immediate_support_slabs}
    pairs=[]
    queries=0
    for i,first in enumerate(plan.paths):
        for second in plan.paths[i+1:]:
            answer=cancelled()
            if type(answer) is not bool:
                raise ValueError('exact bool material cancellation required')
            if answer or len(pairs)>=policy.max_pairs:
                return TwoTierMaterialReport('incomplete','cancelled' if answer else 'pair-limit',tuple(pairs),queries,False)
            key=frozenset((first.intent.path_id,second.intent.path_id))
            if key in slabs:
                # Rebuilt graph proves actual spatial containment, parent-only
                # contact and global z bounds. Any intersection lies in this
                # exact slab; this says neither full footprint nor clearance.
                pairs.append(SupportedMaterialPair(first.intent.path_id,second.intent.path_id,
                    'declared-immediate-support-slab',slabs[key],None))
                continue
            if queries>=policy.max_queries:
                return TwoTierMaterialReport('incomplete','query-limit',tuple(pairs),queries,False)
            audit=audit_nominal_bead_overlap(supported_bead(first),supported_bead(second),
                policy=replace(policy.pair,max_queries=min(policy.pair.max_queries,policy.max_queries-queries)),cancelled=cancelled)
            queries+=audit.kernel_queries
            pairs.append(SupportedMaterialPair(first.intent.path_id,second.intent.path_id,audit.state,None,audit))
            if audit.state!='disjoint-interiors':
                return TwoTierMaterialReport('failed' if audit.state=='overlap-proven' else 'incomplete',
                    'unrelated-positive-intersection' if audit.state=='overlap-proven' else 'unresolved-unrelated-pair',tuple(pairs),queries,False)
    return TwoTierMaterialReport('nominal-candidate-pairs-accounted','only-declared-support-slabs-or-disjoint-interiors',tuple(pairs),queries,True)
