# Sample Agent Slim – Practical Guide

A concise, modernized guide to the `sample-agent-slim` repo: what it does, how to run it (sidecar vs. sidecar-free), and how to adapt it for your own agent.

---

## What this agent is
- Lightweight Pattern Agentic reference agent.
- Uses **SLIM** for messaging and **Pattern Agent SDK (pa_sdk)** for prompts/session handling.
- Loads tools from **MCP** via `mcp.json`.
- Uses **LangChain** for LLM orchestration.

Repo map (minimal):
```
pa_sample_agent/
  slim_interface.py   # SLIM entrypoint; builds app via pa_sdk or env
  agent_builder.py    # Builds LangChain agent + MCP tools
  agent.py            # Thin wrapper that calls the agent impl
  config.py           # Env-driven settings (Pydantic, hot reload)
  slim_client.py      # CLI client (A2A or legacy)
mcp.json              # MCP tool config
pyproject.toml        # Deps (uv-compatible)
```

---

## Running modes

### 1) Sidecar + A2A (production-style)
Use when Agent Services is available and you want session-token enforcement.
- Required env: `__PA_AGENT_SERVICES_ENDPOINT` (points to Agent Services).
- SLIM endpoint/name/secret are provided by Agent Services; you do **not** set `AGNT_SLIM_*`.
- Prompts fetched via `pa_sdk.prompt("inference")`.
- Client flag: `--a2a`.

### 2) Sidecar-free (local dev)
Use when Agent Services is unavailable. The agent falls back to env-provided SLIM + optional legacy handler (disabled by default).
- Required env: `AGNT_SLIM_LOCAL_NAME`, `AGNT_SLIM_ENDPOINT`, `AGNT_SLIM_AUTH_SECRET`.
- Optional env: `AGNT_SYSTEM_PROMPT`, `AGNT_ENABLE_LEGACY_HANDLER=true`.
- Prompts: from `pa_sdk` if sidecar is set; otherwise uses `AGNT_SYSTEM_PROMPT` if provided.
- Client: without `--a2a`, sends `{"type":"question","prompt":...}` to the legacy handler (only if enabled).

---

## Quick start (sidecar-free local)
1) Start a local SLIM node (no auth):
   ```bash
   cat > slim-config.yaml <<'EOF'
   services:
     slim/0:
       dataplane:
         servers:
           - endpoint: "0.0.0.0:46357"
             auth: { type: none }
             tls:  { insecure: true }
         clients: []
   EOF
   docker run --rm -it \
     -v $(pwd)/slim-config.yaml:/config.yaml \
     -p 46357:46357 \
     ghcr.io/agntcy/slim:1.0.0 \
     /slim --config /config.yaml
   ```
2) Run the agent:
   ```bash
   AGNT_DOT_ENV=.env.dev \
   __PA_AGENT_SERVICES_ENDPOINT= \
   AGNT_ENABLE_LEGACY_HANDLER=true \
   uv run python -m pa_sample_agent.slim_interface
   ```
3) Test (legacy path):
   ```bash
   AGNT_DOT_ENV=.env.dev \
   __PA_AGENT_SERVICES_ENDPOINT= \
   uv run python -m pa_sample_agent.slim_client "What time is it in New York?"
   ```

---

## Quick start (sidecar + A2A)
1) Ensure Agent Services is reachable (e.g., port-forward `svc/pattern-agentic-continuum` 8000:8000 and `svc/pa-slim-server` 46357:46357).
2) Run the agent (keep sidecar env set):
   ```bash
   AGNT_DOT_ENV=.env.dev \
   uv run python -m pa_sample_agent.slim_interface
   ```
3) Test A2A:
   ```bash
   AGNT_DOT_ENV=.env.dev \
   uv run python -m pa_sample_agent.slim_client --a2a "Hello"
   ```

---

## Config you’ll touch
- `.env.dev` (gitignored): API keys, `AGNT_SLIM_*`, optional `AGNT_SYSTEM_PROMPT`, `AGNT_ENABLE_LEGACY_HANDLER`.
- `mcp.json`: add/remove MCP tools.
- `agent_builder.py`: swap models or tweak LangChain setup.
- `slim_interface.py`: adjust handlers or system prompt selection logic.

---

## Troubleshooting
- `invalid_session_token`: you’re hitting a SLIM that expects session tokens (A2A) without a sidecar. Use the legacy path or bring up Agent Services.
- No response on legacy path: ensure `AGNT_ENABLE_LEGACY_HANDLER=true` and you’re running the client **without** `--a2a`.
- Connection refused: make sure the local SLIM Docker container is running and no port-forward is occupying 46357.

---

## Adapting for a new agent
1) Copy the repo to a new folder/name.
2) Update `.env.dev` with your keys and SLIM values.
3) Edit `mcp.json` to point at the tools your agent needs.
4) Adjust `agent_builder.py` / `agent.py` for custom behavior.
5) Choose a run mode (sidecar or sidecar-free) and follow the matching quick start.

That’s it—minimal glue, quick iteration, clear run modes. Enjoy. 
