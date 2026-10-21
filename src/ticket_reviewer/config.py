"""Settings loader: YAML file + TR_<SECTION>__<KEY> env overrides; secrets only via env."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class AzureDevOpsSettings:
    base_url: str = "https://dev.azure.com"
    organization: str = ""
    project: str = ""
    pat_env: str = "ADO_PAT"
    proxy: str | None = None
    wiql: str = ""
    verify_ssl: bool = True

    @property
    def pat(self) -> str:
        return os.environ.get(self.pat_env, "")


@dataclass
class ProviderSettings:
    base_url: str
    model: str
    api_key_env: str = ""
    proxy: str | None = None
    verify_ssl: bool = True
    timeout: float = 60.0

    @property
    def api_key(self) -> str:
        return os.environ.get(self.api_key_env, "") if self.api_key_env else ""


@dataclass
class LLMSettings:
    default: str = ""
    providers: dict[str, ProviderSettings] = field(default_factory=dict)

    @property
    def active(self) -> ProviderSettings:
        return self.providers[self.default]


@dataclass
class SchedulerSettings:
    interval_seconds: int = 300


@dataclass
class WorkflowSettings:
    approve_state: str | None = None
    reject_state: str | None = None
    comment_on_approve: bool = True


@dataclass
class PathSettings:
    prompts_dir: str = "config/prompts"
    rules_file: str = "config/rules/change_ticket.yaml"
    skills_dir: str = "config/skills"
    system_prompt: str = "system.md"
    user_prompt: str = "review.md"
    skills: list[str] = field(default_factory=list)


@dataclass
class Settings:
    azure_devops: AzureDevOpsSettings
    llm: LLMSettings
    scheduler: SchedulerSettings
    workflow: WorkflowSettings
    paths: PathSettings


def _apply_env(data: dict, prefix: str = "TR_") -> None:
    for key, val in os.environ.items():
        if not key.startswith(prefix) or "__" not in key:
            continue
        parts = [p.lower() for p in key[len(prefix):].split("__")]
        node = data
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = yaml.safe_load(val)


def load_settings(path: str | Path) -> Settings:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    _apply_env(data)
    llm = data.get("llm", {})
    return Settings(
        azure_devops=AzureDevOpsSettings(**data.get("azure_devops", {})),
        llm=LLMSettings(
            default=llm.get("default", ""),
            providers={k: ProviderSettings(**v) for k, v in llm.get("providers", {}).items()}),
        scheduler=SchedulerSettings(**data.get("scheduler", {})),
        workflow=WorkflowSettings(**data.get("workflow", {})),
        paths=PathSettings(**data.get("paths", {})),
    )
