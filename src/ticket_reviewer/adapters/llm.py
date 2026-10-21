from __future__ import annotations

import httpx


class OpenAICompatibleClient:
    """Works for internal gateways (vLLM, Ollama, LiteLLM...) and external OpenAI-style APIs."""

    def __init__(self, base_url: str, model: str, api_key: str = "", proxy: str | None = None,
                 verify_ssl: bool = True, timeout: float = 60.0, http: httpx.Client | None = None):
        self._url = f"{base_url.rstrip('/')}/chat/completions"
        self._model = model
        self._headers = {"Authorization": f"******"} if api_key else {}
        self._http = http or httpx.Client(proxy=proxy, verify=verify_ssl, timeout=timeout)

    def complete(self, system: str, user: str) -> str:
        r = self._http.post(self._url, headers=self._headers, json={
            "model": self._model, "temperature": 0,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
