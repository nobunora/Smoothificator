"""Offline 10-degree cuboid: interpolate exposed slice steps, never blanket hatch.

Research viewer adapter only. Nominal cell certificates allow penetration and
do not establish full-footprint contact, improvement or chronological safety.
"""
from collections import defaultdict
from fractions import Fraction as F
import hashlib
import json
import math
import subprocess
from time import monotonic
from uuid import uuid4
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY
from smoothificator_preview.native_scene import _config
from tools.audit_layered_preview_overlap import source_segments
from tools.audit_top_contact_cells import audit_strip
from tools.solve_step_rectangles import Section, fill_tiled_section, split_line_intervals
from tools.build_cuboid_top_review import ROOT, prepare_fixture
from tools.compare_top_surface_residual import overlapping_sources


MIN_WIDTH = F('.25')
MAX_WIDTH = F('.45')
MIN_HEIGHT = F('.05')
LAYER_HEIGHT_FACTOR = F('.9')
INSET = F('.3')


def slicer_height_limit(source: bytes):
    """Bind the maximum to the source slicer's configured layer_height."""
    lines = source.decode('ascii').splitlines()
    start,end = lines.index('; CONFIG_BLOCK_START'),lines.index('; CONFIG_BLOCK_END')
    settings = [F(line.split(' = ',1)[1]) for line in lines[start+1:end]
                if line.startswith('; layer_height = ')]
    if len(settings) != 1 or settings[0] <= 0:
        raise ValueError('one positive configured layer_height is required')
    maximum = settings[0]*LAYER_HEIGHT_FACTOR
    if maximum < MIN_HEIGHT:
        raise ValueError('configured layer height gives maximum below minimum candidate height')
    return settings[0],maximum


def sliced_top_face(project: bytes):
    """Read the actual slicer's placed mesh, not an assumed plate offset."""
    from io import BytesIO
    with ZipFile(BytesIO(project)) as archive:
        main = ET.fromstring(archive.read('3D/3dmodel.model'))
        component = main.find('.//{*}component')
        item = main.find('.//{*}build/{*}item')
        if component is None or item is None:
            raise ValueError('missing placed cuboid mesh')
        transform = tuple(F(v) for v in item.attrib['transform'].split())
        identity = tuple(map(F, (1,0,0,0,1,0,0,0,1)))
        if (transform[:9] != identity or len(transform) != 12
                or component.attrib.get('transform') != '1 0 0 0 1 0 0 0 1 0 0 0'):
            raise ValueError('unexpected cuboid placement rotation')
        path = next(v for k,v in component.attrib.items() if k.endswith('}path'))
        part = ET.fromstring(archive.read(path.lstrip('/')))
    vertices = [tuple(F(n.attrib[a])+transform[9+i] for i,a in enumerate('xyz'))
                for n in part.findall('.//{*}vertex')]
    if len(vertices) != 8 or len(part.findall('.//{*}triangle')) != 12:
        raise ValueError('unexpected cuboid topology')
    # Generator's vertex order is retained in the exported mesh; verify the
    # four actual top corners form the expected X-directed tilted rectangle.
    a,b,c,d = vertices[4:]
    if not (a[1:] == b[1:] and c[1:] == d[1:] and a[0] == d[0]
            and b[0] == c[0] and b[0]-a[0] == 20 and c[1]>b[1]):
        raise ValueError('unexpected top rectangle')
    slope = (c[2]-b[2])/(c[1]-b[1])
    if abs(math.degrees(math.atan(float(slope)))-10) > .00001:
        raise ValueError('model is not tilted 10 degrees about X')
    return (a[0],b[0],a[1],c[1]), slope, a[2]-slope*a[1]


def baseline(source, digest, minimum_audit_z):
    rows = source_segments(source,expected_sha256=digest)
    metadata = {}
    feature, height = '', None
    for number,line in enumerate(source.decode('ascii').splitlines(),1):
        if line.startswith('; FEATURE: '):
            feature = line[11:]
        if line.startswith('; LAYER_HEIGHT:'):
            height = F(line.split(':',1)[1].strip())
        metadata[number] = feature,height
    exact, omitted = [], []
    for z,ax,ay,bx,by,w,n in rows:
        height = metadata[n][1]
        if height is None or not 0 < height <= F(str(w)):
            # The slicer can emit sub-height gap infill. Preserve its complete
            # viewer geometry; omit from top queries only when its maximum Z
            # is strictly below every queried contact plane.
            if height is None or F(str(z)) >= minimum_audit_z:
                raise ValueError('unsupported bead in top audit domain')
            omitted.append({'line':n,'maximum_z_mm':z,'reason':'below-all-top-audit-planes'})
            continue
        exact.append(ExactNominalTopSegment(str(n),tuple(F(str(v)) for v in (ax,ay,z)),
                    tuple(F(str(v)) for v in (bx,by,z)),F(str(w)),height,'structural'))
    return rows, tuple(exact), metadata, omitted


