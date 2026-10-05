"""Writes a freshly formatted 8 MB PS2 memory card image (PCSX2 .ps2: 16384 pages of 512 bytes, each
followed by 16 spare bytes of ECC), laid out the way the console formats one (mymc's layout):

  cluster 0        superblock          clusters 8      indirect FAT cluster (lists the FAT clusters)
  clusters 9..40   FAT (32 clusters)   clusters 41..   allocatable; the root directory is the first
  last two erase blocks: backup blocks (left erased)

    python make_mc_image.py <out.ps2>
"""
import struct
import sys
import time

PAGE = 512
SPARE = 16
PPC = 2                      # pages per cluster
PPB = 16                     # pages per erase block
CLUSTER = PAGE * PPC
CLUSTERS = 8192
ALLOC_OFFSET = 41
ALLOC_END = 8135
IFC = 8
FAT_FIRST, FAT_COUNT = 9, 32
BACKUP1, BACKUP2 = 1023, 1022


def popcount(x):
    return bin(x).count('1')


PARITY = [popcount(b) & 1 for b in range(256)]
CPMASKS = [0x55, 0x33, 0x0F, 0x00, 0xAA, 0xCC, 0xF0]
COLMASK = [sum(PARITY[b & m] << i for i, m in enumerate(CPMASKS)) for b in range(256)]


def ecc128(chunk):
    cp, lp0, lp1 = 0x77, 0x7F, 0x7F
    for i, b in enumerate(chunk):
        cp ^= COLMASK[b]
        if PARITY[b]:
            lp0 ^= ~i
            lp1 ^= i
    return bytes([cp & 0xFF, lp0 & 0x7F, lp1 & 0xFF])


def spare_for(page):
    ecc = b''.join(ecc128(page[i:i + 128]) for i in range(0, PAGE, 128))
    return ecc + b'\0' * (SPARE - len(ecc))


def tod():
    t = time.gmtime()
    # sec, min, hour, day, month, year (the PS2's date-time layout, 8 bytes)
    return struct.pack('<xBBBBBH', t.tm_sec, t.tm_min, t.tm_hour, t.tm_mday, t.tm_mon, t.tm_year)


def dir_entry(mode, length, cluster, name):
    e = bytearray(512)
    struct.pack_into('<HxxI', e, 0, mode, length)
    e[8:16] = tod()
    struct.pack_into('<II', e, 16, cluster, 0)
    e[24:32] = tod()
    struct.pack_into('<I', e, 32, 0)
    e[64:64 + len(name)] = name
    return bytes(e)


def main():
    clusters = [b'\xff' * CLUSTER for _ in range(CLUSTERS)]

    sb = bytearray(b'\xff' * CLUSTER)
    sb[0:0x152] = b'\0' * 0x152
    sb[0:28] = b'Sony PS2 Memory Card Format '
    sb[0x1C:0x1C + 12] = b'1.2.0.0'.ljust(12, b'\0')
    struct.pack_into('<HHHH', sb, 0x28, PAGE, PPC, PPB, 0xFF00)
    struct.pack_into('<IIIIII', sb, 0x30, CLUSTERS, ALLOC_OFFSET, ALLOC_END, 0, BACKUP1, BACKUP2)
    struct.pack_into('<32I', sb, 0x50, *([IFC] + [0] * 31))
    struct.pack_into('<32I', sb, 0xD0, *([0xFFFFFFFF] * 32))
    sb[0x150], sb[0x151] = 2, 0x52
    clusters[0] = bytes(sb)

    # the indirect FAT cluster lists the FAT clusters
    ifc = list(range(FAT_FIRST, FAT_FIRST + FAT_COUNT)) + [0xFFFFFFFF] * (256 - FAT_COUNT)
    clusters[IFC] = struct.pack('<256I', *ifc)

    # the FAT: every allocatable cluster free, except the root directory (alloc cluster 0, one cluster)
    fat = [0x7FFFFFFF] * (FAT_COUNT * 256)
    fat[0] = 0xFFFFFFFF
    for i in range(ALLOC_END, len(fat)):
        fat[i] = 0xFFFFFFFF if i < ALLOC_END else fat[i]
    for k in range(FAT_COUNT):
        clusters[FAT_FIRST + k] = struct.pack('<256I', *fat[k * 256:(k + 1) * 256])

    # the root directory: "." and ".."
    root = dir_entry(0x8427, 2, 0, b'.') + dir_entry(0xA426, 0, 0, b'..')
    clusters[ALLOC_OFFSET] = root

    out = bytearray()
    for c in clusters:
        for p in range(PPC):
            page = c[p * PAGE:(p + 1) * PAGE]
            out += page + (spare_for(page) if page != b'\xff' * PAGE else b'\xff' * SPARE)
    open(sys.argv[1], 'wb').write(bytes(out))
    print('wrote', sys.argv[1], len(out))


if __name__ == '__main__':
    main()
