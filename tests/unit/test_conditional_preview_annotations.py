"""Optional preview metadata changes comments only and restores recognized state."""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
import tempfile
import unittest

from tests.unit.test_conditional_nominal_copy import BODY, conditional_fixture, insertion_fixture
from tests.unit.test_supplemental_z_hop import path_fixture
from tools.conditional_nominal_body import interpret_nominal_body
from tools.conditional_nominal_copy import associate_derived_path, compose_conditional_nominal_copy, write_conditional_copy
from tools.conditional_preview_annotations import ConditionalPreviewAnnotationPolicy
from tools.freeze_supplemental_emission import freeze_numeric_emission


ANNOTATIONS = ConditionalPreviewAnnotationPolicy(1000, 1000, 24)
PRIOR = b'; LAYER_HEIGHT: 0.200\r\n; LINE_WIDTH: 0.420\r\n; Z_HEIGHT: 3.000\r\n'
TAGS = (b'; LAYER_HEIGHT:', b'; LINE_WIDTH:', b'; Z_HEIGHT:', b'; FEATURE:')


def fixture_with_two_paths():
    inputs = conditional_fixture(PRIOR+BODY)
    insertion = insertion_fixture(inputs)
    thin = insertion.paths[0]
    frozen = freeze_numeric_emission(path_fixture('thick', '.18'), insertion.policy)
    association = associate_derived_path(interpret_nominal_body(*inputs), inputs[3], frozen,
        original_recipe=thin.original_recipe, original_inputs=thin.original_inputs,
        geometry_evidence=thin.geometry_evidence, matched_source_lines=thin.association.matched_source_lines)
    thick = replace(thin, frozen_emission=frozen, association=association)
    return inputs, replace(insertion, paths=(thick, thin))


class ConditionalPreviewAnnotationTests(unittest.TestCase):
    def test_thin_first_physical_height_top_actual_width_and_exact_restore_comments_only(self):
        inputs, insertion = fixture_with_two_paths()
        ordinary = compose_conditional_nominal_copy(*inputs, (insertion,))
        annotated = compose_conditional_nominal_copy(*inputs, (insertion,), annotation_policy=ANNOTATIONS)
        first = ordinary.insertion_spans[0]
        second = annotated.insertion_spans[0]
        raw = ordinary.output_bytes[first.output_start:first.output_end]
        block = annotated.output_bytes[second.output_start:second.output_end]
        stripped = b''.join(line for line in block.splitlines(keepends=True) if not line.startswith(TAGS))
        self.assertEqual(stripped, raw)
        self.assertLess(block.index(b'; LAYER_HEIGHT: 0.08'), block.index(b'; LAYER_HEIGHT: 0.18'))
        self.assertIn(b'; Z_HEIGHT: 3.08\r\n', block)
        self.assertIn(b'; Z_HEIGHT: 3.18\r\n', block)
        expected = sorted((p.frozen_emission for p in insertion.paths), key=lambda p: (p.path.height_mm, p.path.path_id))
        widths = [line.split(b': ', 1)[1] for line in block.splitlines() if line.startswith(b'; LINE_WIDTH:')][:-1]
        self.assertEqual(tuple(map(lambda n: F(n.decode()), widths)), tuple(F(str(w)) for path in expected for w in path.physical_width_mm))
        self.assertTrue(all(b'/' not in line for line in block.splitlines() if line.startswith(TAGS[:3])))
        self.assertTrue(block.endswith(b'; LAYER_HEIGHT: 0.200\r\n; LINE_WIDTH: 0.420\r\n; Z_HEIGHT: 3.000\r\n; FEATURE: Outer wall\r\n'))
        self.assertIsNotNone(second.preview_annotation_identity)
        self.assertEqual(annotated.output_bytes[:second.output_start]+annotated.output_bytes[second.output_end:], inputs[0])
        self.assertFalse(annotated.printable_authorized)

    def test_unknown_or_malformed_prior_state_and_comment_decimal_budgets_reject(self):
        for prefix in (b'', PRIOR.replace(b'0.420', b'21/50')):
            inputs = conditional_fixture(prefix+BODY)
            insertion = insertion_fixture(inputs)
            with self.assertRaises(ValueError):
                compose_conditional_nominal_copy(*inputs, (insertion,), annotation_policy=ANNOTATIONS)
        inputs, insertion = fixture_with_two_paths()
        for policy in (ConditionalPreviewAnnotationPolicy(1, 1000, 24),
                       ConditionalPreviewAnnotationPolicy(1000, 1, 24), ConditionalPreviewAnnotationPolicy(1000, 1000, 3)):
            with self.assertRaises(ValueError):
                compose_conditional_nominal_copy(*inputs, (insertion,), annotation_policy=policy)

    def test_atomic_write_rebuild_requires_same_annotation_policy_and_LF_source(self):
        inputs = conditional_fixture((PRIOR+BODY).replace(b'\r\n', b'\n'))
        insertion = insertion_fixture(inputs)
        copy = compose_conditional_nominal_copy(*inputs, (insertion,), annotation_policy=ANNOTATIONS)
        self.assertNotIn(b'\r\n', copy.output_bytes)
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source, project, target = folder/'source.txt', folder/'source.3mf', folder/'copy.UNVERIFIED.txt'
            source.write_bytes(inputs[0])
            project.write_bytes(inputs[1])
            kwargs = dict(source_path=source, project_path=project, producer=inputs[2], descriptor=inputs[3],
                          entry=inputs[4], motion=inputs[5], insertions=(insertion,))
            with self.assertRaises(ValueError):
                write_conditional_copy(copy, target, **kwargs)
            self.assertFalse(target.exists())
            write_conditional_copy(copy, target, annotation_policy=ANNOTATIONS, **kwargs)
            self.assertEqual(target.read_bytes(), copy.output_bytes)


if __name__ == '__main__':
    unittest.main()
