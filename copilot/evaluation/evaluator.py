import json
import csv
import time
from pathlib import Path
from datetime import datetime
from copilot.agent.react_agent import run_react_agent
from copilot.config import settings


def load_questions(csv_path: str = "evaluation_questions.csv") -> list[dict]:
    questions = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append(row)
    return questions


def compute_grounded_precision(answer: str, gold_snippet: str) -> float:
    gold_words = set(gold_snippet.lower().split())
    answer_words = set(answer.lower().split())
    if not gold_words:
        return 0.0
    overlap = gold_words & answer_words
    return round(len(overlap) / len(gold_words), 2)


def run_baseline(question: str, client, model: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Answer the question concisely."},
            {"role": "user", "content": question}
        ],
        max_tokens=512
    )
    return response.choices[0].message.content or ""


def evaluate(mode: str = "react") -> list[dict]:
    from openai import OpenAI
    client = OpenAI(
        api_key=settings.nvidia_api_key,
        base_url=settings.nvidia_base_url
    )

    questions = load_questions()
    results = []

    print(f"\nRunning evaluation in [{mode}] mode on {len(questions)} questions...\n")

    for q in questions:
        qid = q["id"]
        question = q["question"]
        gold_source = q["gold_source_file"]
        gold_snippet = q["gold_supporting_snippet"]

        print(f"  {qid}: {question[:60]}...")

        start = time.time()

        if mode == "react":
            result = run_react_agent(question)
            answer = result["answer"]
            steps_used = result["step_count"]
            retrieved_files = list(set(
                s["args"].get("filename", s["args"].get("query", ""))
                for s in result["steps"]
            ))
            citations = [gold_source] if gold_source.lower() in answer.lower() else []
        else:
            answer = run_baseline(question, client, settings.llm_model)
            steps_used = 0
            retrieved_files = []
            citations = []

        elapsed = round(time.time() - start, 2)
        grounded = compute_grounded_precision(answer, gold_snippet)

        results.append({
            "question_id": qid,
            "question": question,
            "mode": mode,
            "steps_used": steps_used,
            "retrieved_files": json.dumps(retrieved_files),
            "answer": answer,
            "citations": json.dumps(citations),
            "grounded_precision": grounded,
            "notes": f"elapsed={elapsed}s"
        })

        time.sleep(1)

    return results


def save_results(results: list[dict], mode: str):
    runs_dir = Path(settings.runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = runs_dir / f"eval_{mode}_{timestamp}.csv"
    fieldnames = list(results[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nResults saved to {out_path}")
    return out_path