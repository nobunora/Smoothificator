"""Render Z offsets bounded by line thickness; historical excessive drops fail."""
from fractions import Fraction as F
import hashlib
import json
from uuid import uuid4

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from tools.build_tilted_cuboid_review import ROOT, render_scene, slicer_height_limit
from tools.build_tilted_cuboid_review import sliced_top_face
from tools.analyze_thickness_z_offsets import bounded_offset


def build(source,project,analysis):
    if (analysis['state'] != 'bounded' or analysis['scope'] != 'uniform-downward-translation-display-only'
            or hashlib.sha256(source).hexdigest() != analysis['source_slice_sha256']):
        raise ValueError('bounded source-bound contact analysis is required')
    if hashlib.sha256(project).hexdigest() != analysis['placed_project_sha256']:
        raise ValueError('unpinned placed project')
    maximum_height = slicer_height_limit(source)[1]
    shift = F(analysis['uniform_downward_shift_exact_mm'])
    if not 0 <= shift <= F(1):
        raise ValueError('invalid bounded viewer translation')
    if any(shift > F(row['height_exact_mm'])/10 for row in analysis['lines']):
        raise ValueError('Z offset exceeds ten percent of line height; historical burial probe rejected')
    candidates = []
    for index,row in enumerate(analysis['lines']):
        ax,ay,z = map(F,row['start_exact_mm'])
        bx,by,ez = map(F,row['end_exact_mm'])
        w,h = F(row['width_exact_mm']),F(row['height_exact_mm'])
        if ay != by or z != ez or not ax < bx or not F('.25') <= w <= F('.45'):
            raise ValueError('unsupported probe geometry')
        if not F('.05') <= h <= maximum_height:
            raise ValueError('invalid fixture bead height')
        bottom = z-h-shift
        if (bottom > F(row['nominal_support']['minimum_lower_exact_mm'])
                or bottom > F(row['diamond_support']['minimum_lower_exact_mm'])):
            raise ValueError('translation does not reach certified support')
        segment = ExactNominalTopSegment(f'lowered-contact-probe-{index+1}',
            (ax,ay,z-shift),(bx,by,z-shift),w,h,'candidate')
        candidates.append((segment,{'review_status':'UNVERIFIED INTERSECTION / BURIED MATERIAL PROBE',
            'original_top_exact_mm':str(z),'uniform_downward_shift_exact_mm':str(shift),
            'nominal_and_diamond_centerline_upper_envelope_contact_verified':True,
            'central_strip_width_mm':0,'continuous_contact_verified':False,
            'useful_surface_interpolation_verified':False,'shape_improvement_verified':False,
            'nominal_peak_above_shifted_top_lower_mm':row['nominal_peak_above_shifted_top_lower_mm']}))
    content,manifest = render_scene(source,analysis['source_slice_sha256'],project,
        candidates=candidates,section_diagnostics=[])
    content = content.replace('; UNVERIFIED VIEW ONLY - STEP INTERPOLATION HYPOTHESES - DO NOT PRINT',
        '; UNVERIFIED VIEW ONLY - UNIFORM Z DROP / BURIED INTERSECTION PROBE - DO NOT PRINT')
    content = content.replace('; CONFIG_BLOCK_START',
        '; Contact permits burial in existing material; NOT an accepted interpolation path\n; CONFIG_BLOCK_START',1)
    manifest.update(scope='uniform-z-contact-burial-display-only',
        uniform_downward_shift_exact_mm=str(shift),uniform_downward_shift_mm=float(shift),
        nominal_and_diamond_centerline_upper_envelope_contact_verified=True,
        full_footprint_contact_verified=False,useful_surface_interpolation_verified=False,
        source_contact_analysis_sha256=hashlib.sha256(json.dumps(analysis,sort_keys=True).encode()).hexdigest(),
        limitations=analysis['limitations'])
    return content,manifest


