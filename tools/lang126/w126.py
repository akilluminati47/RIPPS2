"""Writes tr126/<Language>.json from a batch's {language: (46 strings, 7 labels)}"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LABELS = list(json.load(open(os.path.join(HERE, 'labels126.json'), encoding='utf-8')))
N = len(json.load(open(os.path.join(HERE, 's126.json'), encoding='utf-8')))


def save(T):
    os.makedirs(os.path.join(HERE, 'tr126'), exist_ok=True)
    for lang, (s, l) in T.items():
        assert len(s) == N and len(l) == len(LABELS), (lang, len(s), len(l))
        json.dump({'s': {str(i): v for i, v in enumerate(s)}, 'l': dict(zip(LABELS, l))},
                  open(os.path.join(HERE, 'tr126', lang + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', ', '.join(T))
