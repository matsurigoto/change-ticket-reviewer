# change-ticket-reviewer
AI agent that polls Azure DevOps change tickets, reviews them (rules + LLM), then approves (state change) or comments reasons.

```
pip install -e .[dev] && pytest
ADO_PAT=... INTERNAL_LLM_API_KEY=... ticket-reviewer --config config/settings.yaml [--once]
docker build -t ticket-reviewer .
```
See `docs/design.md` for architecture, config, framework evaluation and reference projects.
