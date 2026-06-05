# Case Study 3

**Question ID:** 21  
**Document:** thesis_doc_04_evaluation_and_ablation_report.docx  
**Category:** evidence selection  
**Difficulty:** hard

## Question

Which ablation result best supports keeping the Reliability Gate in the proposed system?

## Baseline (Naive RAG)

The ablation result showing that removing the Reliability Gate increased unsupported final answers from 3 percent to 11 percent best supports keeping it [4]. This indicates the gate reduces unsupported answers by enforcing deterministic citation and context checks [1].

---

**Sources:**

[1] thesis_doc_04_evaluation_and_ablation_report.docx
[4] thesis_doc_04_evaluation_and_ablation_report.docx

## Agentic RAG (Proposed)

The ablation result showing that removing the Reliability Gate increased unsupported final answers from 3 percent to 11 percent best supports keeping it [1][5]. This indicates that the gate prevents deterministic citation and context checks from being bypassed, which would otherwise allow a substantial rise in unsupported outputs [2].

---

**Sources:**

[1] thesis_doc_04_evaluation_and_ablation_report.docx
[2] thesis_doc_04_evaluation_and_ablation_report.docx
[5] thesis_doc_04_evaluation_and_ablation_report.docx

## RAGAS (if available)

- Baseline faithfulness: N/A
- Agentic faithfulness: N/A

_Add Streamlit screenshots side-by-side in your thesis._