# Documentation Index

This directory contains the documentation for the current graduation project repository.
The current implementation is a Streamlit based Agentic RAG system with hierarchical multi-agent orchestration, self-reflection, hybrid retrieval, and graph-based reasoning.

## Current Submission Documents

Use these files as the main technical references:

| File | Purpose |
|------|---------|
| `THESIS_ARCHITECTURE.md` | Thesis-oriented architecture description |
| `AGENT_ARCHITECTURE.md` | Agent roles and state flow |
| `WORKFLOW_ARCHITECTURE.md` | LangGraph workflow description |
| `THESIS_EXPERIMENT_GUIDE.md` | How to reproduce thesis benchmarks |
| `FINAL_REPORT.md` | Current implementation and result summary |
| `RAGAS_EVALUATION_REPORT.md` | RAGAS and custom evaluation explanation |
| `ABLATION_REPORT.md` | Component and ablation evidence |
| `USER_GUIDE.md` | How to run and use the Streamlit app |

## Current Code Facts

| Item | Current implementation |
|------|------------------------|
| Main app file | `app.py` |
| UI framework | Streamlit |
| LLM backend | DeepSeek through Anthropic-compatible API |
| Required LLM env vars | `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL` |
| Default embedding model | `BAAI/bge-large-en-v1.5` through SentenceTransformers |
| Optional embedding backend | Voyage AI, only when `EMBEDDING_MODEL` is set to a Voyage model |
| Vector store | ChromaDB |
| Keyword retrieval | BM25 with `rank-bm25` |
| Graph reasoning | NetworkX knowledge graph |
| Full workflow | `src/orchestration/complete_workflow.py` |
| Baseline | `src/baselines/naive_rag.py` |
| Thesis benchmark runner | `evaluation/run_thesis_benchmark.py` |

## Experimental Evidence

| Evidence | Path |
|----------|------|
| General benchmark dataset | `data/evaluation/thesis_multi_document_dataset.json` |
| Complex reasoning dataset | `data/evaluation/thesis_complex_reasoning_dataset.json` |
| General benchmark results | `results/thesis_multi_document/` |
| Complex reasoning results | `results/thesis_complex_reasoning/` |
| Controlled thesis documents | `data/thesis_corpus/` |
| Case studies | `results/thesis_complex_reasoning/case_studies/` |

