"""Deterministic, config-driven field checks (run before the LLM)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from .domain import WorkItem


@dataclass(frozen=True)
class Rule:
    id: str
    field: str
    check: str
    message: str
    value: object = None


@dataclass(frozen=True)
class Failure:
    rule_id: str
    message: str


def _text(v) -> str:
    return "" if v is None else str(v).strip()


CHECKS = {
    "required": lambda v, arg: _text(v) != "",
    "min_length": lambda v, arg: len(_text(v)) >= int(arg),
    "regex": lambda v, arg: re.search(arg, _text(v)) is not None,
    "one_of": lambda v, arg: _text(v) in [str(a) for a in arg],
}


def evaluate_rules(item: WorkItem, rules: list[Rule]) -> list[Failure]:
    failures = []
    for r in rules:
        check = CHECKS.get(r.check)
        if check is None:
            raise ValueError(f"unknown check '{r.check}' in rule '{r.id}'")
        if not check(item.fields.get(r.field), r.value):
            failures.append(Failure(r.id, r.message))
    return failures


def load_rules(path: str | Path) -> list[Rule]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return [Rule(**r) for r in data.get("rules", [])]
