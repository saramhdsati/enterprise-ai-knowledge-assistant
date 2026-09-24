import json
import os
import sys
import re
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core import state
from app.retrieval.hybrid_search import hybrid_search
from app.generation.context_builder import build_context
from app.generation.llm import generate_answer

GOLDEN_DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "eval", "golden_dataset.json")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "eval", "eval_results.json")

TOP_K = 6


def load_golden_dataset():
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- Retrieval Metrics ----------

def hit_rate_at_k(retrieved_sources, expected_source):
    return 1 if expected_source in retrieved_sources else 0


def reciprocal_rank(retrieved_sources, expected_source):
    for i, src in enumerate(retrieved_sources):
        if src == expected_source:
            return 1 / (i + 1)
    return 0


# ---------- Generation Metrics (LLM-as-judge via Groq) ----------

def judge_faithfulness(answer, context):
    prompt = f"""You are a strict evaluator. Determine if the ANSWER is fully supported by the CONTEXT below.
Reply with ONLY a number from 1 to 5, with no explanation:
5 = fully supported, no invented information
3 = partially supported, some unsupported details
1 = mostly or fully unsupported (hallucinated)

CONTEXT:
{context}

ANSWER:
{answer}

Score (1-5 only):"""

    response = state.groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=200,
    )
    content = response.choices[0].message.content.strip()
    matches = re.findall(r"[1-5]", content)
    return int(matches[-1]) if matches else None


def judge_relevance(question, answer):
    prompt = f"""You are a strict evaluator. Determine if the ANSWER actually addresses the QUESTION asked.
Reply with ONLY a number from 1 to 5, with no explanation:
5 = directly and completely answers the question
3 = partially answers it
1 = does not answer the question at all

QUESTION:
{question}

ANSWER:
{answer}

Score (1-5 only):"""

    response = state.groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=200,
    )
    content = response.choices[0].message.content.strip()
    matches = re.findall(r"[1-5]", content)
    return int(matches[-1]) if matches else None

def run_evaluation():
    dataset = load_golden_dataset()
    results = []

    print(f"Running evaluation on {len(dataset)} questions...\n")

    for i, item in enumerate(dataset, 1):
        question = item["question"]
        expected_source = item["expected_source"]
        department = item.get("department", "ALL")

        allowed_departments = ["ALL"] if department == "ALL" else [department]
        retrieved_chunks = hybrid_search(question, top_k=TOP_K, allowed_departments=allowed_departments)
        retrieved_sources = [c["source_file"] for c in retrieved_chunks]

  
        if "health insurance plan options" in question.lower() or "physical office locations" in question.lower():
            print("\n--- DEBUG: retrieved chunks for this question ---")
            for c in retrieved_chunks:
                print(f"[{c['source_file']}] {c['text'][:150]}...")
            print("--- END DEBUG ---\n")

        context = build_context(retrieved_chunks)
        answer = generate_answer(question, context)

        hit = hit_rate_at_k(retrieved_sources, expected_source)
        rr = reciprocal_rank(retrieved_sources, expected_source)
        faithfulness = judge_faithfulness(answer, context)
        relevance = judge_relevance(question, answer)

        result = {
            "question": question,
            "expected_source": expected_source,
            "retrieved_sources": retrieved_sources,
            "hit": hit,
            "reciprocal_rank": rr,
            "answer": answer,
            "faithfulness_score": faithfulness,
            "relevance_score": relevance,
        }
        results.append(result)

        print(f"[{i}/{len(dataset)}] hit={hit} rr={rr:.2f} faithfulness={faithfulness} relevance={relevance}  — {question[:60]}")

    # ---------- Aggregate ----------
    n = len(results)
    avg_hit_rate = sum(r["hit"] for r in results) / n
    avg_mrr = sum(r["reciprocal_rank"] for r in results) / n

    valid_faithfulness = [r["faithfulness_score"] for r in results if r["faithfulness_score"] is not None]
    valid_relevance = [r["relevance_score"] for r in results if r["relevance_score"] is not None]
    avg_faithfulness = sum(valid_faithfulness) / len(valid_faithfulness) if valid_faithfulness else None
    avg_relevance = sum(valid_relevance) / len(valid_relevance) if valid_relevance else None

    summary = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "num_questions": n,
        "top_k": TOP_K,
        f"hit_rate@{TOP_K}": round(avg_hit_rate, 3),
        "mrr": round(avg_mrr, 3),
        "avg_faithfulness_1to5": round(avg_faithfulness, 2) if avg_faithfulness else None,
        "avg_relevance_1to5": round(avg_relevance, 2) if avg_relevance else None,
    }

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for k, v in summary.items():
        print(f"{k}: {v}")

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "details": results}, f, ensure_ascii=False, indent=2)

    print(f"\nFull results saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    run_evaluation()