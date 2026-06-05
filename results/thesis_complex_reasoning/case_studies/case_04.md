# Case Study 4

**Question ID:** 25  
**Document:** thesis_doc_04_evaluation_and_ablation_report.docx  
**Category:** evaluation and ablation explanation  
**Difficulty:** hard

## Question

How should the latency cost be interpreted in high reliability and low risk settings?

## Baseline (Naive RAG)

In high reliability settings, the additional latency is acceptable when the question needs evidence validation or multi-hop reasoning [1][3]. In low risk direct lookup settings, the latency is unnecessary and a baseline route may be preferable [1][2][3]. The latency cost should be reported as a limitation rather than hidden [3].

---

**Sources:**

[1] thesis_doc_04_evaluation_and_ablation_report.docx
[2] thesis_doc_04_evaluation_and_ablation_report.docx
[3] thesis_doc_04_evaluation_and_ablation_report.docx

## Agentic RAG (Proposed)

The latency cost is a limitation of the proposed system and should be reported as a limitation rather than hidden [1][2].  
In high reliability settings, the additional latency is acceptable when the question needs evidence validation or multi hop reasoning [2].  
In low risk direct lookup settings, a baseline route may be preferable, and the latency is considered unnecessary [1][2].

---

**Sources:**

[1] thesis_doc_04_evaluation_and_ablation_report.docx
[2] thesis_doc_04_evaluation_and_ablation_report.docx

## RAGAS (if available)

- Baseline faithfulness: N/A
- Agentic faithfulness: N/A

_Add Streamlit screenshots side-by-side in your thesis._