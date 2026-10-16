"""Static diagnostic/port shape tests do not certify locking or proof issuance."""
from dataclasses import FrozenInstanceError, fields, replace
import inspect
from typing import ContextManager, get_type_hints
import unittest

from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.application.serialization import identity_root, semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.plan import IdentityReference
from adaptive_subedge.domain.runtime_validation import AttemptDiagnosticSnapshot, ValidationEvidence, WorkingFileCommitKey
from adaptive_subedge.domain.status import AttemptRevision, AttemptState, InjectionAttemptRecord
from adaptive_subedge.ports.working_file_commit import WorkingFileCommitLockRegistry
from tests.unit.test_plan_v2_graph import plan_content_v2


class RuntimeInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.unknown = ValidationEvidence("unknown", None, "diagnostic_checks_v1", None, None)
        self.rejected = ValidationEvidence("rejected", None, "diagnostic_checks_v1", ReasonCode.INVALID_GEOMETRY, "failure-fixture")
        self.revision = AttemptRevision(7, InjectionAttemptRecord("attempt", None, "source", AttemptState.STARTED))
        self.snapshot = AttemptDiagnosticSnapshot(self.revision, self.unknown, self.unknown, self.unknown, self.rejected)
        self.key = WorkingFileCommitKey("opaque-key", "future-resolver-policy")

    def test_exact_required_frozen_fields(self):
        for instance, count in ((self.unknown, 5), (self.snapshot, 5), (self.key, 2)):
            self.assertEqual(len(fields(instance)), count)
            self.assertFalse(hasattr(instance, "__dict__"))
            for omitted in fields(instance):
                values = {f.name: getattr(instance, f.name) for f in fields(instance) if f != omitted}
                with self.subTest(dto=type(instance).__name__, field=omitted.name), self.assertRaises(TypeError):
                    type(instance)(**values)
            with self.assertRaises(FrozenInstanceError):
                setattr(instance, fields(instance)[0].name, None)

    def test_unknown_and_rejected_state_matrix(self):
        for reason in (ReasonCode.INVALID_GEOMETRY, "invalid-geometry", 0):
            with self.assertRaises(ContractError):
                replace(self.unknown, reason=reason)
        for reference in ("diagnostic", "", 0):
            with self.assertRaises(ContractError):
                replace(self.unknown, evidence_reference=reference)
        for reason in ReasonCode:
            replace(self.rejected, reason=reason, evidence_reference=None)
        for reason in (None, "invalid-geometry", True):
            with self.assertRaises(ContractError):
                replace(self.rejected, reason=reason)
        for reference in ("", " \t", 0, {}):
            with self.assertRaises(ContractError):
                replace(self.rejected, evidence_reference=reference)

    def test_validated_always_rejected_even_with_subject_and_evidence(self):
        subject = IdentityReference("execution-config", "1", "1", "a" * 64)
        for base in (self.unknown, self.rejected):
            for value in ("validated", "VALIDATED", "UNKNOWN", "", None, True):
                with self.assertRaises(ContractError):
                    replace(base, state=value, subject=subject)
        with self.assertRaises(ContractError):
            ValidationEvidence("validated", subject, "diagnostic_checks_v1", None, "proof")

    def test_supported_subject_roles_versions_and_policy(self):
        for kind, version in (("compatibility-descriptor", "1"), ("plugin-settings", "1"),
                              ("plugin-settings", "2"), ("execution-config", "1"), ("source-working-file", "1")):
            subject = IdentityReference(kind, version, "1", "a" * 64)
            replace(self.unknown, subject=subject)
            replace(self.rejected, subject=subject)
        for kind, version, encoding in (("source-geometry", "1", "1"), ("subedge-plan", "2", "1"),
                                        ("execution-config", "2", "1"), ("plugin-settings", "3", "1"),
                                        ("source-working-file", "1", "2")):
            with self.assertRaises(ContractError):
                replace(self.unknown, subject=IdentityReference(kind, version, encoding, "a" * 64))
        for policy in ("", " ", "other", None, 1):
            with self.assertRaises(ContractError):
                replace(self.unknown, validation_policy_version=policy)

    def test_exact_nested_types_and_no_string_subclasses(self):
        class Text(str):
            pass
        class Subject(IdentityReference):
            pass
        class Evidence(ValidationEvidence):
            pass
        class Revision(AttemptRevision):
            pass
        for subject in ({}, "a" * 64, Subject("execution-config", "1", "1", "a" * 64)):
            with self.assertRaises(ContractError):
                replace(self.unknown, subject=subject)
        for change in ({"state": Text("unknown")}, {"validation_policy_version": Text("diagnostic_checks_v1")}):
            with self.assertRaises(ContractError):
                replace(self.unknown, **change)
        with self.assertRaises(ContractError):
            replace(self.rejected, evidence_reference=Text("reference"))
        for field in ("compatibility", "plugin_settings", "execution_config", "source_working_file"):
            for value in ({}, Evidence("unknown", None, "diagnostic_checks_v1", None, None)):
                with self.assertRaises(ContractError):
                    replace(self.snapshot, **{field: value})
        for revision in ({}, self.revision.record, Revision(7, self.revision.record)):
            with self.assertRaises(ContractError):
                replace(self.snapshot, attempt_revision=revision)

    def test_each_check_accepts_only_its_own_role(self):
        slots = {"compatibility": "compatibility-descriptor", "plugin_settings": "plugin-settings",
                 "execution_config": "execution-config", "source_working_file": "source-working-file"}
        for field, role in slots.items():
            for subject_role in slots.values():
                evidence = replace(self.unknown, subject=IdentityReference(subject_role, "1", "1", "a" * 64))
                if role == subject_role:
                    replace(self.snapshot, **{field: evidence})
                else:
                    with self.assertRaises(ContractError):
                        replace(self.snapshot, **{field: evidence})
        replace(self.snapshot, plugin_settings=replace(self.unknown, subject=IdentityReference("plugin-settings", "2", "1", "a" * 64)))

    def test_snapshot_derives_ids_without_store_mutation_or_receipt(self):
        self.assertEqual((self.snapshot.attempt_id, self.snapshot.record_revision), ("attempt", 7))
        with self.assertRaises(TypeError):
            AttemptDiagnosticSnapshot(self.revision, self.unknown, self.unknown, self.unknown, self.unknown, attempt_id="other")
        store = InjectionAttemptStore(max_attempts=2, max_revisions_per_attempt=2)
        record = store.begin(None, "source")
        before = store.history(record.attempt_id)
        view = replace(self.snapshot, attempt_revision=before[0])
        self.assertEqual(view.attempt_id, record.attempt_id)
        self.assertEqual(store.history(record.attempt_id), before)
        self.assertIs(view.attempt_revision.record.state, AttemptState.STARTED)

    def test_commit_key_is_opaque_and_requires_explicit_policy(self):
        key = WorkingFileCommitKey(" raw/key ", " policy ")
        self.assertEqual(key.key_id, " raw/key ")
        self.assertEqual(key.resolver_policy_version, " policy ")
        for field in ("key_id", "resolver_policy_version"):
            for value in (None, "", " \t", 1, {}):
                with self.assertRaises(ContractError):
                    replace(key, **{field: value})

    def test_runtime_objects_excluded_from_canonical_roots(self):
        for value in (self.unknown, self.snapshot, self.key):
            with self.assertRaises(ContractError):
                semantic_tree(value)
            for domain, version in (("subedge-plan", "1"), ("subedge-plan", "2"), ("plugin-settings", "2")):
                with self.assertRaises(ContractError):
                    identity_root(domain, value, schema_version=version)
            with self.assertRaises(ContractError):
                replace(plan_content_v2(), directional_error=value)

    def test_port_is_only_noninstantiable_synchronous_protocol(self):
        self.assertTrue(WorkingFileCommitLockRegistry._is_protocol)
        with self.assertRaises(TypeError):
            WorkingFileCommitLockRegistry()
        method = WorkingFileCommitLockRegistry.hold
        signature = inspect.signature(method)
        self.assertEqual(tuple(signature.parameters), ("self", "key"))
        self.assertFalse(inspect.iscoroutinefunction(method))
        self.assertIs(signature.parameters["key"].default, inspect.Parameter.empty)
        hints = get_type_hints(method)
        self.assertEqual(hints, {"key": WorkingFileCommitKey, "return": ContextManager[None]})


if __name__ == "__main__":
    unittest.main()
