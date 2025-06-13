# MIPP Benchmark

MIPP (Model Ideology, Personality & Perspective) Benchmark is a framework for evaluating generative AI models beyond pure capability. It measures how a model presents ideological positions, cultural literacy, personality traits and meta-cognitive transparency while maintaining factual accuracy.

This repository contains a reference implementation of the benchmark.  The
question sets are drawn from the full specification document and cover all four
modules:

* **Ideological Mapping** – 98 questions covering political spectrum and policy
  trade-offs
* **Cultural & Religious Literacy** – 115 questions spanning world religions
  and cultural sensitivity scenarios
* **Personality & Authenticity** – 61 creative and humour prompts
* **Meta-Cognitive Transparency** – 60 questions assessing self‑awareness and
  bias acknowledgement

Python utilities are provided for scoring model responses and generating simple
visualizations.

## Repository layout

- `data/questions/` – JSON question sets for each evaluation module
- `data/rubrics/` – scoring guidelines and rubrics
- `tools/scorer.py` – script used to score a set of model responses
- `tools/visualizer.py` – simple spider chart generator for composite scores
- `tools/generate_responses.py` – utility for producing model answers via the OpenAI API
- `results/` – directory for storing model profiles and comparison output
- `docs/` – additional documentation

See `docs/METHODOLOGY.md` for a detailed description of the benchmark design.

## Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

To generate responses using the OpenAI API and save them to `results/my_run.json`:

```bash
export OPENAI_API_KEY=sk-...
python3 tools/generate_responses.py --model gpt-3.5-turbo results/my_run.json
```

You can then manually score these responses according to the rubric in
`data/rubrics/scoring_guidelines.json` and place the per-question scores in a JSON
file (see `tools/templates/response_example.json` for format). Aggregate module
and overall scores:

```bash
python3 tools/scorer.py my_scores.json results/score_summary.json
```

Finally, visualize the module scores:

```bash
python3 tools/visualizer.py results/score_summary.json results/chart.png
```

The `tools/extract_questions.py` utility can regenerate question JSON files from
the provided Word document if needed.
