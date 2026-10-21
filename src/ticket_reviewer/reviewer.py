from __future__ import annotations

import json
import logging
import re

from .domain import Decision, Verdict, WorkItem
from .ports import LLMClient
from .rules import Rule, evaluate_rules

log = logging.getLogger(__name__)


class Reviewer:
    """Rules first (cheap, deterministic), then LLM judgement."""

    def __init__(self, llm: LLMClient, rules: list[Rule], system_prompt: str, user_template: str):
        self._llm, self._rules = llm, rules
        self._system, self._template = system_prompt, user_template

    def review(self, item: WorkItem) -> Verdict:
        failures = evaluate_rules(item, self._rules)
        if failures:
            return Verdict(Decision.REJECT, [f.message for f in failures])
        user = self._template.format(
            id=item.id, title=item.title, state=item.state,
            fields=json.dumps(item.fields, ensure_ascii=False, indent=2, default=str))
        try:
            return _parse(self._llm.complete(self._system, user))
        except Exception as e:  # LLM down, timeout, ...
            log.exception("LLM review failed for %s", item.id)
            return Verdict(Decision.ERROR, [f"LLM call failed: {e}"])


def _parse(reply: str) -> Verdict:
    m = re.search(r"\{.*\}", reply, re.S)
    try:
        data = json.loads(m.group(0)) if m else None
        approved = data["approved"]
        if not isinstance(approved, bool):
            raise TypeError("approved must be boolean")
        reasons = [str(r) for r in data.get("reasons", [])]
    except (ValueError, KeyError, TypeError, AttributeError):
        return Verdict(Decision.ERROR, ["unparseable LLM reply"])
    return Verdict(Decision.APPROVE if approved else Decision.REJECT, reasons)
