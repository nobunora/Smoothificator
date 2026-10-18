"""Native opt-in admission filters immutable intents before final graph freeze."""
from dataclasses import dataclass

from tools.freeze_supplemental_emission import freeze_numeric_emission
from tools.native_empirical_material import evaluate_empirical_segments
from tools.supplemental_z_hop import SupplementalPath,rounded


@dataclass(frozen=True)
class EmpiricalPathAdmission:
    path_id: str
    retained: bool
    reason: str
    segment_proofs: tuple


def filter_empirical_intents(intents, *, hop, correction):
    if type(intents) is not tuple or not intents:
        raise ValueError('nonempty immutable empirical intent family required')
    by_id={intent.path_id:intent for intent in intents}
    if len(by_id)!=len(intents) or any(p.parent_path_id is not None and p.parent_path_id not in by_id for p in intents):
        raise ValueError('invalid empirical intent parent association')
    decisions={}
    for intent in intents:
        numeric=freeze_numeric_emission(SupplementalPath(intent.path_id,intent.support_plane_z_mm,intent.width_mm,
            intent.physical_height_mm,intent.points_mm),hop)
        path_correction=correction.for_path(intent.path_id)
        if any(rounded(amount*path_correction.factor,hop.e_places)<=0 for amount in numeric.relative_e_mm):
            decisions[intent.path_id]=EmpiricalPathAdmission(intent.path_id,False,'corrected-deposition-rounded-zero',())
            continue
        proofs=evaluate_empirical_segments(numeric,path_correction,hop,correction.policy)
        accepted=all(proof.accepted for proof in proofs)
        decisions[intent.path_id]=EmpiricalPathAdmission(intent.path_id,accepted,
            'modeled-minimum-proven' if accepted else 'modeled-minimum-not-proven',proofs)
    changed=True
    while changed:
        changed=False
        for intent in intents:
            decision=decisions[intent.path_id]
            if decision.retained and intent.parent_path_id is not None and not decisions[intent.parent_path_id].retained:
                decisions[intent.path_id]=EmpiricalPathAdmission(intent.path_id,False,'parent-removed',decision.segment_proofs)
                changed=True
    survivors=tuple(p for p in intents if decisions[p.path_id].retained)
    return survivors,tuple(decisions[p.path_id] for p in intents)
