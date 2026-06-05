# Case Study 1

**Question ID:** 5  
**Document:** thesis_doc_01_rag_system_design.docx  
**Category:** relationship reasoning  
**Difficulty:** hard

## Question

How does the reliability gate relate citations to retrieved chunks?

## Baseline (Naive RAG)

The reliability gate checks whether citation numbers in the answer refer to available chunks and whether retrieved context exists [1]. If these checks fail but context is still available, the system can fall back to a deterministic evidence summary [1].

---

**Sources:**

[1] thesis_doc_01_rag_system_design.docx

## Agentic RAG (Proposed)

The reliability gate verifies that citation numbers in the answer refer to available chunks and checks that retrieved context exists [1].

---

**Sources:**

[1] thesis_doc_01_rag_system_design.docx

## RAGAS (if available)

- Baseline faithfulness: N/A
- Agentic faithfulness: N/A

_Add Streamlit screenshots side-by-side in your thesis._