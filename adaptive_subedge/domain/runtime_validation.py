"""Runtime diagnostic declarations, never validation authority or store receipts."""
from dataclasses import dataclass

from .errors import ContractError, ReasonCode
from .plan import IdentityReference
from .status import AttemptRevision


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, message)


def _text(value: object) -> bool:
    return type(value) is str and bool(value.strip())


@dataclass(frozen=True, slots=True)
class ValidationEvidence:
    state: str
    subject: IdentityReference | None
    validation_policy_version: str
    reason: ReasonCode | None
    evidence_reference: str | None

    def __post_init__(self):
        _require(type(self.state) is str and self.state in ("unknown", "rejected"),
                 "diagnostics cannot establish validated evidence")
        _require(type(self.validation_policy_version) is str
                 and self.validation_policy_version == "diagnostic_checks_v1",
                 "unsupported diagnostic policy")
        if self.subject is not None:
            _require(type(self.subject) is IdentityReference, "exact diagnostic subject required")
            _require((self.subject.identity_type, self.subject.schema_version,
                      self.subject.canonical_encoding_version) in (
                          ("compatibility-descriptor", "1", "1"),
                          ("plugin-settings", "1", "1"), ("plugin-settings", "2", "1"),
                          ("execution-config", "1", "1"), ("source-working-file", "1", "1")),
                     "unsupported diagnostic subject role/version")
        if self.state == "unknown":
            _require(self.reason is None and self.evidence_reference is None,
                     "unknown evidence cannot claim a failure result")
        else:
            _require(type(self.reason) is ReasonCode, "rejected evidence requires an exact reason")
            _require(self.evidence_reference is None or _text(self.evidence_reference),
                     "invalid failure evidence reference")


@dataclass(frozen=True, slots=True)
class AttemptDiagnosticSnapshot:
    attempt_revision: AttemptRevision
    compatibility: ValidationEvidence
    plugin_settings: ValidationEvidence
    execution_config: ValidationEvidence
    source_working_file: ValidationEvidence

    def __post_init__(self):
        _require(type(self.attempt_revision) is AttemptRevision, "exact attempt revision required")
        for evidence, role in ((self.compatibility, "compatibility-descriptor"),
                               (self.plugin_settings, "plugin-settings"),
                               (self.execution_config, "execution-config"),
                               (self.source_working_file, "source-working-file")):
            _require(type(evidence) is ValidationEvidence, "exact diagnostic evidence required")
            _require(evidence.subject is None or evidence.subject.identity_type == role,
                     "diagnostic subject belongs to another check")

    @property
    def attempt_id(self) -> str:
        return self.attempt_revision.record.attempt_id

    @property
    def record_revision(self) -> int:
        return self.attempt_revision.revision


@dataclass(frozen=True, slots=True)
class WorkingFileCommitKey:
    key_id: str
    resolver_policy_version: str

    def __post_init__(self):
        _require(_text(self.key_id) and _text(self.resolver_policy_version),
                 "nonblank opaque commit key and resolver policy required")
