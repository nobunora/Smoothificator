"""Continuous interval bounds for a uniform downward viewer-only translation.

Also retains a closed-cell finite-width diagnostic. Upper-envelope contact may mean burial in existing
material, not a useful additive path or print/nozzle-clearance authorization.
"""
from fractions import Fraction as F
import hashlib
import json
from time import monotonic

from adaptive_subedge.domain.support_cell import ExactTopCellXY
from adaptive_subedge.engine.support_cell import query_exact_nominal_top_cell
from tools.audit_orca_diamond_contact import query_diamond_cell
from tools.audit_top_contact_cells import audit_strip
from tools.audit_line_support import minimum_centerline_support
from tools.build_tilted_cuboid_review import ROOT, baseline
from tools.compare_top_surface_residual import overlapping_sources


def minimum_support(cell,sources,*,query_cell=query_exact_nominal_top_cell,
                    tolerance=F('.001'),max_cells=2047,timeout_seconds=8):
    """Bound infimum over a closed union, with separate upper witnesses.

    Tiny-cell witnesses bound the infimum from above only. The lower bound
    requires complete closed-cell coverage and is never inferred from samples.
    """
    if tolerance <= 0 or max_cells < 1 or timeout_seconds <= 0:
        raise ValueError('invalid support minimum budget')
    sources = overlapping_sources(sources,cell)
    if not sources:
        return {'state':'unresolved','reason':'no spatial support','cells_queried':0}
    deadline = monotonic()+timeout_seconds
    upper = max(max(s.start_xyz_mm[2],s.end_xyz_mm[2]) for s in sources)
    search_high = upper
    lower = upper-F('.5')
    count = 0
    certificates = []
    witness_upper = upper
    peak_lower = None
    whole = query_cell(cell,sources,max_sources=1000,max_coordinate_bits=4096,
        sqrt_fraction_bits=128,cancelled=lambda:False)
    count += 1
    if whole.top_z_lower_mm is not None:
        lower = max(lower,whole.top_z_lower_mm)
    # These witnesses only bound extrema from one side. Complete contact
    # always comes from the independent closed-cell strip audit below.
    for fraction in (F(1,4),F(1,2),F(3,4)):
        cx = cell.x_min_mm+(cell.x_max_mm-cell.x_min_mm)*fraction
        cy = (cell.y_min_mm+cell.y_max_mm)/2
        radius = min(F('.00001'),(cell.y_max_mm-cell.y_min_mm)/100)
        tiny = ExactTopCellXY(cx-radius,cx+radius,cy-radius,cy+radius)
        q = query_cell(tiny,overlapping_sources(sources,tiny),max_sources=1000,
            max_coordinate_bits=4096,sqrt_fraction_bits=128,cancelled=lambda:False)
        count += 1
        if q.top_z_upper_mm is not None:
            witness_upper = min(witness_upper,q.top_z_upper_mm)
        if q.top_z_lower_mm is not None:
            peak_lower = q.top_z_lower_mm if peak_lower is None else max(peak_lower,q.top_z_lower_mm)

    def audit(threshold):
        nonlocal count,witness_upper
        report = audit_strip(cell,sources,threshold,query_cell=query_cell,
            max_cells=max_cells,max_depth=20,cancelled=lambda:monotonic()>=deadline)
        count += report['cells_queried']
        for witness in report['gap_witnesses']:
            if witness['top_upper_mm'] is not None:
                witness_upper = min(witness_upper,F(witness['top_upper_mm']))
        return report

    certificate = audit(lower)
    if certificate['state'] != 'nominal-strip-intersection-proven':
        return {'state':'unresolved','reason':'initial bounded contact floor unresolved',
                'cells_queried':count,'initial_floor_audit':certificate}
    certificates.append(certificate)
    search_high = min(search_high,witness_upper)
    for iteration in range(10):
        if search_high-lower <= tolerance or monotonic() >= deadline:
            break
        threshold = (lower+search_high)/2
        trial = audit(threshold)
        if trial['state'] == 'nominal-strip-intersection-proven':
            lower = threshold
            certificates.append(trial)
        else:
            # A timeout is not a geometric upper bound. It only limits this
            # search; witness_upper is updated exclusively from valid bounds.
            search_high = threshold
        search_high = min(search_high,witness_upper)
    return {'state':'full-bounded','minimum_lower_exact_mm':str(lower),
        'minimum_upper_exact_mm':str(witness_upper),
        'peak_lower_exact_mm':str(peak_lower) if peak_lower is not None else str(lower),
        'minimum_lower_mm':float(lower),'minimum_upper_mm':float(witness_upper),
        'closed_leaf_count':certificates[-1]['leaf_counts']['reaches-bottom'],
        'cells_queried':count,'minimum_bracket_width_mm':float(witness_upper-lower),
        'whole_strip_floor_certificate':certificates[-1],
        'contact_scope':'entire requested closed XY rectangle; intersection allows penetration'}



