"""Print RIPPS2's DIAG ring from a running lab PCSX2 over PINE (slot 28012), no menu steps needed. The ring's address comes from
the unstripped opl.elf CI uploads as RIPPS2-symbols. Usage: diagring.py <opl.elf> <seconds to wait> <out.txt>"""
import socket
import struct
import sys
import time


def symbol(path, name):
    d = open(path, 'rb').read()
    assert d[:4] == b'\x7fELF' and d[4] == 1 and d[5] == 1
    shoff, = struct.unpack_from('<I', d, 32)
    shentsize, shnum = struct.unpack_from('<HH', d, 46)
    for i in range(shnum):
        sh = struct.unpack_from('<10I', d, shoff + i * shentsize)
        if sh[1] != 2:  # SHT_SYMTAB
            continue
        link = struct.unpack_from('<10I', d, shoff + sh[6] * shentsize)
        strs = d[link[4]:link[4] + link[5]]
        for j in range(sh[5] // 16):
            nm, val, size = struct.unpack_from('<III', d, sh[4] + j * 16)
            if strs[nm:strs.index(b'\0', nm)] == name:
                return val, size
    raise SystemExit('no symbol ' + name.decode())


def read_block(addr, size, port=28012):
    out = bytearray()
    s = socket.create_connection(('127.0.0.1', port), timeout=10)
    s.settimeout(10)
    try:
        step = 8
        batch = 256
        for a in range(addr, addr + size, step * batch):
            n = min(batch, (addr + size - a + step - 1) // step)
            msg = b''.join(b'\x03' + struct.pack('<I', a + k * step) for k in range(n))
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
    return bytes(out[:size])


addr, size = symbol(sys.argv[1], b'diagRing')
deadline = time.time() + float(sys.argv[2])
last = b''
bgm, _ = symbol(sys.argv[1], b'bgmIsPlaying')
start = None
samples = []
while time.time() < deadline:
    try:
        last = read_block(addr, size)
        word = read_block(bgm & ~7, 8)
        if start is None:
            start = time.time()
        samples.append(('%.0f' % (time.time() - start), word[bgm & 7]))
    except OSError:
        pass
    time.sleep(3)
text = last.split(b'\0')[0].decode('latin1').replace('\r', '')
text += '\nmusic flag by seconds since the first read: ' + ' '.join('%s:%d' % s for s in samples) + '\n'
open(sys.argv[3], 'w', encoding='utf-8').write(text)
print('diagRing at %#x, %d bytes used' % (addr, len(text)))
print(text)
