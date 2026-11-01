"""Build 129's translations are written by tr_a.py to tr_d.py through this: 29 strings (s129.json order) and 3 labels
(labels129.json order) a language, into tr129/<Language>.json for merge129.py."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LABELS = list(json.load(open(os.path.join(HERE, 'labels129.json'), encoding='utf-8')))
EN = json.load(open(os.path.join(HERE, 's129.json'), encoding='utf-8'))


def write(T):
    os.makedirs(os.path.join(HERE, 'tr129'), exist_ok=True)
    for lang, (s, l) in T.items():
        assert len(s) == len(EN) and len(l) == len(LABELS), (lang, len(s), len(l))
        json.dump({'s': {str(i): v for i, v in enumerate(s)}, 'l': dict(zip(LABELS, l))},
                  open(os.path.join(HERE, 'tr129', lang + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', ', '.join(T))
