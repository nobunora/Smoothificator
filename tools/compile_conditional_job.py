"""All-target recipe compilation and conditional byte-preserving copy orchestration."""
from dataclasses import asdict, dataclass, replace
from fractions import Fraction as F
from hashlib import sha256
import json
import re

from orca_plugin.gcode.source_profile import _unique_object, read_sliced_profile
from tools.compile_nominal_recipe import (
    CircleRecipe, ContourRecipe, ExplicitPatchRecipe, GridVertexDisplacement, PinnedRingRecipe,
    compile_nominal_recipe,
)
from tools.conditional_nominal_body import fingerprint, interpret_nominal_body
from tools.conditional_nominal_copy import (
    ConditionalInsertion, ConditionalPathInput, associate_derived_path, compose_conditional_nominal_copy,
    _anchor_from_trace,
)
from tools.conditional_nominal_model import (
    ConditionalNominalModel, RawGeometryReassociation, extract_conditional_nominal_model, reassociate_raw_nominal_geometry,
)
from tools.prepare_source_contour_intents import ContourConstructionPolicy, SourceJointDetour
from tools.prepare_executable_ring_intents import prepare_ring_intents
from tools.supplemental_z_hop import policy_from_slice


LEGACY_F917_SOURCE_SHA256 = 'f917caf88191253f22004d47545daa4e6f78f4b4132d61529101271e4d3ba288'


@dataclass(frozen=True)
class ConditionalCompilationPolicy:
    max_groups: int
    max_paths: int
    max_total_segments: int
    construction: ContourConstructionPolicy

    def __post_init__(self):
        if (any(type(v) is not int or v < 1 for v in (self.max_groups, self.max_paths, self.max_total_segments))
                or type(self.construction) is not ContourConstructionPolicy):
            raise ValueError('explicit bounded immutable compilation resources required')


@dataclass(frozen=True)
class CompiledConditionalGroup:
    floor_z_mm: F
    upper_z_mm: F
    triangle_left_radius_mm: F
    triangle_base_mm: F
    triangle_rise_mm: F
    original_path_count: int
    paths: tuple
    insertion: ConditionalInsertion


@dataclass(frozen=True)
class CompiledConditionalJob:
    manifest_sha256: str
    coverage_sha256: str
    original_manifest_sha256: str
    model_identity: str
    reassociation_identity: str
    compilation_policy: ConditionalCompilationPolicy
    groups: tuple[CompiledConditionalGroup, ...]
    excluded_steps: tuple[tuple[F, F, F, F], ...]
    copy: object
    state: str = 'compiled-UNVERIFIED-no-geometry-selection'


def _exact_integer(reference, *, minimum=0):
    if type(reference) is int and reference >= minimum:
        return reference
    raise ValueError('exact integer category and range required for count/index')


def _source_line(reference):
    if type(reference) is int:
        return _exact_integer(reference, minimum=1)
    if type(reference) is str and re.fullmatch('[1-9][0-9]*', reference):
        return int(reference)
    raise ValueError('canonical positive integer source line identity required')


