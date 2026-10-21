import httpx
from ticket_reviewer.adapters.llm import OpenAICompatibleClient


def test_complete_posts_chat_payload():
    def h(req):
        assert req.url.path == "/v1/chat/completions"
        assert req.headers["authorization"] == "Bearer k"
        body = __import__("json").loads(req.content)
        assert body["model"] == "m" and body["messages"][0] == {"role": "system", "content": "S"}
        return httpx.Response(200, json={"choices": [{"message": {"content": "hello"}}]})
    c = OpenAICompatibleClient("http://x/v1", "m", "k", http=httpx.Client(transport=httpx.MockTransport(h)))
    assert c.complete("S", "U") == "hello"
