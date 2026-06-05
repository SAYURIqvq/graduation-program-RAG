# Thesis Experiment Guide

## Purpose

This guide explains how to reproduce the thesis benchmark evidence in this repository. The project uses controlled synthetic documents so that the evaluation is focused on the thesis topic: hierarchical multi-agent RAG, self-reflection, and graph-based reasoning.

## Main Data Files

| Item | Path |
|------|------|
| Controlled thesis corpus | `data/thesis_corpus/` |
| General benchmark dataset | `data/evaluation/thesis_multi_document_dataset.json` |
| Complex reasoning dataset | `data/evaluation/thesis_complex_reasoning_dataset.json` |
| General benchmark output | `results/thesis_multi_document/` |
| Complex benchmark output | `results/thesis_complex_reasoning/` |

The complex reasoning benchmark is the main experiment for the thesis. The general benchmark is a supporting comparison showing that baseline RAG remains competitive on simpler questions.

## Environment

Create `.env` from `.env.example` and set at least:

```bash
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_AUTH_TOKEN=your_deepseek_api_key
ANTHROPIC_MODEL=deepseek-chat
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
```

## Step 1: Rebuild the Controlled Corpus and Indexes

```bash
python scripts/build_thesis_complex_reasoning_benchmark.py
```

This script writes the four thesis DOCX files, the complex reasoning dataset, the ChromaDB thesis index, the BM25 thesis index, and the graph file used by the benchmark.

## Step 2: Run the General Benchmark

```bash
python evaluation/run_thesis_benchmark.py \
  --dataset data/evaluation/thesis_multi_document_dataset.json \
  --output results/thesis_multi_document \
  --persist-directory data/chroma_thesis_eval \
  --bm25-index data/bm25_thesis_eval.pkl \
  --graph-path data/graphs/thesis_multi_document_graph.pkl \
  --full-workflow \
  --critic-max-iterations 0 \
  --max-tokens 700 \
  --no-ragas
```

Expected output files:

| File | Purpose |
|------|---------|
| `answers.json` | Raw baseline and agentic answers |
| `experiment_table.csv` | Per-question metrics |
| `custom_metrics_summary.md` | Main summary table when RAGAS is skipped |
| `category_level_summary.md` | Category breakdown |
| `document_level_summary.md` | Document breakdown |
| `case_studies/` | Representative case study files |

## Step 3: Run the Complex Reasoning Benchmark

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

This is the main reported result for the thesis.

## Main Result to Report

From `results/thesis_complex_reasoning/custom_metrics_summary.md`:

| Metric | Baseline | Agentic | Delta |
|--------|----------|---------|-------|
| Thesis Complex Reasoning Score | 0.850 | 0.921 | +0.070 |
| Missing Information Accuracy | 0.833 | 1.000 | +0.167 |
| Multi-hop Coverage | 0.838 | 0.865 | +0.027 |
| Graph Reasoning Success | 0.882 | 0.923 | +0.041 |
| Average Latency | 13.92s | 70.05s | +56.13s |

## Optional RAGAS Scoring

RAGAS can be run by removing `--no-ragas` or using the benchmark runner's RAGAS resume mode. It is slower because each case requires judge model calls. For the final report, custom metrics are acceptable as the main result because they directly measure missing information handling, multi-hop coverage, and graph reasoning success.

## Recommended Thesis Discussion

The correct conclusion is not that agentic RAG is always better. The evidence supports this more precise conclusion:

Baseline RAG is fast and competitive for direct questions. The proposed hierarchical agentic RAG system has clearer advantages on complex reasoning, evidence validation, missing information handling, and graph-based relationship questions, but it has higher latency.
