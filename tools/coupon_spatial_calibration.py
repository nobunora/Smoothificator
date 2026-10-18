"""Source-bound specimen geometry calibration; never patches emitted E."""
from dataclasses import asdict, dataclass, replace
from fractions import Fraction as F
from hashlib import sha256
import json
import math
import re

from adaptive_subedge.engine.empirical_material import section_angle_degrees
from adaptive_subedge.engine.smooth_dimensions import target_dimensions_for_angle
from tools.native_smooth_dimensions import NativeSmoothDimensionTaper, resolve_tapered_root, emission_hop_for_taper
from tools.prepare_two_tier_intents import SupportedPathIntent
from tools.freeze_supplemental_emission import freeze_numeric_emission
from tools.supplemental_z_hop import HopPolicy, SupplementalPath, rounded
from tools.stepped_coupon_fixture import SteppedCouponFixture

PI=F(str(math.pi))


@dataclass(frozen=True)
class CouponCalibrationPolicy:
    windows: tuple = ((F('6.5'),F('8.5'),F('.2')),(F('10.5'),F('12.5'),F('.2')),(F(14),F(16),F('-.1')))
    shoulder_mm: F = F('.5')
    tail_start_mm: F = F(16)
    tail_end_mm: F = F(17)
    tail_height_mm: F = F('.012')
    tail_width_mm: F = F('.015')
    minimum_height_mm: F = F('.01')
    minimum_width_mm: F = F('.012')
    tail_admission_width_mm: F = F('.14')
    maximum_tail_angle_degrees: F = F(45)
    dimension_grid_mm: F = F('.001')
    maximum_height_ticks: int = 200
    maximum_width_extra_ticks: int = 1
    schema_version: int = 2
    coordinate: str = 'projected'
    reference_geometry_sha256: str = ''

    def __post_init__(self):
        scalar_names=('shoulder_mm','tail_start_mm','tail_end_mm','tail_height_mm','tail_width_mm',
            'minimum_height_mm','minimum_width_mm','tail_admission_width_mm','maximum_tail_angle_degrees','dimension_grid_mm')
        values=tuple(getattr(self,k) for k in scalar_names)
        if any(type(v) is not F or v<=0 or max(v.numerator.bit_length(),v.denominator.bit_length())>128 for v in values):
            raise ValueError('bounded positive specimen settings required')
        if (type(self.windows) is not tuple or not 1<=len(self.windows)<=8
                or any(type(w) is not tuple or len(w)!=3 or any(type(v) is not F or max(abs(v.numerator).bit_length(),v.denominator.bit_length())>128 for v in w)
                    or not 0<=w[0]<w[1]<=100 or not F('-.9')<=w[2]<=1 for w in self.windows)):
            raise ValueError('bounded explicit specimen windows required')
        if not (self.shoulder_mm<=5 and self.tail_start_mm<self.tail_end_mm<=100
                and self.minimum_height_mm<=self.tail_height_mm<=self.tail_width_mm<=F('.45')
                and self.minimum_width_mm<=self.tail_width_mm and self.tail_admission_width_mm<=F('.45')
                and self.maximum_tail_angle_degrees<=45 and self.dimension_grid_mm==F('.001')
                and all((v/self.dimension_grid_mm).denominator==1 for v in (self.tail_height_mm,self.tail_width_mm,self.minimum_height_mm,self.minimum_width_mm))
                and type(self.maximum_height_ticks) is int and 1<=self.maximum_height_ticks<=200
                and type(self.maximum_width_extra_ticks) is int and 0<=self.maximum_width_extra_ticks<=1
                and type(self.schema_version) is int and self.schema_version in (1,2,3)
                and type(self.coordinate) is str and self.coordinate in ('surface_arc','projected','reference_angle')
                and (self.schema_version!=1 or self.coordinate=='surface_arc')
                and ((self.schema_version==3 and self.coordinate=='reference_angle' and type(self.reference_geometry_sha256) is str and re.fullmatch('[0-9a-f]{64}',self.reference_geometry_sha256) is not None)
                    or (self.schema_version<3 and self.coordinate!='reference_angle' and self.reference_geometry_sha256==''))):
            raise ValueError('ordered specimen geometry/search bounds required')


