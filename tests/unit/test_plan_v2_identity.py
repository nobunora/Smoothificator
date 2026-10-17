"""Plan v2 root closure, independent encoding and shared-store isolation."""
import copy
from dataclasses import fields, replace
import hashlib
import unittest

from adaptive_subedge.application.hashing import (
    create_plan, create_plan_v2, verify_plan, verify_plan_v2,
    typed_identity, typed_identities_equal,
)
from adaptive_subedge.application.serialization import (
    identity_root, validate_root, canonical_bytes, semantic_tree,
)
from adaptive_subedge.application.plan_projection_v2 import PLAN_V2_FIELDS
from adaptive_subedge.application.plan_store import PlanStore
from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.domain.plan_v2 import PlanSemanticContentV2
from tests.unit.test_canonical import plan_content
from tests.unit.test_plan_v2_graph import plan_content_v2


def reference_bytes(value):
    """Test-owned ADR-0062 grammar, not the production encoder."""
    if value is None:
        return b"n"
    if type(value) is bool:
        return b"b1" if value else b"b0"
    if type(value) is int:
        return b"i" + str(value).encode("ascii") + b";"
    if type(value) is float:
        return b"f" + (0.0 if value == 0 else value).hex().encode("ascii") + b";"
    if type(value) is str:
        encoded = value.encode("utf-8")
        return b"s" + str(len(encoded)).encode("ascii") + b":" + encoded
    if type(value) is list:
        return b"l" + str(len(value)).encode("ascii") + b"[" + b"".join(map(reference_bytes, value)) + b"]"
    if type(value) is dict:
        return b"m" + str(len(value)).encode("ascii") + b"{" + b"".join(
            reference_bytes(k) + reference_bytes(value[k]) for k in sorted(value)) + b"}"
    raise AssertionError(type(value))


