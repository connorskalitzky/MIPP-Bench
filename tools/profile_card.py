import argparse
import json
from pathlib import Path


CARD_WIDTH = 41


def load_results(path: Path):
    return json.loads(path.read_text())


def center(text: str) -> str:
    return text.center(CARD_WIDTH - 2)


def bar(value: float, max_length: int = 20) -> str:
    filled = int(value / 100 * max_length)
    return '█' * filled + '░' * (max_length - filled)


def profile_card(results: dict) -> str:
    lines = ["┌" + "─" * (CARD_WIDTH - 2) + "┐"]
    title = f"MODEL PROFILE"
    lines.append("│" + center(title) + "│")
    lines.append("├" + "─" * (CARD_WIDTH - 2) + "┤")

    modules = results.get("module_scores", {})
    lines.append("│ Ideological: " + bar(modules.get("module_a_ideology", 0)) + " │")
    lines.append("│ Cultural:    " + bar(modules.get("module_b_cultural", 0)) + " │")
    lines.append("│ Personality: " + bar(modules.get("module_c_personality", 0)) + " │")
    lines.append("│ Transparency:" + bar(modules.get("module_d_transparency", 0)) + " │")

    dims = results.get("dimension_scores", {})
    lines.append("│" + " " * (CARD_WIDTH - 2) + "│")
    lines.append(
        f"│ Accuracy: {str(round(dims.get('factual_accuracy', 0))).rjust(3)}/100" + " " * 15 + "│"
    )
    lines.append(
        f"│ Transparency: {str(round(dims.get('bias_transparency', 0))).rjust(3)}/100" + " " * 9 + "│"
    )
    consistency = results.get("consistency_score", 0)
    lines.append(
        f"│ Consistency: {str(round(consistency)).rjust(3)}/100" + " " * 12 + "│"
    )
    lines.append("│" + " " * (CARD_WIDTH - 2) + "│")

    overall = results.get("overall_score", 0)
    bti = results.get("bias_transparency_index", 0)
    lines.append(
        f"│ Overall Score: {overall:5.1f}" + " " * 17 + "│"
    )
    lines.append(
        f"│ Bias Transparency: {bti:5.1f}" + " " * 15 + "│"
    )
    lines.append("└" + "─" * (CARD_WIDTH - 2) + "┘")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate simple text profile card")
    parser.add_argument("summary", help="JSON file from advanced_scorer.py")
    parser.add_argument("out", help="Output text file")
    args = parser.parse_args()
    results = load_results(Path(args.summary))
    card = profile_card(results)
    Path(args.out).write_text(card)
    print(card)


if __name__ == "__main__":
    main()

