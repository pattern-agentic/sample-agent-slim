Local dev without Agent Services
===============================

What changed
- Allow reading `AGNT_SLIM_LOCAL_NAME`, `AGNT_SLIM_ENDPOINT`, `AGNT_SLIM_AUTH_SECRET` directly (no sidecar required).
- Optional `AGNT_SYSTEM_PROMPT` for local runs.
- Optional legacy handler (`type: "question"`) for sidecar-free/unauthenticated SLIM; gated by `AGNT_ENABLE_LEGACY_HANDLER=true`.

How to run locally (no sidecar, no session tokens)
1) Run a local SLIM node (no auth), e.g.:
   ```
   cat > slim-config.yaml <<'EOF'
   services:
     slim/0:
       dataplane:
         servers:
           - endpoint: "0.0.0.0:46357"
             auth:
               type: none
             tls:
               insecure: true
         clients: []
   EOF
   docker run --rm -it \
     -v $(pwd)/slim-config.yaml:/config.yaml \
     -p 46357:46357 \
     ghcr.io/agntcy/slim:1.0.0 \
     /slim --config /config.yaml
   ```
2) Start the agent:
   ```
   AGNT_DOT_ENV=.env.dev \
   __PA_AGENT_SERVICES_ENDPOINT= \
   AGNT_ENABLE_LEGACY_HANDLER=true \
   uv run python -m pa_sample_agent.slim_interface
   ```
3) Send a legacy request (no session token needed):
   ```
   AGNT_DOT_ENV=.env.dev \
   __PA_AGENT_SERVICES_ENDPOINT= \
   uv run python -m pa_sample_agent.slim_client "Hello"
   ```
   For A2A, you still need the sidecar/session token.

Sidecar issue observed
- Cluster Agent Services (pattern-agentic-continuum) is misconfigured: logs show missing `database_host` and `redis_url`, so `/mint-agent-token` fails. That’s why A2A against the cluster SLIM was rejected for missing session token.

Notes
- Keep prompts in `.env.dev` (gitignored). Do not commit keys/secrets.
- `AGNT_ENABLE_LEGACY_HANDLER` should remain `false` in prod; only enable for local dev.
