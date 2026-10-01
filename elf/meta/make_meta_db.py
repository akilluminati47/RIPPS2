"""RIPPS2 metadata database tools.

The database is one small text file per game, db/<GAMEID>.cfg, in OPL's key=value form (Title,
Description, Genre, Developer, Publisher, Release, Players, Vmode, Aspect, Scan, Rating). RIPPS2 reads
it from CFG/cfg.tar on the drive the game is on (the archive layout wOPL also reads). The game's own
CFG/<GAMEID>.cfg keeps its settings ($ keys), and anything written there wins on the PS2.

    python make_meta_db.py pack [--out cfg.tar]
        Checks db/*.cfg, applies overrides/<GAMEID>.cfg on top (hand-written fixes: a key there
        replaces the database's), and writes the archive. Copy it to <drive>/CFG/cfg.tar.

    python make_meta_db.py split <CFG folder> <out folder>
        For an existing OPL CFG folder: writes settings-only copies of every <GAMEID>.cfg to
        <out folder>/CFG/ and the metadata it found to <out folder>/db/, so the metadata can move
        into the archive. The input folder is never modified.

    python make_meta_db.py check
        Only the checks.
"""
import io
import os
import re
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, 'db')
OVERRIDES = os.path.join(HERE, 'overrides')

META_KEYS = ['Title', 'Description', 'Genre', 'Developer', 'Publisher', 'Release', 'Players', 'Vmode',
             'Aspect', 'Scan', 'Rating', 'Esrb', 'Language', 'Notes']
BADGES = {'Players': r'players/[1-8]', 'Vmode': r'vmode/(ntsc|pal|multi)', 'Aspect': r'aspect/(s|w|w1|w2)',
          'Scan': r'scan/(240p|240p1|480i|480p|480p1|480p2|480p3|480p4|480p5|576i|576p|720p|1080i|1080i2|1080p)',
          'Rating': r'rating/[0-5]'}
ID_RE = re.compile(r'^[A-Z]{4}_\d{3}\.\d{2}$')
VALUE_MAX = 255  # the PS2 side's value field, NUL included
ENTRY_MAX = 4096


def read_cfg(path):
    keys = {}
    for raw in open(path, 'rb').read().decode('latin-1').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or line.startswith('//') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        keys[k.strip()] = v.strip()
    return keys


def write_cfg(keys):
    order = [k for k in META_KEYS if k in keys] + sorted(k for k in keys if k not in META_KEYS)
    return ''.join('%s=%s\n' % (k, keys[k]) for k in order).encode('ascii')


def check(gid, keys, where):
    problems = []
    if not ID_RE.match(gid):
        problems.append('%s: %s is not a disc id like SLUS_210.50' % (where, gid))
    for k, v in keys.items():
        if k.startswith('$'):
            problems.append('%s: %s is a setting; settings belong in the game\'s own CFG' % (where, k))
        if k not in META_KEYS:
            problems.append('%s: unknown key %s' % (where, k))
        if len(v.encode('latin-1', 'replace')) > VALUE_MAX - 1:
            problems.append('%s: %s is %d characters (at most %d)' % (where, k, len(v), VALUE_MAX - 1))
        if any(ord(c) > 126 or ord(c) < 32 for c in v):
            problems.append('%s: %s has non-ASCII characters' % (where, k))
        if '—' in v or '–' in v or ' -- ' in v:
            problems.append('%s: %s has a dash used as punctuation' % (where, k))
        if k in BADGES and not re.fullmatch(BADGES[k], v):
            problems.append('%s: %s=%s is not a value the badges know' % (where, k, v))
    if 'Title' not in keys:
        problems.append('%s: no Title' % where)
    return problems


def load_db():
    entries = {}
    if not os.path.isdir(DB):
        return entries
    for name in sorted(os.listdir(DB)):
        if name.lower().endswith('.cfg'):
            entries[name[:-4]] = read_cfg(os.path.join(DB, name))
    if os.path.isdir(OVERRIDES):
        for name in sorted(os.listdir(OVERRIDES)):
            if name.lower().endswith('.cfg'):
                gid = name[:-4]
                entries.setdefault(gid, {}).update(read_cfg(os.path.join(OVERRIDES, name)))
    return entries


def cmd_check():
    entries = load_db()
    problems = []
    for gid, keys in entries.items():
        problems += check(gid, keys, gid)
    for p in problems:
        print('  ' + p)
    print('%d games, %d problems' % (len(entries), len(problems)))
    return entries, problems


def cmd_pack(out):
    entries, problems = cmd_check()
    if problems:
        sys.exit('not packed: fix the problems above first')
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w', format=tarfile.USTAR_FORMAT) as tar:
        for gid in sorted(entries):
            data = write_cfg(entries[gid])
            if len(data) > ENTRY_MAX:
                sys.exit('%s: the entry is %d bytes (at most %d)' % (gid, len(data), ENTRY_MAX))
            info = tarfile.TarInfo(gid + '.cfg')
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            tar.addfile(info, io.BytesIO(data))
    open(out, 'wb').write(buf.getvalue())
    print('wrote %s (%d games, %d bytes)' % (out, len(entries), len(buf.getvalue())))


def cmd_split(src, out):
    os.makedirs(os.path.join(out, 'CFG'), exist_ok=True)
    os.makedirs(os.path.join(out, 'db'), exist_ok=True)
    moved = 0
    for name in sorted(os.listdir(src)):
        gid = name[:-4]
        if not name.lower().endswith('.cfg') or not ID_RE.match(gid):
            continue
        keys = read_cfg(os.path.join(src, name))
        meta = {k: v for k, v in keys.items() if k in META_KEYS}
        settings = {k: v for k, v in keys.items() if k not in META_KEYS}
        if meta:
            open(os.path.join(out, 'db', name), 'wb').write(write_cfg(meta))
            moved += 1
        if settings:
            text = ''.join('%s=%s\r\n' % (k, v) for k, v in settings.items())
            open(os.path.join(out, 'CFG', name), 'wb').write(text.encode('latin-1'))
    print('split %s: metadata for %d games in %s, settings in %s' % (src, moved, os.path.join(out, 'db'), os.path.join(out, 'CFG')))


def main():
    args = sys.argv[1:]
    if not args or args[0] == 'check':
        cmd_check()
    elif args[0] == 'pack':
        out = args[args.index('--out') + 1] if '--out' in args else os.path.join(HERE, 'cfg.tar')
        cmd_pack(out)
    elif args[0] == 'split' and len(args) == 3:
        cmd_split(args[1], args[2])
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
