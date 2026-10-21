from ticket_reviewer.domain import WorkItem, Decision, Verdict
from ticket_reviewer.workflow import ReviewWorkflow, ActionPolicy


class FakeSource:
    def __init__(self, items):
        self.items, self.comments, self.states = items, [], []

    def find_pending(self):
        return self.items

    def add_comment(self, wid, text):
        self.comments.append((wid, text))

    def set_state(self, wid, state):
        self.states.append((wid, state))


class FakeReviewer:
    def __init__(self, verdict):
        self.v = verdict

    def review(self, item):
        return self.v


ITEMS = [WorkItem(id=1, title="a", state="Review", fields={})]
POLICY = ActionPolicy(approve_state="Approved", reject_state=None, comment_on_approve=True)


def test_approve_transitions_and_comments():
    s = FakeSource(ITEMS)
    ReviewWorkflow(s, FakeReviewer(Verdict(Decision.APPROVE, ["ok"])), POLICY).run_once()
    assert s.states == [(1, "Approved")] and s.comments


def test_reject_comments_reasons_without_state_change():
    s = FakeSource(ITEMS)
    ReviewWorkflow(s, FakeReviewer(Verdict(Decision.REJECT, ["bad A", "bad B"])), POLICY).run_once()
    assert not s.states and "bad A" in s.comments[0][1] and "bad B" in s.comments[0][1]


def test_reject_state_configurable():
    s = FakeSource(ITEMS)
    p = ActionPolicy(approve_state="Approved", reject_state="Rejected")
    ReviewWorkflow(s, FakeReviewer(Verdict(Decision.REJECT, ["x"])), p).run_once()
    assert s.states == [(1, "Rejected")]


def test_error_takes_no_action():
    s = FakeSource(ITEMS)
    ReviewWorkflow(s, FakeReviewer(Verdict(Decision.ERROR, ["llm down"])), POLICY).run_once()
    assert not s.states and not s.comments


def test_one_failing_item_does_not_stop_others():
    class Flaky(FakeSource):
        def add_comment(self, wid, text):
            if wid == 1:
                raise RuntimeError("api")
            super().add_comment(wid, text)
    s = Flaky([WorkItem(1, "a", "Review", {}), WorkItem(2, "b", "Review", {})])
    ReviewWorkflow(s, FakeReviewer(Verdict(Decision.REJECT, ["x"])), POLICY).run_once()
    assert [c[0] for c in s.comments] == [2]