def step_candidates(bounds, slope, intercept, sources, *, maximum_height):
    """Solve rectangles in a flat-terrace section, then audit whole paths.

    The section is an explicit staircase approximation. A 2D solution alone
    never establishes feasibility for the actual 3D stadium envelope. No
    support-based clipping of a candidate is performed.
    """
    if slope <= 0:
        return [], [{'reason':'non-positive-slope-no-rising-step-section'}]
    x0,x1,y0,y1 = bounds
    x0,x1 = x0+INSET,x1-INSET
    levels = sorted({s.start_xyz_mm[2] for s in sources
                     if slope*y0+intercept <= s.start_xyz_mm[2] <= slope*y1+intercept})
    candidates,diagnostics = [], []
    augmented = tuple(sources)
    for level in levels:
        higher = [s for s in sources if s.start_xyz_mm[2] > level
                  and max(s.start_xyz_mm[0],s.end_xyz_mm[0])+s.width_mm/2 >= x0
                  and min(s.start_xyz_mm[0],s.end_xyz_mm[0])-s.width_mm/2 <= x1]
        if not higher:
            diagnostics.append({'terrace_z_mm':float(level),'reason':'terminal-edge-no-next-riser'})
            continue
        frontier = min(y1,min(min(s.start_xyz_mm[1],s.end_xyz_mm[1])-s.width_mm/2 for s in higher))
        left = max(y0,(level-intercept)/slope)
        if frontier <= left:
            diagnostics.append({'terrace_z_mm':float(level),'reason':'no-positive-rectangle-section'})
            continue
        rectangles,residual = fill_tiled_section(Section(left,frontier,level,slope,intercept),
            minimum_line_width=MIN_WIDTH,maximum_line_width=MAX_WIDTH,
            minimum_height=MIN_HEIGHT,maximum_height=maximum_height)
        diagnostics.append({'terrace_z_mm':float(level),
            'model':'flat terrace at command Z; higher-source conservative XY bbox frontier',
            'reason':'2d-rectangles-found' if rectangles else 'no-feasible-2d-rectangle',
            'maximum_section_gap_mm':float(slope*frontier+intercept-level),
            'maximum_height_at_minimum_width_mm':float(slope*(frontier-MIN_WIDTH)+intercept-level),
            'rectangle_count':len(rectangles),'residual_sections':len(residual),
            'actual_3d_nonexistence_proven':False})
        for rectangle_index,rectangle in enumerate(rectangles):
            intervals = split_line_intervals(rectangle,minimum_width=MIN_WIDTH,maximum_width=MAX_WIDTH)
            group_id = f'terrace-{level}-rectangle-{rectangle_index+1}'
            group_plan = {'terrace_z_mm':float(level),'reason':'rectangle-line-tiling',
                'rectangle_id':group_id,'line_count':len(intervals),
                'rectangle_exact_mm':list(map(str,(rectangle.left,rectangle.right,rectangle.bottom,rectangle.top))),
                'line_intervals_exact_mm':[[str(a),str(b)] for a,b in intervals],
                'line_width_exact_mm':str(intervals[0][1]-intervals[0][0]) if intervals else None,
                'nominal_rectangular_coverage_exact':bool(intervals)}
            diagnostics.append(group_plan)
            if not intervals:
                raise ValueError('rectangle solver returned untileable width')
            group = []
            for line_index,(a,b) in enumerate(intervals):
                w,h = b-a,rectangle.top-rectangle.bottom
                y,z = (a+b)/2,rectangle.top
                footprint = ExactTopCellXY(x0,x1,a,b)
                selected = overlapping_sources(augmented,footprint)
                # Nominal rectangular tiling is not solid coverage by rounded
                # stadium beads. Check every line's whole-X central flat band.
                deadline = monotonic()+3
                contact = audit_strip(ExactTopCellXY(x0,x1,y-F('.01'),y+F('.01')),
                    selected,rectangle.bottom,max_cells=1023,max_depth=18,
                    cancelled=lambda:monotonic()>=deadline)
                if contact['state'] != 'nominal-strip-intersection-proven':
                    diagnostics.append({'terrace_z_mm':float(level),
                        'reason':'2d-solution-requires-3d-support-reconstruction',
                        'rectangle_id':group_id,'failed_line_index':line_index+1,
                        'whole_path_contact':contact})
                    break
                candidate = ExactNominalTopSegment(f'{group_id}-line-{line_index+1}',
                    (x0,y,z),(x1,y,z),w,h,'candidate')
                group.append((candidate,{'terrace_z_mm':float(level),
                    'rectangle_id':group_id,'line_index':line_index+1,'line_count':len(intervals),
                    'nominal_width_exact_mm':str(w),
                    'rectangle_exact_mm':group_plan['rectangle_exact_mm'],
                    'whole_path_central_strip':contact,'continuous_contact_verified':False,
                    'shape_improvement_verified':False,'review_status':'UNVERIFIED tiled rectangle / 3D central-strip hypothesis'}))
            if len(group) != len(intervals):
                # Do not emit a partially supported rectangle or use it as
                # the foundation of subsequent rectangles.
                break
            candidates.extend(group)
            augmented += tuple(candidate for candidate,review in group)
    return candidates,diagnostics


