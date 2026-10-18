"""Offline concentric VIEW_ONLY hypotheses for the revolved exponential top."""
from fractions import Fraction as F
import argparse
import hashlib
import json
import math
import subprocess
from uuid import uuid4

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from tools.revolved_exponential_fixture import ROOT, REVIEW_FOLDER, prepare, placed_geometry
from tools.build_tilted_cuboid_review import baseline, slicer_height_limit, render_scene
from tools.build_triangle_rectangle_review import (
    validate_dimensions, analysis_minimum_height, line_placement, step_base_applicable,
    posed_intersection_area, COARSE_POSITION_STEP_MM,
)
from tools.solve_triangle_rectangle import pack


RING_SEGMENTS = 192


def positive_ray_interval(row, center):
    """Numerical intersection of a finite flat-cap footprint with +X ray."""
    _,ax,ay,bx,by,width,_ = row
    cx,cy,_ = center
    dx,dy = bx-ax,by-ay
    length = math.hypot(dx,dy)
    nx,ny = -dy/length*width/2,dx/length*width/2
    polygon = ((ax+nx,ay+ny),(bx+nx,by+ny),(bx-nx,by-ny),(ax-nx,ay-ny))
    crossings = []
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if a[1] == b[1]:
            if abs(a[1]-cy)<1e-10:
                crossings.extend((a[0],b[0]))
        elif min(a[1],b[1])<=cy<=max(a[1],b[1]):
            crossings.append(a[0]+(cy-a[1])*(b[0]-a[0])/(b[1]-a[1]))
    if not crossings or max(crossings)<cx:
        return None
    return max(0.,min(crossings)-cx),max(crossings)-cx


def radial_steps(rows,metadata,center,top):
    edges = {}
    for row in rows:
        level = F(str(row[0]))
        if level < top[0][1]-F('.000001'):
            continue
        interval = positive_ray_interval(row,center)
        if interval is None:
            continue
        radius = F(f'{interval[0]:.9f}')
        if level <= top[0][1]+F('.000001'):
            radius = F(0)
        if level not in edges or radius<edges[level][0]:
            edges[level] = radius,row[-1]
    steps = []
    levels = sorted(edges)
    for lower,upper in zip(levels,levels[1:]):
        (left,a),(right,b) = edges[lower],edges[upper]
        if not F(0)<=left<right<=top[-1][0]:
            continue
        if metadata[b][1] != upper-lower:
            raise ValueError('radial step does not match actual layer height')
        steps.append((lower,upper,left,right,(a,b)))
    return steps


def ring_vertices(center,radius,z,segments=RING_SEGMENTS):
    points = tuple((F(f'{center[0]+float(radius)*math.cos(2*math.pi*j/segments):.9f}'),
                    F(f'{center[1]+float(radius)*math.sin(2*math.pi*j/segments):.9f}'),z)
                   for j in range(segments))
    return points+(points[0],)


