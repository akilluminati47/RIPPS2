"""Build 126's language kit: the strings of elf/lang/_strings.yml a language has no translation for (German is the
reference: every language was complete at build 125), and the labels build 126 added or changed. Writes s126.json and
labels126.json for merge126.py.    python tools/lang126/make126.py"""
import json
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LANG = os.path.join(HERE, '..', '..', 'elf', 'lang')
KEPT = ('psx-place', 'github.com', 'LX:', 'LY:', 'RX:', 'RY:', 'PID:', 'VID:', 'REV:')
template = [it['en'] for it in yaml.safe_load(open(os.path.join(LANG, '_strings.yml'), encoding='utf-8'))['strings']]
langs = sorted(f[:-4] for f in os.listdir(LANG) if f.endswith('.yml') and not f.startswith('_'))
done = {l: (yaml.safe_load(open(os.path.join(LANG, l + '.yml'), encoding='utf-8')).get('strings') or {}) for l in langs}
missing = [en for en in template if sum(1 for l in langs if not done[l].get(en)) == len(langs)]
missing = [en for en in missing if not any(k in en for k in KEPT) and en not in ('MX4SIO', 'USB', 'iLink', 'ART', 'MEDIA', 'icyson55')
           and not (' - ' in en or (', ' in en and en[0].isalpha() and en.count(',') >= 2 and '%' not in en and len(en) < 80))]  # credits: names
json.dump(missing, open(os.path.join(HERE, 's126.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
base = {}
cur = None
for line in open(os.path.join(HERE, '..', '..', '..', 'RiptOPL', 'lng_tmpl', '_base.yml'), encoding='utf-8'):
    line = line.rstrip('\r\n')
    if line.startswith('- label: '):
        cur = line[9:].strip()
    elif line.startswith('  string: ') and cur:
        v = line[10:]
        base[cur] = json.loads(v) if v.startswith('"') else v
LABELS = ['RIPPS2_LIST_CFG_TEXT', 'HINT_RIPPS2_LIST_CFG_TEXT', 'RIPPS2_PS1_PREFER', 'HINT_RIPPS2_PS1_PREFER', 'RIPPS2_MY_PADS',
          'HINT_RIPPS2_MY_PADS', 'HINT_BOOT_SND']
json.dump({k: base[k] for k in LABELS}, open(os.path.join(HERE, 'labels126.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(missing), 'strings,', len(LABELS), 'labels; per language untranslated:',
      sorted(set(sum(1 for en in template if not done[l].get(en)) for l in langs)))
