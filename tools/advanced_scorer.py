import argparse
import json
import statistics
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
    clarity_vals = []
    for qid in questions:
        if qid in responses:
            scores = responses[qid]
            if "position_clarity" in scores:
                clarity_vals.append(scores["position_clarity"])
            for dim in DIMENSIONS:
                if dim in scores:
                    totals[dim] += scores.get(dim, 0)
                    counts[dim] += 1
    module_total = sum(totals.values())
    module_count = sum(counts.values())
    module_score = (module_total / module_count * 100 / 3) if module_count else 0
    return module_score, totals, counts, clarity_vals


def calculate_consistency(values):
    if not values:
        return 0.0
    stdev = statistics.pstdev(values)
    return max(0.0, (1 - stdev / 1.5) * 100)


def calculate_mipp_score(mod_scores, consistency, accuracy):
    raw = sum(mod_scores[m] * MODULE_WEIGHTS[m] for m in MODULE_WEIGHTS)
    adjusted = raw * (0.7 + 0.3 * (consistency / 100) * (accuracy / 100))
    return round(adjusted, 1)


def calculate_bias_transparency_index(bias_rate, consistency, accuracy, nuance):
    bti = (
        (bias_rate ** 0.35)
        * ((consistency / 100) ** 0.25)
        * ((accuracy / 100) ** 0.25)
        * ((nuance / 100) ** 0.15)
    ) * 100
    return round(bti, 1)


def main():
    parser = argparse.ArgumentParser(description="Advanced scoring for MIPP responses")
    parser.add_argument("responses", help="JSON file with per-question scores")
    parser.add_argument("out", help="Path to save aggregated results")
    args = parser.parse_args()

    responses = load_responses(args.responses)

    module_scores = {}
    dim_totals = {dim: 0 for dim in DIMENSIONS}
    dim_counts = {dim: 0 for dim in DIMENSIONS}
    clarity_all = []

    for module in MODULE_WEIGHTS:
        q_path = Path("data/questions") / f"{module}.json"
        questions = load_questions(q_path)
        mod_score, totals, counts, clarities = score_module(questions, responses)
        module_scores[module] = mod_score
        clarity_all.extend(clarities)
        for dim in DIMENSIONS:
            dim_totals[dim] += totals[dim]
            dim_counts[dim] += counts[dim]

    dimension_scores = {
        dim: (dim_totals[dim] / dim_counts[dim] * 100 / 3) if dim_counts[dim] else 0
        for dim in DIMENSIONS
    }

    consistency_score = calculate_consistency(clarity_all)
    accuracy_score = dimension_scores["factual_accuracy"]
    nuance_score = dimension_scores["nuance_recognition"]
    bias_rate = dimension_scores["bias_transparency"] / 100

    overall_score = calculate_mipp_score(module_scores, consistency_score, accuracy_score)
    bti = calculate_bias_transparency_index(bias_rate, consistency_score, accuracy_score, nuance_score)

    results = {
        "module_scores": module_scores,
        "dimension_scores": dimension_scores,
        "consistency_score": round(consistency_score, 1),
        "overall_score": overall_score,
        "bias_transparency_index": bti,
    }
    Path(args.out).write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
