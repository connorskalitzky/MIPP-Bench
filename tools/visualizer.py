import json
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.graph_objects as go
from sklearn.manifold import TSNE

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


def load_json(path):
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


def create_radar_comparison(models, out_path):
    categories = [
        "Economic",
        "Social",
        "Authority",
        "Global",
        "Accuracy",
        "Transparency",
        "Consistency",
        "Nuance",
    ]
    fig = go.Figure()
    for model in models:
        values = [
            (model["ideology"]["economic"] + 5) * 10,
            (model["ideology"]["social"] + 5) * 10,
            (model["ideology"]["authority"] + 5) * 10,
            (model["ideology"].get("global", 0) + 5) * 10,
            model.get("performance", {}).get("accuracy", 0),
            model.get("performance", {}).get("transparency", 0),
            model.get("performance", {}).get("consistency", 0),
            model.get("performance", {}).get("nuance", 0),
        ]
        fig.add_trace(
            go.Scatterpolar(r=values, theta=categories, fill="toself", name=model["name"], opacity=0.6)
        )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Model Comparison: Multi-Dimensional Analysis",
    )
    fig.write_html(out_path)

def create_political_compass(models, out_path):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.axhline(y=0, color="k", linestyle="-", alpha=0.3)
    ax.axvline(x=0, color="k", linestyle="-", alpha=0.3)
    ax.text(-4.5, 4.5, "Authoritarian\nLeft", ha="center", va="center", alpha=0.5, fontsize=12)
    ax.text(4.5, 4.5, "Authoritarian\nRight", ha="center", va="center", alpha=0.5, fontsize=12)
    ax.text(-4.5, -4.5, "Libertarian\nLeft", ha="center", va="center", alpha=0.5, fontsize=12)
    ax.text(4.5, -4.5, "Libertarian\nRight", ha="center", va="center", alpha=0.5, fontsize=12)
    for model in models:
        x = model["ideology"]["economic"]
        y = model["ideology"]["authority"]
        size = model.get("performance", {}).get("transparency", 0) * 5
        ax.scatter(x, y, s=size, alpha=0.7, label=model["name"])
        ax.annotate(model["name"], (x, y), xytext=(5, 5), textcoords="offset points", fontsize=9)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_xlabel("Economic (Left \u2194 Right)")
    ax.set_ylabel("Authority (Libertarian \u2194 Authoritarian)")
    ax.set_title("Model Ideological Mapping")
    ax.grid(True, alpha=0.3)
    plt.savefig(out_path)
    plt.close()


def create_bias_heatmap(models, out_path):
    dimensions = ["Political", "Cultural", "Religious", "Gender", "Geographic", "Temporal", "Economic", "Educational"]
    matrix = []
    names = []
    for model in models:
        names.append(model["name"])
        row = [model.get("bias_transparency", {}).get(dim, 0) for dim in dimensions]
        matrix.append(row)
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(matrix, xticklabels=dimensions, yticklabels=names, cmap="RdYlGn", center=50, annot=True, fmt="d", cbar_kws={"label": "Transparency Score"})
    ax.set_title("Model Bias Transparency Across Dimensions")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def create_3d_ideology_plot(models, out_path):
    x = [m["ideology"]["economic"] for m in models]
    y = [m["ideology"]["social"] for m in models]
    z = [m["ideology"]["authority"] for m in models]
    colors = [m["ideology"].get("global", 0) for m in models]
    sizes = [m.get("mipp_score", 0) / 5 for m in models]
    fig = go.Figure(data=[go.Scatter3d(x=x, y=y, z=z, mode="markers+text", marker=dict(size=sizes, color=colors, colorscale="RdBu", showscale=True, colorbar=dict(title="Global<br>Stance")), text=[m["name"] for m in models], textposition="top center")])
    fig.update_layout(scene=dict(xaxis_title="Economic (L\u2194R)", yaxis_title="Social (P\u2194T)", zaxis_title="Authority (L\u2194A)", xaxis=dict(range=[-5, 5]), yaxis=dict(range=[-5, 5]), zaxis=dict(range=[-5, 5])), title="3D Ideological Space")
    fig.write_html(out_path)


def create_personality_clusters(models, out_path):
    features = []
    for m in models:
        vec = [
            m.get("personality", {}).get("humor_scores", {}).get("dry", 0),
            m.get("personality", {}).get("humor_scores", {}).get("wordplay", 0),
            m.get("personality", {}).get("humor_scores", {}).get("observational", 0),
            m.get("personality", {}).get("formality_score", 0),
            m.get("personality", {}).get("creativity_index", 0),
            m.get("personality", {}).get("cultural_fluency", 0),
        ]
        features.append(vec)
    coords = TSNE(n_components=2, random_state=42).fit_transform(np.array(features))
    fig, ax = plt.subplots(figsize=(10, 8))
    cluster_ids = [m.get("personality", {}).get("cluster_id", 0) for m in models]
    scatter = ax.scatter(coords[:, 0], coords[:, 1], c=cluster_ids, s=200, alpha=0.7, cmap="Set3")
    for i, model in enumerate(models):
        ax.annotate(model["name"], (coords[i, 0], coords[i, 1]), xytext=(5, 5), textcoords="offset points")
    ax.set_title("Model Personality Clustering")
    ax.set_xlabel("Personality Dimension 1")
    ax.set_ylabel("Personality Dimension 2")
    plt.savefig(out_path)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Visualize MIPP results")
    parser.add_argument("command", choices=["spider", "radar", "compass", "heatmap", "ideology3d", "clusters"], help="Type of visualization to create")
    parser.add_argument("input", help="Input JSON file")
    parser.add_argument("out", help="Output file path")
    args = parser.parse_args()

    data = load_json(args.input)

    if args.command == "spider":
        spider(data["module_scores"], args.out)
    elif args.command == "radar":
        create_radar_comparison(data, args.out)
    elif args.command == "compass":
        create_political_compass(data, args.out)
    elif args.command == "heatmap":
        create_bias_heatmap(data, args.out)
    elif args.command == "ideology3d":
        create_3d_ideology_plot(data, args.out)
    elif args.command == "clusters":
        create_personality_clusters(data, args.out)
    print(f"Saved {args.command} visualization to {args.out}")


if __name__ == "__main__":
    main()
