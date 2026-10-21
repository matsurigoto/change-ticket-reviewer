from __future__ import annotations

import base64
import json

import httpx

from ..domain import WorkItem

API = "7.1"


class AzureDevOpsClient:
    """TicketSource backed by the Azure DevOps REST API (PAT auth)."""

    def __init__(self, base_url: str, organization: str, project: str, pat: str, wiql: str,
                 proxy: str | None = None, verify_ssl: bool = True, http: httpx.Client | None = None):
        self._org = f"{base_url.rstrip('/')}/{organization}"
        self._project, self._wiql = project, wiql
        token = base64.b64encode(f":{pat}".encode()).decode()
        self._headers = {"Authorization": f"Basic {token}"}
        self._http = http or httpx.Client(proxy=proxy, verify=verify_ssl, timeout=30)

    def _request(self, method, url, **kw) -> dict:
        r = self._http.request(method, url, headers={**self._headers, **kw.pop("headers", {})}, **kw)
        r.raise_for_status()
        return r.json()

    def find_pending(self) -> list[WorkItem]:
        res = self._request("POST", f"{self._org}/{self._project}/_apis/wit/wiql",
                            params={"api-version": API}, json={"query": self._wiql})
        ids = [str(w["id"]) for w in res.get("workItems", [])]
        if not ids:
            return []
        res = self._request("GET", f"{self._org}/_apis/wit/workitems",
                            params={"ids": ",".join(ids), "api-version": API})
        return [WorkItem(id=w["id"], title=w["fields"].get("System.Title", ""),
                         state=w["fields"].get("System.State", ""), fields=w["fields"])
                for w in res.get("value", [])]

    def add_comment(self, work_item_id: int, text: str) -> None:
        self._request("POST", f"{self._org}/{self._project}/_apis/wit/workItems/{work_item_id}/comments",
                      params={"api-version": "7.1-preview.4"}, json={"text": text})

    def set_state(self, work_item_id: int, state: str) -> None:
        self._request("PATCH", f"{self._org}/_apis/wit/workitems/{work_item_id}",
                      params={"api-version": API},
                      headers={"Content-Type": "application/json-patch+json"},
                      content=json.dumps(
                          [{"op": "add", "path": "/fields/System.State", "value": state}]))
