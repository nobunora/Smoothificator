"""Synthetic byte-copy and anchor rejection contracts."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
from hashlib import sha256
import unittest
from unittest.mock import patch

from orca_plugin.gcode.linear_trace import MachineState, trace_linear_execution
from tests.unit.test_supplemental_z_hop import anchor_fixture, path_fixture, policy_fixture
from tools.supplemental_copy import (
    SupplementalInsertion, compose_supplemental_copy, synthetic_anchor,
)


SOURCE = b'; original comment\r\nG1 X5 F1250\r\n; layer\nG1 Y6\n; tail without newline'
OFFSET = len(b'; original comment\r\nG1 X5 F1250\r\n')


def request(source=SOURCE, offset=OFFSET):
    anchor = synthetic_anchor(source, offset, initial_state=anchor_fixture())
    return SupplementalInsertion(anchor, (path_fixture(),), F('3.2'), policy_fixture())


class SupplementalCopyTests(unittest.TestCase):
    def test_mixed_newlines_comments_missing_final_newline_and_multiple_insertions(self):
        later = len(SOURCE) - len(b'; tail without newline')
        artifact = compose_supplemental_copy(SOURCE, (request(), request(offset=later)))
        self.assertFalse(artifact.printable_authorized)
        self.assertFalse(artifact.runtime_injection_authorized)
        self.assertEqual(artifact.source_sha256, sha256(SOURCE).hexdigest())
        self.assertEqual(artifact.output_sha256, sha256(artifact.output_bytes).hexdigest())
        spans = artifact.insertion_spans
        self.assertIn(b'\r\nG1 Z', artifact.output_bytes[spans[0].output_start:spans[0].output_end])
        self.assertNotIn(b'\r', artifact.output_bytes[spans[1].output_start:spans[1].output_end])
        cursor = 0
        recovered = []
        for span in spans:
            recovered.append(artifact.output_bytes[cursor:span.output_start])
            cursor = span.output_end
        recovered.append(artifact.output_bytes[cursor:])
        self.assertEqual(b''.join(recovered), SOURCE)
        self.assertTrue(artifact.output_bytes.endswith(b'; tail without newline'))
        self.assertEqual(trace_linear_execution(artifact.output_bytes, initial_state=anchor_fixture()).final_state,
                         trace_linear_execution(SOURCE, initial_state=anchor_fixture()).final_state)
        with self.assertRaises(FrozenInstanceError):
            artifact.printable_authorized = True

    def test_complete_final_line_allows_eof_and_zero_boundary(self):
        source = b'; fixture\r\n'
        for offset in (0, len(source)):
            artifact = compose_supplemental_copy(source, (request(source, offset),))
            self.assertEqual(len(artifact.insertion_spans), 1)

    def test_unsafe_interior_negative_bool_and_unterminated_eof_offsets_reject(self):
        for offset in (-1, True, 2, OFFSET - 1, len(SOURCE), len(SOURCE) + 1):
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                request(offset=offset)

    def test_unknown_command_after_anchor_and_unknown_encoding_reject(self):
        for suffix in (b'\nM981 S1\n', b'\n; opaque \xff\n', b'\nG1 X2\x00\n'):
            with self.subTest(suffix=suffix), self.assertRaises(ValueError):
                request(SOURCE + suffix)

    def test_forged_hash_state_and_initial_context_reject(self):
        original = request()
        for anchor in (replace(original.anchor, source_sha256='0' * 64),
                       replace(original.anchor, saved_state=replace(anchor_fixture(), logical_e_mm=F(0))),
                       replace(original.anchor, initial_state=None)):
            with self.subTest(anchor=anchor), self.assertRaises(ValueError):
                compose_supplemental_copy(SOURCE, (replace(original, anchor=anchor),))
        with self.assertRaises(ValueError):
            compose_supplemental_copy(SOURCE + b'\n', (original,))

    def test_duplicate_reverse_mutable_empty_and_different_context_reject(self):
        first, second = request(), request(offset=0)
        for insertions in ((), [first], (first, first), (first, second)):
            with self.subTest(insertions=insertions), self.assertRaises(ValueError):
                compose_supplemental_copy(SOURCE, insertions)
        other_state = replace(anchor_fixture(), logical_e_mm=F(1))
        later = replace(first, anchor=synthetic_anchor(SOURCE, OFFSET, initial_state=other_state))
        with self.assertRaisesRegex(ValueError, 'one synthetic'):
            compose_supplemental_copy(SOURCE, (second, later))

    def test_unknown_or_unretracted_state_rejects_composition(self):
        for state in (MachineState(), replace(anchor_fixture(), retraction_debt_mm=F(0))):
            with self.subTest(state=state), self.assertRaises(ValueError):
                anchor = synthetic_anchor(b'; fixture\n', 0, initial_state=state)
                compose_supplemental_copy(b'; fixture\n', (replace(request(), anchor=anchor),))

    def test_existing_complete_partial_and_canonical_markers_reject(self):
        artifact = compose_supplemental_copy(SOURCE, (request(),))
        for source in (artifact.output_bytes, b'; SUPPLEMENTAL_CYCLE_BEGIN\n', b'; ADAPTIVE_SUBEDGE_END\n'):
            with self.subTest(source=source[:30]), self.assertRaisesRegex(ValueError, 'marker'):
                synthetic_anchor(source, 0, initial_state=anchor_fixture())

    def test_independent_cycle_replay_rejects_bad_composer_output(self):
        for block in (b'G1 X999\n', b'M981 S1\n'):
            with patch('tools.supplemental_copy.compose_retracted_cycle', return_value=block):
                with self.assertRaisesRegex(ValueError, 'restore exact'):
                    compose_supplemental_copy(SOURCE, (request(),))
