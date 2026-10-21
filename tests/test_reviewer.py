import json
from ticket_reviewer.domain import WorkItem, Decision
from ticket_reviewer.reviewer import Reviewer
from ticket_reviewer.rules import Rule


class FakeLLM:
    def __init__(self, reply):
        self.reply, self.calls = reply, []

    def complete(self, system, user):
        self.calls.append((system, user))
        return self.reply


RULES = [Rule(id="rb", field="RB", check="required", message="need rollback")]


def make(reply, **kw):
    llm = FakeLLM(reply)
    return Reviewer(llm, RULES, system_prompt="SYS", user_template="ID={id} {fields}", **kw), llm


def wi(**f):
    return WorkItem(id=7, title="t", state="Review", fields=f)


def test_rule_failure_rejects_without_llm_call():
    r, llm = make("{}")
    v = r.review(wi())
    assert v.decision is Decision.REJECT and "need rollback" in v.reasons[0] and not llm.calls


def test_llm_approve():
    r, llm = make(json.dumps({"approved": True, "reasons": []}))
    v = r.review(wi(RB="x"))
    assert v.decision is Decision.APPROVE and "ID=7" in llm.calls[0][1]


def test_llm_reject_with_reasons_and_code_fence():
    r, _ = make('```json\n{"approved": false, "reasons": ["no monitoring"]}\n```')
    v = r.review(wi(RB="x"))
    assert v.decision is Decision.REJECT and v.reasons == ["no monitoring"]


def test_unparseable_llm_reply_is_error_not_approval():
    r, _ = make("looks good!")
    assert r.review(wi(RB="x")).decision is Decision.ERROR


def test_llm_exception_is_error():
    class Boom:
        def complete(self, s, u):
            raise RuntimeError("down")
    r = Reviewer(Boom(), RULES, "s", "{id}")
    assert r.review(wi(RB="x")).decision is Decision.ERROR
