# Ablation and Component Evidence

## Purpose

This document summarises the component evidence available in the repository. It should be read together with the benchmark outputs under `results/`.

## Available Evidence Files

| File | Purpose |
|------|---------|
| `data/ablation_results.json` | Early component comparison data for baseline, hierarchical, hybrid, and graph retrieval |
| `results/thesis_complex_reasoning/custom_metrics_summary.md` | Main complex reasoning comparison between baseline and proposed workflow |
| `results/thesis_complex_reasoning/category_level_summary.md` | Category-level breakdown |
| `results/thesis_complex_reasoning/case_studies/` | Representative case studies |
| `data/evaluation/thesis_complex_reasoning_dataset.json` | Stress benchmark used for the main thesis comparison |

## Current Interpretation

The early ablation file shows that the graph retrieval component is selective: it returns useful evidence for relationship-oriented questions, but it may return no chunks when a query does not contain enough graph entities. This matches the thesis discussion that graph search is not a universal replacement for vector retrieval.

The main complex benchmark gives the clearest component-level evidence for the final system:

| Metric | Baseline | Agentic | Delta |
|--------|----------|---------|-------|
| Thesis Complex Reasoning Score | 0.850 | 0.921 | +0.070 |
| Missing Information Accuracy | 0.833 | 1.000 | +0.167 |
| Multi-hop Coverage | 0.838 | 0.865 | +0.027 |
| Graph Reasoning Success | 0.882 | 0.923 | +0.041 |
| Average Latency | 13.92s | 70.05s | +56.13s |

## Academic Claim Supported

The evidence supports a careful claim: the proposed hierarchical agentic RAG system improves reliability-oriented behaviour on complex reasoning tasks, especially missing information handling and graph relationship reasoning, but it is slower than the baseline and should not be presented as always better for simple direct questions.

## Limitations

The ablation evidence is controlled and project-specific. It is suitable for a graduation project report, but it should not be described as a large public benchmark. The benchmark documents are synthetic controlled documents designed to test the target capabilities of this system.