def encode_coupon_policy(policy):
    if type(policy) is not CouponCalibrationPolicy:raise ValueError('specimen policy type')
    document=asdict(policy)
    if policy.schema_version==1:document.pop('coordinate')
    if policy.schema_version<3:document.pop('reference_geometry_sha256')
    return json.dumps(document,default=str,sort_keys=True,separators=(',',':')).encode('ascii')+b'\n'


def decode_coupon_policy(content):
    if type(content) is not bytes or len(content)>10000:raise ValueError('bounded specimen JSON required')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('duplicate specimen setting')
            result[key]=value
        return result
    try:raw=json.loads(content,object_pairs_hook=unique)
    except RecursionError as exc:raise ValueError('specimen JSON nesting exceeds parser bound') from exc
    if type(raw) is not dict:raise ValueError('closed specimen schema required')
    if type(raw.get('schema_version')) is not int:raise ValueError('specimen integer settings required')
    expected=set(CouponCalibrationPolicy.__dataclass_fields__)
    if raw.get('schema_version')==1:expected.remove('coordinate')
    if raw.get('schema_version') in (1,2):expected.remove('reference_geometry_sha256')
    if set(raw)!=expected:raise ValueError('closed specimen schema required')
    if raw['schema_version']==1:raw['coordinate']='surface_arc'
    if raw['schema_version']<3:raw['reference_geometry_sha256']=''
    if type(raw['coordinate']) is not str:raise ValueError('specimen coordinate enum required')
    integers=('maximum_height_ticks','maximum_width_extra_ticks','schema_version')
    if any(type(raw[k]) is not int for k in integers):raise ValueError('specimen integer settings required')
    if any(type(v) is not str for k,v in raw.items() if k not in integers+('windows','coordinate','reference_geometry_sha256')):raise ValueError('exact string specimen numbers required')
    if (type(raw['windows']) is not list or any(type(w) is not list or len(w)!=3
            or any(type(v) is not str for v in w) for w in raw['windows'])):
        raise ValueError('exact specimen window strings required')
    try:
        return CouponCalibrationPolicy(**{k:tuple(tuple(F(v) for v in w) for w in value) if k=='windows'
            else value if k in integers+('coordinate','reference_geometry_sha256') else F(value) for k,value in raw.items()})
    except (TypeError,ZeroDivisionError,OverflowError) as exc:raise ValueError('invalid specimen numbers') from exc


def policy_identity(policy):return sha256(encode_coupon_policy(policy)).hexdigest()


def smoothstep(t):
    t=max(F(0),min(F(1),t));return t*t*t*(10-15*t+6*t*t)


def window_factor(distance,policy):
    factor=1+sum((gain*smoothstep((distance-(a-policy.shoulder_mm))/policy.shoulder_mm)
        *smoothstep(((b+policy.shoulder_mm)-distance)/policy.shoulder_mm) for a,b,gain in policy.windows),F(0))
    if factor<=0:raise ValueError('specimen-window-factor-nonpositive')
    return factor


def stadium_area(width,height):return height*(width-(1-PI/4)*height)


def _profile_segments(profile):
    if type(profile) is not tuple or not 2<=len(profile)<=4096 or any(type(p) is not tuple or len(p)!=2
            or any(type(v) is not F or max(abs(v.numerator).bit_length(),v.denominator.bit_length())>256 for v in p) for p in profile):
        raise ValueError('bounded placed profile required')
    cumulative=0.0;segments=[]
    for a,b in zip(profile,profile[1:]):
        if b[0]<=a[0] or b[1]<a[1]:raise ValueError('ordered rising placed profile required')
        length=math.hypot(float(b[0]-a[0]),float(b[1]-a[1]))
        if not math.isfinite(length):raise ValueError('nonfinite profile')
        segments.append((a,b,cumulative,length));cumulative+=length
    return segments


