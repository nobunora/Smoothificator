"""Closed Settings v2 identity, full field coverage and v1 isolation."""
from copy import deepcopy
from dataclasses import asdict, fields, is_dataclass, replace, FrozenInstanceError
import hashlib
import json
import math
import unittest

from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.domain.settings import (
    CandidateBeadBounds, SupportCoverageThresholds, SupportRefinementPolicy,
    MeshSectionPolicy, ToolClearanceProfile, ToolRadialKeepOut,
)
from adaptive_subedge.domain.settings_v2 import (
    PluginSettingsV2, SupportQueryNumericPolicy, ClassicJerkCorneringLimit,
    CandidateMotionLimits, DirectionalErrorWeights, OptimizerCostPolicy,
    CandidateExecutionPolicy,
)
from adaptive_subedge.application.hashing import fingerprint_plugin_settings, typed_identities_equal, create_plan
from adaptive_subedge.application.serialization import identity_root, validate_root, canonical_bytes
from tests.unit.test_estimator_settings import estimator
from tests.unit.test_v1_settings_fingerprint_golden import v1_settings, _golden_tree_bytes
from tests.unit.test_canonical import plan_content


def settings_v2():
    return PluginSettingsV2(
        "2", .05, .08, .01, v1_settings().regularity_policy,
        ToolClearanceProfile("synthetic", "1", "not-calibrated", 12., .1, .2,
            (ToolRadialKeepOut(0., .6), ToolRadialKeepOut(8., .9))),
        CandidateBeadBounds(.08, .2, .3, .6), SupportCoverageThresholds(.8, .1),
        SupportRefinementPolicy(.1, 2., .01, .01, 4, .001),
        SupportQueryNumericPolicy("support_query_length_v1", .0001), estimator(),
        MeshSectionPolicy("research-v1", .0001, .0002, .0003, .0004, "research-stability-v1"),
        CandidateMotionLimits(20., 500., ClassicJerkCorneringLimit("classic_jerk_v1", 5.)),
        DirectionalErrorWeights(1., 2.),
        OptimizerCostPolicy("lexicographic_v1", "hard_bidirectional_max",
            "lex_complexity_time_commanded_volume", "planned_intent_counts_v1",
            "weighted_directional_p95_rational_v1", "unavailable_v1",
            "commanded_volume_sum_v1", "canonical_semantic_bytes_v1", 100),
        CandidateExecutionPolicy("candidate_execution_v1", "chronological_dependency_first_v1"), False,
    )


def leaf_paths(value, prefix=()):
    if is_dataclass(value):
        for field in fields(value):
            yield from leaf_paths(getattr(value, field.name), prefix + (field.name,))
    elif type(value) is tuple:
        for i, item in enumerate(value):
            yield from leaf_paths(item, prefix + (i,))
    else:
        yield prefix, value


def changed_leaf(value, path, replacement):
    if not path:
        return replacement
    key, *rest = path
    if type(key) is int:
        items = list(value)
        items[key] = changed_leaf(items[key], rest, replacement)
        return tuple(items)
    return replace(value, **{key: changed_leaf(getattr(value, key), rest, replacement)})


