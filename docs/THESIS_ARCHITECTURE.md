# Thesis Architecture and Innovation Points

## Figure 1: Overall System Architecture

```mermaid
flowchart TB
  subgraph UI["Presentation Layer"]
    ST["Streamlit Web UI"]
  end

  subgraph Orchestration["Agent Orchestration Layer"]
    P["Planner Agent"]
    D["Query Decomposer"]
    RC["Retrieval Coordinator"]
    V["Validator Agent"]
    SY["Synthesis Agent"]
    W["Writer Agent"]
    CR["Critic Agent"]
    RG["Reliability Gate"]
  end

  subgraph Retrieval["Retrieval Layer"]
    VS["Vector Search"]
    BM["BM25 Keyword Search"]
    GR["Graph Search"]
  end

  subgraph Storage["Storage and Graph Layer"]
    CH[("ChromaDB Vector Store")]
    KG[("Knowledge Graph")]
  end

  subgraph Models["Model Layer"]
    EMB["BGE Embeddings"]
    LLM["DeepSeek LLM"]
  end

  ST --> P
  P --> D
  D --> RC
  RC --> VS
  RC --> BM
  RC --> GR
  VS --> CH
  BM --> CH
  GR --> KG
  VS --> EMB
  P --> LLM
  V --> LLM
  W --> LLM
  CR --> LLM
  RC --> V
  V --> SY
  SY --> W
  W --> CR
  CR --> RG
  RG --> FA["Final Answer with Citations"]
  V -. "retry retrieval if evidence is weak" .-> RC
  CR -. "regenerate if quality is low" .-> W
```

## Figure 2: Baseline vs Proposed Pipeline

```mermaid
flowchart LR
  subgraph B["Baseline RAG"]
    BQ["Question"] --> BV["Vector Retrieval"]
    BV --> BW["Answer Generation"]
    BW --> BA["Answer"]
  end

  subgraph A["Proposed Agentic RAG"]
    AQ["Question"] --> AP["Planner"]
    AP --> AD["Decomposer"]
    AD --> AR["Hybrid Retrieval"]
    AR --> AV["Validator"]
    AV --> AS["Synthesis"]
    AS --> AW["Writer"]
    AW --> AC["Critic"]
    AC --> AG["Reliability Gate"]
    AG --> AA["Answer with Citations"]
  end
```

## Innovation Points

### 1. Hierarchical Multi-Agent Orchestration

The system is not a fixed retrieve-then-generate pipeline. It uses a planner, decomposer, retrieval coordinator, validator, synthesis agent, writer, critic, and reliability gate.

### 2. Hybrid Retrieval

The retrieval coordinator combines vector search, BM25 keyword retrieval, and graph search. This gives the system semantic, lexical, and relationship-based evidence channels.

### 3. Self-Reflection and Reliability Control

The validator checks evidence before writing. The critic reviews generated answers and can trigger regeneration. The reliability gate performs final grounding and citation checks.

### 4. Graph-Based Reasoning

The graph components extract entities and relationships from documents and use NetworkX graph retrieval for relationship questions.

### 5. Baseline Comparison

The project includes a vector-only baseline in `src/baselines/naive_rag.py`. The benchmark runner evaluates both baseline and proposed workflow over the same controlled documents.

## Suggested Captions

| Figure | Caption |
|--------|---------|
| Figure 3.1 | Overall architecture of the proposed Agentic RAG system |
| Figure 3.2 | Comparison between baseline RAG and the proposed hierarchical multi-agent RAG workflow |
| Figure 4.1 | General benchmark result comparison |
| Figure 4.2 | Complex reasoning benchmark result comparison |