def surface_arc_at_y(profile,y):
    for a,b,start,length in _profile_segments(profile):
        if a[0]<=y<=b[0]:return F(format(start+length*float((y-a[0])/(b[0]-a[0])),'.8f'))
    raise ValueError('path outside placed profile')


def profile_angle_at_arc(profile,distance):
    for a,b,start,length in _profile_segments(profile):
        if start<=float(distance)<=start+length:return section_angle_degrees(b[0]-a[0],b[1]-a[1])
    raise ValueError('anchor outside placed profile')


def profile_angle_at_projected(profile,distance):
    y=profile[0][0]+distance
    for a,b,_,_ in _profile_segments(profile):
        if a[0]<=y<=b[0]:return section_angle_degrees(b[0]-a[0],b[1]-a[1])
    raise ValueError('projected anchor outside placed profile')


@dataclass(frozen=True)
class CouponCalibrationSourcePath:
    reference_intent: SupportedPathIntent
    admission_hop: HopPolicy
    mode: str = 'reference'
    section_base_mm: F = F(1)
    section_rise_mm: F = F(0)


@dataclass(frozen=True)
class NativeCouponCalibration:
    policy: CouponCalibrationPolicy
    placed_profile: tuple
    geometry_sha256: str
    catalog_sha256: str
    reference_taper: NativeSmoothDimensionTaper
    anchor_reference_path_id: str
    paths: tuple[CouponCalibrationSourcePath,...]
    stepped_fixture: SteppedCouponFixture | None = None

    def __post_init__(self):
        if type(self.policy) is not CouponCalibrationPolicy or type(self.reference_taper) is not NativeSmoothDimensionTaper:raise ValueError('immutable specimen policy/reference required')
        if self.reference_taper.policy.schema_version!=5:raise ValueError('specimen calibration requires V5 reference policy')
        _profile_segments(self.placed_profile)
        if (self.policy.schema_version==3)!=(type(self.stepped_fixture) is SteppedCouponFixture):raise ValueError('angle calibration requires exact stepped fixture')
        if any(type(v) is not str or re.fullmatch('[0-9a-f]{64}',v) is None for v in (self.geometry_sha256,self.catalog_sha256)):
            raise ValueError('specimen geometry/catalog identity required')
        if (type(self.paths) is not tuple or not 0<len(self.paths)<=1000 or any(type(p) is not CouponCalibrationSourcePath
                or type(p.reference_intent) is not SupportedPathIntent or type(p.admission_hop) is not HopPolicy
                or p.mode not in ('reference','residual') for p in self.paths)
                or len({p.reference_intent.path_id for p in self.paths})!=len(self.paths)):
            raise ValueError('bounded unique specimen source paths required')
        anchor=self.reference_taper.for_path(self.anchor_reference_path_id)
        if anchor.original_intent.points_mm[0][1]!=max(p.original_intent.points_mm[0][1] for p in self.reference_taper.paths):
            raise ValueError('specimen anchor is not last accepted nominal family')
        for path in self.paths:
            if self.policy.schema_version==3 and (type(path.section_base_mm) is not F or type(path.section_rise_mm) is not F or path.section_base_mm<=0 or path.section_rise_mm!=self.reference_taper.policy.admission_layer_height_mm):
                raise ValueError('angle calibration requires actual saved-height source section')
            if path.mode=='reference':
                original=self.reference_taper.for_path(path.reference_intent.path_id)
                if self.policy.schema_version==3 and (path.section_base_mm,path.section_rise_mm)!=(original.section_base_mm,original.section_rise_mm):raise ValueError('angle calibration source differs from V5 section')
                expected_hop=emission_hop_for_taper(original.admission_hop,self.reference_taper.policy)
                if path.admission_hop!=expected_hop or resolve_tapered_root(original,original.admission_hop,self.reference_taper.policy).resolved_intent!=path.reference_intent:
                    raise ValueError('specimen reference differs from authoritative V5 mapping')
            else:
                if (type(path.section_base_mm) is not F or type(path.section_rise_mm) is not F
                        or path.section_rise_mm!=self.reference_taper.policy.admission_layer_height_mm
                        or path.section_base_mm*path.section_base_mm<2*self.policy.tail_admission_width_mm**2
                        or not self.reference_taper.policy.maximum_angle_degrees<section_angle_degrees(path.section_base_mm,path.section_rise_mm)<=self.policy.maximum_tail_angle_degrees
                        or F(str(path.admission_hop.bounds.min_candidate_width_mm))!=self.policy.tail_admission_width_mm):
                    raise ValueError('explicit residual source admission required')
            intent=path.reference_intent
            if (intent.parent_path_id is not None or intent.support_plane_z_mm!=intent.original_source_floor_z_mm
                    or intent.remaining_height_mm!=intent.physical_height_mm
                    or any(point[2]!=intent.support_plane_z_mm+intent.physical_height_mm for point in intent.points_mm)
                    or any(point[1]!=intent.points_mm[0][1] for point in intent.points_mm)):
                raise ValueError('specimen requires unchanged-floor roots')
            freeze_numeric_emission(SupplementalPath(intent.path_id,intent.support_plane_z_mm,intent.width_mm,intent.physical_height_mm,intent.points_mm),path.admission_hop)

    def for_path(self,path_id):
        paths=tuple(p for p in self.paths if p.reference_intent.path_id==path_id)
        if len(paths)!=1:raise ValueError('missing specimen source path')
        return paths[0]


