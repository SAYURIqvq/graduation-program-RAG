# RAGAS Status for Thesis Multi Document Benchmark

The full 32 question benchmark was completed for both baseline and proposed agentic RAG answers. RAGAS scoring is not included as the primary result for this run because local full-system RAGAS evaluation was too slow and unstable in the current environment.

Primary thesis result files:

- `answers.json`
- `experiment_table.csv`
- `custom_metrics_summary.md`
- `document_level_summary.md`
- `category_level_summary.md`
- `case_studies/`

Supplementary RAGAS evidence remains available in `docs/RAGAS_EVALUATION_REPORT.md`, where the WriterAgent and reliability gate were validated on controlled RAGAS cases.

For the report, use the multi document benchmark as the main full-system comparison and use the RAGAS report as supplementary validation evidence.
