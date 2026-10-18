"""Source-bound Z comparison limited to +/- ten percent of each line height."""
from fractions import Fraction as F
import hashlib
import json

from adaptive_subedge.domain.support_cell import ExactTopCellXY
from tools.audit_line_support import audit_line
from tools.build_tilted_cuboid_review import ROOT, baseline, slicer_height_limit
from tools.compare_top_surface_residual import overlapping_sources


MAX_OFFSET_FRACTION = F('.1')
OFFSET_FRACTIONS = (F('-.1'),F('-.05'),F(0),F('.05'),F('.1'))


def bounded_offset(height,fraction):
    if type(height) is not F or type(fraction) is not F or height <= 0:
        raise ValueError('exact positive line height and exact fraction required')
    if abs(fraction) > MAX_OFFSET_FRACTION:
        raise ValueError('Z offset exceeds ten percent of line height')
    return height*fraction


def analyze(source,plan):
    digest = hashlib.sha256(source).hexdigest()
    if digest != plan['source_slice_sha256']:
        raise ValueError('unpinned baseline')
    configured_height,maximum_height = slicer_height_limit(source)
    bounds = tuple(map(F,plan['top_face_bounds_exact_mm']))
    slope,intercept = map(F,plan['target_plane_z_equals_by_plus_c_exact'])
    groups = [g for g in plan['section_diagnostics'] if g['reason']=='rectangle-line-tiling']
    minimum_floor = min(F(g['rectangle_exact_mm'][2]) for g in groups)
    rows,sources,metadata,omitted = baseline(source,digest,minimum_floor-maximum_height*MAX_OFFSET_FRACTION)
    x0,x1 = bounds[0]+F('.3'),bounds[1]-F('.3')
    variants = []
    for fraction in OFFSET_FRACTIONS:
        lines = []
        for group in groups:
            _,_,bottom,z = map(F,group['rectangle_exact_mm'])
            h = z-bottom
            for index,(a,b) in enumerate(group['line_intervals_exact_mm']):
                a,b = F(a),F(b)
                y,w = (a+b)/2,b-a
                offset = bounded_offset(h,fraction)
                top = z+offset
                selected = overlapping_sources(sources,ExactTopCellXY(x0,x1,a,b))
                nominal = audit_line(x0,x1,y,top-h,selected)
                diamond = audit_line(x0,x1,y,top-h,selected,model='diamond')
                inside = top <= slope*a+intercept
                lines.append({'rectangle_id':group['rectangle_id'],'line_index':index+1,
                    'start_exact_mm':list(map(str,(x0,y,top))),
                    'end_exact_mm':list(map(str,(x1,y,top))),
                    'original_top_exact_mm':str(z),'width_exact_mm':str(w),'height_exact_mm':str(h),
                    'z_offset_exact_mm':str(offset),'z_offset_mm':float(offset),
                    'rectangle_height_above_original_floor_mm':float(max(F(0),top-bottom)),
                    'height_retained_fraction_exact':str(max(F(0),top-bottom)/h),
                    'target_rectangular_envelope_within_model':inside,
                    'nominal_centerline_contact':nominal,'diamond_centerline_contact':diamond,
                    'verified_interpolation_path':False,'printable_authorized':False})
        variants.append({'offset_fraction_exact':str(fraction),
            'offset_percent':float(fraction*100),'lines':lines,
            'within_target_envelope_count':sum(r['target_rectangular_envelope_within_model'] for r in lines),
            'both_centerline_contact_count':sum(r['nominal_centerline_contact']['state']==
                r['diamond_centerline_contact']['state']=='full-centerline-intersection-proven' for r in lines),
            'verified_interpolation_path_count':0})
    return {'scope':'line-thickness-bounded-z-offset-display-only',
        'source_slice_sha256':digest,'placed_project_sha256':plan['placed_project_sha256'],
        'source_plan_sha256':hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest(),
        'maximum_offset_fraction_exact':str(MAX_OFFSET_FRACTION),
        'configured_layer_height_mm':float(configured_height),'maximum_line_height_mm':float(maximum_height),
        'original_segment_count':len(rows),'omitted_low_sources':omitted,'variants':variants,
        'selected_offset_fraction_exact':'-1/10','printable_authorized':False,
        'shape_improvement_verified':False,'full_footprint_contact_verified':False,
        'limitations':'Bounded Z trial, not accepted paths. Centerline coverage is analytic; full-width contact, actual volume intersection, global error improvement and nozzle clearance remain unverified.'}


def main():
    folder = ROOT/'artifacts/cuboid-tilt10-review'
    report = analyze((folder/'original-slice/plate_1.gcode').read_bytes(),
                     json.loads((folder/'current-review.json').read_text()))
    (folder/'thickness-z-offsets.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:v for k,v in variant.items() if k!='lines'} for variant in report['variants']],indent=2))


if __name__ == '__main__':
    main()
