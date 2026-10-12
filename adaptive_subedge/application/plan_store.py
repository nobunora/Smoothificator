"""Atomic bounded immutable-plan publication with ADR-0065 session epochs."""
from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock
from uuid import uuid4

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.plan import SubEdgePlan
from .hashing import verify_plan


@dataclass(frozen=True, slots=True)
class PublishedPlan:
    plan: SubEdgePlan
    plugin_session_epoch: str
    analysis_generation_id: int


@dataclass(frozen=True, slots=True)
class PlanSnapshot:
    plugin_session_epoch: str
    candidates: tuple[PublishedPlan, ...]


class PlanStore:
    """No authoritative injection status; one lock owns all publication state."""

    def __init__(self, capacity: int):
        if type(capacity) is not int or capacity <= 0:
            raise ContractError(ReasonCode.INVALID_SETTING, "capacity must be positive")
        self._capacity = capacity
        self._lock = RLock()
        self._epoch = uuid4().hex
        self._next_generation = 0
        self._plans: OrderedDict[str, PublishedPlan] = OrderedDict()

    @property
    def plugin_session_epoch(self) -> str:
        with self._lock:
            return self._epoch

    def publish(self, plan: SubEdgePlan) -> PublishedPlan:
        verify_plan(plan)
        with self._lock:
            self._next_generation += 1
            entry = PublishedPlan(plan, self._epoch, self._next_generation)
            self._plans.pop(plan.plan_hash, None)
            self._plans[plan.plan_hash] = entry
            while len(self._plans) > self._capacity:
                self._plans.popitem(last=False)
            return entry

    def snapshot(self) -> PlanSnapshot:
        with self._lock:
            return PlanSnapshot(self._epoch, tuple(self._plans.values()))

    def reset(self) -> str:
        with self._lock:
            self._plans.clear()
            self._epoch = uuid4().hex
            self._next_generation = 0
            return self._epoch

    def eligible(self, snapshot: PlanSnapshot) -> tuple[SubEdgePlan, ...]:
        """An immutable snapshot survives eviction, but not explicit session reset."""
        with self._lock:
            if snapshot.plugin_session_epoch != self._epoch:
                return ()
            return tuple(x.plan for x in snapshot.candidates if x.plugin_session_epoch == self._epoch and x.plan.content.injectable is True)
