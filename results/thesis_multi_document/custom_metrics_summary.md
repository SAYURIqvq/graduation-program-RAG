# Custom Metrics Summary (Baseline vs Agentic)

Generated: 2026-06-03T00:37:15
Questions: 32

| Metric | Baseline | Agentic | Delta (A-B) |
|--------|----------|---------|-------------|
| Ground Truth Keyword Coverage | 0.782 | 0.789 | +0.007 |
| Citation Rate | 0.938 | 0.938 | +0.000 |
| Citation-Based Context Usage | 0.578 | 0.375 | -0.203 |
| Average Word Count | 50.906 | 51.594 | +0.688 |
| Average Latency (s) | 10.28 | 55.60 | +45.32 |
| Average Retrieved Chunks | 2.0 | 3.0 | +1.0 |

Ground truth coverage wins: Agentic 9, Baseline 6, Ties 17.

_Use this table when RAGAS scoring is skipped. Use `summary_table.md` only after running without `--no-ragas`._