"""Composition root: wires settings -> adapters -> workflow."""
from __future__ import annotations

import logging
import time
from pathlib import Path

from .adapters.azure_devops import AzureDevOpsClient
from .adapters.llm import OpenAICompatibleClient
from .config import Settings
from .reviewer import Reviewer
from .rules import load_rules
from .workflow import ActionPolicy, ReviewWorkflow

log = logging.getLogger(__name__)


def build_system_prompt(s: Settings) -> str:
    base = Path(s.paths.prompts_dir) / s.paths.system_prompt
    parts = [base.read_text(encoding="utf-8")]
    for name in s.paths.skills:
        parts.append((Path(s.paths.skills_dir) / name / "SKILL.md").read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def build_workflow(s: Settings) -> ReviewWorkflow:
    a, p = s.azure_devops, s.llm.active
    source = AzureDevOpsClient(a.base_url, a.organization, a.project, a.pat, a.wiql, a.proxy, a.verify_ssl)
    llm = OpenAICompatibleClient(p.base_url, p.model, p.api_key, p.proxy, p.verify_ssl, p.timeout)
    template = (Path(s.paths.prompts_dir) / s.paths.user_prompt).read_text(encoding="utf-8")
    reviewer = Reviewer(llm, load_rules(s.paths.rules_file), build_system_prompt(s), template)
    w = s.workflow
    return ReviewWorkflow(source, reviewer, ActionPolicy(w.approve_state, w.reject_state, w.comment_on_approve))


def run_forever(s: Settings, once: bool = False) -> None:
    wf = build_workflow(s)
    while True:
        wf.run_once()
        if once:
            return
        time.sleep(s.scheduler.interval_seconds)
