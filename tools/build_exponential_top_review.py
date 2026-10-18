"""Generate and angle-bin an offline exponential curved-top Orca review."""
import argparse
from fractions import Fraction as F
import hashlib
import json
import subprocess
from uuid import uuid4

from tools.exponential_top_fixture import ROOT, REVIEW_FOLDER, prepare, placed_profile, target_at
from tools.build_triangle_rectangle_review import build
from tools.evaluate_curved_surface import evaluate, write_csv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reslice',action='store_true')
    parser.add_argument('--minimum-width-mm',type=F,default=F('.25'))
    parser.add_argument('--maximum-width-mm',type=F,default=F('.45'))
    parser.add_argument('--minimum-height-mm',type=F,default=F('.08'),
        help='minimum remaining height after overlap')
    parser.add_argument('--overlap-percent',type=F,default=F(0),help='0..30; positive penetrates')
    args = parser.parse_args()
    folder = REVIEW_FOLDER
    sliced = folder/'original-slice'
    receipt_path = folder/'slice-receipt.json'
    if args.reslice or not receipt_path.is_file():
        project = prepare(folder)
        sliced.mkdir(exist_ok=True)
        command = [str(ROOT/'artifacts/runtime/orca-nightly/OrcaSlicer/orca-slicer.exe'),
            '--slice','0','--orient','0','--arrange','0','--export-3mf','sliced.3mf',
            '--datadir',str(folder/'cli-profile'),'--outputdir',str(sliced),str(project)]
        run = subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
        (folder/'slice-stdout.log').write_bytes(run.stdout)
        (folder/'slice-stderr.log').write_bytes(run.stderr)
        if run.returncode:
            raise RuntimeError('offline curve slice failed; inspect slice logs')
        receipt_path.write_text(json.dumps({
            'source_slice_sha256':hashlib.sha256((sliced/'plate_1.gcode').read_bytes()).hexdigest(),
            'placed_project_sha256':hashlib.sha256((sliced/'sliced.3mf').read_bytes()).hexdigest(),
            'input_project_sha256':hashlib.sha256(project.read_bytes()).hexdigest()},indent=2)+'\n')
    source,project = (sliced/'plate_1.gcode').read_bytes(),(sliced/'sliced.3mf').read_bytes()
    receipt = json.loads(receipt_path.read_text())
    try:
        content,manifest = build(source,project,
            expected_source_sha256=receipt['source_slice_sha256'],
            expected_project_sha256=receipt['placed_project_sha256'],curved_top=True,
            minimum_width_mm=args.minimum_width_mm,maximum_width_mm=args.maximum_width_mm,
            minimum_height_mm=args.minimum_height_mm,overlap_percent=args.overlap_percent)
    except ValueError as error:
        parser.error(str(error))
    manifest.update(scope='exponential-curved-top-angle-review-only',
        fixture=json.loads((folder/'fixture.json').read_text()))
    target = folder/f'exponential-top-{uuid4().hex}.UNVERIFIED_VIEW_ONLY.gcode'
    manifest.update(viewer_file=str(target),viewer_sha256=hashlib.sha256(content.encode('ascii')).hexdigest())
    coarse = evaluate(source,project,manifest,nx=64,ny=1536)
    fine = evaluate(source,project,manifest,nx=128,ny=3072)
    bounds,top = placed_profile(project)
    alignment = []
    for step in manifest['section_diagnostics']:
        lower = F(step['lower_z_exact_mm'])
        a,b = F(step['left_edge_exact_mm']),F(step['right_edge_exact_mm'])
        alignment.append({'floor_z_mm':float(lower),
            'assumed_triangle_height_mm':float(F(step['triangle_height_exact_mm'])),
            'mesh_height_above_floor_at_left_mm':float(target_at(top,a)[0]-lower),
            'mesh_height_above_floor_at_right_mm':float(target_at(top,b)[0]-lower)})
    report = {'source_slice_sha256':manifest['source_slice_sha256'],
        'placed_project_sha256':manifest['placed_project_sha256'],
        'viewer_sha256':manifest['viewer_sha256'],'coarse':coarse,'fine':fine,
        'primary_comparison':'source_covered_only_angle_bins; fixed common source-covered mask, exclusions explicitly counted',
        'step_mesh_alignment':alignment,
        'all_projection_comparison':'angle_bins; includes bed-plane reference for empty columns, sensitive to edge sampling'}
    target.write_bytes(content.encode('ascii'))
    (folder/'current-review.json').write_text(json.dumps(manifest,indent=2)+'\n')
    target.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (folder/'angle-errors.json').write_text(json.dumps(report,indent=2)+'\n')
    write_csv(folder/'angle-errors.csv',fine)
    print(json.dumps({'viewer_file':str(target),'candidate_count':manifest['candidate_count'],
        'original_segment_count':manifest['original_segment_count'],'fine':fine},indent=2))


if __name__ == '__main__':
    main()
