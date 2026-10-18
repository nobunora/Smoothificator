"""Actual adjacent-layer step triangles rendered as UNVERIFIED Orca probes."""
from fractions import Fraction as F
import argparse
import hashlib
import json
import math
from uuid import uuid4

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY
from tools.audit_line_support import audit_line
from tools.build_tilted_cuboid_review import (
    ROOT, MIN_WIDTH, MAX_WIDTH, INSET, baseline, render_scene,
    sliced_top_face, slicer_height_limit,
)
from tools.compare_top_surface_residual import overlapping_sources
from tools.solve_triangle_rectangle import finite_triangle_rectangle_intersection_area, pack


COARSE_POSITION_STEP_MM = F('.005')
MAXIMUM_OVERLAP_PERCENT = F(30)
DEFAULT_MINIMUM_HEIGHT_MM = F('.08')


def step_base_applicable(base_mm, minimum_width_mm):
    """Exact sqrt(2)*minimum-width gate without rounding a square root."""
    if (type(base_mm) is not F or type(minimum_width_mm) is not F
            or base_mm <= 0 or minimum_width_mm <= 0):
        raise ValueError('positive exact step base and minimum width required')
    return base_mm*base_mm >= 2*minimum_width_mm*minimum_width_mm


def validate_dimensions(minimum_width_mm, maximum_width_mm, minimum_height_mm, maximum_height_mm):
    dimensions = (minimum_width_mm,maximum_width_mm,minimum_height_mm,maximum_height_mm)
    if (any(type(v) is not F for v in dimensions) or min(dimensions) <= 0
            or minimum_width_mm > maximum_width_mm or minimum_height_mm > maximum_height_mm):
        raise ValueError('positive exact dimensions, min width <= max width and min height <= slicer height limit required')


def line_placement(layer_top_mm, height_mm, overlap_percent):
    """Command Z is the bead top; positive percent lowers the whole bead."""
    if (any(type(v) is not F for v in (layer_top_mm,height_mm,overlap_percent))
            or height_mm <= 0 or not 0 <= overlap_percent <= MAXIMUM_OVERLAP_PERCENT):
        raise ValueError('exact height and overlap percent in [0, 30] required')
    bottom = layer_top_mm-height_mm*overlap_percent/100
    return bottom,bottom+height_mm


def analysis_minimum_height(minimum_height_mm, overlap_percent, maximum_height_mm):
    """Preserve required height above the floor after overlap penetration."""
    line_placement(F(0),minimum_height_mm,overlap_percent)
    if type(maximum_height_mm) is not F or maximum_height_mm <= 0:
        raise ValueError('positive exact slicer height limit required')
    compensated = minimum_height_mm/(1-overlap_percent/100)
    if compensated > maximum_height_mm:
        raise ValueError('overlap-compensated minimum thickness exceeds slicer maximum height')
    return compensated


def posed_intersection_area(base, rise, rectangle, bottom):
    """Finite triangle area after independent contact-Z adjustment."""
    return finite_triangle_rectangle_intersection_area(base, rise, rectangle.left_mm,
        rectangle.right_mm, bottom, bottom+rectangle.height_mm)


def extract_steps(bounds, sources):
    """Cross-section edges witnessed by X-directed source beads at mid-X.

    This adapter is deliberately limited to this planar cuboid. Every edge
    bead must cover the complete candidate X interval; no bbox-only inference.
    """
    x0,x1,y0,y1 = bounds
    mid_x = (x0+x1)/2
    by_level = {}
    for s in sources:
        ax,ay,z = s.start_xyz_mm
        bx,by,_ = s.end_xyz_mm
        if ay == by and min(ax,bx) <= mid_x <= max(ax,bx):
            by_level.setdefault(z, []).append(s)
    steps = []
    levels = sorted(by_level)
    for lower,upper in zip(levels, levels[1:]):
        edge_beads = [min(by_level[z], key=lambda s:s.start_xyz_mm[1]-s.width_mm/2)
                      for z in (lower,upper)]
        left,right = (s.start_xyz_mm[1]-s.width_mm/2 for s in edge_beads)
        if not y0 <= left < right <= y1:
            continue
        if any(min(s.start_xyz_mm[0],s.end_xyz_mm[0]) > x0+INSET
               or max(s.start_xyz_mm[0],s.end_xyz_mm[0]) < x1-INSET for s in edge_beads):
            raise ValueError('section edge does not span the candidate X interval')
        if edge_beads[1].height_mm != upper-lower:
            raise ValueError('adjacent Z interval does not match actual upper layer height')
        steps.append((lower,upper,left,right,edge_beads))
    return steps


