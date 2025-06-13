import json
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import numpy as np

MODULES = [
    'module_a_ideology',
    'module_b_cultural',
    'module_c_personality',
    'module_d_transparency'
]

LABELS = [
    'Ideology',
    'Culture',
    'Personality',
    'Transparency'
]


def load_results(path):
    return json.loads(Path(path).read_text())


def spider(scores, out_path):
    values = [scores[m] for m in MODULES]
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(values))

    fig, ax = plt.subplots(subplot_kw=dict(polar=True))
    ax.plot(angles, values, 'o-', linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(LABELS)
    ax.set_title('MIPP Module Scores')
    plt.savefig(out_path)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Visualize MIPP results")
    parser.add_argument("results", help="JSON file produced by scorer.py")
    parser.add_argument("out", help="Output image path")
    args = parser.parse_args()

    results = load_results(args.results)
    spider(results["module_scores"], args.out)
    print(f"Saved spider chart to {args.out}")


if __name__ == "__main__":
    main()