def compile_conditional_job(*, inputs, model, reassociation, manifest_bytes, coverage_bytes,
        original_manifest_bytes, pinned_contents, bounds, xyz_places, e_places,
        policy, cancelled):
    """Account every original target, construct every path and compose every cycle.

    This compilation is not nominal selection. Contact/material/spill/tool audits
    must freshly consume the resulting actual geometry and chronology.
    """
    if (type(model) is not ConditionalNominalModel or type(reassociation) is not RawGeometryReassociation
            or type(policy) is not ConditionalCompilationPolicy or not callable(cancelled)
            or type(pinned_contents) is not tuple):
        raise ValueError('exact model/bijection/bounded resources and immutable inputs required')

    def checkpoint():
        answer = cancelled()
        if type(answer) is not bool:
            raise ValueError('exact bool compilation cancellation required')
        if answer:
            raise ValueError('conditional compilation cancelled')

    checkpoint()
    source, project, producer, descriptor, entry, motion = inputs
    trace = interpret_nominal_body(*inputs)
    if ((model.source_sha256, model.project_sha256, model.descriptor_identity, model.entry_identity)
            != (descriptor.source_sha256, descriptor.project_sha256, trace.descriptor_identity, trace.entry_identity)
            or (reassociation.new_source_sha256, reassociation.new_project_sha256)
            != (model.source_sha256, model.project_sha256)):
        raise ValueError('current model/source/entry/reassociation mismatch')
    manifest = json.loads(manifest_bytes, object_pairs_hook=_unique_object)
    coverage = json.loads(coverage_bytes, object_pairs_hook=_unique_object)
    original_manifest = json.loads(original_manifest_bytes, object_pairs_hook=_unique_object)
    current_schema = manifest.get('schema') == 'conditional-whole-job-current-source-recipes-v1'
    if current_schema:
        if ((manifest.get('current_source_sha256'), manifest.get('current_project_sha256'))
                != (descriptor.source_sha256, descriptor.project_sha256)):
            raise ValueError('CURRENT source/project recipe identity mismatch')
        coverage_schema, coverage_recipe_key = 'explicit-current-source-target-coverage-v1', 'current_recipe_sha256'
        contour_line_key, detour_line_key, patch_line_key = ('source_lines_current', 'source_segment_id_current',
                                                           'support_source_line_current')
    else:
        coverage_schema, coverage_recipe_key = 'explicit-original-target-step-coverage-v2', 'recipe_v5_sha256'
        contour_line_key, detour_line_key, patch_line_key = ('source_lines_f917', 'source_segment_id_f917',
                                                           'support_source_line_f917')
        # Legacy identity names are restricted to the exact producer-original
        # source they name. A derived baseline must explicitly use CURRENT.
        if descriptor.source_sha256 != LEGACY_F917_SOURCE_SHA256:
            raise ValueError('legacy f917 recipe requires its named original source; use CURRENT schema')
    if (manifest.get('schema') not in ('research-whole-job-explicit-input-recipes-v5',
                                     'conditional-whole-job-current-source-recipes-v1')
            or coverage.get('schema') != coverage_schema
            or coverage[coverage_recipe_key] != sha256(manifest_bytes).hexdigest()
            or coverage['original_manifest_sha256'] != sha256(original_manifest_bytes).hexdigest()
            or manifest['proof_source_sha256'] != reassociation.old_source_sha256):
        raise ValueError('unknown/stale manifest/coverage/reference schema or identity')
    contents = dict(pinned_contents)
    if len(contents) != len(pinned_contents) or any(type(k) is not str or type(v) is not bytes for k, v in pinned_contents):
        raise ValueError('unique named pinned content bytes required')
    for name, digest in manifest['input_and_proof_sha256'].items():
        checkpoint()
        if name not in contents or sha256(contents[name]).hexdigest() != digest:
            raise ValueError('missing/stale pinned recipe implementation or evidence: '+name)
    # Only bytes explicitly pinned by this recipe manifest may establish the
    # target corpus. Extra caller contents cannot authorize a replacement target.
    by_digest = {digest: contents[name] for name, digest in manifest['input_and_proof_sha256'].items()}
    if sha256(original_manifest_bytes).hexdigest() not in by_digest:
        raise ValueError('original target manifest is not bound to declared validated input pins')
    old_digests = (reassociation.old_source_sha256, reassociation.old_project_sha256, reassociation.old_rows_sha256)
    if any(d not in by_digest for d in old_digests):
        raise ValueError('complete pinned original nominal reference bytes required')
    rebuilt_association = reassociate_raw_nominal_geometry(model, inputs=inputs, cancelled=cancelled, old_source=by_digest[old_digests[0]],
        old_project=by_digest[old_digests[1]], old_rows=by_digest[old_digests[2]],
        expected_old_source_sha256=old_digests[0], expected_old_project_sha256=old_digests[1], expected_old_rows_sha256=old_digests[2])
    if rebuilt_association != reassociation:
        raise ValueError('raw source geometry bijection cannot be reconstructed from pinned references')
    groups = manifest['groups']
    steps = coverage['steps']
    target_steps = original_manifest['section_diagnostics']
    for key in ('original_selected_step_count', 'mapped_proposed_groups', 'explicit_exclusions'):
        _exact_integer(coverage[key], minimum=0 if key == 'explicit_exclusions' else 1)
    for key in ('proposed_total_paths', 'recorded_path_segments'):
        _exact_integer(manifest[key], minimum=1)
    if (not 0 < len(groups) <= policy.max_groups or len(steps) != len(target_steps)
            or len(steps) != coverage['original_selected_step_count']):
        raise ValueError('all target steps and bounded proposed groups required')
    by_floor = {F(g['floor_z_mm']): g for g in groups}
    if len(by_floor) != len(groups) or list(by_floor) != sorted(by_floor):
        raise ValueError('unique increasing group floors required')
    excluded, expected_floors, previous = [], [], None
    if F(coverage['criterion']['minimum_width_mm']) != F(str(bounds.min_candidate_width_mm)):
        raise ValueError('target exclusion criterion differs from explicit plugin bounds')
    for step, target in zip(steps, target_steps):
        checkpoint()
        floor, upper = F(step['floor_z_mm']), F(step['upper_z_mm'])
        left, base, rise = F(step['left_radius_mm']), F(step['triangle_base_mm']), F(step['triangle_height_mm'])
        if (floor, upper, left, base, rise) != tuple(F(target[k]) for k in ('floor_z_exact_mm',
                'upper_z_exact_mm', 'left_radius_exact_mm', 'triangle_base_exact_mm', 'triangle_height_exact_mm')):
            raise ValueError('target coverage/reference geometry mismatch')
        if previous is not None and floor <= previous:
            raise ValueError('ordered unique original target floors required')
        previous = floor
        threshold = 2*F(str(bounds.min_candidate_width_mm))**2
        if step['status'] == 'explicit-short-base-exclusion':
            if base**2 >= threshold or floor in by_floor:
                raise ValueError('short-base exclusion requires strict existing squared criterion')
            excluded.append((floor, upper, base, base*rise/2))
        elif step['status'] == 'mapped-to-proposed-group':
            if floor not in by_floor or base**2 < threshold:
                raise ValueError('missing proposed group or undeclared short-base policy')
            expected_floors.append(floor)
            group = by_floor[floor]
            triangle = group['triangle']
            if ((F(group['original_step_floor_z_mm']), F(group['original_upper_z_mm']),
                    F(triangle['left_radius_exact_mm']), F(triangle['triangle_base_exact_mm']), F(triangle['triangle_height_exact_mm']))
                    != (floor, upper, left, base, rise)
                    or tuple(step['emitted_path_ids']) != tuple(p['emitted_path_id'] for p in group['paths'])):
                raise ValueError('proposed group/paths differ from declared original target coverage')
        else:
            raise ValueError('unknown target disposition')
    if set(expected_floors) != set(by_floor):
        raise ValueError('extra/omitted target groups')
    if len(excluded) != coverage['explicit_exclusions'] or len(groups) != coverage['mapped_proposed_groups']:
        raise ValueError('target coverage disposition counts mismatch')
    line_map = dict(reassociation.old_to_new_lines)
    spans = {s.line_number: s for s in model.spans}
    if len(line_map) != len(model.spans) or set(line_map.values()) != set(spans):
        raise ValueError('incomplete source geometry line bijection')
    profile = read_sliced_profile(project, source, include_motion_caps=True)
    model_identity, reassociation_identity = fingerprint(model), fingerprint(reassociation)
    canonical = policy_from_slice(profile, bounds, xyz_places=xyz_places, e_places=e_places)
    compiled_groups, proposal_ids, emitted_ids, segment_count = [], set(), set(), 0
    rebuilt_ring_sets = {}
    for group in groups:
        checkpoint()
        floor, upper = F(group['original_step_floor_z_mm']), F(group['original_upper_z_mm'])
        cap_events = tuple(e for e in trace.events if e.command in ('G0', 'G1') and e.feature == 'Outer wall'
            and e.scope_after is not None and e.deposited_filament_mm is not None and e.deposited_filament_mm > 0
            and e.before.xyz_mm[2] == floor and e.after.xyz_mm[2] == floor and e.before.xyz_mm[:2] != e.after.xyz_mm[:2])
        if not cap_events:
            raise ValueError('missing current floor external-wall feed witnesses')
        group_policy = replace(canonical, candidate_speed_mm_s=min(canonical.candidate_speed_mm_s,
            min(e.after.feed_mm_min for e in cap_events)/60))
        last_floor = max(s.line_number for s in model.spans if s.original_geometry.end_xyz_mm[2] == floor)
        opening = next((e for e in trace.events if e.command == 'M624' and e.line_number > last_floor), None)
        if opening is None:
            raise ValueError('missing next-layer scoped conditional anchor')
        anchor = _anchor_from_trace(descriptor, trace, entry, motion, opening.byte_offset+len(opening.raw))
        if anchor.eligibility_issues:
            raise ValueError('ineligible fresh conditional group anchor')
        next_material = next(s for s in model.spans if s.line_number > opening.line_number)
        if next_material.original_geometry.end_xyz_mm[2] != upper:
            raise ValueError('anchor not before declared immediate upper source deposition')
        paths, insertion_paths = [], []
        _exact_integer(group['proposed_path_count'], minimum=1)
        _exact_integer(group['original_preview_path_count'], minimum=1)
        if len(group['paths']) != group['proposed_path_count']:
            raise ValueError('declared group path count mismatch')
        for path_recipe in group['paths']:
            checkpoint()
            proposal_id, emitted_id = path_recipe['proposal_id'], path_recipe['emitted_path_id']
            if proposal_id in proposal_ids or emitted_id in emitted_ids:
                raise ValueError('duplicate proposal or emitted path identity')
            proposal_ids.add(proposal_id)
            emitted_ids.add(emitted_id)
            if len(emitted_ids) > policy.max_paths:
                raise ValueError('job path budget')
            geometry = path_recipe['geometry_recipe']
            kind = geometry['kind']
            if kind == 'circle':
                if geometry['phase_radians_exact'] != '0' or geometry['direction'] != 'counterclockwise':
                    raise ValueError('only explicit phase-zero counterclockwise circles supported')
                recipe = CircleRecipe(tuple(map(F, geometry['center_xy_mm'])), F(geometry['radius_mm']),
                    geometry['chord_count'], F(geometry['radial_band_budget_mm']))
            elif kind in ('source_contour', 'trimmed_open_source_contour'):
                old_lines = tuple(_source_line(i) for i in geometry['source_lines_fc'])
                current_lines = tuple(line_map[i] for i in old_lines)
                if current_schema and 'source_lines_f917' in geometry:
                    raise ValueError('ambiguous legacy/current contour source naming')
                if current_lines != tuple(_source_line(i) for i in geometry[contour_line_key]):
                    raise ValueError('declared contour source mapping mismatch')
                contour = tuple(spans[line].original_geometry for line in current_lines)
                for detour in geometry.get('joint_detours', []):
                    if current_schema and 'source_segment_id_f917' in detour:
                        raise ValueError('ambiguous legacy/current detour source naming')
                    if line_map[_source_line(detour['source_segment_id_fc'])] != _source_line(detour[detour_line_key]):
                        raise ValueError('detour original/current source identity mismatch')
                detours = tuple(SourceJointDetour(d[detour_line_key], F(d['locality_mm']))
                    for d in geometry.get('joint_detours', []))
                displacements, retained = (), None
                if kind == 'trimmed_open_source_contour':
                    adjustment = geometry['pre_freeze_grid_vertex_adjustment']
                    displacements = (GridVertexDisplacement(adjustment['generated_vertex_index_zero_based'],
                        tuple(map(F, adjustment['delta_xy_mm'])), geometry['trim_reason']),)
                    retained = tuple(_exact_integer(i, minimum=1)-1 for i in geometry['retained_original_edge_ids_one_based'])
                recipe = ContourRecipe(contour, F(geometry['inward_offset_mm']),
                    F(geometry['minimum_generated_segment_mm']), detours, retained, displacements,
                    geometry.get('coalesce_collinear_source_vertices', False))
            elif kind == 'source_aligned_patch':
                support = line_map[_source_line(geometry['support_source_line_fc'])]
                if current_schema and 'support_source_line_f917' in geometry:
                    raise ValueError('ambiguous legacy/current patch source naming')
                if support != _source_line(geometry[patch_line_key]):
                    raise ValueError('patch original/current support identity mismatch')
                recipe = ExplicitPatchRecipe((tuple(map(F, geometry['start_xyz_mm'])), tuple(map(F, geometry['end_xyz_mm']))),
                    (str(support),), geometry['construction'])
            elif kind == 'pinned_original_ring_factory':
                ring_digests = tuple(geometry[key] for key in ('original_source_sha256', 'original_project_sha256', 'original_manifest_sha256'))
                if any(d not in by_digest for d in ring_digests):
                    raise ValueError('pinned original ring source/project/manifest bytes required')
                if ring_digests not in rebuilt_ring_sets:
                    rebuilt_ring_sets[ring_digests] = prepare_ring_intents(by_digest[ring_digests[1]],
                        by_digest[ring_digests[0]], by_digest[ring_digests[2]])
                original = next((r for r in rebuilt_ring_sets[ring_digests].rings if r.path.path_id == geometry['source_ring_id']), None)
                if original is None:
                    raise ValueError('missing pinned original ring factory construction')
                if tuple(_exact_integer(i) for i in geometry['selected_endpoint_indices']) != original.selected_endpoint_indices:
                    raise ValueError('original ring selected endpoint provenance mismatch')
                recipe = PinnedRingRecipe(original.path, geometry['original_source_sha256'], geometry['original_project_sha256'],
                    geometry['original_manifest_sha256'], tuple(map(F, geometry['center_xy_mm'])),
                    F(geometry['radius_mm']), F(geometry['radial_band_budget_mm']))
            else:
                raise ValueError('unknown whole-job recipe family')
            if ((F(path_recipe['original_step_floor_z_mm']), F(path_recipe['original_upper_z_mm'])) != (floor, upper)
                    or F(path_recipe['command_z_mm']) != floor+F(path_recipe['remaining_height_mm'])
                    or F(path_recipe['bottom_z_mm']) != F(path_recipe['command_z_mm'])-F(path_recipe['physical_height_mm'])
                    or F(path_recipe['overlap_fraction']) != 1-F(path_recipe['remaining_height_mm'])/F(path_recipe['physical_height_mm'])):
                raise ValueError('recipe dimensions disagree with declared source interval/top/bottom/overlap')
            compiled = compile_nominal_recipe(proposal_id=proposal_id, emitted_path_id=emitted_id,
                source_sha256=model.source_sha256, project_sha256=model.project_sha256,
                floor_z_mm=floor, upper_z_mm=upper, width_mm=F(path_recipe['intent_width_mm']),
                height_mm=F(path_recipe['physical_height_mm']), remaining_height_mm=F(path_recipe['remaining_height_mm']),
                recipe=recipe, emission_policy=group_policy, construction_policy=policy.construction, cancelled=cancelled,
                reference_points=tuple(tuple(map(F, p)) for p in path_recipe['points_xyz_mm']),
                reference_relative_e=tuple(F(s['E']) for s in path_recipe['segments']),
                reference_widths=tuple(float(s['width_from_E']) for s in path_recipe['segments']))
            segment_count += len(compiled.frozen_emission.relative_e_mm)
            if kind == 'trimmed_open_source_contour' and tuple(_exact_integer(i, minimum=1)-1 for i in geometry['removed_original_edge_ids_one_based']) != compiled.removed_reference_edge_indices:
                raise ValueError('declared removed arc edge provenance mismatch')
            if segment_count > policy.max_total_segments:
                raise ValueError('job segment budget')
            evidence = json.dumps({'recipe': path_recipe, 'compiled_recipe_identity': compiled.recipe_identity,
                'model_identity': model_identity, 'reassociation_identity': reassociation_identity,
                'statement': 'fresh geometry input only; no old source execution/geometry acceptance transfer'},
                sort_keys=True, separators=(',', ':')).encode('ascii')
            association = associate_derived_path(trace, descriptor, compiled.frozen_emission,
                original_recipe=manifest_bytes, original_inputs=(original_manifest_bytes, coverage_bytes),
                geometry_evidence=evidence, matched_source_lines=tuple(e.line_number for e in cap_events))
            insertion_paths.append(ConditionalPathInput(compiled.frozen_emission, association, manifest_bytes,
                (original_manifest_bytes, coverage_bytes), evidence))
            paths.append(compiled)
        triangle = group['triangle']
        compiled_groups.append(CompiledConditionalGroup(floor, upper, F(triangle['left_radius_exact_mm']),
            F(triangle['triangle_base_exact_mm']), F(triangle['triangle_height_exact_mm']), group['original_preview_path_count'],
            tuple(paths), ConditionalInsertion(anchor, tuple(insertion_paths), upper, group_policy)))
    if len(emitted_ids) != manifest['proposed_total_paths'] or segment_count != manifest['recorded_path_segments']:
        raise ValueError('declared complete job graph counts mismatch')
    composed = compose_conditional_nominal_copy(*inputs, tuple(g.insertion for g in compiled_groups))
    return CompiledConditionalJob(sha256(manifest_bytes).hexdigest(), sha256(coverage_bytes).hexdigest(),
        sha256(original_manifest_bytes).hexdigest(), model_identity, reassociation_identity, policy,
        tuple(compiled_groups), tuple(excluded), composed)
