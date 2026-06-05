# Case Study 2

**Question ID:** 13  
**Document:** thesis_doc_02_multi_agent_workflow.docx  
**Category:** relationship reasoning  
**Difficulty:** hard

## Question

How is the Critic Agent connected to the Writer Agent in the workflow?

## Baseline (Naive RAG)

After the Writer Agent produces an answer, the Critic Agent evaluates its accuracy, relevance, completeness, and citation quality [1]. If the answer does not meet the threshold, the Critic Agent returns feedback and requests regeneration [1]. The Writer Agent then generates a revised answer based on that feedback [1]. This self-reflection loop is limited by a maximum number of iterations to prevent endless cycles [1].

---

**Sources:**

[1] thesis_doc_02_multi_agent_workflow.docx

## Agentic RAG (Proposed)

The Critic Agent is connected to the Writer Agent through a self-reflection loop. After the Writer Agent produces an answer, the Critic Agent evaluates its accuracy, relevance, completeness, and citation quality [1]. If the answer fails to meet the quality threshold, the Critic Agent returns feedback, and the Writer Agent generates a revised answer [1]. This regeneration loop is limited by a maximum number of iterations to prevent endless cycles [1].

---

**Sources:**

[1] thesis_doc_02_multi_agent_workflow.docx

## RAGAS (if available)

- Baseline faithfulness: N/A
- Agentic faithfulness: N/A

_Add Streamlit screenshots side-by-side in your thesis._