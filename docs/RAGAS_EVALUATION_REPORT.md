# RAGAS and Evaluation Report

## Purpose

This document explains the evaluation setup used by the project. The repository supports both RAGAS scoring and custom thesis metrics. The custom metrics are the main reported results because full RAGAS runs are slower and less stable for repeated local benchmarking.

## Current Evaluation Stack

| Component | Current implementation |
|-----------|------------------------|
| Benchmark runner | `evaluation/run_thesis_benchmark.py` |
| RAGAS evaluator | `src/evaluation/ragas_evaluator.py` |
| LLM judge | DeepSeek through Anthropic-compatible `ChatAnthropic` |
| Embeddings for RAGAS | BGE-large through SentenceTransformers |
| Baseline system | `src/baselines/naive_rag.py` |
| Proposed system | `CompleteAgenticRAGWorkflow` |

Older provider-specific evaluation notes are no longer the current configuration. The current evaluator overrides RAGAS defaults with the project LLM and BGE embeddings.

## Metrics

RAGAS metrics supported by `RAGASEvaluator`:

| Metric | Meaning |
|--------|---------|
| `answer_relevancy` | Whether the answer addresses the question |
| `faithfulness` | Whether the answer is grounded in the retrieved context |
| `context_precision` | Whether retrieved contexts are useful |
| `context_recall` | Whether retrieved contexts cover the reference answer |
| `overall` | Average of the four metrics above |

Custom thesis metrics written by `run_thesis_benchmark.py`:

| Metric | Meaning |
|--------|---------|
| Ground Truth Keyword Coverage | Coverage of reference answer terms |
| Ground Truth Keyword F1 | Balance between coverage and precision |
| Citation Rate | Whether the answer contains citations |
| Citation-Based Context Usage | Whether citations point to retrieved contexts |
| Missing Information Accuracy | Whether missing information questions are answered honestly |
| Multi-hop Coverage | Whether answers cover required multi-hop terms |
| Graph Reasoning Success | Whether graph relationship terms are connected correctly |
| Evidence Support Rate | Whether required evidence terms appear in the answer |
| Latency | End-to-end answer time |

## Main Result Files

| Output | Path |
|--------|------|
| General benchmark answers | `results/thesis_multi_document/answers.json` |
| General benchmark summary | `results/thesis_multi_document/custom_metrics_summary.md` |
| Complex benchmark answers | `results/thesis_complex_reasoning/answers.json` |
| Complex benchmark summary | `results/thesis_complex_reasoning/custom_metrics_summary.md` |
| Category summary | `results/thesis_complex_reasoning/category_level_summary.md` |
| Document summary | `results/thesis_complex_reasoning/document_level_summary.md` |
| Case studies | `results/thesis_complex_reasoning/case_studies/` |

## Reproduction Command

```bash
python evaluation/run_thesis_benchmark.py \
  --dataset data/evaluation/thesis_complex_reasoning_dataset.json \
  --output results/thesis_complex_reasoning \
  --persist-directory data/chroma_thesis_eval \
  --bm25-index data/bm25_thesis_eval.pkl \
  --graph-path data/graphs/thesis_multi_document_graph.pkl \
  --full-workflow \
  --critic-max-iterations 0 \
  --max-tokens 700 \
  --no-ragas
```

To run RAGAS, remove `--no-ragas` or use the benchmark runner's RAGAS resume option on existing answers. RAGAS requires a valid `ANTHROPIC_AUTH_TOKEN`.

## Interpretation

RAGAS is useful as an external faithfulness and relevancy check. The thesis also needs custom metrics because the project title focuses on missing information handling, graph reasoning, and multi-hop coverage, which are not fully explained by the standard RAGAS metrics alone.
