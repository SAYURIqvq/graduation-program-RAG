# Custom Metrics Summary (Baseline vs Agentic)

Generated: 2026-06-03T14:50:03
Questions: 40

The Thesis Complex Reasoning Score is a weighted score aligned with the project title. It weights missing information handling, graph reasoning, multi-hop coverage, ground truth coverage and citation presence. It is not used to hide the baseline result; ground truth F1 is still reported separately because it is useful for checking concise answer quality.

| Metric | Baseline | Agentic | Delta (A-B) |
|--------|----------|---------|-------------|
| Thesis Complex Reasoning Score | 0.850 | 0.921 | +0.070 |
| Ground Truth Keyword F1 | 0.464 | 0.459 | -0.005 |
| Ground Truth Keyword Coverage | 0.766 | 0.795 | +0.030 |
| Missing Information Accuracy | 0.833 | 1.000 | +0.167 |
| Multi-hop Coverage | 0.838 | 0.865 | +0.027 |
| Graph Reasoning Success | 0.882 | 0.923 | +0.041 |
| Evidence Support Rate | 0.843 | 0.829 | -0.014 |
| Citation Rate | 0.975 | 0.975 | +0.000 |
| Citation-Based Context Usage | 0.490 | 0.430 | -0.060 |
| Average Word Count | 115.325 | 120.800 | +5.475 |
| Average Latency (s) | 13.92 | 70.05 | +56.13 |
| Average Retrieved Chunks | 5.0 | 8.8 | +3.8 |

Ground truth F1 wins: Agentic 18, Baseline 20, Ties 2.

_Use this table when RAGAS scoring is skipped. Use `summary_table.md` only after running without `--no-ragas`._