def build_scene(source: bytes, digest: str, project: bytes):
    bounds,slope,intercept = sliced_top_face(project)
    configured_height,maximum_height = slicer_height_limit(source)
    rows,exact,metadata,omitted = baseline(source,digest,slope*bounds[2]+intercept-maximum_height)
    candidates,skipped = step_candidates(bounds,slope,intercept,exact,maximum_height=maximum_height)
    return render_scene(source,digest,project,candidates=candidates,section_diagnostics=skipped)


def render_scene(source: bytes, digest: str, project: bytes, *, candidates, section_diagnostics,
                 curved_top_geometry=None):
    """Shared native representation for explicitly unverified research scenes."""
    if curved_top_geometry is None:
        bounds,slope,intercept = sliced_top_face(project)
        minimum_top_z = slope*bounds[2]+intercept
        surface_metadata = {'tilt_x_degrees':10,
            'target_plane_z_equals_by_plus_c_exact':[str(slope),str(intercept)]}
    else:
        bounds,minimum_top_z = curved_top_geometry
        surface_metadata = {'surface_type':'monotone exponential-angle top mesh'}
    configured_height,maximum_height = slicer_height_limit(source)
    rows,exact,metadata,omitted = baseline(source,digest,minimum_top_z-maximum_height)
    skipped = section_diagnostics
    lines = source.decode('ascii').splitlines()
    start,end = lines.index('; CONFIG_BLOCK_START'),lines.index('; CONFIG_BLOCK_END')
    config,diameter = _config(tuple(tuple(line[2:].split(' = ',1))
        for line in lines[start+1:end] if line.startswith('; ') and ' = ' in line
        and line[2:].split(' = ',1)[0] not in ('wipe_tower_x','wipe_tower_y')))
    by_z = defaultdict(list)
    for z,ax,ay,bx,by,w,number in rows:
        by_z[F(str(z))].append(((F(str(ax)),F(str(ay)),F(str(bx)),F(str(by)),
                                 F(str(w)),metadata[number][1]),metadata[number][0]))
    for s,review in candidates:
        ax,ay,_ = s.start_xyz_mm
        bx,by,_ = s.end_xyz_mm
        by_z[s.start_xyz_mm[2]].append(((ax,ay,bx,by,s.width_mm,s.height_mm),'Custom'))
    n = lambda v: f'{float(v):.9f}'.rstrip('0').rstrip('.')
    output = ['; generated by OrcaSlicer compatible Smoothificator viewer representation',
              '; UNVERIFIED VIEW ONLY - STEP INTERPOLATION HYPOTHESES - DO NOT PRINT',
              '; '+('Mesh tilted 10 degrees about X before slicing' if curved_top_geometry is None
                     else 'Exponential-angle curved top mesh')+'; no blanket top hatch',
              '; Original extrusion coordinates retained; chronological program not retained',
              '; CONFIG_BLOCK_START']
    output.extend(f'; {k} = {v}' for k,v in config)
    output.extend(('; CONFIG_BLOCK_END','G21','G90','M83','G92 E0'))
    for z,segments in sorted(by_z.items()):
        output.extend(('; CHANGE_LAYER',f'; Z_HEIGHT: {n(z)}'))
        for (ax,ay,bx,by,w,h),feature in segments:
            area = float(w*h)+(math.pi/4-1)*float(h*h)
            extrusion = math.hypot(float(bx-ax),float(by-ay))*area/(math.pi*(diameter/2)**2)
            output.extend((f'G1 X{n(ax)} Y{n(ay)} Z{n(z)} F1200',f'; FEATURE: {feature}',
                f'; LINE_WIDTH: {n(w)}',f'; LAYER_HEIGHT: {n(h)}',
                f'G1 X{n(bx)} Y{n(by)} E{n(extrusion)} F1200'))
    content = '\n'.join(output)+'\n'
    if len(content) > 4_194_304 or not content.isascii():
        raise ValueError('bounded scene size exceeded')
    manifest = {'scope':'tilted-cuboid-step-interpolation-display-only',
        **surface_metadata,'source_slice_sha256':digest,
        'placed_project_sha256':hashlib.sha256(project).hexdigest(),
        'top_face_bounds_exact_mm':list(map(str,bounds)),
        'original_segment_count':len(rows),'original_layer_count':len(set(r[0] for r in rows)),
        'top_query_omissions':omitted,
        'viewer_layer_count':len(by_z),'candidate_count':len(candidates),'section_diagnostics':skipped,
        'planned_line_count':sum(d.get('line_count',0) for d in skipped if d['reason']=='rectangle-line-tiling'),
        'rectangle_constraints_mm':{'minimum_width':float(MIN_WIDTH),'maximum_width':float(MAX_WIDTH),
            'minimum_height':float(MIN_HEIGHT),'maximum_height':float(maximum_height)},
        'height_limit_basis':{'source':'source CONFIG_BLOCK layer_height',
            'configured_layer_height_mm':float(configured_height),'factor_exact':str(LAYER_HEIGHT_FACTOR)},
        'continuous_contact_verified':False,'shape_improvement_verified':False,
        'printable_authorized':False,
        'limitations':'Exact maximum rectangles in a flat-terrace 2D approximation; not a proof of feasibility or nonexistence for the actual 3D bead envelope. No path clipping. Continuous whole-path central-strip contact is an additional gate; full footprint, global error reduction and clearance unproven.'}
    manifest['candidate_segments'] = [dict(review,id=s.segment_id,
        start_mm=list(map(float,s.start_xyz_mm)),end_mm=list(map(float,s.end_xyz_mm)),
        width_mm=float(s.width_mm),height_mm=float(s.height_mm)) for s,review in candidates]
    return content,manifest


