# Agent Architecture

## Overview

The system uses a hierarchical multi-agent architecture. Agents communicate through the shared `AgentState` model in `src/models/agent_state.py` and inherit common execution behaviour from `BaseAgent` in `src/agents/base_agent.py`.

## Hierarchy

```text
Level 1: Strategic
  Planner Agent

Level 2: Tactical
  Query Decomposer
  Retrieval Coordinator
  Validator Agent
  Synthesis Agent
  Writer Agent
  Critic Agent
  Reliability Gate

Level 3: Operational Retrieval
  Vector Search Agent
  Keyword Search Agent
  Graph Search Agent
```

## Shared State

Important `AgentState` fields:

| Field | Purpose |
|-------|---------|
| `query` | Original user query |
| `complexity` | Planner complexity score |
| `strategy` | `simple`, `multihop`, or `graph` |
| `sub_queries` | Decomposed questions |
| `chunks` | Retrieved evidence chunks |
| `retrieval_round` | Number of retrieval attempts |
| `validation_status` | Validator decision |
| `validation_score` | Validator score |
| `answer` | Generated answer |
| `citations` | Citation identifiers |
| `critic_score` | Critic quality score |
| `critic_feedback` | Feedback for regeneration |
| `metadata` | Trace and component metadata |

## BaseAgent Pattern

Each agent implements `execute(state)` and should be called through `run(state)` so timing, logging, and error wrapping are recorded.

```python
class MyAgent(BaseAgent):
    def execute(self, state: AgentState) -> AgentState:
        state.metadata["my_agent"] = {"status": "done"}
        return state
```

## Production Retrieval Agents

Use the production retrieval agents under `src/retrieval/` for application and benchmark work:

| Agent | Path |
|-------|------|
| Vector search | `src/retrieval/vector_search.py` |
| Keyword search | `src/retrieval/keyword_search.py` |
| Graph search | `src/retrieval/graph_search.py` |

The files under `src/agents/retrieval/` are legacy test-oriented agents and should not be described as the main production retrieval path.

## Reliability Design

The reliability design comes from three checks:

1. The validator checks whether retrieved evidence is relevant and sufficient.
2. The critic checks whether the written answer is accurate, complete, cited, clear, and relevant.
3. The reliability gate checks citation and grounding before the final answer is shown.

This structure matches the thesis claim of self-reflection and reliable RAG.
