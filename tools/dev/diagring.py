"""Print RIPPS2's DIAG ring and sound trace from a running lab PCSX2 over PINE (slot 28012), no menu steps needed. Addresses come from the unstripped
opl.elf CI uploads as RIPPS2-symbols. Usage: diagring.py <opl.elf> <seconds to keep reading> <out.txt>. The last good read wins, so stop before a game launches.
Also decodes a saved DIAG.TXT's "who asked" column: diagring.py <opl.elf> --names <DIAG.TXT>"""
import bisect
import re
import socket
import struct
import sys
import time

NAMES = ['boot', 'cancel', 'confirm', 'cursor', 'message', 'transition', 'bd_connect', 'bd_disconnect', 'page_in', 'page_out', 'error', 'save', 'launch', 'disc', 'random']
WHAT = ['played', 'NO VOICE', 'off', 'held', 'dropped, loading', 'no sound', 'drive sound quiet', 'waits for frame', 'same, too soon', 'gave way', 'muted', 'LOAD starts', 'LOAD ends', 'boot sound']


def symbols(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'\x7fELF' and d[4] == 1 and d[5] == 1
    shoff, = struct.unpack_from('<I', d, 32)
    shentsize, shnum = struct.unpack_from('<HH', d, 46)
    objs, funcs = {}, []
    for i in range(shnum):
        sh = struct.unpack_from('<10I', d, shoff + i * shentsize)
        if sh[1] != 2:  # SHT_SYMTAB
            continue
        link = struct.unpack_from('<10I', d, shoff + sh[6] * shentsize)
        strs = d[link[4]:link[4] + link[5]]
        for j in range(sh[5] // 16):
            nm, val, size, info = struct.unpack_from('<IIIB', d, sh[4] + j * 16)
            name = strs[nm:strs.index(b'\0', nm)].decode('latin1')
            if info & 15 == 2:
                funcs.append((val, name))
            elif name:
                objs.setdefault(name, (val, size))
    funcs.sort()
    return objs, funcs


def func_of(funcs, addr):
    if not addr:
        return '-'
    i = bisect.bisect_right([f[0] for f in funcs], addr) - 1
    return funcs[i][1] if i >= 0 else '%08X' % addr


def read_block(addr, size, port=28012):
    out = bytearray()
    s = socket.create_connection(('127.0.0.1', port), timeout=10)
    s.settimeout(10)
    try:
        base = addr & ~7
        total = size + addr - base
        for a in range(base, base + total, 8 * 256):
            n = min(256, (base + total - a + 7) // 8)
            msg = b''.join(b'\x03' + struct.pack('<I', a + k * 8) for k in range(n))
            s.sendall(struct.pack('<I', len(msg) + 4) + msg)
            need = 5 + 8 * n
            r = b''
            while len(r) < need:
                c = s.recv(need - len(r))
                if not c:
                    raise OSError('closed')
                r += c
            if r[4] != 0:
                raise OSError('PINE refused')
            out += r[5:]
    finally:
        s.close()
    return bytes(out[addr - base:addr - base + size])


def snd(i):
    return NAMES[i] if 0 <= i < len(NAMES) else '-'


if __name__ == '__main__':
    objs, funcs = symbols(sys.argv[1])
    if sys.argv[2] == '--names':
        for line in open(sys.argv[3], encoding='latin1'):
            line = line.rstrip()
            m = re.search(r' ([0-9A-F]{8})$', line)
            print(line[:-8] + func_of(funcs, int(m.group(1), 16)) if m else line)
        sys.exit(0)
    ring, ring_size = objs['diagRing']
    tr, tr_size = objs.get('sfxTraceRing', (0, 0))
    count = objs.get('sfxTraceCount', (0, 0))[0]
    bgm = objs['bgmIsPlaying'][0]
    deadline = time.time() + float(sys.argv[2])
    last, trace, n, start, samples = b'', b'', 0, None, []
    while time.time() < deadline:
        try:
            d = read_block(ring, ring_size)
            flag = read_block(bgm, 1)[0]
            if tr:
                t, c = read_block(tr, tr_size), struct.unpack('<I', read_block(count, 4))[0]
                trace, n = t, c
            last = d
            start = start or time.time()
            samples.append('%.0f:%d' % (time.time() - start, flag))
        except OSError:
            pass
        time.sleep(3)
    text = last.split(b'\0')[0].decode('latin1').replace('\r', '')
    text += '\nmusic flag by seconds since the first read: ' + ' '.join(samples) + '\n'
    if trace:
        max_e = tr_size // 16
        text += '\nsound trace, %d events:\n' % n
        for i in range(max(0, n - max_e), n):
            ms, frm, asked, played, voice, what, live = struct.unpack_from('<IIbbbBB', trace, (i % max_e) * 16)
            text += '%7.2f  %-14s %-14s v%-2d live %-2d %-18s %s\n' % (ms / 1000, snd(asked), snd(played), voice, live, WHAT[what] if what < len(WHAT) else '?', func_of(funcs, frm))
    open(sys.argv[3], 'w', encoding='utf-8').write(text)
    print(text)