def main():
    folder = ROOT/'artifacts/cuboid-tilt10-review'
    project,stl = prepare_fixture(folder,tilt_degrees=10)
    sliced = folder/'original-slice'
    sliced.mkdir(exist_ok=True)
    command = [str(ROOT/'artifacts/runtime/orca-nightly/OrcaSlicer/orca-slicer.exe'),
        '--slice','0','--orient','0','--arrange','0','--export-3mf','sliced.3mf',
        '--datadir',str(folder/'cli-profile'),'--outputdir',str(sliced),str(project)]
    run = subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
    (folder/'slice-stdout.log').write_bytes(run.stdout)
    (folder/'slice-stderr.log').write_bytes(run.stderr)
    if run.returncode:
        raise RuntimeError(f'offline slice failed {run.returncode}; inspect logs')
    source = (sliced/'plate_1.gcode').read_bytes()
    content,manifest = build_scene(source,hashlib.sha256(source).hexdigest(),(sliced/'sliced.3mf').read_bytes())
    target = folder/f'cuboid-tilt10-steps-{uuid4().hex}.UNVERIFIED_VIEW_ONLY.gcode'
    target.write_bytes(content.encode('ascii'))
    manifest.update(viewer_file=str(target),viewer_sha256=hashlib.sha256(content.encode('ascii')).hexdigest(),
                    input_3mf_sha256=hashlib.sha256(project.read_bytes()).hexdigest(),
                    input_stl_sha256=hashlib.sha256(stl.read_bytes()).hexdigest())
    target.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (folder/'current-review.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k!='candidate_segments'},indent=2))


if __name__ == '__main__':
    main()
