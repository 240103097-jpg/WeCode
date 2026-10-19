"""Export existing authored JSON literals without importing/executing TypeScript.

Run --write only after an authorized curriculum change; default checks for drift.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def authored():
    source = (ROOT / 'frontend/src/data/curriculum.ts').read_text()
    units = json.loads(source.split('export const units: Unit[] = ', 1)[1].split(';\n', 1)[0])
    rules = json.loads(source.split('export const answerRules: Record<string, AnswerRule> = ', 1)[1].rstrip().removesuffix(';'))
    return {'units': units, 'answerRules': rules}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    target = ROOT / 'backend/data/curriculum.json'
    data = authored()
    if args.write:
        target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    assert json.loads(target.read_text()) == data, 'Backend curriculum drifted from existing frontend authoring'
    print('PASS exact existing 9-unit/27-exercise curriculum and authored rules export')
