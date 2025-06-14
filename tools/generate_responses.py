import argparse
import json
import os
from pathlib import Path

try:  # optional dependency
    import openai
except ImportError:  # pragma: no cover
    openai = None

try:  # optional dependency for local models
    from transformers import pipeline
except Exception:  # pragma: no cover - transformers may not be installed
    pipeline = None


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


def ask_openai(messages, model: str, temperature: float):
    if openai is None:
        raise RuntimeError('openai package not installed')
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY env var not set')
    openai.api_key = api_key
    resp = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def ask_hf(prompt: str, model: str, temperature: float, max_tokens: int):
    if pipeline is None:
        raise RuntimeError('transformers package not installed')
    pipe = pipeline('text-generation', model=model)
    out = pipe(prompt, max_new_tokens=max_tokens, do_sample=True, temperature=temperature)
    return out[0]['generated_text'].strip()


def generate(model: str, temperature: float, out_path: Path, dry_run: bool = False,
             backend: str = 'openai', max_tokens: int = 512, randomize: bool = False):
    questions = load_questions()
    answers = {}
    for module, qs in questions.items():
        history = []
        qlist = list(qs)
        if randomize:
            import random
            random.shuffle(qlist)
        for q in qlist:
            qid = q['id']
            prompt = q['prompt']
            if dry_run:
                ans = ''
            else:
                if backend == 'openai':
                    messages = history + [{'role': 'user', 'content': prompt}]
                    ans = ask_openai(messages, model, temperature)
                    history.extend([
                        {'role': 'user', 'content': prompt},
                        {'role': 'assistant', 'content': ans},
                    ])
                else:
                    ans = ask_hf(prompt, model, temperature, max_tokens)
            answers[qid] = ans
    out_path.write_text(json.dumps(answers, indent=2))
    print(f'Saved {len(answers)} responses to {out_path}')


def main():
    parser = argparse.ArgumentParser(description='Generate model responses for MIPP questions using OpenAI API')
    parser.add_argument('--model', default='gpt2', help='Model name or path')
    parser.add_argument('--backend', choices=['openai', 'hf'], default='openai',
                        help='Generation backend: openai or hf (HuggingFace)')
    parser.add_argument('--temperature', type=float, default=0.7, help='Sampling temperature')
    parser.add_argument('--max-tokens', type=int, default=256, help='Max new tokens for HF models')
    parser.add_argument('--dry-run', action='store_true', help='Skip model calls and create blank response file')
    parser.add_argument('--randomize', action='store_true', help='Randomize question order within each module')
    parser.add_argument('output', help='Path to save responses JSON')
    args = parser.parse_args()

    generate(args.model, args.temperature, Path(args.output), args.dry_run,
             backend=args.backend, max_tokens=args.max_tokens, randomize=args.randomize)


if __name__ == '__main__':
    main()
