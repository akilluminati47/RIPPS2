"""RIPPS2 host tests (build 76): RiptOPL's own host checks, run on the patched tree, plus RIPPS2's.

    python3 elf/tests/run_host_tests.py riptopl      (riptopl = the tree elf/build.sh --prepare-only made)

Every RiptOPL test (<tree>/.github/scripts/test_*.py) and every RIPPS2 test (elf/tests/test_ripps2_*.py)
runs. A failure fails the run unless expected_failures.txt names that test with the reason RIPPS2
differs on purpose; a listed test that passes again is reported so its line can go.
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def expected():
    out = {}
    for line in (HERE / 'expected_failures.txt').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            name, _, why = line.partition(' ')
            out[name] = why.strip()
    return out


def main():
    tree = Path(sys.argv[1] if len(sys.argv) > 1 else 'riptopl').resolve()
    tests = sorted((tree / '.github' / 'scripts').glob('test_*.py')) + sorted(HERE.glob('test_ripps2_*.py'))
    env = dict(os.environ, RIPTOPL_DIR=str(tree))
    allowed = expected()
    bad, stale = [], []
    for t in tests:
        r = subprocess.run([sys.executable, str(t)], cwd=str(tree), env=env, capture_output=True, text=True, timeout=600)
        ok = r.returncode == 0
        tag = 'PASS' if ok else ('EXPECTED' if t.name in allowed else 'FAIL')
        print('%-8s %s' % (tag, t.name))
        if not ok and t.name not in allowed:
            bad.append(t.name)
            print('\n'.join('    ' + l for l in (r.stdout + r.stderr).strip().splitlines()[-25:]))
        if ok and t.name in allowed:
            stale.append(t.name)
    for name in stale:
        print('NOTE     %s passes now: take it out of expected_failures.txt' % name)
    print('%d tests, %d failed unexpectedly' % (len(tests), len(bad)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
