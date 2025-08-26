# agentic_kg

A minimal project scaffold for an agent using Google ADK.

## Developer

These steps assume you have `uv` installed and Python 3.12 available.

- Install uv: see `https://docs.astral.sh/uv/getting-started/installation/`

### 1) Initialize the project

- Create a virtual environment and install dependencies with uv:

```
uv sync
```

- Environment variables:
  - Copy `.env.example` to `.env` and adjust as needed.
  - Key values (examples):
    - `OPENAI_API_KEY=sk-...` (optional)
    - `NEO4J_DSN=bolt://neo4j:secret@localhost:7687/neo4j`
    - `LOGLEVEL=INFO`

### 2) Run tests

- Unit tests (fast, no Docker required):

```
uv run pytest -q
```

- Integration tests (Neo4j via Testcontainers; requires Docker running):

```
uv run pytest -q -m integration
```

- Run everything (override default marker filter):

```
uv run pytest -q -m "integration or not integration"
```

### 3) Launch the agent with Google ADK

There are two supported ways:

- Using the ADK CLI to run the agent folder directly (recommended for interactive dev):

```
uv run adk run src/agentic_kg/agents/user_intent_agent
```

This will discover `root_agent` from `src/agentic_kg/agents/user_intent_agent/agent.py`.

- Using the package entrypoint (if you expose a `main()` that returns an agent instance):

```
uv run python -c "from agentic_kg.agent import main; agent = main(); print(f'Loaded agent: {agent.name}')"
```

### Notes on imports and side-effects

- Importing `agentic_kg` is side-effect free. Initialization occurs only when invoking `agentic_kg.agent.main()` or when the ADK CLI imports the specific agent module.
- Configuration is loaded via Pydantic Settings (`agentic_kg.common.config.agentic_kgSettings`) which reads `.env` automatically. Logging level is applied on first `get_settings()` call.

### Differences from the deeplearning course

- context state values have a "status" field to indicate "draft", "proposal", "approved", "rejected". In the course notebooks, these states were separate keys for each value. For example, the course used "perceived_user_goal" and "approved_user_goal" keys, which have been combined into a single "user_intent" key with a "status" field.
