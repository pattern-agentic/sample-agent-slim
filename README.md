# Pattern Agentic - Sample Agent

Sample Agent demonstrating best practices for use on the Pattern Agentic platform:

  - settings loaded from env variables
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

## Endpoints


### Inference

```bash
AGNT_DOT_ENV=.env.dev uv run python -m pa_sample_agent.slim_client "What time is it in New York?"


{"answer":"The current time in New York is 12:19 AM on Friday, November 14, 2025."}
```
