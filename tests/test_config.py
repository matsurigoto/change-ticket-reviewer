from ticket_reviewer.config import load_settings

YAML = """
azure_devops:
  base_url: https://dev.azure.com
  organization: org
  project: proj
  pat_env: ADO_PAT
  proxy: http://proxy:8080
  wiql: "SELECT [System.Id] FROM WorkItems"
llm:
  default: internal
  providers:
    internal: {base_url: http://llm.local/v1, model: m1, api_key_env: K1}
    external: {base_url: https://api.openai.com/v1, model: m2, api_key_env: K2, proxy: http://p:1}
scheduler: {interval_seconds: 60}
workflow: {approve_state: Approved}
"""


def test_load_settings_with_env_overrides(tmp_path, monkeypatch):
    p = tmp_path / "s.yaml"
    p.write_text(YAML)
    monkeypatch.setenv("ADO_PAT", "secret")
    monkeypatch.setenv("TR_LLM__DEFAULT", "external")
    monkeypatch.setenv("TR_AZURE_DEVOPS__PROJECT", "other")
    s = load_settings(p)
    assert s.azure_devops.pat == "secret" and s.azure_devops.project == "other"
    assert s.llm.default == "external" and s.llm.active.model == "m2"
    assert s.llm.providers["external"].proxy == "http://p:1"
    assert s.scheduler.interval_seconds == 60
    assert s.workflow.approve_state == "Approved" and s.workflow.reject_state is None
