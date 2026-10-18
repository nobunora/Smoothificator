"""Opt-in commanded-volume correction; nominal geometry is not a physical claim."""
from dataclasses import dataclass
from fractions import Fraction as F
import re

from adaptive_subedge.domain.empirical_material import EmpiricalMaterialPolicy
from adaptive_subedge.engine.empirical_material import factor_for_angle, validate_resolved_policy, compare_modeled_minimum_thickness
from adaptive_subedge.application.empirical_material_settings import policy_identity
from orca_plugin.gcode.linear_trace import _words
from tools.supplemental_z_hop import rounded, _text


@dataclass(frozen=True)
class NativeEmpiricalPathCorrection:
    path_id: str
    angle_degrees: F
    maximum_angle_degrees: F
    factor: F

    def __post_init__(self):
        if (type(self.path_id) is not str or not re.fullmatch(r'[A-Za-z0-9_-]+', self.path_id)
                or len(self.path_id)>128
                or any(type(v) is not F or max(abs(v.numerator).bit_length(),v.denominator.bit_length())>256
                    for v in (self.angle_degrees,self.maximum_angle_degrees,self.factor))
                or self.angle_degrees < 0 or self.maximum_angle_degrees <= 0 or not 0 < self.factor <= 1):
            raise ValueError('exact bounded empirical path correction required')


@dataclass(frozen=True)
class NativeEmpiricalMaterialCorrection:
    policy_identity: str
    policy: EmpiricalMaterialPolicy
    paths: tuple[NativeEmpiricalPathCorrection,...]

    def __post_init__(self):
        if (type(self.policy_identity) is not str or not re.fullmatch('[0-9a-f]{64}',self.policy_identity)
                or type(self.paths) is not tuple or not 0<len(self.paths)<=1000
                or any(type(p) is not NativeEmpiricalPathCorrection for p in self.paths)
                or len({p.path_id for p in self.paths}) != len(self.paths)):
            raise ValueError('immutable uniquely bound empirical correction required')
        validate_resolved_policy(self.policy)
        if self.policy_identity!=policy_identity(self.policy):
            raise ValueError('empirical policy identity mismatch')
        for path in self.paths:
            expected=factor_for_angle(path.angle_degrees,self.policy)
            if path.maximum_angle_degrees!=expected.maximum_angle_degrees or path.factor!=expected.factor:
                raise ValueError('empirical factor differs from bound policy')

    def for_path(self,path_id):
        matches=tuple(p for p in self.paths if p.path_id==path_id)
        if len(matches)!=1:
            raise ValueError('missing empirical path correction')
        return matches[0]


def evaluate_empirical_segments(frozen, correction, hop, material_policy):
    """Exact final-E minimum-area proof; nominal design width stays authoritative."""
    validate_resolved_policy(material_policy)
    expected=factor_for_angle(correction.angle_degrees,material_policy)
    if correction.factor!=expected.factor or correction.maximum_angle_degrees!=expected.maximum_angle_degrees:
        raise ValueError('empirical thickness factor differs from policy')
    threshold=material_policy.minimum_modeled_thickness_mm
    if threshold is None:
        return ()  # Explicit historical V1 policy, never a V2 trial default.
    if hop is None or threshold!=F(str(hop.bounds.min_candidate_height_mm)):
        raise ValueError('empirical minimum thickness differs from nominal plan bound')
    if correction.path_id!=frozen.path.path_id:
        raise ValueError('empirical thickness path identity mismatch')
    multiplier=hop.print_flow_ratio*hop.filament_flow_ratio
    if hop.other_flow_enabled:
        multiplier*=hop.outer_flow_ratio
    proofs=[]
    for start,end,amount in zip(frozen.path.points_mm,frozen.path.points_mm[1:],frozen.relative_e_mm):
        changed=tuple(index for index in range(3) if start[index]!=end[index])
        if len(changed)!=1 or changed[0]==2:
            raise ValueError('empirical thickness requires exact axis-aligned XY length')
        length=abs(end[changed[0]]-start[changed[0]])
        corrected=rounded(amount*correction.factor,hop.e_places)
        if corrected<=0:
            raise ValueError('empirical deposition collapsed at command precision')
        proofs.append(compare_modeled_minimum_thickness(corrected_e_mm=corrected,
            filament_diameter_mm=hop.filament_diameter_mm,length_mm=length,
            flow_multiplier=multiplier,nominal_width_mm=frozen.path.width_mm,minimum_height_mm=threshold))
    if len(proofs)!=len(frozen.relative_e_mm):
        raise ValueError('empirical thickness segment coverage mismatch')
    return tuple(proofs)


def apply_empirical_material_correction(block, frozen, correction, e_places, *, hop, material_policy):
    """Only rewrite frozen moving positive-E rows, after nominal annotations.

    Positive stationary unretraction/reconciliation, all other bytes and nominal
    preview metadata remain unchanged. Returned E amounts are commanded volume,
    never an inverse-stadium width or a physical coverage certificate.
    """
    if type(correction) is not NativeEmpiricalPathCorrection or correction.path_id!=frozen.path.path_id:
        raise ValueError('empirical correction/frozen path identity mismatch')
    if type(e_places) is not int or not 0<=e_places<=12:
        raise ValueError('bounded empirical E precision required')
    if material_policy.minimum_modeled_thickness_mm is not None and (hop is None or e_places!=hop.e_places):
        raise ValueError('empirical proof and emission precision differ')
    proofs=evaluate_empirical_segments(frozen,correction,hop,material_policy)
    if any(not proof.accepted for proof in proofs):
        raise ValueError('empirical modeled minimum thickness not proven')
    output=[]; amounts=[]
    for line in block.splitlines(keepends=True):
        text=line.split(b';',1)[0].strip().decode('ascii')
        if text:
            command,words=_words(text)
            if command in ('G0','G1') and words.get('E',F(0))>0 and ('X' in words or 'Y' in words):
                index=len(amounts)
                if index>=len(frozen.relative_e_mm) or words['E']!=frozen.relative_e_mm[index]:
                    raise ValueError('empirical deposition differs from nominal frozen E')
                amount=rounded(words['E']*correction.factor,e_places)
                if not 0<amount<=words['E']:
                    raise ValueError('empirical deposition collapsed or exceeds nominal E')
                line,count=re.subn(rb'(?<!\S)E[+-]?[0-9]+(?:\.[0-9]+)?(?=\s|$)',
                    b'E'+_text(amount,e_places).encode('ascii'),line)
                if count!=1:
                    raise ValueError('empirical E token grammar drift')
                amounts.append(amount)
        output.append(line)
    if len(amounts)!=len(frozen.relative_e_mm):
        raise ValueError('incomplete empirical deposition coverage')
    return b''.join(output),tuple(amounts)
