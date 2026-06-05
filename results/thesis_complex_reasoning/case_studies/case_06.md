# Case Study 6

**Question ID:** 32  
**Document:** thesis_doc_04_evaluation_and_ablation_report.docx  
**Category:** evaluation and ablation explanation  
**Difficulty:** hard

## Question

Why is the complex benchmark not evidence that agentic RAG should replace baseline RAG for every query?

## Baseline (Naive RAG)

[{'signature': '31f876ad-dc8e-4f41-8ede-5b5882d82d8e', 'thinking': 'We are asked: "Why is the complex benchmark not evidence that agentic RAG should replace baseline RAG for every query?" We need to answer strictly from context.\n\nLet\'s scan the context for relevant statements. In [1] and [2], we see: "The report does not claim that agentic RAG is always better than baseline RAG. For simple factual questions, baseline can be faster and sufficient. The proposed system is most useful when the question requires citations, comparison, missing information handling, relationship reasoning or quality control." And "The benchmark is a controlled document benchmark, not a large public leaderboard. The number of documents is small, but the documents are selected to cover different reasoning needs." Also [2]: "The main interpretation is that baseline RAG is competitive for simple fact extraction, but hierarchical agentic RAG is stronger on complex reasoning and reliability oriented tasks." Also [5]: "It is not designed to prove that agentic RAG is better for every query. It is designed to test the type of reliability oriented tasks that motivate a hierarchical multi agent framework."\n\nSo the reasons are: the benchmark targets reliability-oriented, complex tasks; simple factual queries are better served by baseline RAG which is faster; the benchmark is controlled, small, not representative of all query types; agentic RAG incurs latency and is overkill for simple lookups. We\'ll cite [1][2][5] appropriately.\n\nAnswer: The benchmark is not evidence that agentic RAG should replace baseline RAG for every query because it was specifically designed to test reliability-oriented, complex reasoning tasks, not all query types [5]. Baseline RAG remains competitive and sufficient for simple factual questions where speed is important [1][2]. The benchmark is a controlled, small-scale document set rather than a large public leaderboard, so it does not demonstrate superiority across all scenarios [1]. Additionally, the proposed system introduces higher latency, making it less suitable for low-risk direct lookups where baseline routes are preferable [2][5].', 'type': 'thinking'}]

---

**Sources:**

[1] thesis_doc_04_evaluation_and_ablation_report.docx
[2] thesis_doc_04_evaluation_and_ablation_report.docx
[5] thesis_doc_04_evaluation_and_ablation_report.docx

## Agentic RAG (Proposed)

The complex benchmark is specifically designed to test reliability-oriented tasks such as multi-hop relationship reasoning, graph dependency reasoning, evidence selection, missing information handling, and self-reflection—the very tasks that motivate a hierarchical multi-agent framework [2][7]. It is not intended to prove that agentic RAG is better for every query [2]. The evaluation report explicitly states that agentic RAG is not always superior, as the baseline can be faster and sufficient for simple factual questions [4]. Additionally, the agentic system incurs higher latency (31.7 seconds vs. 18.4 seconds), which is a limitation that makes it unnecessary for low-risk direct lookup settings [1][4]. Therefore, the benchmark's scope and findings do not support replacing baseline RAG for all query types.

---

**Sources:**

[1] thesis_doc_04_evaluation_and_ablation_report.docx
[2] thesis_doc_04_evaluation_and_ablation_report.docx
[4] thesis_doc_04_evaluation_and_ablation_report.docx
[7] thesis_doc_04_evaluation_and_ablation_report.docx

## RAGAS (if available)

- Baseline faithfulness: N/A
- Agentic faithfulness: N/A

_Add Streamlit screenshots side-by-side in your thesis._