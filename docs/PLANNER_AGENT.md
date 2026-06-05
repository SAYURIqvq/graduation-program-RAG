# Planner Agent

## Overview

The Planner Agent is the strategic Level 1 agent. It analyses the user query, estimates complexity, and selects an execution strategy.

Code path: `src/agents/planner.py`

## Strategy Mapping

| Strategy | Condition | Typical use |
|----------|-----------|-------------|
| `simple` | Complexity below `planner_complexity_threshold_simple` | Direct factual questions |
| `multihop` | Between simple and graph thresholds | Comparison, synthesis, multi-part questions |
| `graph` | Complexity above `planner_complexity_threshold_multihop` or relationship-heavy query | Entity relationship and dependency questions |

Default thresholds are configured in `src/config.py`:

```text
PLANNER_COMPLEXITY_THRESHOLD_SIMPLE=0.3
PLANNER_COMPLEXITY_THRESHOLD_MULTIHOP=0.7
```

## LLM Backend

The project uses `create_chat_model` through the backward-compatible alias `create_chat_model`. Despite the legacy function name, the current backend is DeepSeek through an Anthropic-compatible API.

```python
from src.config import get_settings
from src.llm.chat_model import create_chat_model
from src.agents.planner import PlannerAgent
from src.models.agent_state import AgentState

settings = get_settings()
llm = create_chat_model(settings)
planner = PlannerAgent(llm=llm)

state = AgentState(query="How does the validator affect answer reliability?")
result = planner.run(state)
print(result.complexity)
print(result.strategy)
```

## Role in the Full Workflow

The planner does not answer the question directly. It prepares the route for later agents. In the complete workflow, its output is consumed by the Query Decomposer and Retrieval Coordinator.
