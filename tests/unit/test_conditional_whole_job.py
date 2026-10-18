"""Complete actual all-target compilation and source-bound rejection gates."""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
from hashlib import sha256
import json
import runpy
import unittest

from tools.compile_conditional_job import compile_conditional_job
from tools.exponential_top_fixture import ROOT


class ConditionalWholeJobTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arguments = runpy.run_path(str(ROOT/'artifacts/conditional-whole-job-review/reproduce.py'))['compile_actual'](return_arguments=True)

    def changed_manifest(self, manifest):
        encoded = json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()
        coverage = json.loads(self.arguments['coverage_bytes'])
        coverage['recipe_v5_sha256'] = sha256(encoded).hexdigest()
        return dict(self.arguments, manifest_bytes=encoded, coverage_bytes=json.dumps(coverage).encode())

    def test_all16_steps28_paths_and_original_bytes_exactly_accounted(self):
        job = compile_conditional_job(**self.arguments)
        self.assertEqual((len(job.groups), len(job.excluded_steps)), (12, 4))
        paths = tuple(p for g in job.groups for p in g.paths)
        self.assertEqual(len(paths), 28)
        self.assertEqual(len({p.emitted_path_id for p in paths}), 28)
        self.assertEqual(sum(len(p.frozen_emission.relative_e_mm) for p in paths), 2853)
        self.assertTrue(all(p.geometry_matches_reference and p.relative_e_matches_reference and p.widths_match_reference for p in paths))
        recovered, cursor = [], 0
        for span in job.copy.insertion_spans:
            recovered.append(job.copy.output_bytes[cursor:span.output_start])
            cursor = span.output_end
        recovered.append(job.copy.output_bytes[cursor:])
        self.assertEqual(b''.join(recovered), self.arguments['inputs'][0])
        self.assertFalse(job.copy.printable_authorized)

    def test_coverage_schema_duplicate_and_unknown_recipe_fail_closed(self):
        original = json.loads(self.arguments['manifest_bytes'])
        mutations = []
        missing = deepcopy(original)
        missing['groups'].pop()
        mutations.append(missing)
        duplicate = deepcopy(original)
        duplicate['groups'][0]['paths'][1]['emitted_path_id'] = duplicate['groups'][0]['paths'][0]['emitted_path_id']
        mutations.append(duplicate)
        unknown = deepcopy(original)
        unknown['groups'][0]['paths'][0]['geometry_recipe']['kind'] = 'unknown'
        mutations.append(unknown)
        wrong_triangle = deepcopy(original)
        wrong_triangle['groups'][0]['triangle']['triangle_base_exact_mm'] = '1'
        mutations.append(wrong_triangle)
        fractional = deepcopy(original)
        geometry = fractional['groups'][2]['paths'][0]['geometry_recipe']
        geometry['source_lines_fc'][0] = float(geometry['source_lines_fc'][0])+0.9
        geometry['source_lines_f917'][0] = float(geometry['source_lines_f917'][0])+0.9
        mutations.append(fractional)
        bad_count = deepcopy(original)
        bad_count['groups'][0]['proposed_path_count'] = True
        mutations.append(bad_count)
        for manifest in mutations:
            with self.subTest(manifest=manifest['groups'][0]['family']), self.assertRaises(ValueError):
                compile_conditional_job(**self.changed_manifest(manifest))

    def test_stale_owner_and_forged_current_model_or_bijection_reject(self):
        contents = self.arguments['pinned_contents']
        with self.assertRaisesRegex(ValueError, 'stale pinned'):
            compile_conditional_job(**dict(self.arguments, pinned_contents=((contents[0][0], contents[0][1]+b' '),)+contents[1:]))
        model = self.arguments['model']
        forged = replace(model, spans=(replace(model.spans[0], raw_commanded_e_mm=F(99)),)+model.spans[1:])
        with self.assertRaisesRegex(ValueError, 'stale/forged'):
            compile_conditional_job(**dict(self.arguments, model=forged))
        association = self.arguments['reassociation']
        wrong = replace(association, old_to_new_lines=association.old_to_new_lines[::-1])
        with self.assertRaisesRegex(ValueError, 'cannot be reconstructed'):
            compile_conditional_job(**dict(self.arguments, reassociation=wrong))

    def test_unpinned_replacement_target_manifest_cannot_hide_original_step(self):
        original = json.loads(self.arguments['original_manifest_bytes'])
        original['section_diagnostics'].pop()
        replacement = json.dumps(original).encode()
        coverage = json.loads(self.arguments['coverage_bytes'])
        coverage['steps'].pop()
        coverage['original_selected_step_count'] -= 1
        coverage['explicit_exclusions'] -= 1
        coverage['original_manifest_sha256'] = sha256(replacement).hexdigest()
        with self.assertRaisesRegex(ValueError, 'not bound to declared'):
            compile_conditional_job(**dict(self.arguments, original_manifest_bytes=replacement,
                                           coverage_bytes=json.dumps(coverage).encode()))


if __name__ == '__main__':
    unittest.main()
