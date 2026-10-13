"""ADR-0049/0062/0064 independent byte vectors and runtime identity exclusion."""
import hashlib
import struct
import unittest
from dataclasses import replace

from adaptive_subedge.application.serialization import canonical_array_token, canonical_bytes
from adaptive_subedge.application.hashing import create_plan, typed_identity
from adaptive_subedge.application.plan_store import PlanStore
from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.status import AttemptState
from tests.unit.test_canonical import plan_content


class IdentityBoundaryVectors(unittest.TestCase):
    def test_unicode_codepoint_sequences_are_not_normalized(self):
        precomposed = "\u00e9"
        decomposed = "e\u0301"
        self.assertEqual(canonical_bytes(precomposed), b"s2:" + precomposed.encode("utf-8"))
        self.assertEqual(canonical_bytes(decomposed), b"s3:" + decomposed.encode("utf-8"))
        self.assertNotEqual(canonical_bytes(precomposed), canonical_bytes(decomposed))
        self.assertNotEqual(
            typed_identity("source-geometry", {"label": precomposed}).digest_hex,
            typed_identity("source-geometry", {"label": decomposed}).digest_hex,
        )

    def test_empty_array_and_rank_zero_use_independent_golden_framing(self):
        header = b"ASE_ARRAY_V1\0i64"
        preimage = header + struct.pack(">IQQ", 2, 0, 4)
        reference = hashlib.sha256(
            b"AdaptiveSubEdgeCanonicalV1\0array\0" + preimage
        ).hexdigest()
        empty = canonical_array_token("i64", (0, 4), ())
        self.assertEqual(empty["digest_hex"], reference)
        self.assertEqual(empty["shape"], [0, 4])
        scalar = canonical_array_token("i64", (), (7,))
        self.assertNotEqual(scalar["digest_hex"], empty["digest_hex"])
        with self.assertRaises(ContractError):
            canonical_array_token("i64", (0, 4), (1,))
        with self.assertRaises(ContractError):
            canonical_array_token("i64", (), ())

    def test_generation_attempts_and_reset_not_part_of_plan_identity(self):
        semantic = plan_content()
        original = create_plan(semantic)
        store = PlanStore(2)
        pub1 = store.publish(original)
        attempt_store = InjectionAttemptStore()
        started = attempt_store.begin(original.plan_hash, "synthetic-working-copy")
        attempt_store.transition(started.attempt_id, AttemptState.SKIPPED, ReasonCode.STALE_PLAN)
        pub2 = store.publish(create_plan(semantic))
        self.assertGreater(pub2.analysis_generation_id, pub1.analysis_generation_id)
        self.assertEqual(original.plan_hash, pub2.plan.plan_hash)
        old_epoch = store.plugin_session_epoch
        store.reset()
        self.assertNotEqual(old_epoch, store.plugin_session_epoch)
        self.assertEqual(store.publish(create_plan(semantic)).plan.plan_hash, original.plan_hash)
        self.assertEqual(len(attempt_store.snapshot()), 1)

    def test_wrong_typed_reference_fails_closed_even_for_well_formed_digest(self):
        original = plan_content()
        wrong_reference = typed_identity("source-geometry", {"label": "not-plugin-settings"})
        malformed = replace(original, plugin_settings=wrong_reference)
        with self.assertRaises(ContractError):
            create_plan(malformed)


if __name__ == "__main__":
    unittest.main()
