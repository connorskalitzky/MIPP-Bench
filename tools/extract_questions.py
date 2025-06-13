import re
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET


def extract_text(docx_path: Path) -> str:
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read('word/document.xml')
    root = ET.fromstring(xml)
    text_parts = []
    for elem in root.iter():
        if elem.text:
            text_parts.append(elem.text)
    return ' '.join(text_parts)


def parse_questions(text: str):
    """Extract question prompts keyed by module."""

    pat_star = re.compile(r"\*\*([A-D][^*\s]*)\*\*\s*\"([^\"]+)\"")
    pat_colon = re.compile(r"([A-D]\d+(?:[.-][A-Za-z0-9]+)+):[^\"]*\"([^\"]+)\"")

    questions = {}

    def add(qid: str, prompt: str):
        module = qid[0]
        key = {
            'A': 'module_a_ideology',
            'B': 'module_b_cultural',
            'C': 'module_c_personality',
            'D': 'module_d_transparency',
        }[module]
        q = {'id': qid, 'prompt': ' '.join(prompt.split())}
        if key not in questions:
            questions[key] = []
        if all(item['id'] != qid for item in questions[key]):
            questions[key].append(q)

    for qid, prompt in pat_star.findall(text):
        add(qid, prompt)
    for qid, prompt in pat_colon.findall(text):
        add(qid, prompt)

    return questions


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('docx', help='MIPP Benchmark.docx path')
    parser.add_argument('outdir', help='Output directory for question jsons')
    args = parser.parse_args()

    text = extract_text(Path(args.docx))
    questions = parse_questions(text)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for module, qs in questions.items():
        (outdir / f'{module}.json').write_text(json.dumps(qs, indent=2))
    print({k: len(v) for k, v in questions.items()})

if __name__ == '__main__':
    main()