def build_bounded(source,project,analysis,*,fraction=F('-.1')):
    if (analysis['scope'] != 'line-thickness-bounded-z-offset-display-only'
            or hashlib.sha256(source).hexdigest()!=analysis['source_slice_sha256']
            or hashlib.sha256(project).hexdigest()!=analysis['placed_project_sha256']):
        raise ValueError('source-bound thickness offset analysis required')
    bounded_offset(F(1),fraction)
    variants = [v for v in analysis['variants'] if F(v['offset_fraction_exact'])==fraction]
    if len(variants)!=1:
        raise ValueError('one matching offset variant required')
    maximum_height = slicer_height_limit(source)[1]
    bounds,slope,intercept = sliced_top_face(project)
    candidates = []
    for index,row in enumerate(variants[0]['lines']):
        ax,ay,z = map(F,row['start_exact_mm'])
        bx,by,ez = map(F,row['end_exact_mm'])
        w,h = F(row['width_exact_mm']),F(row['height_exact_mm'])
        offset = bounded_offset(h,fraction)
        if (ay!=by or z!=ez or not ax<bx or not F('.25')<=w<=F('.45')
                or not F('.05')<=h<=maximum_height
                or z!=F(row['original_top_exact_mm'])+offset
                or offset!=F(row['z_offset_exact_mm'])):
            raise ValueError('invalid bounded offset geometry')
        if z > slope*(ay-w/2)+intercept:
            raise ValueError('offset exceeds model rectangular envelope')
        s = ExactNominalTopSegment(f'thickness-offset-probe-{index+1}',
                                  (ax,ay,z),(bx,by,z),w,h,'candidate')
        candidates.append((s,{'review_status':'UNVERIFIED LINE-THICKNESS Z OFFSET / CONTACT GAPS REMAIN',
            'offset_fraction_exact':str(fraction),'z_offset_exact_mm':str(offset),
            'physical_line_height_exact_mm':str(h),
            'height_above_original_floor_mm':row['rectangle_height_above_original_floor_mm'],
            'nominal_centerline_contact':row['nominal_centerline_contact'],
            'diamond_centerline_contact':row['diamond_centerline_contact'],
            'continuous_contact_verified':False,'useful_surface_interpolation_verified':False,
            'shape_improvement_verified':False}))
    content,manifest = render_scene(source,analysis['source_slice_sha256'],project,
        candidates=candidates,section_diagnostics=[])
    content = content.replace('; UNVERIFIED VIEW ONLY - STEP INTERPOLATION HYPOTHESES - DO NOT PRINT',
        '; UNVERIFIED VIEW ONLY - LINE THICKNESS +/-10% Z TRIAL - DO NOT PRINT')
    content = content.replace('; CONFIG_BLOCK_START',
        '; Contact gaps remain; no clipping or excessive lowering to manufacture contact\n; CONFIG_BLOCK_START',1)
    manifest.update(scope='line-thickness-bounded-z-offset-display-only',
        offset_fraction_exact=str(fraction),maximum_offset_fraction_exact='1/10',
        full_footprint_contact_verified=False,useful_surface_interpolation_verified=False,
        source_contact_analysis_sha256=hashlib.sha256(json.dumps(analysis,sort_keys=True).encode()).hexdigest(),
        limitations=analysis['limitations'])
    return content,manifest


def main():
    folder = ROOT/'artifacts/cuboid-tilt10-review'
    analysis = json.loads((folder/'thickness-z-offsets.json').read_text())
    content,manifest = build_bounded((folder/'original-slice/plate_1.gcode').read_bytes(),
                            (folder/'original-slice/sliced.3mf').read_bytes(),analysis)
    target = folder/f'cuboid-thickness-z-{uuid4().hex}.UNVERIFIED_VIEW_ONLY.gcode'
    target.write_bytes(content.encode('ascii'))
    manifest.update(viewer_file=str(target),viewer_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    target.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (folder/'current-thickness-z-review.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k!='candidate_segments'},indent=2))


if __name__ == '__main__':
    main()
