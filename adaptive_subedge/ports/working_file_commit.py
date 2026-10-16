"""Commit exclusion port only; no resolver, locking provider or filesystem I/O."""
from typing import ContextManager, Protocol

from adaptive_subedge.domain.runtime_validation import WorkingFileCommitKey


class WorkingFileCommitLockRegistry(Protocol):
    def hold(self, key: WorkingFileCommitKey) -> ContextManager[None]: ...
