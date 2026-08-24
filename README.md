# Pattern Agentic - Sample Agent

Sample Agent demonstrating best practices for use on the Pattern Agentic platform:

  - settings loaded from env variables or from dotenv files (with hot reload)
  - [SLIM](https://docs.agntcy.org/messaging/slim-core/) for communication
  - MCP tools loaded from configurable path 


## Code highlights

### Configuration

[config.py](pa_sample_agent/config.py)

Settings / secrets loaded from env variables or env files.

### Agent implementation

[agent.py](pa_sample_agent/agent.py)

Agent implementation, hiding most of the model / framework
implementation details.

### Agent builder

[agent_builder.py](pa_sample_agent/agent_builder.py)

Agent builder creates the agent using the config settings and chosen
agent framework (example: langchain).

### SLIM interface

[slim_interface.py](pa_sample_agent/slim_interface.py)

Exposes the agent using SLIM messages. 

## Installation

```bash
uv sync
```

## Configuration

Copy `env.example` to `.env.dev` and set `OPENROUTER_API_KEY` and the
various other parameters.

MCP tools are configured in `mcp.json`.

## Running

```bash
AGNT_DOT_ENV=.env.dev uv run python -m pa_sample_agent.slim_interface
```

NOTE: for development, it is possible to run a slim server locally. Set the slim endpoint to `http://localhost:46357` and run using docker, see [Slim howto](https://docs.agntcy.org/messaging/slim-howto/#using-docker):

```bash
cat << EOF > ./slim-config.yaml
# <slim config here>
EOF

docker run -it -v ./slim-config.yaml:/slim-config.yaml -p 46357:46357 \
    ghcr.io/agntcy/slim:0.7.1 /slim --config /slim-config.yaml
```

NB: the slim docker image tag is e.g. `0.7.1`, not `v0.7.1`

### Observability (optional)

SLIM ships native OpenTelemetry support for its own connection/session lifecycle
(separate from anything the agent itself does). It's off by default. To turn it
on, add this to `slim-config.yaml`'s `tracing` block:

```yaml
tracing:
  opentelemetry:
    enabled: true
    service_name: "slim-data-plane"
    service_version: "v0.1.0"
    grpc:
      endpoint: "http://otel-collector:4317"
      tls:
        insecure: true
```

Then run a collector to receive it — `telemetry/docker-compose.yml` stands up an
OTEL Collector pre-wired to export to Grafana Cloud:

```bash
cp telemetry/env.grafana.example telemetry/.env.grafana
# fill in GRAFANA_OTLP_INSTANCE_ID and GRAFANA_OTLP_TOKEN — see comments in the file
cd telemetry && docker compose up -d
```

Make sure the SLIM container and the collector are on the same docker network
(`docker network connect <network> slim-dev`, or run both via one compose file) —
SLIM's default collector endpoint (`localhost:4317`) does not resolve across
separate containers.

## Endpoints


### Inference

```bash
AGNT_DOT_ENV=.env.dev uv run python -m pa_sample_agent.slim_client "What time is it in New York?"


{"answer":"The current time in New York is 12:19 AM on Friday, November 14, 2025."}
```
