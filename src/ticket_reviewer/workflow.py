from __future__ import annotations

import logging
from dataclasses import dataclass

from .domain import Decision, Verdict
from .ports import TicketSource

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ActionPolicy:
    """What to do with a verdict. Extend here for custom flows."""
    approve_state: str | None = None
    reject_state: str | None = None
    comment_on_approve: bool = True


class ReviewWorkflow:
    def __init__(self, source: TicketSource, reviewer, policy: ActionPolicy):
        self._source, self._reviewer, self._policy = source, reviewer, policy

    def run_once(self) -> None:
        for item in self._source.find_pending():
            try:
                self._handle(item.id, self._reviewer.review(item))
            except Exception:
                log.exception("failed handling work item %s", item.id)

    def _handle(self, wid: int, v: Verdict) -> None:
        p = self._policy
        if v.decision is Decision.ERROR:
            log.warning("work item %s left untouched: %s", wid, v.reasons)
        elif v.decision is Decision.APPROVE:
            if p.comment_on_approve:
                self._source.add_comment(wid, _format("✅ Review passed", v.reasons))
            if p.approve_state:
                self._source.set_state(wid, p.approve_state)
        else:
            self._source.add_comment(wid, _format("❌ Review rejected", v.reasons))
            if p.reject_state:
                self._source.set_state(wid, p.reject_state)


def _format(title: str, reasons: list[str]) -> str:
    return "\n".join([title, *(f"- {r}" for r in reasons)])
