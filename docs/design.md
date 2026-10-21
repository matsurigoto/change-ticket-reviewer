# Design, framework evaluation, references

## Architecture
`domain` (WorkItem/Verdict) ← `ports` (TicketSource, LLMClient) ← `adapters` (Azure DevOps REST, OpenAI-compatible LLM)
→ `rules` (deterministic checks) + `reviewer` (rules → LLM) → `workflow` (ActionPolicy: approve/reject/error) → `app` (wiring, polling loop).
Run as a long-lived Deployment (`k8s/deployment.yaml`) or `--once` in a CronJob. Replace/extend `TicketSource` for other boards,
or add an MCP-backed `TicketSource`/tool adapter without touching the core.

## Config
`config/settings.yaml` (ADO URL/org/project/WIQL/proxy, internal+external LLM providers each with own proxy, scheduler, state transitions),
`config/prompts/`, `config/rules/`, `config/skills/<name>/SKILL.md`. Env override: `TR_<SECTION>__<KEY>`. Secrets only via env (`*_env`).

## Framework choice
The flow is fixed (fetch → rules → one LLM judgement → act), so no agent framework is required for v1; a thin `LLMClient` port keeps it swappable.
- **LangChain**: good for model/tool integrations, but heavy for a single-call review.
- **LangGraph**: best fit when the flow grows (multi-step review, human-in-the-loop approval, retries, checkpointing). Recommended upgrade path: wrap `Reviewer` as a graph node.
- **OpenHands**: a coding agent that works in sandboxes; not suited for form/field review.
- Alternatives: PydanticAI / OpenAI Agents SDK (typed outputs, MCP support), LiteLLM (unified gateway for internal+external models), official `azure-devops-mcp` for MCP access.

## Similar projects to study (verify before relying; not fetched offline)
- microsoft/azure-devops-mcp – MCP server for work items.
- langchain-ai/langgraph – stateful agent graphs, human-in-the-loop.
- BerriAI/litellm – multi-provider routing/proxy settings.
- All-Hands-AI/OpenHands – agent architecture reference.
- qodo-ai/pr-agent – LLM review bot with prompt/config files in TOML, the closest model for "review and comment".
