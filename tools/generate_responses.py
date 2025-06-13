import argparse
import json
import os
from pathlib import Path

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None


MODULES = [
    'module_a_ideology',
    'module_b_cultural',
    'module_c_personality',
    'module_d_transparency'
]


def load_questions():
    qdir = Path('data/questions')
    questions = {}
    for module in MODULES:
        path = qdir / f'{module}.json'
        questions[module] = json.loads(path.read_text())
    return questions


def ask_openai(prompt: str, model: str, temperature: float):
    if openai is None:
        raise RuntimeError('openai package not installed')
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY env var not set')
    openai.api_key = api_key
    resp = openai.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def generate(model: str, temperature: float, out_path: Path, dry_run: bool = False):
    questions = load_questions()
    answers = {}
    for module, qs in questions.items():
        for q in qs:
            qid = q['id']
            prompt = q['prompt']
            if dry_run:
                ans = ''
            else:
                ans = ask_openai(prompt, model, temperature)
            answers[qid] = ans
    out_path.write_text(json.dumps(answers, indent=2))
    print(f'Saved {len(answers)} responses to {out_path}')


def main():
    parser = argparse.ArgumentParser(description='Generate model responses for MIPP questions using OpenAI API')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='OpenAI model name')
    parser.add_argument('--temperature', type=float, default=0.7, help='Sampling temperature')
    parser.add_argument('--dry-run', action='store_true', help='Skip API calls and create blank response file')
    parser.add_argument('output', help='Path to save responses JSON')
    args = parser.parse_args()

    generate(args.model, args.temperature, Path(args.output), args.dry_run)


if __name__ == '__main__':
    main()