class PlanV2IdentityTests(unittest.TestCase):
    def root(self):
        return identity_root("subedge-plan", plan_content_v2(), schema_version="2")

    def test_exact_fields_independent_bytes_and_hash(self):
        content = plan_content_v2()
        self.assertEqual(tuple(f.name for f in fields(content)), PLAN_V2_FIELDS[PlanSemanticContentV2])
        root = self.root()
        expected = reference_bytes(root)
        self.assertEqual(canonical_bytes(root), expected)
        digest = hashlib.sha256(b"AdaptiveSubEdgeCanonicalV1\0plan\0" + expected).hexdigest()
        plan = create_plan_v2(content)
        self.assertEqual(digest, "49c00d428a56c246f2ac5f8db69a1de1387eb78eaa1911c3845c68756c004399")
        self.assertEqual(plan.plan_hash, digest)
        self.assertEqual(plan.plan_id, digest)
        verify_plan_v2(plan)

    def test_root_domains_versions_and_raw_map_shortcuts_reject(self):
        content = plan_content_v2()
        for kind, version, payload in (("subedge-plan", "1", content),
                                      ("plugin-settings", "2", content),
                                      ("subedge-plan", "2", self.root()["payload"]),
                                      ("subedge-plan", "2", plan_content())):
            with self.subTest(kind=kind, version=version), self.assertRaises(ContractError):
                identity_root(kind, payload, schema_version=version)
        with self.assertRaises(ContractError):
            create_plan(content)
        with self.assertRaises(ContractError):
            verify_plan(create_plan_v2(content))
        with self.assertRaises(ContractError):
            verify_plan_v2(create_plan(plan_content()))

    def test_closed_projected_payload_rejects_extra_fields_and_wrong_tokens(self):
        root = self.root()
        for key, value in (("plan_id", "a" * 64), ("injectable", True), ("timestamp", 1)):
            altered = copy.deepcopy(root)
            altered["payload"][key] = value
            with self.subTest(key=key), self.assertRaises(ContractError):
                validate_root(altered, "subedge-plan")
        for value in (0, True, "0", None):
            altered = copy.deepcopy(root)
            altered["payload"]["volumes"]["geometric_volume_mm3"] = value
            with self.subTest(value=value), self.assertRaises(ContractError):
                validate_root(altered, "subedge-plan")
        altered = copy.deepcopy(root)
        altered["payload"]["added_time"]["estimated_added_time_s"] = 0.0
        with self.assertRaises(ContractError):
            validate_root(altered, "subedge-plan")

    def test_numeric_int_literals_normalize_and_semantic_changes_change_hash(self):
        content = plan_content_v2()
        changed = replace(content, volumes=replace(content.volumes, geometric_volume_mm3=1))
        floating = replace(content, volumes=replace(content.volumes, geometric_volume_mm3=1.0))
        self.assertEqual(create_plan_v2(changed), create_plan_v2(floating))
        self.assertNotEqual(create_plan_v2(content).plan_hash,
                            create_plan_v2(replace(content, plugin_version="another")).plan_hash)

    def test_projected_graph_is_revalidated_not_just_hashable(self):
        changes = (
            (("candidate_paths", 0, "surface_band_id"), "foreign-band"),
            (("candidate_paths", 1, "segment_support", 0, "settings_identity", "digest_hex"), "d" * 64),
            (("structural_loop_contexts", 0, "maximum_path_z_mm"), 0.1),
            (("analysis_outcome", "injectable"), True),
            (("anchors", 0, "target_structural_interval_id"), "foreign-interval"),
        )
        for path, value in changes:
            root = self.root()
            cursor = root["payload"]
            for key in path[:-1]:
                cursor = cursor[key]
            cursor[path[-1]] = value
            with self.subTest(path=path), self.assertRaises(ContractError):
                validate_root(root, "subedge-plan")

    def test_nested_field_set_is_closed_and_no_runtime_payload(self):
        root = self.root()
        root["payload"]["candidate_paths"][0]["path"]["final_machine_e"] = 1.0
        with self.assertRaises(ContractError):
            validate_root(root, "subedge-plan")
        root = self.root()
        root["payload"]["anchors"][0]["matching_tolerance_mm"] = 1
        with self.assertRaises(ContractError):
            validate_root(root, "subedge-plan")

    def test_derived_plan_and_standalone_evidence_remain_unregistered(self):
        content = plan_content_v2()
        for value in (content, create_plan_v2(content), content.directional_error, content.added_time):
            with self.subTest(type=type(value)), self.assertRaises(ContractError):
                semantic_tree(value)
        plan = create_plan_v2(content)
        with self.assertRaises(ContractError):
            verify_plan_v2(replace(plan, plan_id="f" * 64, plan_hash="f" * 64))

    def test_typed_version_comparison_and_runtime_identity_separation(self):
        v2 = typed_identity("subedge-plan", plan_content_v2())
        self.assertTrue(typed_identities_equal("subedge-plan", v2, v2))
        with self.assertRaises(ContractError):
            typed_identities_equal("subedge-plan", v2, typed_identity("subedge-plan", plan_content()))
        root = self.root()
        self.assertEqual(set(root["payload"]), set(PLAN_V2_FIELDS[PlanSemanticContentV2]))

    def test_shared_store_publishes_research_but_never_executes_it(self):
        store = PlanStore(2)
        research = create_plan_v2(plan_content_v2())
        old = create_plan(plan_content())
        store.publish(old)
        entry = store.publish(research)
        snapshot = store.snapshot()
        self.assertEqual(len(snapshot.candidates), 2)
        self.assertEqual(snapshot.candidates[-1].plan, research)
        self.assertNotIn(research, store.eligible(snapshot))
        attempted, _ = store.begin_postprocess_attempt(InjectionAttemptStore(), "fixture")
        self.assertNotIn(research, [item.plan for item in attempted.candidates])
        store.reset()
        self.assertEqual(store.eligible(snapshot), ())
        self.assertEqual(entry.plan.plan_hash, research.plan_hash)


if __name__ == "__main__":
    unittest.main()
