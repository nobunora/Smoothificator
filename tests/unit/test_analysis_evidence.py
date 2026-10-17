"""Evidence shape is separate from proof, canonical Plan identity and permission."""
from dataclasses import FrozenInstanceError, replace
import math
import unittest

from adaptive_subedge.domain.analysis_evidence import (
    TimeEstimateAvailable, TimeEstimateUnavailable, ErrorConvergenceEvidence, DirectionalErrorEvidence,
)
from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.domain.metrics import BidirectionalSurfaceErrorMetrics
from adaptive_subedge.domain.plan import IdentityReference
from adaptive_subedge.application.serialization import semantic_tree


def policy(digest="a"):
    return IdentityReference("plugin-settings", "2", "1", digest * 64)


def available():
    return TimeEstimateAvailable("available", 0., "synthetic-model",
        IdentityReference("execution-config", "1", "1", "b" * 64), "synthetic-proof-not-physical")


def unknown():
    return ErrorConvergenceEvidence("unknown", policy(), 0, None, None)


class AnalysisEvidenceTests(unittest.TestCase):
    def test_zero_available_time_and_unknown_time_are_distinct_types(self):
        known = available()
        missing = TimeEstimateUnavailable("unavailable", "time-model-unavailable", ("predictor",))
        self.assertEqual(known.estimated_added_time_s, 0.)
        self.assertFalse(hasattr(missing, "estimated_added_time_s"))
        with self.assertRaises(TypeError):
            TimeEstimateUnavailable("unavailable", "time-model-unavailable", ("predictor",), estimated_added_time_s=0.)
        with self.assertRaises(FrozenInstanceError):
            missing.reason = "missing-model-evidence"

    def test_available_requires_actual_identity_shape_and_evidence(self):
        base = available()
        for field, value in (("tag", "unavailable"), ("evidence_reference", " "),
                             ("predictor_model_version", "unavailable_v1"),
                             ("predictor_model_version", ""), ("resolved_execution_config", policy())):
            with self.subTest(field=field), self.assertRaises(ContractError):
                replace(base, **{field: value})
        for value in (True, -1., math.nan, math.inf, 10**400, None):
            with self.subTest(value=str(value)[:15]), self.assertRaises(ContractError):
                replace(base, estimated_added_time_s=value)

    def test_unavailable_rejects_unknown_reasons_and_dependency_shapes(self):
        base = TimeEstimateUnavailable("unavailable", "missing-model-evidence", ("model",))
        for value in ((), [], ("x", "x"), (" ",), (1,), ({},)):
            with self.subTest(value=value), self.assertRaises(ContractError):
                replace(base, missing_dependency_ids=value)
        for field, value in (("reason", "guess"), ("tag", "available"), ("reason", None)):
            with self.assertRaises(ContractError):
                replace(base, **{field: value})

    def test_convergence_state_matrix(self):
        ErrorConvergenceEvidence("converged", policy(), 2, "proof", None)
        ErrorConvergenceEvidence("failed", policy(), 0, None, "missing-error-evidence")
        for args in (
            ("unknown", 1, None, None), ("unknown", 0, "proof", None),
            ("unknown", 0, None, "missing-error-evidence"),
            ("converged", 0, "proof", None), ("converged", 1, None, None),
            ("converged", 1, "proof", "invalid-error-domain"),
            ("failed", 1, None, None), ("failed", 1, None, "guess"),
            ("converged", True, "proof", None), ("unknown", -1, None, None),
        ):
            state, count, reference, reason = args
            with self.subTest(args=args), self.assertRaises(ContractError):
                ErrorConvergenceEvidence(state, policy(), count, reference, reason)

    def test_two_directions_preserve_unknown_and_require_same_policy(self):
        metrics = BidirectionalSurfaceErrorMetrics(.2, .3, .1, .2, .1, .2)
        converged = ErrorConvergenceEvidence("converged", policy(), 2, "proof", None)
        value = DirectionalErrorEvidence(metrics, converged, unknown())
        self.assertEqual(value.src_to_pred.state, "unknown")
        self.assertFalse(hasattr(value, "injectable"))
        with self.assertRaises(ContractError):
            replace(value, src_to_pred=replace(unknown(), estimator_policy=policy("c")))
        with self.assertRaises(ContractError):
            replace(value, pred_to_src={})
        with self.assertRaises(ContractError):
            replace(unknown(), estimator_policy=replace(policy(), schema_version="1"))

    def test_standalone_evidence_never_enters_current_canonical_registry(self):
        metrics = BidirectionalSurfaceErrorMetrics(.2, .3, .1, .2, .1, .2)
        for value in (available(), TimeEstimateUnavailable("unavailable", "time-model-unavailable", ("model",)),
                      unknown(), DirectionalErrorEvidence(metrics, unknown(), unknown())):
            with self.subTest(dto=type(value).__name__), self.assertRaises(ContractError):
                semantic_tree(value)


if __name__ == "__main__":
    unittest.main()