class SettingsV2Tests(unittest.TestCase):
    def test_independent_complete_byte_vector(self):
        settings = settings_v2()
        # dataclasses.asdict enumerates actual declared fields independently of
        # the production serializer whitelist; all fixture float fields are floats.
        payload = json.loads(json.dumps(asdict(settings)))
        expected_root = {"identity_type": "plugin-settings", "schema_version": "2",
                         "canonical_encoding_version": "1", "payload": payload}
        expected_bytes = _golden_tree_bytes(expected_root)
        expected_hash = hashlib.sha256(b"AdaptiveSubEdgeCanonicalV1\0plugin-settings\0" + expected_bytes).hexdigest()
        actual = identity_root("plugin-settings", settings, schema_version="2")
        self.assertEqual(canonical_bytes(actual), expected_bytes)
        self.assertEqual(fingerprint_plugin_settings(settings).digest_hex, expected_hash)
        self.assertEqual(len(fields(settings)), 17)

    def test_every_leaf_changes_identity_or_is_rejected_by_fixed_contract(self):
        base = settings_v2()
        base_hash = fingerprint_plugin_settings(base)
        changed, rejected = 0, 0
        for path, value in leaf_paths(base):
            candidate = ({str: lambda: value + "-unknown", float: lambda: value + .00001,
                          int: lambda: value + 1, bool: lambda: not value,
                          type(None): lambda: "synthetic-evidence"}[type(value)])()
            with self.subTest(path=path):
                try:
                    variant = changed_leaf(base, path, candidate)
                except ContractError:
                    rejected += 1
                else:
                    self.assertNotEqual(fingerprint_plugin_settings(variant), base_hash)
                    changed += 1
        self.assertGreater(changed, 45)
        self.assertGreater(rejected, 10)
        no_profile = replace(base, tool_clearance_profile=None)
        self.assertNotEqual(fingerprint_plugin_settings(no_profile), base_hash)

    def test_root_versions_and_v1_plan_are_isolated(self):
        settings = settings_v2()
        old = fingerprint_plugin_settings(v1_settings())
        new = fingerprint_plugin_settings(settings)
        self.assertEqual(new.schema_version, "2")
        self.assertTrue(typed_identities_equal("plugin-settings", new, new))
        for call in (
            lambda: typed_identities_equal("plugin-settings", old, new),
            lambda: identity_root("plugin-settings", settings),
            lambda: identity_root("plugin-settings", v1_settings(), schema_version="2"),
            lambda: identity_root("source-geometry", settings, schema_version="2"),
            lambda: identity_root("plugin-settings", asdict(settings), schema_version="2"),
            lambda: create_plan(replace(plan_content(), plugin_settings=new)),
        ):
            with self.assertRaises(ContractError):
                call()

    def test_closed_root_rejects_unknown_missing_and_mismatched_payload(self):
        root = identity_root("plugin-settings", settings_v2(), schema_version="2")
        mutations = [lambda p: p.update(extra="x"), lambda p: p.pop("mesh_section_policy"),
                     lambda p: p.update(schema_version="1"),
                     lambda p: p["optimizer_cost_policy"].update(time_estimator_model_version="invented"),
                     lambda p: p["candidate_motion_limits"].update(extra=1),
                     lambda p: p.update(physical_injection_requested=True)]
        for mutate in mutations:
            candidate = deepcopy(root)
            mutate(candidate["payload"])
            with self.assertRaises(ContractError):
                validate_root(candidate, "plugin-settings")

    def test_numeric_boundaries_and_unknown_policies_fail_closed(self):
        base = settings_v2()
        for bad in (True, -1., 0., math.nan, math.inf, 10**400, "0.1"):
            with self.subTest(bad=str(bad)[:20]), self.assertRaises(ContractError):
                replace(base, surface_error_tolerance_mm=bad)
        for bad in (True, 0, -1, 1., math.inf):
            with self.assertRaises(ContractError):
                replace(base.optimizer_cost_policy, max_candidate_evaluations=bad)
        for cls, args in (
            (DirectionalErrorWeights, (0., 0.)),
            (DirectionalErrorWeights, (True, 1.)),
            (SupportQueryNumericPolicy, ("future", .1)),
            (ClassicJerkCorneringLimit, ("junction_deviation", .1)),
        ):
            with self.assertRaises(ContractError):
                cls(*args)
        with self.assertRaises(ContractError):
            replace(base, candidate_motion_limits={})
        with self.assertRaises(ContractError):
            replace(base, physical_injection_requested=True)

    def test_projected_root_requires_float_tokens_but_constructor_accepts_ints(self):
        base = settings_v2()
        integer_input = replace(base, directional_error_weights=DirectionalErrorWeights(1, 2))
        self.assertEqual(fingerprint_plugin_settings(base), fingerprint_plugin_settings(integer_input))
        root = identity_root("plugin-settings", base, schema_version="2")
        root["payload"]["directional_error_weights"]["pred_to_src_weight"] = 1
        with self.assertRaises(ContractError):
            validate_root(root, "plugin-settings")

    def test_nested_dtos_and_policy_subclasses_are_not_accepted(self):
        base = settings_v2()
        for field in fields(base):
            value = getattr(base, field.name)
            if is_dataclass(value):
                with self.subTest(field=field.name), self.assertRaises(ContractError):
                    replace(base, **{field.name: asdict(value)})
        class PolicyString(str):
            pass
        with self.assertRaises(ContractError):
            SupportQueryNumericPolicy(PolicyString("support_query_length_v1"), .1)

    def test_new_positive_caps_and_weight_boundaries(self):
        base = settings_v2()
        cases = ((base.support_query_numeric_policy, "support_query_length_tolerance_mm"),
                 (base.candidate_motion_limits, "max_candidate_speed_mm_s"),
                 (base.candidate_motion_limits, "max_subedge_acceleration_mm_s2"),
                 (base.candidate_motion_limits.cornering_limit, "max_subedge_jerk_mm_s"))
        for dto, field in cases:
            for bad in (False, 0., -1., math.inf, math.nan, 10**400):
                with self.subTest(field=field, bad=str(bad)[:15]), self.assertRaises(ContractError):
                    replace(dto, **{field: bad})
        for values in ((0., 1.), (1., 0.), (1e308, 1e308)):
            self.assertIsInstance(DirectionalErrorWeights(*values), DirectionalErrorWeights)
        for values in ((0., 0.), (-1., 1.), (1., math.nan), (True, 1.), (1., math.inf)):
            with self.assertRaises(ContractError):
                DirectionalErrorWeights(*values)

    def test_immutability_required_fields_and_number_normalization(self):
        base = settings_v2()
        with self.assertRaises(FrozenInstanceError):
            base.schema_version = "1"
        with self.assertRaises(TypeError):
            PluginSettingsV2(**{k: v for k, v in asdict(base).items() if k != "schema_version"})
        with self.assertRaises(TypeError):
            replace(base, unexpected=True)
        a = replace(base, candidate_seam_gap_mm=0)
        b = replace(base, candidate_seam_gap_mm=-0.)
        self.assertEqual(fingerprint_plugin_settings(a), fingerprint_plugin_settings(b))
        large = DirectionalErrorWeights(1e308, 1e308)
        self.assertEqual(large.pred_to_src_weight, 1e308)  # no overflowing float sum


if __name__ == "__main__":
    unittest.main()
