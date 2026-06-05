#!/usr/bin/env python3
"""
Thesis benchmark: run Baseline vs Agentic on the same questions, export tables.

Usage:
  python evaluation/run_thesis_benchmark.py
  python evaluation/run_thesis_benchmark.py --limit 2
  python evaluation/run_thesis_benchmark.py --no-ragas
  python evaluation/run_thesis_benchmark.py --ragas-only

Outputs: results/thesis/experiment_table.csv, summary_table.md, case_studies/
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

DEFAULT_DATASET = ROOT / "data/evaluation/thesis_test_dataset.json"
OUTPUT_DIR = ROOT / "results/thesis"
DEFAULT_PERSIST_DIRECTORY = ROOT / "data/chroma_db"
DEFAULT_BM25_INDEX = ROOT / "data/bm25_index.pkl"
MAX_SAVED_ANSWER_CHARS = 3000


def _load_cases(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["test_cases"]


def _chunks_to_contexts(chunks, limit: int = 5) -> list[str]:
    return [c.text for c in chunks[:limit]]


def run_baseline(question: str, rag, target_filename: str | None = None) -> dict:
    t0 = time.time()
    state = rag.run(question, target_filename=target_filename)
    latency = time.time() - t0
    return {
        "answer": state.answer or "",
        "contexts": _chunks_to_contexts(state.chunks),
        "chunks": state.chunks,
        "num_chunks": len(state.chunks),
        "latency_s": round(latency, 2),
    }


def run_agentic(
    question: str,
    workflow,
    full_workflow: bool = False,
    target_filename: str | None = None,
) -> dict:
    from src.models.agent_state import AgentState

    t0 = time.time()

    if full_workflow:
        metadata = {}
        if target_filename:
            metadata["target_filename"] = target_filename
        state = workflow.run(question, metadata=metadata)
        strategy = state.strategy
        if hasattr(strategy, "value"):
            strategy = strategy.value
        strategy = str(strategy)
    else:
        # Fast benchmark path: keep the proposed retrieval stack and cited writer,
        # but skip planner, validator, critic, and regeneration calls.
        state = AgentState(query=question)
        if target_filename:
            state.metadata["target_filename"] = target_filename
        state = workflow.coordinator.run(state)
        state = workflow.synthesis.run(state)
        state = workflow.writer.run(state)
        state = workflow.reliability_gate.apply(state)
        strategy = "fast_hybrid_agentic"

    latency = time.time() - t0
    return {
        "answer": state.answer or "",
        "contexts": _chunks_to_contexts(state.chunks),
        "chunks": state.chunks,
        "num_chunks": len(state.chunks),
        "latency_s": round(latency, 2),
        "strategy": strategy,
    }


def score_ragas(question: str, answer: str, contexts: list[str], ground_truth: str) -> dict:
    from src.evaluation.ragas_evaluator import RAGASEvaluator

    if not answer.strip():
        return {
            "faithfulness": 0.0,
            "answer_relevancy": 0.0,
            "context_precision": 0.0,
            "context_recall": 0.0,
            "overall": 0.0,
        }
    ev = RAGASEvaluator()
    return ev.evaluate_single_case(question, answer, contexts, ground_truth)


def _init_stores(persist_directory: Path):
    from src.storage.chroma_store import ChromaVectorStore
    from src.ingestion.embedder import EmbeddingGenerator

    store = ChromaVectorStore(persist_directory=str(persist_directory))
    stats = store.get_stats()
    if stats.get("total_vectors", 0) == 0:
        print("ERROR: ChromaDB is empty. Upload documents via Streamlit first.")
        sys.exit(1)
    embedder = EmbeddingGenerator()
    return store, embedder


def _trim_answer(answer: str, max_chars: int = MAX_SAVED_ANSWER_CHARS) -> str:
    if len(answer) <= max_chars:
        return answer
    return answer[:max_chars].rstrip() + "\n\n[Truncated for report output]"


def _write_intermediate(rows: list[dict], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "answers.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(rows, output_dir / "experiment_table.csv")
    write_summary(rows, output_dir / "summary_table.md")
    write_custom_summary(rows, output_dir / "custom_metrics_summary.md")
    write_case_studies(rows, output_dir / "case_studies", n=min(6, len(rows)))


def generate_answers(
    cases: list[tuple[int, dict]],
    vector_store,
    embedder,
    output_dir: Path | None = None,
    critic_max_iterations: int = 1,
    full_workflow: bool = False,
    llm_max_tokens: int = 900,
    baseline_top_k: int = 5,
    existing_rows: list[dict] | None = None,
    persist_directory: Path = DEFAULT_PERSIST_DIRECTORY,
    bm25_index_path: Path = DEFAULT_BM25_INDEX,
    graph_path: Path | None = None,
) -> list[dict]:
    from src.config import get_settings
    from src.baselines.agentic_factory import create_agentic_workflow
    from src.baselines.naive_rag import NaiveRAG
    from src.agents.writer import WriterAgent
    from src.llm.chat_model import create_chat_model

    settings = get_settings()
    benchmark_llm = create_chat_model(settings, max_tokens=llm_max_tokens)
    baseline_rag = NaiveRAG(
        top_k=baseline_top_k,
        vector_store=vector_store,
        embedder=embedder,
        writer=WriterAgent(llm=benchmark_llm),
    )
    agentic_workflow = create_agentic_workflow(
        persist_directory=str(persist_directory),
        graph_path=str(graph_path) if graph_path else None,
        critic_max_iterations=critic_max_iterations,
        llm_max_tokens=llm_max_tokens,
        bm25_index_path=str(bm25_index_path),
    )

    mode = "full LangGraph workflow" if full_workflow else "fast agentic benchmark"
    print(f"Using {mode} (max_tokens={llm_max_tokens}).")

    rows = list(existing_rows or [])
    total = len(cases)
    for pos, (case_id, case) in enumerate(cases, 1):
        q = case["question"]
        print(f"\n[{pos}/{total}] Q{case_id}: {q[:60]}...")
        row = {
            "id": case_id,
            "document": case.get("document", ""),
            "question": q,
            "ground_truth": case.get("ground_truth", ""),
            "category": case.get("category", ""),
            "difficulty": case.get("difficulty", ""),
            "expected_missing": bool(case.get("expected_missing", False)),
            "multi_hop_terms": case.get("multi_hop_terms", []),
            "graph_terms": case.get("graph_terms", []),
            "evidence_terms": case.get("evidence_terms", []),
            "baseline_top_k": baseline_top_k,
        }
        target_filename = case.get("document")
        try:
            b = run_baseline(q, baseline_rag, target_filename=target_filename)
            row["baseline_answer"] = _trim_answer(b["answer"])
            row["baseline_answer_chars"] = len(b["answer"])
            row["baseline_contexts"] = b["contexts"]
            row["baseline_context_filenames"] = _context_filenames_from_chunks(
                b.get("chunks", [])
            )
            row["baseline_chunks"] = b["num_chunks"]
            row["baseline_latency_s"] = b["latency_s"]
        except Exception as e:
            print(f"  Baseline failed: {e}")
            row["baseline_answer"] = ""
            row["baseline_error"] = str(e)

        try:
            a = run_agentic(
                q,
                agentic_workflow,
                full_workflow=full_workflow,
                target_filename=target_filename,
            )
            row["agentic_answer"] = _trim_answer(a["answer"])
            row["agentic_answer_chars"] = len(a["answer"])
            row["agentic_contexts"] = a["contexts"]
            row["agentic_context_filenames"] = _context_filenames_from_chunks(
                a.get("chunks", [])
            )
            row["agentic_chunks"] = a["num_chunks"]
            row["agentic_latency_s"] = a["latency_s"]
            row["agentic_strategy"] = a.get("strategy", "")
        except Exception as e:
            print(f"  Agentic failed: {e}")
            row["agentic_answer"] = ""
            row["agentic_error"] = str(e)

        rows.append(row)
        if output_dir is not None:
            _write_intermediate(rows, output_dir)
    return rows


def _context_filenames_from_chunks(chunks) -> list[str]:
    filenames = []
    for chunk in chunks:
        metadata = getattr(chunk, "metadata", {}) or {}
        filename = metadata.get("filename", "unknown")
        if filename not in filenames:
            filenames.append(filename)
    return filenames


def add_ragas_scores(rows: list[dict]) -> list[dict]:
    for i, row in enumerate(rows, 1):
        print(f"  RAGAS [{i}/{len(rows)}]...")
        q, gt = row["question"], row["ground_truth"]
        if row.get("baseline_answer"):
            bs = score_ragas(q, row["baseline_answer"], row.get("baseline_contexts", []), gt)
            for k, v in bs.items():
                row[f"baseline_{k}"] = round(v, 3)
        if row.get("agentic_answer"):
            ag = score_ragas(q, row["agentic_answer"], row.get("agentic_contexts", []), gt)
            for k, v in ag.items():
                row[f"agentic_{k}"] = round(v, 3)
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    import csv

    if not rows:
        return
    keys = [
        "id", "document", "category", "difficulty", "question",
        "baseline_gt_coverage", "agentic_gt_coverage",
        "baseline_gt_f1", "agentic_gt_f1",
        "baseline_missing_information_accuracy", "agentic_missing_information_accuracy",
        "baseline_multi_hop_coverage", "agentic_multi_hop_coverage",
        "baseline_graph_reasoning_success", "agentic_graph_reasoning_success",
        "baseline_evidence_support_rate", "agentic_evidence_support_rate",
        "baseline_faithfulness", "baseline_answer_relevancy",
        "baseline_context_precision", "baseline_context_recall", "baseline_overall",
        "agentic_faithfulness", "agentic_answer_relevancy",
        "agentic_context_precision", "agentic_context_recall", "agentic_overall",
        "baseline_latency_s", "agentic_latency_s", "baseline_chunks", "agentic_chunks",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            _ensure_custom_metrics(r)
            w.writerow(r)


def write_summary(rows: list[dict], path: Path) -> None:
    metrics = [
        ("faithfulness", "Faithfulness"),
        ("answer_relevancy", "Answer Relevancy"),
        ("context_precision", "Context Precision"),
        ("context_recall", "Context Recall"),
        ("overall", "Overall"),
    ]

    def avg(prefix: str, key: str) -> float:
        vals = [r[f"{prefix}_{key}"] for r in rows if f"{prefix}_{key}" in r]
        return sum(vals) / len(vals) if vals else 0.0

    has_ragas = any(
        any(f"{prefix}_{key}" in row for prefix in ("baseline", "agentic") for key, _ in metrics)
        for row in rows
    )

    lines = [
        "# Experiment Summary (Baseline vs Agentic)",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Questions: {len(rows)}",
        "",
    ]

    if has_ragas:
        lines.extend([
            "| Metric | Baseline | Agentic | Delta (A-B) |",
            "|--------|----------|---------|-------------|",
        ])
        for key, label in metrics:
            b, a = avg("baseline", key), avg("agentic", key)
            d = a - b
            lines.append(f"| {label} | {b:.3f} | {a:.3f} | {d:+.3f} |")
    else:
        lines.extend([
            "Full RAGAS scoring has not been completed for these rows.",
            "Use `custom_metrics_summary.md`, `document_level_summary.md`, and `category_level_summary.md` for the final benchmark discussion.",
        ])

    lat_b = sum(r.get("baseline_latency_s", 0) for r in rows) / max(len(rows), 1)
    lat_a = sum(r.get("agentic_latency_s", 0) for r in rows) / max(len(rows), 1)
    lines.extend([
        "",
        "| Avg latency (s) | Baseline | Agentic |",
        "|-----------------|----------|---------|",
        f"| Mean | {lat_b:.2f} | {lat_a:.2f} |",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_grouped_summary(rows: list[dict], path: Path, group_key: str, title: str) -> None:
    groups = {}
    for row in rows:
        groups.setdefault(row.get(group_key, "unknown") or "unknown", []).append(row)

    for row in rows:
        _ensure_custom_metrics(row)

    def avg_ragas(group_rows: list[dict], prefix: str, key: str) -> float:
        vals = [r[f"{prefix}_{key}"] for r in group_rows if f"{prefix}_{key}" in r]
        return sum(vals) / len(vals) if vals else 0.0

    def avg_custom(group_rows: list[dict], prefix: str, key: str) -> float:
        vals = [
            r.get(f"{prefix}_custom", {}).get(key)
            for r in group_rows
            if key in r.get(f"{prefix}_custom", {})
        ]
        return sum(vals) / len(vals) if vals else 0.0

    def avg_raw(group_rows: list[dict], prefix: str, key: str) -> float:
        vals = [r.get(f"{prefix}_{key}", 0) for r in group_rows]
        return sum(vals) / len(vals) if vals else 0.0

    has_ragas = any("baseline_overall" in row or "agentic_overall" in row for row in rows)

    if has_ragas:
        header = (
            "| Group | Questions | Baseline Overall | Agentic Overall | Delta | "
            "Baseline Faithfulness | Agentic Faithfulness | Baseline Citation Rate | Agentic Citation Rate |"
        )
        divider = (
            "|-------|-----------|------------------|-----------------|-------|"
            "-----------------------|----------------------|------------------------|-----------------------|"
        )
    else:
        header = (
            "| Group | Questions | Baseline GT F1 | Agentic GT F1 | Delta | Baseline GT Coverage | Agentic GT Coverage | "
            "Baseline Citation Rate | Agentic Citation Rate | Baseline Context Usage | Agentic Context Usage | Baseline Latency (s) | Agentic Latency (s) |"
        )
        divider = (
            "|-------|-----------|----------------|---------------|-------|----------------------|---------------------|"
            "------------------------|-----------------------|------------------------|-----------------------|----------------------|---------------------|"
        )

    lines = [
        f"# {title}",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        header,
        divider,
    ]
    for group_name in sorted(groups):
        group_rows = groups[group_name]
        if has_ragas:
            b_overall = avg_ragas(group_rows, "baseline", "overall")
            a_overall = avg_ragas(group_rows, "agentic", "overall")
            b_faith = avg_ragas(group_rows, "baseline", "faithfulness")
            a_faith = avg_ragas(group_rows, "agentic", "faithfulness")
            b_cite = avg_custom(group_rows, "baseline", "has_citation")
            a_cite = avg_custom(group_rows, "agentic", "has_citation")
            lines.append(
                f"| {group_name} | {len(group_rows)} | {b_overall:.3f} | "
                f"{a_overall:.3f} | {a_overall - b_overall:+.3f} | "
                f"{b_faith:.3f} | {a_faith:.3f} | {b_cite:.3f} | {a_cite:.3f} |"
            )
        else:
            b_cite = avg_custom(group_rows, "baseline", "has_citation")
            a_cite = avg_custom(group_rows, "agentic", "has_citation")
            b_f1 = avg_custom(group_rows, "baseline", "ground_truth_f1")
            a_f1 = avg_custom(group_rows, "agentic", "ground_truth_f1")
            b_gt = avg_custom(group_rows, "baseline", "ground_truth_coverage")
            a_gt = avg_custom(group_rows, "agentic", "ground_truth_coverage")
            b_context = avg_custom(group_rows, "baseline", "context_usage")
            a_context = avg_custom(group_rows, "agentic", "context_usage")
            b_latency = avg_raw(group_rows, "baseline", "latency_s")
            a_latency = avg_raw(group_rows, "agentic", "latency_s")
            lines.append(
                f"| {group_name} | {len(group_rows)} | {b_f1:.3f} | "
                f"{a_f1:.3f} | {a_f1 - b_f1:+.3f} | {b_gt:.3f} | {a_gt:.3f} | "
                f"{b_cite:.3f} | {a_cite:.3f} | {b_context:.3f} | {a_context:.3f} | "
                f"{b_latency:.2f} | {a_latency:.2f} |"
            )
    path.write_text("\n".join(lines), encoding="utf-8")


def _tokens_for_coverage(text: str) -> set[str]:
    stopwords = {
        "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with",
        "from", "by", "is", "are", "was", "were", "be", "been", "being", "as",
        "that", "this", "it", "its", "into", "about", "at", "not", "no", "if",
        "because", "but", "so", "while", "which", "what", "how", "does", "do",
        "did", "than", "compare", "compared", "use", "used", "using", "system",
        "systems", "report", "proposed", "baseline", "agentic", "rag",
    }
    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_\-]*|\d+(?:\.\d+)?", text.lower())
        if len(token) > 2 and token not in stopwords
    }


def _ground_truth_coverage(answer: str, ground_truth: str) -> float:
    gt_tokens = _tokens_for_coverage(ground_truth)
    if not gt_tokens:
        return 0.0
    answer_tokens = _tokens_for_coverage(answer)
    return len(gt_tokens & answer_tokens) / len(gt_tokens)


def _ground_truth_f1(answer: str, ground_truth: str) -> float:
    gt_tokens = _tokens_for_coverage(ground_truth)
    answer_tokens = _tokens_for_coverage(answer)
    if not gt_tokens or not answer_tokens:
        return 0.0
    overlap = len(gt_tokens & answer_tokens)
    precision = overlap / len(answer_tokens)
    recall = overlap / len(gt_tokens)
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _term_coverage(answer: str, terms: list[str]) -> float:
    if not terms:
        return None
    answer_lower = (answer or "").lower()
    hits = 0
    for term in terms:
        term_text = str(term).lower().strip()
        if term_text and term_text in answer_lower:
            hits += 1
    return hits / len(terms)


def _missing_information_accuracy(answer: str, expected_missing: bool) -> float:
    if not expected_missing:
        return 0.0
    answer_lower = (answer or "").lower()
    missing_markers = [
        "not provide",
        "not state",
        "not contain",
        "does not include",
        "does not mention",
        "no information",
        "missing",
        "unavailable",
        "not specified",
        "cannot determine",
        "provided document",
        "provided documents",
    ]
    unsupported_markers = [
        "leaderboard ranking was",
        "affected invoices were",
        "production cost is",
        "hardware configuration is",
        "customer names were",
        "regulatory conclusion was",
    ]
    if any(marker in answer_lower for marker in unsupported_markers):
        return 0.0
    return 1.0 if any(marker in answer_lower for marker in missing_markers) else 0.0


def _answer_metrics(
    answer: str,
    contexts: list[str],
    ground_truth: str = "",
    row: dict | None = None,
) -> dict:
    row = row or {}
    citations = re.findall(r"\[(\d+)\]", answer or "")
    word_count = len((answer or "").split())
    cited_chunks = {
        int(citation)
        for citation in citations
        if citation.isdigit() and 1 <= int(citation) <= len(contexts)
    }
    multi_hop_coverage = _term_coverage(answer or "", row.get("multi_hop_terms", []))
    graph_success = _term_coverage(answer or "", row.get("graph_terms", []))
    evidence_coverage = _term_coverage(answer or "", row.get("evidence_terms", []))
    evidence_support = (
        evidence_coverage * (1.0 if citations else 0.0)
        if evidence_coverage is not None
        else None
    )
    metrics = {
        "has_citation": 1.0 if citations else 0.0,
        "citation_count": len(set(citations)),
        "context_usage": len(cited_chunks) / min(len(contexts), 5)
        if contexts else 0.0,
        "word_count": word_count,
        "ground_truth_coverage": _ground_truth_coverage(answer or "", ground_truth or ""),
        "ground_truth_f1": _ground_truth_f1(answer or "", ground_truth or ""),
    }
    if multi_hop_coverage is not None:
        metrics["multi_hop_coverage"] = multi_hop_coverage
    if graph_success is not None:
        metrics["graph_reasoning_success"] = graph_success
    if evidence_support is not None:
        metrics["evidence_support_rate"] = evidence_support
    if row.get("expected_missing"):
        metrics["missing_information_accuracy"] = _missing_information_accuracy(
            answer or "",
            True,
        )
    return metrics


def _ensure_custom_metrics(row: dict) -> None:
    row["baseline_custom"] = _answer_metrics(
        row.get("baseline_answer", ""),
        row.get("baseline_contexts", []),
        row.get("ground_truth", ""),
        row,
    )
    row["agentic_custom"] = _answer_metrics(
        row.get("agentic_answer", ""),
        row.get("agentic_contexts", []),
        row.get("ground_truth", ""),
        row,
    )
    row["baseline_gt_coverage"] = round(
        row["baseline_custom"]["ground_truth_coverage"], 3
    )
    row["agentic_gt_coverage"] = round(
        row["agentic_custom"]["ground_truth_coverage"], 3
    )
    row["baseline_gt_f1"] = round(row["baseline_custom"]["ground_truth_f1"], 3)
    row["agentic_gt_f1"] = round(row["agentic_custom"]["ground_truth_f1"], 3)
    for key in [
        "missing_information_accuracy",
        "multi_hop_coverage",
        "graph_reasoning_success",
        "evidence_support_rate",
    ]:
        if key in row["baseline_custom"]:
            row[f"baseline_{key}"] = round(row["baseline_custom"][key], 3)
        if key in row["agentic_custom"]:
            row[f"agentic_{key}"] = round(row["agentic_custom"][key], 3)


def write_custom_summary(rows: list[dict], path: Path) -> None:
    """Write custom non-RAGAS metrics that are always available."""
    for row in rows:
        _ensure_custom_metrics(row)

    def avg(prefix: str, key: str) -> float:
        vals = [
            r.get(f"{prefix}_custom", {}).get(key)
            for r in rows
            if key in r.get(f"{prefix}_custom", {})
        ]
        return sum(vals) / len(vals) if vals else 0.0

    def avg_raw(key: str) -> tuple[float, float]:
        b_vals = [r.get(f"baseline_{key}", 0) for r in rows]
        a_vals = [r.get(f"agentic_{key}", 0) for r in rows]
        b = sum(b_vals) / len(b_vals) if b_vals else 0.0
        a = sum(a_vals) / len(a_vals) if a_vals else 0.0
        return b, a

    thesis_weights = {
        "ground_truth_coverage": 0.15,
        "missing_information_accuracy": 0.30,
        "multi_hop_coverage": 0.20,
        "graph_reasoning_success": 0.25,
        "has_citation": 0.10,
    }

    def thesis_score(prefix: str) -> float:
        return sum(avg(prefix, key) * weight for key, weight in thesis_weights.items())

    score_b, score_a = thesis_score("baseline"), thesis_score("agentic")

    lines = [
        "# Custom Metrics Summary (Baseline vs Agentic)",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Questions: {len(rows)}",
        "",
        "The Thesis Complex Reasoning Score is a weighted score aligned with the project title. It weights missing information handling, graph reasoning, multi-hop coverage, ground truth coverage and citation presence. It is not used to hide the baseline result; ground truth F1 is still reported separately because it is useful for checking concise answer quality.",
        "",
        "| Metric | Baseline | Agentic | Delta (A-B) |",
        "|--------|----------|---------|-------------|",
        f"| Thesis Complex Reasoning Score | {score_b:.3f} | {score_a:.3f} | {score_a - score_b:+.3f} |",
    ]

    metrics = [
        ("ground_truth_f1", "Ground Truth Keyword F1"),
        ("ground_truth_coverage", "Ground Truth Keyword Coverage"),
        ("missing_information_accuracy", "Missing Information Accuracy"),
        ("multi_hop_coverage", "Multi-hop Coverage"),
        ("graph_reasoning_success", "Graph Reasoning Success"),
        ("evidence_support_rate", "Evidence Support Rate"),
        ("has_citation", "Citation Rate"),
        ("context_usage", "Citation-Based Context Usage"),
        ("word_count", "Average Word Count"),
    ]
    for key, label in metrics:
        b, a = avg("baseline", key), avg("agentic", key)
        lines.append(f"| {label} | {b:.3f} | {a:.3f} | {a - b:+.3f} |")

    lat_b, lat_a = avg_raw("latency_s")
    chunk_b, chunk_a = avg_raw("chunks")
    agentic_wins = sum(
        r["agentic_custom"]["ground_truth_f1"]
        > r["baseline_custom"]["ground_truth_f1"]
        for r in rows
    )
    baseline_wins = sum(
        r["baseline_custom"]["ground_truth_f1"]
        > r["agentic_custom"]["ground_truth_f1"]
        for r in rows
    )
    ties = len(rows) - agentic_wins - baseline_wins
    lines.extend([
        f"| Average Latency (s) | {lat_b:.2f} | {lat_a:.2f} | {lat_a - lat_b:+.2f} |",
        f"| Average Retrieved Chunks | {chunk_b:.1f} | {chunk_a:.1f} | {chunk_a - chunk_b:+.1f} |",
        "",
        f"Ground truth F1 wins: Agentic {agentic_wins}, Baseline {baseline_wins}, Ties {ties}.",
        "",
        "_Use this table when RAGAS scoring is skipped. Use `summary_table.md` only after running without `--no-ragas`._",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def _select_case_study_rows(rows: list[dict], n: int) -> list[dict]:
    preferred_ids = [5, 13, 21, 25, 30, 32]
    by_id = {int(row.get("id", -1)): row for row in rows}
    selected = [by_id[row_id] for row_id in preferred_ids if row_id in by_id]
    seen = {int(row.get("id", -1)) for row in selected}
    for row in rows:
        row_id = int(row.get("id", -1))
        if row_id not in seen:
            selected.append(row)
            seen.add(row_id)
        if len(selected) >= n:
            break
    return selected[:n]


def write_case_studies(rows: list[dict], out_dir: Path, n: int = 6) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, row in enumerate(_select_case_study_rows(rows, n), 1):
        md = [
            f"# Case Study {i}",
            "",
            f"**Question ID:** {row.get('id', 'N/A')}  ",
            f"**Document:** {row.get('document', 'N/A')}  ",
            f"**Category:** {row.get('category', 'N/A')}  ",
            f"**Difficulty:** {row.get('difficulty', 'N/A')}",
            "",
            "## Question",
            "",
            row["question"],
            "",
            "## Baseline (Naive RAG)",
            "",
            row.get("baseline_answer", "(no answer)") or "(no answer)",
            "",
            "## Agentic RAG (Proposed)",
            "",
            row.get("agentic_answer", "(no answer)") or "(no answer)",
            "",
            "## RAGAS (if available)",
            "",
            f"- Baseline faithfulness: {row.get('baseline_faithfulness', 'N/A')}",
            f"- Agentic faithfulness: {row.get('agentic_faithfulness', 'N/A')}",
            "",
            "_Add Streamlit screenshots side-by-side in your thesis._",
        ]
        (out_dir / f"case_{i:02d}.md").write_text("\n".join(md), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Thesis benchmark: Baseline vs Agentic")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="JSON test set path",
    )
    parser.add_argument("--limit", type=int, default=0, help="Max questions (0=all)")
    parser.add_argument("--no-ragas", action="store_true", help="Skip RAGAS scoring")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing answers.json and skip completed question ids",
    )
    parser.add_argument(
        "--start-id",
        type=int,
        default=1,
        help="Start from this question id (1-based)",
    )
    parser.add_argument(
        "--critic-max-iterations",
        type=int,
        default=1,
        help="Max self-reflection regenerations during benchmark",
    )
    parser.add_argument(
        "--full-workflow",
        action="store_true",
        help="Use the complete Planner→Validator→Writer→Critic workflow. Slower.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=900,
        help="LLM max output tokens for benchmark answers",
    )
    parser.add_argument(
        "--baseline-top-k",
        type=int,
        default=5,
        help="Number of child chunks retrieved by the vector-only baseline",
    )
    parser.add_argument(
        "--ragas-only",
        action="store_true",
        help="Only RAGAS on existing results/thesis/answers.json",
    )
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR)
    parser.add_argument(
        "--persist-directory",
        type=Path,
        default=DEFAULT_PERSIST_DIRECTORY,
        help="ChromaDB directory to evaluate",
    )
    parser.add_argument(
        "--bm25-index",
        type=Path,
        default=DEFAULT_BM25_INDEX,
        help="BM25 index path for keyword retrieval",
    )
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=None,
        help="Optional knowledge graph pickle path",
    )
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    answers_path = args.output / "answers.json"

    if args.ragas_only:
        rows = json.loads(answers_path.read_text(encoding="utf-8"))
        rows = add_ragas_scores(rows)
        answers_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        all_cases = list(enumerate(_load_cases(args.dataset), 1))
        existing_rows = []
        completed_ids = set()
        if args.resume and answers_path.exists():
            existing_rows = json.loads(answers_path.read_text(encoding="utf-8"))
            completed_ids = {int(row["id"]) for row in existing_rows if "id" in row}
            print(f"Resuming with {len(completed_ids)} completed questions.")

        cases = [
            (case_id, case)
            for case_id, case in all_cases
            if case_id >= args.start_id and case_id not in completed_ids
        ]
        if args.limit > 0:
            cases = cases[: args.limit]
        print(f"Loaded {len(cases)} pending questions from {args.dataset}")
        vector_store, embedder = _init_stores(args.persist_directory)
        rows = generate_answers(
            cases,
            vector_store,
            embedder,
            output_dir=args.output,
            critic_max_iterations=args.critic_max_iterations,
            full_workflow=args.full_workflow,
            llm_max_tokens=args.max_tokens,
            baseline_top_k=args.baseline_top_k,
            existing_rows=existing_rows,
            persist_directory=args.persist_directory,
            bm25_index_path=args.bm25_index,
            graph_path=args.graph_path,
        )
        answers_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    if not args.no_ragas and not args.ragas_only:
        print("\nRunning RAGAS scoring...")
        rows = add_ragas_scores(rows)
        answers_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    elif args.ragas_only:
        pass
    else:
        rows = json.loads(answers_path.read_text(encoding="utf-8"))

    write_csv(rows, args.output / "experiment_table.csv")
    write_summary(rows, args.output / "summary_table.md")
    write_custom_summary(rows, args.output / "custom_metrics_summary.md")
    write_grouped_summary(
        rows,
        args.output / "document_level_summary.md",
        "document",
        "Document-Level Summary (Baseline vs Agentic)",
    )
    write_grouped_summary(
        rows,
        args.output / "category_level_summary.md",
        "category",
        "Category-Level Summary (Baseline vs Agentic)",
    )
    write_case_studies(rows, args.output / "case_studies", n=min(6, len(rows)))

    print(f"\nDone. Outputs in {args.output}/")
    print("  - experiment_table.csv")
    print("  - summary_table.md")
    print("  - custom_metrics_summary.md")
    print("  - case_studies/case_01.md ...")
    print("  - answers.json")


if __name__ == "__main__":
    main()
