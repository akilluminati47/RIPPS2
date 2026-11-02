"""RIPPS2 build 130: a long video opens. The AVI index (libsmslite demux/avi.c) keeps a bit per video frame, the key
frames and each audio chunk's place, sized once from the header (a two-hour film froze on "Opening the video": 600,000
entries of 12 bytes grown a sixteenth at a time, a failed grow written through). With no room it plays without
skipping. The player's steps go to VIDEO.TXT (smsLiteSetStageLog), and a PS1 game's name comes from the conf_apps.cfg on
its own drive too. On the PC: avi.c itself, built against a made-up AVI, read through, skipped in, and starved."""
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
sms = Path(__file__).resolve().parents[1] / 'libsmslite'
fail = []


def text(p):
    p = Path(p)
    if not p.exists():
        fail.append(str(p) + ' missing')
        return ''
    return p.read_text(encoding='utf-8', errors='replace')


avi = text(sms / 'src/demux/avi.c')
lite = text(sms / 'src/smslite.c')
lite_h = text(sms / 'include/smslite.h')
media = text(root / 'src/ripps2media.c')
vcd = text(root / 'src/vcdsupport.c')
mix = text(root / 'src/mixsupport.c')
opl = text(root / 'src/opl.c')
menusys = text(root / 'src/menusys.c')
files = text(root / 'src/ripps2files.c')


def body(src, start):
    i = src.find(start)
    return src[i:src.find('\n}\n', i)] if i >= 0 else ''


build_rows = body(mix, 'static int mixBuildRows(')

checks = [
    ('SMS_Realloc' not in avi, 'avi.c: the index no longer grows through SMS_Realloc'),
    ('_IdxAdd' in avi and '_IdxDrop' in avi and 'm_pKeyBits' in avi, 'avi.c: _IdxAdd / _IdxDrop and the key bitmap'),
    (avi.count('m_IdxHint') >= 3, 'avi.c: the header\'s counts size the index'),
    ('void smsLiteSetStageLog' in lite_h and 'smsLiteStage("playing: first frame on screen")' in lite, 'smslite: the stage log'),
    ('smsLiteSetStageLog(videoStageLog)' in media and 'VIDEO.TXT' in media, 'ripps2media.c: VIDEO.TXT beside RIPPS2'),
    ('vcdDriveAppsLoad(devPrefix, vcds, n)' in vcd and '"OPL/conf_apps.cfg"' in vcd, 'vcdsupport.c: the drive\'s own conf_apps.cfg'),
    # START rows: made after the master list is written (never saved), last, and only Cross acts on them
    ('MIX_KIND_START' in build_rows and build_rows.find('mixMasterSave(') < build_rows.rfind('MIX_KIND_START'),
     'mixBuildRows: START rows come after the master list is saved'),
    ('return mixStartRowRun(menu, rows, fam);' in mix, 'mixWaitForRow: a START row starts its drive, never launches'),
    (opl.count('itemIsStartRow(curMenu)') >= 3, 'opl.c: Square, Triangle and R3 leave a START row alone'),
    ('menuRandomSkips(it)' in menusys and 'mixIsStartRow' in menusys, 'menusys.c: the random pick skips START rows'),
    # Memory Files: a memory card folder in one mcGetDir; a copy's size check without the 64-bit seek a card lacks
    ('fbScanMcDir(sized)' in files and 'mcGetDir(port, 0, path, 0, FB_MAX, tbl)' in files, 'ripps2files.c: mcGetDir listing'),
    ('size = lseek(chk, 0, SEEK_END);' in files, 'ripps2files.c: the copy check falls back to lseek'),
]
for ok, what in checks:
    if not ok:
        fail.append(what)

# ---- a made-up AVI: 1000 frames (a key every 250), 1700 audio chunks, interleaved, with idx1 ----
FRAMES, KEYS = 1000, 250


def chunk(tag, data):
    return tag + struct.pack('<I', len(data)) + data + (b'\0' if len(data) & 1 else b'')


def lst(kind, body):
    return b'LIST' + struct.pack('<I', len(body) + 4) + kind + body


