from __future__ import annotations

from typing import Protocol

from .domain import WorkItem


class TicketSource(Protocol):
    def find_pending(self) -> list[WorkItem]: ...
    def add_comment(self, work_item_id: int, text: str) -> None: ...
    def set_state(self, work_item_id: int, state: str) -> None: ...


class LLMClient(Protocol):
    def complete(self, system: str, user: str) -> str: ...