def coupon_emission_hop(admission_hop,policy):
    if type(admission_hop) is not HopPolicy or type(policy) is not CouponCalibrationPolicy:raise ValueError('specimen bounds adapter type')
    return replace(admission_hop,bounds=replace(admission_hop.bounds,
        min_candidate_height_mm=float(policy.minimum_height_mm),min_candidate_width_mm=float(policy.minimum_width_mm)))


def calibration_targets(source,calibration):
    intent=source.reference_intent;p=calibration.policy;y=intent.points_mm[0][1]
    distance=(section_angle_degrees(source.section_base_mm,source.section_rise_mm)*F(20,45) if p.coordinate=='reference_angle'
        else y-calibration.placed_profile[0][0] if p.coordinate=='projected' else surface_arc_at_y(calibration.placed_profile,y))
    reference_area=stadium_area(intent.width_mm,intent.physical_height_mm);reference_height=intent.physical_height_mm
    if p.coordinate in ('projected','reference_angle') and source.mode=='residual':
        # The wider admission seed was never emitted; it is not the V5 reference.
        reference_height=calibration.reference_taper.policy.minimum_height_mm
        reference_area=stadium_area(calibration.reference_taper.policy.minimum_width_mm,reference_height)
    if distance<=p.tail_start_mm:
        return distance,reference_area*window_factor(distance,p),reference_height
    anchor=calibration.reference_taper.for_path(calibration.anchor_reference_path_id).original_intent
    angle=(p.tail_start_mm*F(45,20) if p.coordinate=='reference_angle' else profile_angle_at_projected(calibration.placed_profile,p.tail_start_mm) if p.coordinate=='projected'
        else profile_angle_at_arc(calibration.placed_profile,p.tail_start_mm))
    target=target_dimensions_for_angle(min(angle,calibration.reference_taper.policy.maximum_angle_degrees),anchor.width_mm,anchor.physical_height_mm,calibration.reference_taper.policy)
    q16=stadium_area(target.target_width_mm,target.target_height_mm)*window_factor(p.tail_start_mm,p)
    qtail=stadium_area(p.tail_width_mm,p.tail_height_mm)
    if qtail>q16:raise ValueError('residual area exceeds calibrated handoff area')
    t=smoothstep((distance-p.tail_start_mm)/(p.tail_end_mm-p.tail_start_mm))
    return distance,(1-t)*q16+t*qtail,(1-t)*target.target_height_mm+t*p.tail_height_mm


