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
    totals = {dim: 0 for dim in DIMENSIONS}
    counts = {dim: 0 for dim in DIMENSIONS}
    for qid in questions:
        if qid in responses:
            scores = responses[qid]
            for dim in DIMENSIONS:
                if dim in scores:
                    totals[dim] += scores.get(dim, 0)
                    counts[dim] += 1
    module_total = sum(totals.values())
    module_count = sum(counts.values())
    module_score = (module_total / module_count * 100 / 3) if module_count else 0
    return module_score, totals, counts


def main():
    parser = argparse.ArgumentParser(description="Score MIPP responses")
    parser.add_argument("responses", help="JSON file with per-question scores")
    parser.add_argument("out", help="Path to save aggregated results")
    args = parser.parse_args()

    responses = load_responses(args.responses)

    module_scores = {}
    module_dimension_scores = {}
    dim_totals = {dim: 0 for dim in DIMENSIONS}
    dim_counts = {dim: 0 for dim in DIMENSIONS}

    for module in MODULE_WEIGHTS:
        q_path = Path("data/questions") / f"{module}.json"
        questions = load_questions(q_path)
        mod_score, totals, counts = score_module(questions, responses)
        module_scores[module] = mod_score
        module_dimension_scores[module] = {
            dim: (totals[dim] / counts[dim] * 100 / 3) if counts[dim] else 0
            for dim in DIMENSIONS
        }
        for dim in DIMENSIONS:
            dim_totals[dim] += totals[dim]
            dim_counts[dim] += counts[dim]

    overall = sum(module_scores[m] * MODULE_WEIGHTS[m] for m in MODULE_WEIGHTS)

    dimension_scores = {
        dim: (dim_totals[dim] / dim_counts[dim] * 100 / 3) if dim_counts[dim] else 0
        for dim in DIMENSIONS
    }

    bias_transparency_index = (
        dimension_scores["bias_transparency"] * dimension_scores["factual_accuracy"]
    ) / 100

    results = {
        "module_scores": module_scores,
        "dimension_scores": dimension_scores,
        "module_dimension_scores": module_dimension_scores,
        "overall_score": overall,
        "bias_transparency_index": bias_transparency_index,
    }
    Path(args.out).write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