def build(source, project, *, expected_source_sha256, expected_project_sha256,
          overlap_percent=F(0), minimum_width_mm=MIN_WIDTH, maximum_width_mm=MAX_WIDTH,
          minimum_height_mm=DEFAULT_MINIMUM_HEIGHT_MM, curved_top=False):
    line_placement(F(0),minimum_height_mm,overlap_percent)
    digest = hashlib.sha256(source).hexdigest()
    if digest != expected_source_sha256 or hashlib.sha256(project).hexdigest() != expected_project_sha256:
        raise ValueError('pinned original slice and placed model required')
    if curved_top:
        from tools.exponential_top_fixture import placed_profile
        bounds,top_profile = placed_profile(project)
        slope = None
    else:
        bounds,slope,intercept = sliced_top_face(project)
    _,maximum_height = slicer_height_limit(source)
    validate_dimensions(minimum_width_mm,maximum_width_mm,minimum_height_mm,maximum_height)
    analysis_minimum = analysis_minimum_height(minimum_height_mm,overlap_percent,maximum_height)
    rows,sources,metadata,omitted = baseline(source,digest,F(2))
    candidates,diagnostics = [],[]
    packing_by_dimensions = {}
    x0,x1 = bounds[0]+INSET,bounds[1]-INSET
    for lower,upper,left,right,edges in extract_steps(bounds,sources):
        base,rise = right-left,upper-lower
        record = {'reason':'triangle-rectangle-approximation','lower_z_exact_mm':str(lower),
            'upper_z_exact_mm':str(upper),'left_edge_exact_mm':str(left),'right_edge_exact_mm':str(right),
            'triangle_base_exact_mm':str(base),'triangle_height_exact_mm':str(rise),
            'edge_source_ids':[s.segment_id for s in edges]}
        if not step_base_applicable(base,minimum_width_mm):
            diagnostics.append(dict(record,status='excluded-short-step-base',line_count=0,
                exclusion_rule='base^2 < 2 * minimum_width^2',
                minimum_base_squared_exact_mm2=str(2*minimum_width_mm*minimum_width_mm)))
            continue
        divisions = int(-(-base//COARSE_POSITION_STEP_MM))
        policy = dict(minimum_width_mm=minimum_width_mm,maximum_width_mm=maximum_width_mm,
                      minimum_height_mm=analysis_minimum,maximum_height_mm=maximum_height)
        key = (base,rise)
        if key not in packing_by_dimensions:
            packing_by_dimensions[key] = (pack(base,rise,grid_divisions=divisions,**policy),
                pack(base,rise,grid_divisions=2*divisions,**policy))
        coarse,packing = packing_by_dimensions[key]
        if packing.error_area_mm2 > coarse.error_area_mm2:
            raise ValueError('nested position refinement increased optimum error')
        if not packing.rectangles:
            diagnostics.append(dict(record,status='no-feasible-dimensioned-rectangle'))
            continue
        n = len(packing.rectangles)
        intersections = [posed_intersection_area(base,rise,r,
            -r.height_mm*overlap_percent/100) for r in packing.rectangles]
        areas = [(r.right_mm-r.left_mm)*r.height_mm for r in packing.rectangles]
        if any(2*intersection < area for intersection,area in zip(intersections,areas)):
            raise ValueError('contact Z adjustment exceeds per-line triangle spill limit')
        record.update(status='UNVERIFIED_VIEW_ONLY',line_count=n,
            rectangles_exact_mm=[list(map(str,(left+r.left_mm,left+r.right_mm,lower,lower+r.height_mm)))
                                 for r in packing.rectangles],
            error_area_exact_mm2=str(packing.error_area_mm2),
            posed_error_area_exact_mm2=str(base*rise/2+sum(areas)-2*sum(intersections)),
            posed_individual_spill_fractions_exact=[str((area-intersection)/area)
                for area,intersection in zip(areas,intersections)],
            posed_rectangles_exact_mm=[list(map(str,(left+r.left_mm,left+r.right_mm,
                *line_placement(lower,r.height_mm,overlap_percent)))) for r in packing.rectangles],
            spill_area_exact_mm2=str(packing.spill_area_mm2),
            coarse_error_area_exact_mm2=str(coarse.error_area_mm2),
            position_grid_divisions=packing.grid_divisions,
            position_step_exact_mm=str(base/packing.grid_divisions),
            lattice_optimum_proven=True,optimality_applies_to='zero-overlap reference packing only',
            posed_lattice_optimum_proven=overlap_percent==0,continuous_position_optimum_proven=False,
            individual_spill_fractions_exact=[str(r.spill_area_mm2/((r.right_mm-r.left_mm)*r.height_mm))
                                              for r in packing.rectangles],
            slice_triangle_slope_exact=str(rise/base),
            mesh_plane_slope_exact=None if curved_top else str(slope),
            mesh_triangle_alignment_certified=False)
        diagnostics.append(record)
        for i,r in enumerate(packing.rectangles):
            h,line_width = r.height_mm,r.right_mm-r.left_mm
            if h > line_width:
                raise ValueError('selected bead height exceeds width; unsupported native nominal geometry')
            y = left+(r.left_mm+r.right_mm)/2
            bottom,z = line_placement(lower,h,overlap_percent)
            remaining_height = z-lower
            if remaining_height < minimum_height_mm:
                raise ValueError('overlap leaves less than requested minimum thickness above layer')
            selected = overlapping_sources(sources,ExactTopCellXY(x0,x1,y-line_width/2,y+line_width/2))
            nominal = audit_line(x0,x1,y,bottom,selected)
            diamond = audit_line(x0,x1,y,bottom,selected,model='diamond')
            segment = ExactNominalTopSegment(f'triangle-{lower}-line-{i+1}',
                (x0,y,z),(x1,y,z),line_width,h,'candidate')
            candidates.append((segment,{'review_status':'UNVERIFIED TRIANGLE RECTANGLE / CONTACT NOT ACCEPTED',
                'terrace_z_exact_mm':str(lower),'triangle_index':len(diagnostics),
                'line_index':i+1,'line_count':n,'z_adjustment_exact_mm':str(bottom-lower),
                'overlap_percent_exact':str(overlap_percent),
                'layer_top_z_exact_mm':str(lower),'bottom_z_exact_mm':str(bottom),
                'top_z_exact_mm':str(z),'penetration_depth_exact_mm':str(lower-bottom),
                'remaining_height_above_layer_exact_mm':str(remaining_height),
                'bottom_matches_layer_top':bottom==lower,
                'nominal_centerline_contact':nominal,'diamond_centerline_contact':diamond,
                'continuous_contact_verified':False,'shape_improvement_verified':False}))
    geometry = (bounds,top_profile[0][1]) if curved_top else None
    content,manifest = render_scene(source,digest,project,candidates=candidates,
        section_diagnostics=diagnostics,curved_top_geometry=geometry)
    content = content.replace('STEP INTERPOLATION HYPOTHESES','TRIANGLE SYMMETRIC DIFFERENCE RESEARCH')
    content = content.replace('; CONFIG_BLOCK_START',
        f'; Contact overlap percent: {overlap_percent}; positive lowers by percent of bead height\n; CONFIG_BLOCK_START',1)
    manifest.update(scope='adjacent-layer-triangle-rectangle-display-only',
        step_applicability={'minimum_base_formula':'sqrt(2) * minimum_line_width',
            'minimum_base_mm':math.sqrt(2)*float(minimum_width_mm),
            'minimum_base_squared_exact_mm2':str(2*minimum_width_mm*minimum_width_mm),
            'comparison':'base^2 >= 2 * minimum_line_width^2',
            'excluded_step_count':sum(d['status']=='excluded-short-step-base' for d in diagnostics)},
        rectangle_constraints_mm={'minimum_width':float(minimum_width_mm),
            'maximum_width':float(maximum_width_mm),'minimum_height':float(minimum_height_mm),
            'analysis_minimum_height':float(analysis_minimum),
            'maximum_height':float(maximum_height)},
        rectangle_constraints_exact_mm={'minimum_width':str(minimum_width_mm),
            'maximum_width':str(maximum_width_mm),'minimum_height':str(minimum_height_mm),
            'analysis_minimum_height':str(analysis_minimum),
            'maximum_height':str(maximum_height)},
        objective='minimize symmetric difference of triangle and union of multiple independent rectangles',
        triangle_definition='height = adjacent actual layer Z difference; base = adjacent source edge separation',
        original_target_mesh_alignment_certified=False,
        contact_placement={'overlap_percent_exact':str(overlap_percent),
            'minimum_percent_exact':'0','maximum_percent_exact':str(MAXIMUM_OVERLAP_PERCENT),
            'percent_basis':'each physical bead height',
            'bottom_formula':'layer_top_z - bead_height * overlap_percent / 100',
            'command_z_formula':'bottom_z + bead_height',
            'zero_means':'bottom equals current layer command top Z, not whole-surface contact',
            'positive_means':'penetration below current layer command top Z',
            'minimum_height_basis':'required remaining height above current layer command top Z',
            'analysis_minimum_height_formula':'minimum_height / (1 - overlap_percent / 100)'},
        planned_line_count=len(candidates),
        maximum_spill_fraction_exact='1/2',
        rectangle_model='multiple independent heights and widths; floor anchored; disjoint Y interiors; gaps permitted; repeated sizes permitted',
        continuous_position_optimum_proven=False,
        limitations='Exact-area dynamic programming optimum on nested position lattices with continuous median heights, not a continuous-position or stacked/overlapping packing optimum. Rectangular cross-section differs from physical rounded beads. Whole-footprint contact, original-mesh fit and nozzle clearance remain unverified.')
    return content,manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--overlap-percent',type=F,default=F(0),
        help='positive lowers by this percent of each compensated bead height; 0 to 30, default 0')
    parser.add_argument('--minimum-width-mm',type=F,default=MIN_WIDTH,
        help='minimum line width in mm, default 0.25')
    parser.add_argument('--maximum-width-mm',type=F,default=MAX_WIDTH,
        help='maximum line width in mm, default 0.45')
    parser.add_argument('--minimum-height-mm',type=F,default=DEFAULT_MINIMUM_HEIGHT_MM,
        help='minimum remaining thickness above the current layer after overlap, default 0.08 mm')
    args = parser.parse_args()
    if not 0 <= args.overlap_percent <= MAXIMUM_OVERLAP_PERCENT:
        parser.error('overlap percent must be between 0 and 30')
    folder = ROOT/'artifacts/cuboid-tilt10-review'
    pinned = json.loads((folder/'current-review.json').read_text())
    source = (folder/'original-slice/plate_1.gcode').read_bytes()
    try:
        validate_dimensions(args.minimum_width_mm,args.maximum_width_mm,args.minimum_height_mm,
                            slicer_height_limit(source)[1])
        analysis_minimum_height(args.minimum_height_mm,args.overlap_percent,slicer_height_limit(source)[1])
    except ValueError as error:
        parser.error(str(error))
    content,manifest = build(source,
        (folder/'original-slice/sliced.3mf').read_bytes(),
        expected_source_sha256=pinned['source_slice_sha256'],
        expected_project_sha256=pinned['placed_project_sha256'],overlap_percent=args.overlap_percent,
        minimum_width_mm=args.minimum_width_mm,maximum_width_mm=args.maximum_width_mm,
        minimum_height_mm=args.minimum_height_mm)
    target = folder/f'cuboid-triangle-rectangle-{uuid4().hex}.UNVERIFIED_VIEW_ONLY.gcode'
    target.write_bytes(content.encode('ascii'))
    manifest.update(viewer_file=str(target),viewer_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    target.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (folder/'current-triangle-review.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('candidate_segments','section_diagnostics')},indent=2))


if __name__ == '__main__':
    main()
