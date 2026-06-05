# User Guide

## Running Locally

Install dependencies and start the Streamlit app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

For Streamlit Community Cloud, set the main file path to:

```text
app.py
```

## Required Secrets

The app needs a DeepSeek API key through the Anthropic-compatible configuration.

```toml
ANTHROPIC_BASE_URL = "https://api.deepseek.com/anthropic"
ANTHROPIC_AUTH_TOKEN = "your_deepseek_api_key"
ANTHROPIC_MODEL = "deepseek-chat"
```

Optional settings:

```toml
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
EMBEDDING_DEVICE = "cpu"
```

The default embedding model runs locally through SentenceTransformers. Voyage AI is optional and only needed if you change `EMBEDDING_MODEL` to a Voyage model.

## Uploading Documents

Supported formats:

| Format | Support |
|--------|---------|
| PDF | Yes |
| DOCX | Yes |
| TXT | Yes |

After upload, the app extracts text, creates hierarchical chunks, generates embeddings, stores chunks in ChromaDB, updates BM25 keyword retrieval, and builds graph evidence when possible.

## Asking Questions

Recommended question types:

| Type | Example |
|------|---------|
| Direct fact | What is the reliability gate? |
| Comparison | Compare baseline RAG and agentic RAG in the evaluation report. |
| Multi-hop | How do retrieval validation and critic review work together? |
| Graph reasoning | How is the Billing API connected to compliance review? |
| Missing information | Does the document provide the training dataset size? |

## Modes

| Mode | Meaning |
|------|---------|
| Baseline | Vector-only baseline using `NaiveRAG` |
| Agentic | Full multi-agent workflow using planner, decomposition, retrieval, validation, synthesis, writer, critic, and reliability checks |

Use baseline for fast direct questions. Use agentic mode when the question requires reliability, multiple pieces of evidence, missing information handling, or relationship reasoning.

## Reading Answers

Answers should include citations such as `[1]` or `[2]` when evidence is available. If the uploaded documents do not contain the requested information, the system should say that the information is not available instead of inventing an answer.

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| App says `Set ANTHROPIC_AUTH_TOKEN` | Missing API key | Add the key to `.env` or Streamlit Secrets |
| Upload works but answers are weak | Document does not contain the answer | Upload a relevant document or ask a grounded question |
| Graph search returns little evidence | Query has too few recognised entities | Ask with exact component names from the document |
| First answer is slow | Local embedding model or ChromaDB initialization | Wait for initialization to finish |
| Streamlit Cloud dependency issue | Python/package compatibility | Use `runtime.txt` and `requirements.txt` from this repo |
