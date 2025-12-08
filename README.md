# Pattern Agentic - Sample Agent

Sample Agent demonstrating best practices for use on the Pattern Agentic platform:

  - settings loaded from env variables
  - [SLIM](https://docs.agntcy.org/messaging/slim-core/) for communication via the [AGNTCY app-sdk](https://github.com/agntcy/app-sdk)
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

Exposes the agent using SLIM messages via `agntcy-app-sdk` SLIM transport. 

## Installation

```bash
uv sync
```

## Configuration

Copy `env.example` to `.env.dev` and set `OPENROUTER_API_KEY` and the
various other parameters.

MCP tools are configured in `mcp.json`.

## Running

Start a SLIM gateway (see [app-sdk README](../README.md) for local docker-compose or your own gateway).

```bash
AGNT_DOT_ENV=.env.dev uv run python -m pa_sample_agent.slim_interface
```

In another terminal, send a question:

```bash
AGNT_DOT_ENV=.env.dev uv run python -m pa_sample_agent.slim_client "What time is it in New York?"
```