strh_v = b'vids' + b'XVID' + struct.pack('<IHHIIIIIIIIhhhh', 0, 0, 0, 0, 1, 25, 0, FRAMES, 0, 0, 0, 0, 0, 320, 240)
strf_v = struct.pack('<IiiHH', 40, 320, 240, 1, 24) + b'XVID' + struct.pack('<IiiII', 0, 0, 0, 0, 0)
movi, idx, apos_before = b'', [], []
audio_n = 0
for f in range(FRAMES):
    apos_before.append(audio_n)
    off = 4 + len(movi)  # idx1's places count from the 'movi' tag
    data = bytes([f & 0xFF]) * (100 + f % 7)
    idx.append((b'00dc', 0x10 if f % KEYS == 0 else 0, off, len(data)))
    movi += chunk(b'00dc', data)
    for _ in range(2 if f % 10 < 7 else 1):
        off = 4 + len(movi)
        data = b'\xAA' * 48
        idx.append((b'01wb', 0x10, off, len(data)))
        movi += chunk(b'01wb', data)
        audio_n += 1
strh_a = b'auds' + b'\0\0\0\0' + struct.pack('<IHHIIIIIIIIhhhh', 0, 0, 0, 0, 1152, 48000, 0, audio_n, 0, 0, 0, 0, 0, 0, 0)
strf_a = struct.pack('<HHIIHHH', 0x55, 2, 48000, 16000, 1, 0, 0)
avih = struct.pack('<IIIIIIIIII', 40000, 0, 0, 0x110, FRAMES, 0, 2, 0, 320, 240) + b'\0' * 16
hdrl = lst(b'hdrl', chunk(b'avih', avih) + lst(b'strl', chunk(b'strh', strh_v) + chunk(b'strf', strf_v)) +
           lst(b'strl', chunk(b'strh', strh_a) + chunk(b'strf', strf_a)))
idx1 = chunk(b'idx1', b''.join(t + struct.pack('<III', fl, o, n) for t, fl, o, n in idx))
body = b'AVI ' + hdrl + lst(b'movi', movi) + idx1
riff = b'RIFF' + struct.pack('<I', len(body)) + body

PROG = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "demux/avi.h"
#undef realloc  /* avi.c's reallocs come here (-Drealloc=t_realloc); this file's own go to the C library */
void* realloc ( void*, size_t );

void* g_pSynthBuffer;
void SMSContainer_SetPTSInfo ( SMS_Stream* s, int a, int b ) { (void)s; (void)a; (void)b; }
void SMSContainer_CalcPktFields ( SMS_Stream* s, SMS_AVPacket* p ) { (void)s; (void)p; }
void SMSContainer_GetWAVHeader ( FileContext* f, SMS_CodecContext* c, int n ) {
 f -> Seek ( f, f -> m_CurPos + n ); c -> m_Type = SMS_CodecTypeAudio; c -> m_ID = SMS_CodecID_MP3;
}
SMS_CodecID SMS_CodecGetID ( SMS_CodecType t, uint32_t g ) { (void)t; (void)g; return SMS_CodecID_MPEG4; }
s64 SMS_Rescale ( s64 a, s64 b, s64 c ) { return c ? a * b / c : 0; }
#include <stdarg.h>
void smsLiteStage ( const char* fmt, ... ) { va_list a; if ( !getenv ( "B130_VERBOSE" ) ) return; va_start ( a, fmt ); vprintf ( fmt, a ); va_end ( a ); putchar ( 10 ); }

static unsigned char* g_data; static unsigned int g_size;
static size_t g_max; static int g_reallocs, g_limit;
void* t_realloc ( void* p, size_t n ) {
 if ( g_limit && n > ( size_t )g_limit ) return NULL;
 if ( n > g_max ) g_max = n;
 ++g_reallocs;
 return realloc ( p, n );
}
static int mRead ( FileContext* f, void* b, unsigned int n ) {
 if ( f -> m_CurPos >= g_size ) return 0;
 if ( n > g_size - f -> m_CurPos ) n = g_size - f -> m_CurPos;
 memcpy ( b, g_data + f -> m_CurPos, n ); f -> m_CurPos += n;
 f -> m_pPos = f -> m_pEnd = g_data + f -> m_CurPos; return ( int )n;
}
static int mSeek ( FileContext* f, unsigned int p ) { f -> m_CurPos = p; f -> m_pPos = f -> m_pEnd = g_data + ( p < g_size ? p : g_size ); return ( int )p; }
static int mFill ( FileContext* f ) { unsigned char b; return 0 * f -> m_CurPos + 0 * b; }
static int mStream ( FileContext* f, unsigned int a, unsigned int b ) { (void)f; (void)a; (void)b; return 1; }
static unsigned char g_pkt[ 4096 ]; static SMS_AVPacket g_p;
static SMS_AVPacket* mAlloc ( SMS_RingBuffer* r, int n ) { (void)r; memset ( &g_p, 0, sizeof ( g_p ) ); g_p.m_pData = g_pkt; g_p.m_Size = n; return n <= 4096 ? &g_p : NULL; }
static int mGetByteFill ( FileContext* f ) { return f -> m_CurPos < g_size ? ( f -> m_pEnd = g_data + g_size, 1 ) : 0; }

