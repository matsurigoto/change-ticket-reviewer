from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


@dataclass(frozen=True)
class WorkItem:
    id: int
    title: str
    state: str
    fields: dict = field(default_factory=dict)


class Decision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    ERROR = "error"  # could not decide; leave ticket untouched for a human


@dataclass(frozen=True)
class Verdict:
    decision: Decision
    reasons: list[str] = field(default_factory=list)