def build(source,project,receipt,*, minimum_width=F('.25'),maximum_width=F('.45'),
          minimum_height=F('.08'),overlap_percent=F(0)):
    digest = hashlib.sha256(source).hexdigest()
    if digest!=receipt['source_slice_sha256'] or hashlib.sha256(project).hexdigest()!=receipt['placed_project_sha256']:
        raise ValueError('pinned revolution source and placed model required')
    center,top,vertices = placed_geometry(project)
    _,maximum_height = slicer_height_limit(source)
    validate_dimensions(minimum_width,maximum_width,minimum_height,maximum_height)
    analysis_minimum = analysis_minimum_height(minimum_height,overlap_percent,maximum_height)
    rows,_,metadata,_ = baseline(source,digest,F(2))
    candidates,rings,diagnostics = [],[],[]
    for lower,upper,left,right,witness in radial_steps(rows,metadata,center,top):
        base,rise = right-left,upper-lower
        record = {'floor_z_exact_mm':str(lower),'upper_z_exact_mm':str(upper),
            'left_radius_exact_mm':str(left),'right_radius_exact_mm':str(right),
            'triangle_base_exact_mm':str(base),'triangle_height_exact_mm':str(rise),
            'boundary_source_lines':list(witness),'reason':'radial-step-triangle'}
        if not step_base_applicable(base,minimum_width):
            diagnostics.append(dict(record,status='excluded-short-step-base',ring_count=0))
            continue
        divisions = int(-(-base//COARSE_POSITION_STEP_MM))
        policy = dict(minimum_width_mm=minimum_width,maximum_width_mm=maximum_width,
                      minimum_height_mm=analysis_minimum,maximum_height_mm=maximum_height)
        coarse = pack(base,rise,grid_divisions=divisions,**policy)
        packing = pack(base,rise,grid_divisions=2*divisions,**policy)
        if packing.error_area_mm2>coarse.error_area_mm2:
            raise ValueError('radial lattice refinement increased reference error')
        record.update(status='UNVERIFIED_VIEW_ONLY',ring_count=len(packing.rectangles),
            reference_error_area_exact_mm2=str(packing.error_area_mm2),
            continuous_radial_optimum_proven=False,annular_volume_optimum_proven=False)
        diagnostics.append(record)
        for rectangle in packing.rectangles:
            width,h = rectangle.right_mm-rectangle.left_mm,rectangle.height_mm
            radius = left+(rectangle.left_mm+rectangle.right_mm)/2
            bottom,z = line_placement(lower,h,overlap_percent)
            intersection = posed_intersection_area(base,rise,rectangle,bottom-lower)
            if h>width or z-lower<minimum_height or 2*intersection<width*h:
                raise ValueError('ring nominal dimensions/remaining height/spill policy failed')
            ring_id = f'ring-{len(rings)+1}'
            points = ring_vertices(center,radius,z)
            rings.append({'id':ring_id,'radius_exact_mm':str(radius),'width_exact_mm':str(width),
                'height_exact_mm':str(h),'bottom_z_exact_mm':str(bottom),'top_z_exact_mm':str(z),
                'floor_z_exact_mm':str(lower),'remaining_height_exact_mm':str(z-lower),
                'spill_fraction_exact':str((width*h-intersection)/(width*h)),
                'chord_count':RING_SEGMENTS,'whole_ring_contact_verified':False})
            for i,(a,b) in enumerate(zip(points,points[1:])):
                s = ExactNominalTopSegment(f'{ring_id}-chord-{i+1}',a,b,width,h,'candidate')
                candidates.append((s,{'ring_id':ring_id,'chord_index':i+1,
                    'review_status':'UNVERIFIED REVOLVED CROSS-SECTION HYPOTHESIS',
                    'continuous_contact_verified':False,'shape_improvement_verified':False}))
    cx,cy,_ = center
    radius = top[-1][0]
    bounds = tuple(F(str(v)) for v in (cx-float(radius),cx+float(radius),cy-float(radius),cy+float(radius)))
    content,manifest = render_scene(source,digest,project,candidates=candidates,
        section_diagnostics=diagnostics,curved_top_geometry=(bounds,top[0][1]))
    content = content.replace('STEP INTERPOLATION HYPOTHESES','REVOLVED EXPONENTIAL RINGS')
    manifest.update(scope='revolved-exponential-ring-display-only',surface_type='surface of revolution',
        rectangle_constraints_mm={'minimum_width':float(minimum_width),'maximum_width':float(maximum_width),
            'minimum_height':float(minimum_height),'maximum_height':float(maximum_height)},
        planned_line_count=len(rings),
        rings=rings,ring_count=len(rings),chords_per_ring=RING_SEGMENTS,
        center_mm=list(center),overlap_percent_exact=str(overlap_percent),
        rectangle_constraints_exact_mm={'minimum_width':str(minimum_width),'maximum_width':str(maximum_width),
            'minimum_remaining_height':str(minimum_height),'analysis_minimum_height':str(analysis_minimum),
            'maximum_physical_height':str(maximum_height)},
        excluded_step_count=sum(s['status']=='excluded-short-step-base' for s in diagnostics),
        radial_boundary_method='positive-X source footprint ray; numerically rounded to 9 decimals',
        annular_volume_optimum_proven=False,whole_ring_contact_verified=False,
        limitations='Same radial cross-section packing, expanded to concentric polygonal paths. Source deposition is not rotationally symmetric; ray boundaries do not establish whole-ring support. No annular-volume optimum, full contact, nozzle clearance or printability certificate.')
    return content,manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reslice',action='store_true')
    parser.add_argument('--minimum-width-mm',type=F,default=F('.25'))
    parser.add_argument('--maximum-width-mm',type=F,default=F('.45'))
    parser.add_argument('--minimum-height-mm',type=F,default=F('.08'))
    parser.add_argument('--overlap-percent',type=F,default=F(0))
    args = parser.parse_args()
    folder,sliced = REVIEW_FOLDER,REVIEW_FOLDER/'original-slice'
    if args.reslice or not (folder/'slice-receipt.json').is_file():
        project = prepare()
        sliced.mkdir(exist_ok=True)
        run = subprocess.run([str(ROOT/'artifacts/runtime/orca-nightly/OrcaSlicer/orca-slicer.exe'),
            '--slice','0','--orient','0','--arrange','0','--export-3mf','sliced.3mf',
            '--datadir',str(folder/'cli-profile'),'--outputdir',str(sliced),str(project)],
            cwd=folder,capture_output=True,timeout=180)
        (folder/'slice-stdout.log').write_bytes(run.stdout)
        (folder/'slice-stderr.log').write_bytes(run.stderr)
        if run.returncode:
            raise RuntimeError('revolution offline slice failed')
        (folder/'slice-receipt.json').write_text(json.dumps({
            'source_slice_sha256':hashlib.sha256((sliced/'plate_1.gcode').read_bytes()).hexdigest(),
            'placed_project_sha256':hashlib.sha256((sliced/'sliced.3mf').read_bytes()).hexdigest()},indent=2)+'\n')
    source,project = (sliced/'plate_1.gcode').read_bytes(),(sliced/'sliced.3mf').read_bytes()
    receipt = json.loads((folder/'slice-receipt.json').read_text())
    try:
        content,manifest = build(source,project,receipt,minimum_width=args.minimum_width_mm,
            maximum_width=args.maximum_width_mm,minimum_height=args.minimum_height_mm,
            overlap_percent=args.overlap_percent)
    except ValueError as error:
        parser.error(str(error))
    target = folder/f'revolved-exponential-{uuid4().hex}.UNVERIFIED_VIEW_ONLY.gcode'
    target.write_bytes(content.encode('ascii'))
    manifest.update(viewer_file=str(target),viewer_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (folder/'current-review.json').write_text(json.dumps(manifest,indent=2)+'\n')
    target.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('candidate_segments','rings','section_diagnostics')},indent=2))


if __name__ == '__main__':
    main()
