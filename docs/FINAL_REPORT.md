# Final Project Report Summary

## Project Title

A Hierarchical Multi Agent Framework for Reliable RAG with Self Reflection and Graph Based Reasoning

## Current Implementation

The repository implements a document question answering system using a hierarchical multi-agent RAG pipeline. The user interface is built with Streamlit in `app.py`. The application supports PDF, DOCX, and TXT uploads, indexes documents with hierarchical chunks, stores vectors in ChromaDB, builds a BM25 keyword index, and constructs graph evidence for relationship-oriented queries.

The LLM backend is configured through an Anthropic-compatible API and is currently set up for DeepSeek. The default embedding backend is local SentenceTransformers using `BAAI/bge-large-en-v1.5`. Voyage AI remains optional and is only used if the embedding model is explicitly changed to a Voyage model.

## Main Components

| Component | Code path | Role |
|-----------|-----------|------|
| Streamlit app | `app.py` | Web interface, upload flow, chat, evaluation tab |
| Planner Agent | `src/agents/planner.py` | Query complexity scoring and strategy selection |
| Query Decomposer | `src/agents/query_decomposer.py` | Multi-hop and graph query decomposition |
| Retrieval Coordinator | `src/agents/retrieval_coordinator.py` | Runs vector, keyword, and graph retrieval agents |
| Vector Search | `src/retrieval/vector_search.py` | Semantic search over ChromaDB chunks |
| Keyword Search | `src/retrieval/keyword_search.py` | BM25 lexical retrieval |
| Graph Search | `src/retrieval/graph_search.py` | Relationship-based retrieval using knowledge graph evidence |
| Validator Agent | `src/agents/validator.py` | Checks retrieval sufficiency and can trigger retrieval retry |
| Synthesis Agent | `src/agents/synthesis.py` | Deduplicates and ranks retrieved chunks |
| Writer Agent | `src/agents/writer.py` | Generates grounded answers with citations |
| Critic Agent | `src/agents/critic.py` | Reviews answer quality and can request regeneration |
| Reliability Gate | `src/agents/reliability_gate.py` | Final grounding and citation check |
| Full workflow | `src/orchestration/complete_workflow.py` | LangGraph orchestration for the complete agentic pipeline |
| Baseline RAG | `src/baselines/naive_rag.py` | Vector-only baseline used for comparison |

## Evaluation Summary

The project contains two thesis benchmark tracks.

### General Benchmark

Path: `results/thesis_multi_document/custom_metrics_summary.md`

The general benchmark contains 32 questions over four controlled thesis documents. It shows that baseline RAG is competitive on simpler or direct questions.

| Metric | Baseline | Agentic | Delta |
|--------|----------|---------|-------|
| Ground Truth Keyword Coverage | 0.782 | 0.789 | +0.007 |
| Citation Rate | 0.938 | 0.938 | +0.000 |
| Citation-Based Context Usage | 0.578 | 0.375 | -0.203 |
| Average Latency | 10.28s | 55.60s | +45.32s |

Interpretation: the proposed workflow does not replace the baseline for every simple query. The baseline remains faster and competitive for direct retrieval tasks.

### Complex Reasoning Benchmark

Path: `results/thesis_complex_reasoning/custom_metrics_summary.md`

The complex benchmark contains 40 questions designed around multi-hop reasoning, graph dependency reasoning, evidence selection, missing information handling, self-reflection, and ablation explanation.

| Metric | Baseline | Agentic | Delta |
|--------|----------|---------|-------|
| Thesis Complex Reasoning Score | 0.850 | 0.921 | +0.070 |
| Ground Truth Keyword Coverage | 0.766 | 0.795 | +0.030 |
| Missing Information Accuracy | 0.833 | 1.000 | +0.167 |
| Multi-hop Coverage | 0.838 | 0.865 | +0.027 |
| Graph Reasoning Success | 0.882 | 0.923 | +0.041 |
| Citation Rate | 0.975 | 0.975 | +0.000 |
| Average Latency | 13.92s | 70.05s | +56.13s |

Interpretation: the proposed system shows its clearest value on complex reasoning and reliability-oriented tasks, especially missing information handling and graph reasoning. The tradeoff is substantially higher latency.

## Final Conclusion

The repository supports the thesis title. It implements a hierarchical multi-agent framework, includes self-reflection through validator and critic loops, uses graph-based reasoning through NetworkX and graph retrieval, and provides baseline versus proposed system results. The strongest academic claim should be stated carefully: the proposed workflow is most useful for complex reasoning and reliability-sensitive RAG, while the simpler baseline remains faster and competitive on direct fact retrieval.
