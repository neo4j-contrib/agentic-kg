# Agentic Knowledge Graph Construction

This is a companion project to the [deeplearning.ai short course on agentic knowledge graph construction](https://learn.deeplearning.ai/courses/agentic-knowledge-graph-construction/).

The course is notebook-based, walking through the key concepts of building a multi-agent system. This project is that system.

Features:
- a multi-agent system for constructing knowledge graphs
- meant as a reference implementation for learning and experimentation, not a production tool
- built on top of [Google ADK](https://github.com/google/agent-driver-kit)
- interacts with a local Neo4j database
- rich with opportunities for improvement :)

## Setup

These steps assume you have `uv` installed and Python 3.12 available.

- Install uv: see [uv getting started](https://docs.astral.sh/uv/getting-started/installation/)

### 1) Initialize the project

- Create a virtual environment and install dependencies with uv:

```
uv venv
uv sync
```

### 2) Set up environment variables

- Copy `.env.example` to `.env` and adjust as needed
- `OPENAI_API_KEY=sk-...` (optional)
- `NEO4J_DSN=bolt://neo4j:secret@localhost:7687/neo4j`

### 3) Make CSV files available for import

The local Neo4j database must have access to files in the `import` directory. If you're unsure where that is,
you can run the `multi_agent` and ask it "Where is the import directory?" Copy the sample files there.

There are some example data files under `data`.

## Run the agentic system

Google ADK include a great devtool that can launch a web interface for the agent.

```
adk web src/agentic_kg/coordinators/
```

This will discover the available "coordinators" or top-level agents. There are two:

1. `single_agent` - uses a single sub-agent that can interace with Neo4j directly
2. `multi_agent` - has a hiearchy of specialized sub-agents to collaborate with a user through multiple phases
  - this coordinator can answer basic questions about the environment, like "Is Neo4j ready?" and "Where is the import directory?"
  - `user_intent_agent` - ideates on the kind of graph and purpose of the graph
  - `file_suggestion_agent` - recommends files to use as input
  - `schema_proposal_agent` - proposes a construction plan for making a graph from the files which supports the user goal
  - `graph_construction_agent` - does the work of building the graph


## Testing

There are minimal pytests available.

### 1) Run unit tests

- Unit tests (fast, no Docker required):

```
uv run pytest -q
```

### 2) Run integration tests

- Integration tests (Neo4j via Testcontainers; requires Docker running):

```
uv run pytest -q -m integration
```

## Differences from the deeplearning course

- many agents use a special `finished` tool to signal that they're done

## TODO

- [ ] add the unstructured data import workflow
- [ ] evals! evals! evals!
- [ ] add multiple GraphRAG tools
- [ ] add handling of field types
- [ ] improve `llm_catalog` model selection
- [ ] add hypothetical questions to user goal, which should be used to validate the constructed graph and guide GraphRAG retrievers


## Special Thanks

Special thanks to everyone who worked on the deeplearning course and helped develop and inspire this project.

Particular shout-outs to:
- [Hawraa Salami of deeplearning.ai](https://www.linkedin.com/in/hawraa-salami/) for her guidance and support in developing the course
- [Andrew Ng of deeplearning.ai](https://www.linkedin.com/in/andrewyng/) for raising everyone's game with Deeplearning.ai
- [Adam Cowley of Neo4j](https://www.linkedin.com/in/adamcowley/) for his inspiring work on [GraphAcademy](https://graphacademy.neo4j.com/)
- [Martin O'Hanlon](https://www.linkedin.com/in/martinohanlon/) for his clear, methodical and friendly approach to teaching
- [Neo4j](https://neo4j.com/) for letting me work on this project :)
