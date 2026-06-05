# Case Study 3

**Question ID:** 21  
**Document:** thesis_doc_03_graph_reasoning_case_study.docx  
**Category:** relationship reasoning  
**Difficulty:** hard

## Question

How does the Billing API affect the Audit Dashboard through the Cache Layer and Search Index?

## Baseline (Naive RAG)

The Billing API writes normalized invoice records into the Cache Layer [2]. After a schema migration, the Billing API accepted the new invoice_state field, but the Cache Layer still expected the older status_code field, resulting in records being stored without a searchable status value [2]. The Search Index then reads from the Cache Layer and consequently indexed these incomplete records [2]. Because the Audit Dashboard displays invoice status using data from the Search Index, it showed the affected invoices as “pending review” [2]. Thus, the mismatch introduced by the Billing API propagated through the Cache Layer and Search Index to produce an incorrect display on the Audit Dashboard [2][1].

---

**Sources:**

[1] thesis_doc_03_graph_reasoning_case_study.docx
[2] thesis_doc_03_graph_reasoning_case_study.docx

## Agentic RAG (Proposed)

The Billing API writes normalised invoice records into the Cache Layer [1]. The Search Index reads from the Cache Layer every fifteen minutes, and the Audit Dashboard then displays invoice status using data from the Search Index [1]. During the incident, the Billing API accepted the new `invoice_state` field from the schema migration, but the Cache Layer still expected the `status_code` field, so records were stored without a searchable status value [1]. Because the Search Index subsequently indexed these incomplete records, the Audit Dashboard showed invoices as "pending review" [1]. This chain means that a mismatch between the Billing API and the Cache Layer can propagate through the Search Index and affect what the Audit Dashboard displays, even when the dashboard itself is healthy [1].

---

**Sources:**

[1] thesis_doc_03_graph_reasoning_case_study.docx

## RAGAS (if available)

- Baseline faithfulness: N/A
- Agentic faithfulness: N/A

_Add Streamlit screenshots side-by-side in your thesis._