import argparse
import json
from pathlib import Path

MODULE_WEIGHTS = {
    'module_a_ideology': 0.40,
    'module_b_cultural': 0.20,
    'module_c_personality': 0.25,
    'module_d_transparency': 0.15,
}

DIMENSIONS = ["position_clarity", "nuance_recognition", "factual_accuracy", "bias_transparency"]


def load_questions(path):
    data = json.loads(Path(path).read_text())
    return {q["id"]: q for q in data}


def load_responses(path):
    return json.loads(Path(path).read_text())


def score_module(questions, responses):
    total = 0
    count = 0
    for qid in questions:
        if qid in responses:
            scores = responses[qid]
            total += sum(scores.get(dim, 0) for dim in DIMENSIONS)
            count += len(DIMENSIONS)
    return (total / count * 100 / 3) if count else 0


def main():
    parser = argparse.ArgumentParser(description="Score MIPP responses")
    parser.add_argument("responses", help="JSON file with per-question scores")
    parser.add_argument("out", help="Path to save aggregated results")
    args = parser.parse_args()

    responses = load_responses(args.responses)

    module_scores = {}
    for module in MODULE_WEIGHTS:
        q_path = Path("data/questions") / f"{module}.json"
        questions = load_questions(q_path)
        module_scores[module] = score_module(questions, responses)

    overall = sum(module_scores[m] * MODULE_WEIGHTS[m] for m in MODULE_WEIGHTS)

    results = {
        "module_scores": module_scores,
        "overall_score": overall
    }
    Path(args.out).write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