def resolve_coupon_path(source,calibration):
    """Resolve coherent geometry on bounded grids, then ordinary full-E freeze."""
    distance,area,target_height=calibration_targets(source,calibration)
    original=source.reference_intent;p=calibration.policy;hop=coupon_emission_hop(source.admission_hop,p);grid=p.dimension_grid_mm
    first=max(p.minimum_height_mm,rounded(target_height,3));maximum=min(F(str(hop.bounds.max_candidate_height_mm)),original.original_next_layer_z_mm-original.support_plane_z_mm-grid)
    attempts=[]
    for tick in range(p.maximum_height_ticks):
        height=first+tick*grid
        if height>maximum:break
        width=area/height+(1-PI/4)*height
        if width>F(str(hop.bounds.max_candidate_width_mm)):continue
        floor=(width//grid)*grid;ceil=-(-width//grid)*grid
        widths=sorted(set((floor,ceil,ceil+p.maximum_width_extra_ticks*grid)),key=lambda w:(abs(stadium_area(w,height)-area),w))
        for represented in widths:
            if not max(height,p.minimum_width_mm)<=represented<=F(str(hop.bounds.max_candidate_width_mm)):continue
            points=tuple((x,y,original.support_plane_z_mm+height) for x,y,_ in original.points_mm)
            transformed=replace(original,width_mm=represented,physical_height_mm=height,remaining_height_mm=height,points_mm=points)
            try:freeze=freeze_numeric_emission(SupplementalPath(original.path_id,original.support_plane_z_mm,represented,height,points),hop)
            except ValueError as exc:
                if str(exc)!='nearest E implies width outside bounds':raise
                attempts.append({'height_mm':height,'width_mm':represented,'reason':str(exc)});continue
            if distance>=p.tail_end_mm:
                uncorrected=stadium_area(calibration.reference_taper.policy.minimum_width_mm,calibration.reference_taper.policy.minimum_height_mm)
                if stadium_area(represented,height)>uncorrected:continue
            return transformed,{'path_id':original.path_id,'mode':source.mode,'ruler_coordinate':p.coordinate,
                'calibration_distance_mm':distance,'ruler_surface_arc_mm':surface_arc_at_y(calibration.placed_profile,original.points_mm[0][1]),
                'projected_distance_mm':original.points_mm[0][1]-calibration.placed_profile[0][0],
                'reference_height_mm':original.physical_height_mm,'reference_width_mm':original.width_mm,
                'reference_area_mm2':stadium_area(original.width_mm,original.physical_height_mm),'target_area_mm2':area,
                'calibration_reference_area_mm2':stadium_area(calibration.reference_taper.policy.minimum_width_mm,
                    calibration.reference_taper.policy.minimum_height_mm) if source.mode=='residual' and p.coordinate in ('projected','reference_angle')
                    else stadium_area(original.width_mm,original.physical_height_mm),
                'reference_basis':'clamped-V5-endpoint' if source.mode=='residual' and p.coordinate in ('projected','reference_angle') else 'source-reference-intent',
                'target_height_mm':target_height,'resolved_area_mm2':stadium_area(represented,height),
                'represented_area_error_mm2':stadium_area(represented,height)-area,'resolved_intent':asdict(transformed),
                'width_attempts_mm':attempts,'actual_frozen_e_mm':freeze.relative_e_mm,'reason':'ordinary-stadium-refreeze'}
        # Height increases only solve an over-width requested area; no hidden height fallback.
        if width<=F(str(hop.bounds.max_candidate_width_mm)):break
    raise ValueError('specimen geometry unrepresentable within bounded search')
