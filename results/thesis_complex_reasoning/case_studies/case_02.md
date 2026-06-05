# Case Study 2

**Question ID:** 13  
**Document:** thesis_doc_03_graph_reasoning_case_study.docx  
**Category:** graph dependency reasoning  
**Difficulty:** hard

## Question

Trace the dependency path from Orion Service to Compliance Review in the incident.

## Baseline (Naive RAG)

The dependency path from Orion Service to Compliance Review is Orion Service → Billing API → Cache Layer → Search Index → Audit Dashboard → Compliance Review [1][3][4]. Orion Service publishes invoice events to the Billing API, which writes normalized records into the Cache Layer; the Search Index reads from the Cache Layer, the Audit Dashboard displays the Search Index’s status, and Compliance Review uses that dashboard as evidence [1][2][3]. A failure in the Cache Layer can affect Compliance Review even if both the dashboard and the review process are healthy [4].

---

**Sources:**

[1] thesis_doc_03_graph_reasoning_case_study.docx
[2] thesis_doc_03_graph_reasoning_case_study.docx
[3] thesis_doc_03_graph_reasoning_case_study.docx
[4] thesis_doc_03_graph_reasoning_case_study.docx

## Agentic RAG (Proposed)

The dependency path from Orion Service to Compliance Review is: Orion Service → Billing API → Cache Layer → Search Index → Audit Dashboard → Compliance Review [1][2][5].  
The relationship direction is crucial: Compliance Review depends on Audit Dashboard, Audit Dashboard depends on Search Index, Search Index depends on Cache Layer, Cache Layer depends on Billing API, and Billing API depends on Orion Service [1][5].

---

**Sources:**

[1] thesis_doc_03_graph_reasoning_case_study.docx
[2] thesis_doc_03_graph_reasoning_case_study.docx
[5] thesis_doc_03_graph_reasoning_case_study.docx

## RAGAS (if available)

- Baseline faithfulness: N/A
- Agentic faithfulness: N/A

_Add Streamlit screenshots side-by-side in your thesis._