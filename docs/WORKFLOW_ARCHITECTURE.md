# Workflow Architecture

## Overview

The project contains two LangGraph workflows.

| Workflow | Code path | Purpose |
|----------|-----------|---------|
| `AgenticRAGWorkflow` | `src/orchestration/langgraph_workflow.py` | Earlier planner, retrieval, validator workflow |
| `CompleteAgenticRAGWorkflow` | `src/orchestration/complete_workflow.py` | Full thesis workflow used for the proposed model |

The full workflow is the important one for the thesis benchmark.

## Complete Workflow

```text
START
  -> Planner
  -> Query Decomposer
  -> Retrieval Coordinator
  -> Validator
       if weak evidence: retry retrieval
       else: continue
  -> Synthesis
  -> Writer
  -> Critic
       if low quality and iterations remain: regenerate answer
       else: finish
END
```

## Agent Roles

| Step | Agent | Responsibility |
|------|-------|----------------|
| 1 | Planner | Scores query complexity and selects simple, multihop, or graph strategy |
| 2 | Query Decomposer | Creates sub-queries for complex or graph questions |
| 3 | Retrieval Coordinator | Runs vector, BM25 keyword, and graph retrieval agents |
| 4 | Validator | Checks whether evidence is relevant and sufficient |
| 5 | Synthesis | Deduplicates and ranks retrieved chunks |
| 6 | Writer | Produces a grounded answer with citations |
| 7 | Critic | Reviews answer quality and may request regeneration |
| 8 | Reliability Gate | Final grounding and citation check used by the application layer |

## Retrieval Channels

| Channel | Code path | Function |
|---------|-----------|----------|
| Vector | `src/retrieval/vector_search.py` | Semantic retrieval from ChromaDB |
| Keyword | `src/retrieval/keyword_search.py` | BM25 exact lexical retrieval |
| Graph | `src/retrieval/graph_search.py` | Relationship retrieval through NetworkX graph evidence |

## Retry and Reflection

The system has two reliability loops:

| Loop | Trigger | Result |
|------|---------|--------|
| Validator loop | Retrieved evidence is weak | Run retrieval again, up to the configured retry limit |
| Critic loop | Generated answer has low quality | Regenerate the answer with critic feedback, up to the configured iteration limit |

In the thesis benchmark command, `--critic-max-iterations 0` may be used to reduce runtime. The application can use the full configured critic loop.
