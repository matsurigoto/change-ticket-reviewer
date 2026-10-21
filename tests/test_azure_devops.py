import json
import httpx
from ticket_reviewer.adapters.azure_devops import AzureDevOpsClient


def make(handler):
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return AzureDevOpsClient("https://dev.azure.com", "org", "proj", "pat", "SELECT 1", http=http)


def test_find_pending_runs_wiql_then_fetches_items():
    seen = []

    def h(req):
        seen.append((req.method, req.url.path))
        if req.url.path.endswith("/wiql"):
            return httpx.Response(200, json={"workItems": [{"id": 5}, {"id": 6}]})
        assert req.url.params["ids"] == "5,6"
        return httpx.Response(200, json={"value": [
            {"id": 5, "fields": {"System.Title": "A", "System.State": "Review"}},
            {"id": 6, "fields": {"System.Title": "B", "System.State": "Review"}}]})
    items = make(h).find_pending()
    assert [i.id for i in items] == [5, 6] and items[0].title == "A"
    assert make(h)._headers["Authorization"].startswith("Basic ")


def test_find_pending_empty():
    c = make(lambda r: httpx.Response(200, json={"workItems": []}))
    assert c.find_pending() == []


def test_add_comment_and_set_state():
    calls = []

    def h(req):
        calls.append((req.method, req.url.path, req.headers["content-type"], json.loads(req.content)))
        return httpx.Response(200, json={})
    c = make(h)
    c.add_comment(9, "hi")
    c.set_state(9, "Approved")
    assert calls[0][0] == "POST" and calls[0][1].endswith("/workItems/9/comments") and calls[0][3] == {"text": "hi"}
    assert calls[1][0] == "PATCH" and calls[1][2] == "application/json-patch+json"
    assert calls[1][3] == [{"op": "add", "path": "/fields/System.State", "value": "Approved"}]


def test_http_error_raises():
    import pytest
    c = make(lambda r: httpx.Response(401))
    with pytest.raises(httpx.HTTPStatusError):
        c.find_pending()
