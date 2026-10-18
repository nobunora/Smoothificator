"""Render the error-ranked, balanced placement as explicit unverified probes."""
from fractions import Fraction as F
import hashlib
import json
from uuid import uuid4

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY
from tools.audit_line_support import audit_line
from tools.build_tilted_cuboid_review import ROOT, baseline, render_scene, sliced_top_face, slicer_height_limit
from tools.compare_top_surface_residual import overlapping_sources


def build(source,project,report):
    if (report['scope']!='sampled-full-face-balanced-error-research-only'
            or hashlib.sha256(source).hexdigest()!=report['source_slice_sha256']
            or hashlib.sha256(project).hexdigest()!=report['placed_project_sha256']):
        raise ValueError('source-bound error optimization required')
    if not report['validation_improves_previous']:
        raise ValueError('independent evaluation does not improve previous placement')
    bounds,slope,intercept = sliced_top_face(project)
    maximum_height = slicer_height_limit(source)[1]
    rows,sources,metadata,omitted = baseline(source,report['source_slice_sha256'],F(2))
    x0,x1 = bounds[0]+F('.3'),bounds[1]-F('.3')
    candidates = []
    for index,p in enumerate(report['selected']):
        floor,y,w,h,f,z = map(F,(p['terrace_z_exact_mm'],p['y_exact_mm'],p['width_exact_mm'],
                                p['height_exact_mm'],p['offset_fraction_exact'],p['top_z_exact_mm']))
        middle = slope*y+intercept
        if (not F('.25')<=w<=F('.45') or not F('.05')<=h<=maximum_height or abs(f)>F('.1')
                or z!=floor+h*(1+f) or abs(z-middle)>h/10
                or y-w/2<bounds[2] or y+w/2>bounds[3]):
            raise ValueError('balanced placement or physical limits violated')
        selected = overlapping_sources(sources,ExactTopCellXY(x0,x1,y-w/2,y+w/2))
        nominal = audit_line(x0,x1,y,z-h,selected)
        diamond = audit_line(x0,x1,y,z-h,selected,model='diamond')
        s = ExactNominalTopSegment(f'balanced-error-probe-{index+1}',(x0,y,z),(x1,y,z),w,h,'candidate')
        candidates.append((s,{'review_status':'UNVERIFIED SAMPLED-ERROR OPTIMUM / CONTACT NOT ACCEPTED',
            'terrace_z_exact_mm':str(floor),'offset_fraction_exact':str(f),
            'z_adjustment_exact_mm':str(h*f),'midpoint_target_z_exact_mm':str(middle),
            'midpoint_deviation_exact_mm':str(z-middle),
            'nominal_centerline_contact':nominal,'diamond_centerline_contact':diamond,
            'continuous_contact_verified':False,'shape_improvement_verified':False,
            'global_continuous_minimum_proven':False}))
    content,manifest = render_scene(source,report['source_slice_sha256'],project,
        candidates=candidates,section_diagnostics=[])
    content = content.replace('; UNVERIFIED VIEW ONLY - STEP INTERPOLATION HYPOTHESES - DO NOT PRINT',
        '; UNVERIFIED VIEW ONLY - BALANCED SIGNED ERROR RESEARCH - DO NOT PRINT')
    content = content.replace('; CONFIG_BLOCK_START',
        '; Placement balances shortage and excess; not inscribed-only; contact/clearance unverified\n; CONFIG_BLOCK_START',1)
    manifest.update(scope='balanced-sampled-error-display-only',
        objective=report['objective'],validation_comparison=report['validation_comparison'],
        source_optimization_sha256=hashlib.sha256(json.dumps(report,sort_keys=True).encode()).hexdigest(),
        global_continuous_minimum_proven=False,full_footprint_contact_verified=False,
        limitations=report['limitations'])
    return content,manifest


def main():
    folder = ROOT/'artifacts/cuboid-tilt10-review'
    report = json.loads((folder/'balanced-error-optimization.json').read_text())
    content,manifest = build((folder/'original-slice/plate_1.gcode').read_bytes(),
                            (folder/'original-slice/sliced.3mf').read_bytes(),report)
    target = folder/f'cuboid-balanced-error-{uuid4().hex}.UNVERIFIED_VIEW_ONLY.gcode'
    target.write_bytes(content.encode('ascii'))
    manifest.update(viewer_file=str(target),viewer_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    target.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (folder/'current-balanced-review.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k!='candidate_segments'},indent=2))


if __name__=='__main__':
    main()
