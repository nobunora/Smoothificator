"""Fixed-domain, angle-binned nominal surface errors against placed mesh."""
import csv
from fractions import Fraction as F
import math

from tools.build_tilted_cuboid_review import baseline
from tools.exponential_top_fixture import placed_profile, target_at
from tools.optimize_top_error import Proposal, source_grid, apply_proposals


ANGLE_BINS = tuple((i,i+5) for i in range(0,40,5))


def angle_bin_index(slope):
    angle = math.degrees(math.atan(float(slope)))
    return min(len(ANGLE_BINS)-1,max(0,int(angle//5)))


def summarize(errors, missing):
    if not errors:
        return {'count':0,'missing_source_count':missing,'mae_vertical_mm':None}
    return {'count':len(errors),'missing_source_count':missing,
        'mae_vertical_mm':sum(map(abs,errors))/len(errors),
        'rms_vertical_mm':math.sqrt(sum(v*v for v in errors)/len(errors)),
        'maximum_sampled_absolute_vertical_mm':max(map(abs,errors)),
        'mean_shortage_mm':sum(max(0,-v) for v in errors)/len(errors),
        'mean_excess_mm':sum(max(0,v) for v in errors)/len(errors)}


def compare(grid,after,ys,top):
    buckets = [[[],[],0] for _ in ANGLE_BINS]
    for y,before_row,after_row in zip(ys,grid,after):
        target,slope = target_at(top,F(str(y)))
        index = angle_bin_index(slope)
        for before,z in zip(before_row,after_row):
            if before is None:
                buckets[index][2] += 1
                continue
            buckets[index][0].append(before-float(target))
            buckets[index][1].append(z-float(target))
    result = []
    for (low,high),(before,after,missing) in zip(ANGLE_BINS,buckets):
        a,b = summarize(before,missing),summarize(after,missing)
        result.append({'angle_degrees':[low,high],'before':a,'after':b,
            'mae_change_fraction':None if not before or a['mae_vertical_mm']==0 else
                (b['mae_vertical_mm']/a['mae_vertical_mm']-1)})
    return result


def evaluate(source,project,manifest, *, nx,ny):
    bounds,top = placed_profile(project)
    rows,_,metadata,_ = baseline(source,manifest['source_slice_sha256'],F(2))
    if any(w < float(metadata[number][1]) for _,_,_,_,_,w,number in rows):
        raise ValueError('unmodeled source cross-section prevents empty-column interpretation')
    xs,ys,grid = source_grid(rows,metadata,bounds,nx,ny)
    proposals = [Proposal('curve',F(str(c['start_mm'][1])),F(str(c['width_mm'])),
        F(str(c['height_mm'])),F(0),F(c['top_z_exact_mm']),0) for c in manifest['candidate_segments']]
    x0 = F(str(manifest['candidate_segments'][0]['start_mm'][0])) if proposals else bounds[0]
    x1 = F(str(manifest['candidate_segments'][0]['end_mm'][0])) if proposals else bounds[1]
    # Every source is modeled here. None therefore denotes an empty extrusion
    # column in the nominal model, not an omitted unsupported source. Include
    # the build plane at Z=0 in the full-domain envelope and expose these counts.
    with_bed = [[0. if z is None else z for z in row] for row in grid]
    after = apply_proposals(with_bed,xs,ys,proposals,x0,x1)
    covered_after = [[None if old is None else new for old,new in zip(a,b)] for a,b in zip(grid,after)]
    bins = compare(with_bed,after,ys,top)
    for row in bins:
        row['empty_baseline_columns'] = 0
        row['empty_baseline_columns_filled_by_candidates'] = 0
    for y,a,b in zip(ys,grid,after):
        _,slope = target_at(top,F(str(y)))
        index = angle_bin_index(slope)
        bins[index]['empty_baseline_columns'] += sum(z is None for z in a)
        bins[index]['empty_baseline_columns_filled_by_candidates'] += sum(
            old is None and new>0 for old,new in zip(a,b))
    return {'grid':[nx,ny],'angle_bins':bins,
        'sample_projected_area_mm2':float((bounds[1]-bounds[0])*(bounds[3]-bounds[2]))/(nx*ny),
        'source_covered_only_angle_bins':compare(grid,covered_after,ys,top),
        'metric':'height-direction absolute error of nominal stadium union versus actual placed mesh',
        'domain':'entire projected top face, build plane Z=0 for empty nominal extrusion columns; same fixed grid before/after',
        'empty_column_policy':'all source beads modeled; empty columns counted with bed reference, also report source-covered-only comparison',
        'unmodeled_source_beads':0,
        'continuous_geometry_or_contact_certificate':False}


def write_csv(path,report):
    with path.open('w',newline='',encoding='utf-8-sig') as stream:
        writer = csv.writer(stream)
        writer.writerow(('angle_min_deg','angle_max_deg','samples','missing_samples',
            'before_mae_mm','after_mae_mm','mae_change_percent','before_max_mm','after_max_mm'))
        for row in report['source_covered_only_angle_bins']:
            a,b = row['before'],row['after']
            writer.writerow((*row['angle_degrees'],a['count'],a['missing_source_count'],
                a['mae_vertical_mm'],b['mae_vertical_mm'],100*row['mae_change_fraction'],
                a['maximum_sampled_absolute_vertical_mm'],b['maximum_sampled_absolute_vertical_mm']))
