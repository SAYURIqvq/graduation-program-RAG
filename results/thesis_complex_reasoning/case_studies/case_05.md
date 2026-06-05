# Case Study 5

**Question ID:** 30  
**Document:** thesis_doc_03_graph_reasoning_case_study.docx  
**Category:** graph dependency reasoning  
**Difficulty:** hard

## Question

How does the field mismatch move through records, indexing, dashboard status and compliance review?

## Baseline (Naive RAG)

The field mismatch begins because the Billing API uses the new field `invoice_state` while the Cache Layer expects `status_code`, causing records to be stored without a searchable status value [1]. These incomplete records then enter the Search Index [1]. The Audit Dashboard shows a pending review status because it displays the indexed state rather than the original Billing API payload [1]. Compliance Review, which depends on the Audit Dashboard for month‑end evidence, is consequently affected by the upstream mismatch even when the dashboard and review process themselves are healthy [3][5]. The dependency chain moves from Cache Layer → Search Index → Audit Dashboard → Compliance Review [4].

---

**Sources:**

[1] thesis_doc_03_graph_reasoning_case_study.docx
[3] thesis_doc_03_graph_reasoning_case_study.docx
[4] thesis_doc_03_graph_reasoning_case_study.docx
[5] thesis_doc_03_graph_reasoning_case_study.docx

## Agentic RAG (Proposed)

The field mismatch originates from the schema migration introducing the field `invoice_state` while the Cache Layer still expected the older field `status_code` [1][4]. Because the Cache Layer did not receive the expected field, records were stored without a searchable status value [1][4]. The Search Index then indexed these incomplete records [1][2]. The Audit Dashboard displayed these invoices as "pending review" because it reflected the indexed state rather than the original Billing API payloads [1][2]. Compliance Review depends on the Audit Dashboard for month-end evidence, so the downstream effect reached the review process despite the dashboard and review process themselves being healthy [1].

---

**Sources:**

[1] thesis_doc_03_graph_reasoning_case_study.docx
[2] thesis_doc_03_graph_reasoning_case_study.docx
[4] thesis_doc_03_graph_reasoning_case_study.docx

## RAGAS (if available)

- Baseline faithfulness: N/A
- Agentic faithfulness: N/A

_Add Streamlit screenshots side-by-side in your thesis._