def analyze(source,manifest):
    digest = hashlib.sha256(source).hexdigest()
    if manifest['source_slice_sha256'] != digest:
        raise ValueError('unpinned baseline')
    # Retain every supported source. The only unsupported low-Z gap infill
    # remains far below the bounded 1-mm translation domain.
    plane_floor = min(F(str(d['terrace_z_mm'])) for d in manifest['section_diagnostics'] if 'terrace_z_mm' in d)
    rows,sources,metadata,omitted = baseline(source,digest,plane_floor-F(1))
    bx0,bx1,_,_ = map(F,manifest['top_face_bounds_exact_mm'])
    x0,x1 = bx0+F('.3'),bx1-F('.3')
    results = []
    needed = F(0)
    for group in manifest['section_diagnostics']:
        if group['reason'] != 'rectangle-line-tiling':
            continue
        _,_,bottom,z = map(F,group['rectangle_exact_mm'])
        for index,(a,b) in enumerate(group['line_intervals_exact_mm']):
            a,b = F(a),F(b)
            y,w,h = (a+b)/2,b-a,z-bottom
            cell = ExactTopCellXY(x0,x1,y-F('.01'),y+F('.01'))
            selected = overlapping_sources(sources,ExactTopCellXY(x0,x1,a,b))
            nominal = minimum_centerline_support(x0,x1,y,selected)
            diamond = minimum_centerline_support(x0,x1,y,selected,model='diamond')
            row = {'rectangle_id':group['rectangle_id'],'line_index':index+1,
                'start_exact_mm':list(map(str,(x0,y,z))),'end_exact_mm':list(map(str,(x1,y,z))),
                'width_exact_mm':str(w),'height_exact_mm':str(h),'bottom_exact_mm':str(bottom),
                'nominal_support':nominal,'diamond_support':diamond}
            if nominal['state'] != 'full-bounded' or diamond['state'] != 'full-bounded':
                results.append(row)
                continue
            nominal_need = max(F(0),bottom-F(nominal['minimum_lower_exact_mm']))
            # This proof covers the continuous centerline, not a finite-width band.
            diamond_bottom_upper = bottom
            diamond_need = max(F(0),diamond_bottom_upper-F(diamond['minimum_lower_exact_mm']))
            shift = max(nominal_need,diamond_need)
            needed = max(needed,shift)
            row.update(required_downward_shift_upper_mm=float(shift),
                required_downward_shift_upper_exact_mm=str(shift),
                nominal_support_range_lower_mm=float(F(nominal['peak_lower_exact_mm'])-F(nominal['minimum_upper_exact_mm'])))
            results.append(row)
    complete = bool(results) and all('required_downward_shift_upper_exact_mm' in r for r in results)
    # Round upward to a micrometre and add 1 um beyond the proven bound.
    shift = F(-(-needed//F('.001')))*F('.001')+F('.001') if complete else None
    if shift is not None and shift > F(1):
        complete,shift = False,None
    for row in results:
        if shift is None:
            continue
        z,h = F(row['start_exact_mm'][2]),F(row['height_exact_mm'])
        row.update(shifted_top_z_mm=float(z-shift),
            nominal_peak_above_shifted_top_lower_mm=float(F(row['nominal_support']['peak_lower_exact_mm'])-(z-shift)),
            rectangular_height_remaining_above_original_floor_mm=float(max(F(0),h-shift)))
    return {'scope':'uniform-downward-translation-display-only','state':'bounded' if complete else 'unresolved',
        'source_slice_sha256':digest,'placed_project_sha256':manifest['placed_project_sha256'],
        'original_segment_count':len(rows),'omitted_low_sources':omitted,
        'central_strip_width_mm':0,'contact_scope':'continuous full centerline; width contact unproven','uniform_downward_shift_exact_mm':str(shift) if shift is not None else None,
        'uniform_downward_shift_mm':float(shift) if shift is not None else None,
        'lines':results,'printable_authorized':False,'full_footprint_contact_verified':False,
        'shape_improvement_verified':False,
        'limitations':'Certified centerline upper-envelope contact may bury lines in existing final-baseline material. No full-footprint contact, useful global residual reduction or chronological nozzle clearance claim.'}


def main():
    folder = ROOT/'artifacts/cuboid-tilt10-review'
    manifest = json.loads((folder/'current-review.json').read_text())
    report = analyze((folder/'original-slice/plate_1.gcode').read_bytes(),manifest)
    (folder/'uniform-z-contact.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='lines'},indent=2))


if __name__ == '__main__':
    main()
