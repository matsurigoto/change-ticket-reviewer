from ticket_reviewer.domain import WorkItem
from ticket_reviewer.rules import Rule, evaluate_rules


def item(**fields):
    return WorkItem(id=1, title="t", state="Review", fields=fields)


def test_required_rule_fails_on_missing_or_blank():
    rules = [Rule(id="r1", field="Custom.RollbackPlan", check="required", message="need rollback")]
    assert [f.rule_id for f in evaluate_rules(item(), rules)] == ["r1"]
    assert evaluate_rules(item(**{"Custom.RollbackPlan": "  "}), rules)
    assert evaluate_rules(item(**{"Custom.RollbackPlan": "revert"}), rules) == []


def test_min_length_and_regex_and_one_of():
    f = {"A": "abc", "B": "ticket-12", "C": "prod"}
    rules = [
        Rule(id="len", field="A", check="min_length", value=5, message="short"),
        Rule(id="re", field="B", check="regex", value=r"^CHG-\d+$", message="bad id"),
        Rule(id="env", field="C", check="one_of", value=["dev", "uat"], message="env"),
    ]
    assert {x.rule_id for x in evaluate_rules(item(**f), rules)} == {"len", "re", "env"}


def test_unknown_check_raises():
    import pytest
    with pytest.raises(ValueError):
        evaluate_rules(item(A="x"), [Rule(id="x", field="A", check="nope", message="")])


def test_load_rules(tmp_path):
    from ticket_reviewer.rules import load_rules
    p = tmp_path / "r.yaml"
    p.write_text("rules:\n  - {id: a, field: F, check: required, message: m}\n")
    assert load_rules(p)[0].id == "a"