int main ( int argc, char** argv ) {
 FILE* fp = fopen ( argv[ 1 ], "rb" ); SMS_Container c; FileContext f;
 int starved = atoi ( argv[ 2 ] ), key500audio = atoi ( argv[ 3 ] ), r, i, idx, nv = 0, na = 0, keys = 0, sz;
 int32_t sc, ra; uint32_t n;
 fseek ( fp, 0, SEEK_END ); g_size = ( unsigned int )ftell ( fp ); fseek ( fp, 0, SEEK_SET );
 g_data = malloc ( g_size ); if ( fread ( g_data, 1, g_size, fp ) != g_size ) return 90; fclose ( fp );
 g_limit = starved ? 4000 : 0;
 memset ( &f, 0, sizeof ( f ) ); memset ( &c, 0, sizeof ( c ) );
 f.m_Size = g_size; f.m_pPos = f.m_pEnd = g_data; f.Read = mRead; f.Seek = mSeek; f.Fill = mGetByteFill; f.Stream = mStream;
 (void)mFill;
 c.m_pFileCtx = &f; c.AllocPacket = mAlloc;
 r = SMS_GetContainerAVI ( &c );
 if ( r != 1 || c.m_nStm != 2 ) { printf ( "parse %d, %u streams\n", r, c.m_nStm ); return 1; }
 for ( i = 0; i < 2; ++i ) c.m_pStm[ i ] -> m_pPktBuf = ( SMS_RingBuffer* )&g_p;
 if ( starved ) {
  if ( c.m_Flags & SMS_CONT_FLAGS_SEEKABLE ) { printf ( "starved but seekable\n" ); return 2; }
  if ( smsLiteAviTiming ( &c, 0, &sc, &ra, &n ) != -1 ) { printf ( "starved but timed\n" ); return 3; }
  if ( smsLiteAviKeyFrame ( &c, 0, 1, 10 ) != -1 ) { printf ( "starved but keyed\n" ); return 4; }
 } else {
  if ( !( c.m_Flags & SMS_CONT_FLAGS_SEEKABLE ) ) { printf ( "not seekable\n" ); return 5; }
  if ( smsLiteAviTiming ( &c, 0, &sc, &ra, &n ) || n != 1000 ) { printf ( "timing n %u\n", n ); return 6; }
  if ( smsLiteAviKeyFrame ( &c, 0, 1, 251 ) != 500 || smsLiteAviKeyFrame ( &c, 0, -1, 251 ) != 250 ||
       smsLiteAviKeyFrame ( &c, 0, 1, 999 ) != -1  || smsLiteAviKeyFrame ( &c, 0, -1, 999 ) != 750 ||
       smsLiteAviKeyFrame ( &c, 0, 1, 0 ) != 0     || smsLiteAviKeyFrame ( &c, 0, -1, 500 ) != 500 ) { printf ( "key frames\n" ); return 7; }
  if ( g_reallocs > 8 || g_max > ( 1700 + 64 ) * 4 + 64 ) { printf ( "index grown %d times, largest %u\n", g_reallocs, ( unsigned )g_max ); return 8; }
 }
 while (  ( sz = c.ReadPacket ( &c, &idx ) ) > 0  ) {
  if ( idx == 0 ) { if ( g_p.m_Flags & SMS_PKT_FLAG_KEY ) { if ( g_p.m_DTS % 250 ) { printf ( "key at %d\n", ( int )g_p.m_DTS ); return 9; } ++keys; } ++nv; }
  else ++na;
 }
 if ( nv != 1000 || na != 1700 ) { printf ( "read %d video, %d audio\n", nv, na ); return 10; }
 if ( !starved && keys != 4 ) { printf ( "%d keys\n", keys ); return 11; }
 if ( !starved ) {
  int gotV = -1, gotA = -1;
  if ( !c.Seek ( &c, 0, 1, 260 ) ) { printf ( "seek refused\n" ); return 12; }
  while (  ( gotV < 0 || gotA < 0 ) && c.ReadPacket ( &c, &idx ) > 0  ) {
   if ( idx == 0 && gotV < 0 ) { gotV = ( int )g_p.m_DTS; if ( !( g_p.m_Flags & SMS_PKT_FLAG_KEY ) ) { printf ( "landed off a key\n" ); return 13; } }
   if ( idx == 1 && gotA < 0 ) gotA = ( int )g_p.m_DTS;
  }
  if ( gotV != 500 || gotA != key500audio ) { printf ( "seek landed v %d a %d (want 500, %d)\n", gotV, gotA, key500audio ); return 14; }
  if ( !c.Seek ( &c, 0, -1, 999 ) || c.ReadPacket ( &c, &idx ) <= 0 || idx != 0 || g_p.m_DTS != 750 ) { printf ( "back seek\n" ); return 15; }
 }
 for ( i = 0; i < 2; ++i ) c.m_pStm[ i ] -> Destroy ( c.m_pStm[ i ] );
 printf ( "ok\n" );
 return 0;
}
'''

STUB_TAM = '''#ifndef TAMTYPES_H
#define TAMTYPES_H
#include <stdint.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef uint64_t u64;
typedef int8_t s8; typedef int16_t s16; typedef int32_t s32; typedef int64_t s64;
typedef struct { u64 lo, hi; } u128;
#endif
'''
STUB_KERNEL = '''static inline int SignalSema(int s) { (void)s; return 0; }
static inline int WaitSema(int s) { (void)s; return 0; }
static inline int PollSema(int s) { (void)s; return 0; }
static inline int iSignalSema(int s) { (void)s; return 0; }
'''

cc = shutil.which('gcc') or shutil.which('cc')
if cc is None or not avi:
    print('\n'.join(fail) or 'build130: no host C compiler, programs skipped')
    sys.exit(1 if fail else 0)

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    (td / 'stub').mkdir()
    (td / 'stub/tamtypes.h').write_text(STUB_TAM, encoding='utf-8')
    (td / 'stub/kernel.h').write_text(STUB_KERNEL, encoding='utf-8')
    (td / 't.avi').write_bytes(riff)
    (td / 't.c').write_text(PROG, encoding='utf-8')
    inc = ['-I', str(td / 'stub'), '-I', str(sms / 'src'), '-I', str(sms / 'include')]
    base = [cc, '-std=gnu99', '-g', '-w', '-Drealloc=t_realloc'] + inc
    exe = td / 't.exe'
    built = False
    for extra in (['-fsanitize=address,undefined', '-fno-omit-frame-pointer'], []):  # the sanitizers when the compiler has them
        r = subprocess.run(base + extra + [str(sms / 'src/demux/avi.c'), str(td / 't.c'), '-o', str(exe)], capture_output=True, text=True)
        if r.returncode == 0:
            built = True
            break
    if not built:
        fail.append('avi.c must build on the PC against the made-up AVI: ' + r.stderr[-1200:])
    else:
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0')
        for starved in (0, 1):
            r = subprocess.run([str(exe), str(td / 't.avi'), str(starved), str(apos_before[500])], capture_output=True, text=True,
                               timeout=120, env=env)
            if r.returncode != 0 or 'ok' not in r.stdout:
                # the sanitizer's own lines (what, where, the stack), not its shadow-memory dump
                keep = [l for l in (r.stdout + r.stderr).splitlines()
                        if any(k in l for k in ('ERROR', 'SUMMARY', 'READ of', 'WRITE of', 'located', 'runtime error', ' #'))]
                fail.append('avi.c %s: exit %d: %s' % ('starved of memory' if starved else 'read and skipped', r.returncode,
                                                      '\n'.join(keep[:14]) or (r.stdout + r.stderr)[-800:]))

if fail:
    print('\n'.join(fail))
    sys.exit(1)
print('build130 ok')
