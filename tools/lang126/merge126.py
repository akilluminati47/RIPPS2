"""Merge tr126/<Language>.json (build 126's strings by their number in s126.json, and labels) into elf/lang/<Language>.yml:
new strings go at the end of strings:, labels are replaced in place or added at the end of labels:."""
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LANG = os.path.join(HERE, '..', '..', 'elf', 'lang')
EN = json.load(open(os.path.join(HERE, 's126.json'), encoding='utf-8'))
LABELS = json.load(open(os.path.join(HERE, 'labels126.json'), encoding='utf-8'))
CONV = re.compile(r'%[-+ #0]*\d*(?:\.\d+)?[hlLqjzt]*[diouxXeEfgGcsp%]')


def line(k, v):
    return yaml.safe_dump({k: v}, allow_unicode=True, width=1 << 20, default_flow_style=False, sort_keys=False).rstrip('\n')


def merge(lang, dry):
    data = json.load(open(os.path.join(HERE, 'tr126', lang + '.json'), encoding='utf-8'))
    s, l = data['s'], data['l']
    bad = []
    for i, en in enumerate(EN):
        tr = s.get(str(i))
        if tr is None:
            bad.append('string %d missing' % i)
        elif CONV.findall(en) != CONV.findall(tr):
            bad.append('string %d: %% conversions differ' % i)
        elif en.endswith('\n') != tr.endswith('\n') or en.count('\n') != tr.count('\n'):
            bad.append('string %d: line breaks differ' % i)
    for k, en in LABELS.items():
        tr = l.get(k)
        if tr is None:
            bad.append('label %s missing' % k)
        elif CONV.findall(en) != CONV.findall(tr):
            bad.append('label %s: %% conversions differ' % k)
    extra = set(s) - {str(i) for i in range(len(EN))} | set(l) - set(LABELS)
    if extra:
        bad.append('unknown keys %s' % sorted(extra))
    if bad:
        print(lang, 'NOT merged:', '; '.join(bad))
        return False
    p = os.path.join(LANG, lang + '.yml')
    text = open(p, encoding='utf-8').read()
    lines = text.split('\n')
    cur = yaml.safe_load(text)
    have = cur.get('strings') or {}
    li = lines.index('labels:')
    si = lines.index('strings:')
    known = {e['en'] for e in yaml.safe_load(open(os.path.join(LANG, '_strings.yml'), encoding='utf-8'))['strings']}
    root = yaml.compose(text)  # each entry's lines, from where its key starts to where its value ends
    smap = [v for k, v in root.value if k.value == 'strings'][0]
    spans = []
    for k, v in smap.value:
        last = v.end_mark.line - (1 if v.end_mark.column == 0 else 0)
        spans.append((k.value, k.start_mark.line, last))
    assert spans[0][1] == si + 1 and spans[-1][2] < li, (lang, 'strings section shape')
    body, dropped, n = [], 0, si + 1
    for en, a, b in spans:
        body += lines[n:a]  # blank lines or comments between entries stay
        n = b + 1
        if en not in known:  # a string the template no longer has (its English changed): it goes
            dropped += 1
            continue
        k = EN.index(en) if en in EN else -1
        if k >= 0 and have[en] != s[str(k)]:  # one already there: replaced where it is
            body += ['  ' + x for x in line(en, s[str(k)]).split('\n')]
        else:
            body += lines[a:b + 1]
    body += lines[n:li]
    new_strings = [line(en, s[str(i)]) for i, en in enumerate(EN) if en not in have]
    for x in new_strings:
        body += ['  ' + y for y in x.split('\n')]
    lines = lines[:si + 1] + body + lines[li:]
    li = lines.index('labels:')
    end = len(lines)
    while end > li and lines[end - 1] == '':
        end -= 1
    for k in LABELS:
        rows = [n for n in range(li + 1, end) if lines[n].startswith('  %s:' % k)]
        if rows:
            n = rows[0]
            assert n + 1 >= end or lines[n + 1].startswith('  ') and not lines[n + 1].startswith('   '), (lang, k, 'spans lines')
            lines[n] = '  ' + line(k, l[k])
        else:
            lines.insert(end, '  ' + line(k, l[k]))
            end += 1
    out = '\n'.join(lines)
    got = yaml.safe_load(out)
    for i, en in enumerate(EN):
        assert got['strings'][en] == s[str(i)], (lang, i)
    for k in LABELS:
        assert got['labels'][k] == l[k], (lang, k)
    assert len(got['strings']) == len(have) - dropped + len(new_strings), (lang, 'string count')
    assert len(got['labels']) >= len(cur.get('labels') or {})
    assert all(k in known for k in got['strings']), (lang, 'a stale string left')
    if not dry:  # CRLF, as git's autocrlf checks these files out on Windows
        open(p, 'w', encoding='utf-8', newline='\r\n').write(out)
    print(lang, 'merged:', len(new_strings), 'new strings,', dropped, 'stale dropped,', len(LABELS), 'labels')
    return True


if __name__ == '__main__':
    dry = '--dry' in sys.argv
    langs = [a for a in sys.argv[1:] if not a.startswith('--')]
    ok = all([merge(x, dry) for x in langs])
    sys.exit(0 if ok else 1)
