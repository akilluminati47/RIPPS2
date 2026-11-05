"""v1.4.3-beta's docs, for the moment the user says publish: the README's header, size and What's new in English and all 32
languages (the translations keep their words; only the numbers move), and both psx-place first posts.

    python publish143.py <repo> [--bootcard]

--bootcard: a new BIBLE-SD2PSX-BootCard-f5705eb.zip is on BIBLE's release. Without it, the first post's BOOT card line points at the
3282396 card on its own release page and says it still has the hang.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(sys.argv[1])
BOOTCARD = '--bootcard' in sys.argv
sys.path.insert(0, str(REPO / 'tools' / 'readme-i18n'))
import readme_i18n as R  # noqa: E402

SIZE = '750'  # RIPPS2.elf 2,816,052 bytes = 2,750 KB


def header(t, code=None):
    assert t.count('141') == 1 and t.count('1.4.1') == 1, (code, t)
    return t.replace('141', '143').replace('1.4.1', '1.4.3')


def sizes(t, code=None):
    t, n = re.subn(r'2([.,   ]?)775', r'2\g<1>' + SIZE, t)
    assert n == 1, (code, 'size')
    return t


def whatsnew(t, code=None):
    assert t.count('v1.4.1-beta') == 1, code
    t = t.replace('v1.4.1-beta', 'v1.4.3-beta')
    head = t[:t.index('](')]
    assert head.count('141') == 1, (code, head)
    return head.replace('141', '143') + t[len(head):]


p = REPO / 'README.md'
raw = p.read_bytes().decode('utf-8')
crlf = '\r\n' in raw
lines = raw.replace('\r\n', '\n').split('\n')
fixes = []
for i, l in enumerate(lines):
    if l.startswith('> ### Rip it: RIPPS2 build 141'):
        fn = header
    elif l.startswith('> 1. **[Download RIPPS2.elf]'):
        fn = sizes
    elif l.startswith("> [What's new in build 141]"):
        fn = whatsnew
    else:
        continue
    n = fn(l)
    assert n != l, l[:60]
    fixes.append((l, n, fn))
    lines[i] = n
assert len(fixes) == 3, [f[2].__name__ for f in fixes]
out = '\n'.join(lines)

jsons = {}
for code in R.CODES[1:]:
    jp = REPO / 'i18n' / (code + '.json')
    jraw = jp.read_bytes().decode('utf-8')
    d = json.loads(jraw)
    for old, new, fn in fixes:
        oid, nid = R.sid(old), R.sid(new)
        e = d.pop(oid)
        t = fn(e['t'], code)
        assert t != e['t'], (code, fn.__name__)
        bad = R.problems(new, t)
        assert not bad, (code, fn.__name__, bad, t[:300])
        d[nid] = {'en': nid, 't': t}
    jsons[jp] = (d, '\r\n' in jraw)


def edit(path, pairs):
    b = path.read_bytes().decode('utf-8')
    eol = '\r\n' if '\r\n' in b else '\n'
    for o, n in pairs:
        o2 = o.replace('\n', eol)
        assert b.count(o2) == 1, (path.name, b.count(o2), o[:70])
        b = b.replace(o2, n.replace('\n', eol))
    assert '—' not in b or path.name.endswith('.md'), path.name
    return b


D = REPO / 'tools' / 'discord'
post = edit(D / 'psxplace-post.bbcode', [
    ('Current release: v1.4.1 beta (build 141)', 'Current release: v1.4.3 beta (build 143)'),
    ('in a single .elf (2,775 KB)', 'in a single .elf (2,750 KB)'),
])
card_old = "[*][LEFT][B]SD2PSX owners[/B]: [URL='https://github.com/akilluminati47/BIBLE/releases/latest/download/BIBLE-SD2PSX-BootCard-3282396.zip']BIBLE-SD2PSX-BootCard-3282396.zip[/URL] is a ready BOOT card with BIBLE already bound."
if BOOTCARD:
    card_new = "[*][LEFT][B]SD2PSX owners[/B]: [URL='https://github.com/akilluminati47/BIBLE/releases/latest/download/BIBLE-SD2PSX-BootCard-f5705eb.zip']BIBLE-SD2PSX-BootCard-f5705eb.zip[/URL] is a ready BOOT card with BIBLE already bound."
else:
    card_new = "[*][LEFT][B]SD2PSX owners[/B]: [URL='https://github.com/akilluminati47/BIBLE/releases/download/signed-3282396/BIBLE-SD2PSX-BootCard-3282396.zip']BIBLE-SD2PSX-BootCard-3282396.zip[/URL] is a ready BOOT card with the older BIBLE already bound, and that build's AUTO hang: update it from Manage."
bible = edit(D / 'psxplace-bible-post.bbcode', [
    ('Current: BIBLE 3282396, carried by RIPPS2 v1.4.1 beta', 'Current: BIBLE f5705eb, carried by RIPPS2 v1.4.3 beta'),
    (card_old, card_new),
    ("[URL='https://github.com/akilluminati47/BIBLE/releases/latest/download/BIBLE-signed-3282396.zip']BIBLE-signed-3282396.zip[/URL]",
     "[URL='https://github.com/akilluminati47/BIBLE/releases/latest/download/BIBLE-signed-f5705eb.zip']BIBLE-signed-f5705eb.zip[/URL]"),
    ('[SPOILER="Changes"]\n[B]3282396[/B]',
     '[SPOILER="Changes"]\n[B]f5705eb[/B] (with RIPPS2 1.4.3): a missing file on an AUTO path, on a drive BIBLE has to load a driver for, no longer stops the boot on the splash. BIBLE no longer reads boot.adp into memory, it only tells RIPPS2 the folder. The stage 2 loader is out of the MMCE, MX4SIO and HDD builds. Its own card icon. A plain ELF for consoles with no system update, started by OpenTuna or FunTuna. Lab only so far.\n[B]3282396[/B]'),
])

# everything checked: now write
p.write_bytes((out.replace('\n', '\r\n') if crlf else out).encode('utf-8'))
for jp, (d, jcrlf) in jsons.items():
    js = json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True) + '\n'
    jp.write_bytes((js.replace('\n', '\r\n') if jcrlf else js).encode('utf-8'))
(D / 'psxplace-post.bbcode').write_bytes(post.encode('utf-8'))
(D / 'psxplace-bible-post.bbcode').write_bytes(bible.encode('utf-8'))
print('ok: README and', len(jsons), 'languages, both first posts. Next: python tools/readme-i18n/readme_i18n.py check . then build .')
