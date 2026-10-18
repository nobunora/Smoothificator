"""A derived baseline requires explicit CURRENT identities and fresh anchors."""
from copy import deepcopy
from hashlib import sha256
import json
import runpy
import unittest

from tools.compile_conditional_job import compile_conditional_job
from tools.exponential_top_fixture import ROOT


class CurrentConditionalJobTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        driver = ROOT/'artifacts/exact-debt-derived-review/reproduce.py'
        cls.arguments = runpy.run_path(str(driver))['compile_current'](return_arguments=True)

    def changed(self, manifest):
        encoded = json.dumps(manifest, sort_keys=True).encode()
        coverage = json.loads(self.arguments['coverage_bytes'])
        coverage['current_recipe_sha256'] = sha256(encoded).hexdigest()
        return dict(self.arguments, manifest_bytes=encoded, coverage_bytes=json.dumps(coverage).encode())

    def test_complete_new_baseline_has_fresh_association_anchors_and_unchanged_paths(self):
        job = compile_conditional_job(**self.arguments)
        self.assertEqual((len(job.groups), len(job.excluded_steps)), (12, 4))
        paths = tuple(p for g in job.groups for p in g.paths)
        self.assertEqual((len(paths), sum(len(p.frozen_emission.relative_e_mm) for p in paths)), (28, 2853))
        self.assertTrue(all(p.geometry_matches_reference and p.relative_e_matches_reference and p.widths_match_reference for p in paths))
        source = self.arguments['inputs'][3].source_sha256
        self.assertEqual(source, '2aa69c3ebabc86442456486ee616d3caac2e30850142e670cd8d77937779f374')
        self.assertTrue(all(g.insertion.anchor.source_sha256 == source for g in job.groups))
        self.assertFalse(self.arguments['reassociation'].debt_cropped_new_lines)
        self.assertTrue(all(s.deposition_start_parameter == 0 for s in self.arguments['model'].spans))
        recovered, cursor = [], 0
        for span in job.copy.insertion_spans:
            recovered.append(job.copy.output_bytes[cursor:span.output_start])
            cursor = span.output_end
        recovered.append(job.copy.output_bytes[cursor:])
        self.assertEqual(b''.join(recovered), self.arguments['inputs'][0])
        self.assertFalse(job.copy.printable_authorized)

    def test_stale_identity_mixed_line_schema_and_legacy_retarget_reject(self):
        manifest = json.loads(self.arguments['manifest_bytes'])
        wrong = deepcopy(manifest)
        wrong['current_source_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'CURRENT'):
            compile_conditional_job(**self.changed(wrong))
        mixed = deepcopy(manifest)
        contour = next(p['geometry_recipe'] for g in mixed['groups'] for p in g['paths']
                       if p['geometry_recipe']['kind'] == 'source_contour')
        contour['source_lines_f917'] = contour['source_lines_current']
        with self.assertRaisesRegex(ValueError, 'ambiguous legacy/current'):
            compile_conditional_job(**self.changed(mixed))
        legacy = deepcopy(manifest)
        legacy['schema'] = 'research-whole-job-explicit-input-recipes-v5'
        with self.assertRaisesRegex(ValueError, 'legacy f917'):
            compile_conditional_job(**self.changed(legacy))


if __name__ == '__main__':
    unittest.main()
