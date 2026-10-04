"""Reading any audio file, and writing RIPPS2's two formats: .adp sounds and bgm music.

Reading uses libsndfile (WAV, FLAC, Ogg, MP3, AIFF ...) and falls back on ffmpeg for anything else
(M4A, AAC, video files) when ffmpeg is on the PATH or beside the app. Music is written as Ogg Vorbis
at 192 kbps with no tags (what RIPPS2's player reads; a quality-based VBR file does not play) when
ffmpeg is there, and as 16-bit WAV (bigger, but always plays) when it is not.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

import adpcm

AUDIO_EXT = {'.wav', '.flac', '.ogg', '.mp3', '.aif', '.aiff', '.m4a', '.aac', '.wma', '.opus', '.adp', '.mp4', '.mkv', '.webm'}
BIOS_EXT = {'.bin', '.rom0', '.rom'}
APP_DIR = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
HOME_DIR = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent


def ffmpeg_path():
    local = HOME_DIR / ('ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
    if local.exists():
        return str(local)
    return shutil.which('ffmpeg')


def load(path, rate=44100):
    """Any audio file -> float32 (2, n) at rate."""
    path = str(path)
    if path.lower().endswith('.adp'):
        pcm, r = adpcm.decode(Path(path).read_bytes())
        x = pcm.astype(np.float32) / 32768.0
        x = resample(x[None, :], r, rate)
        return np.vstack([x, x])
    try:
        import soundfile as sf
        data, r = sf.read(path, dtype='float32', always_2d=True)
        x = data.T
    except Exception:
        ff = ffmpeg_path()
        if not ff:
            raise ValueError('cannot read this file without ffmpeg (put ffmpeg.exe beside the app)')
        raw = subprocess.run([ff, '-v', 'error', '-i', path, '-vn', '-ac', '2', '-ar', str(rate), '-f', 'f32le', '-'],
                             capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()
        r = rate
    if x.shape[0] == 1:
        x = np.vstack([x, x])
    elif x.shape[0] > 2:
        x = x[:2]
    if r != rate:
        x = resample(x, r, rate)
    return np.ascontiguousarray(x, np.float32)


_BANKS = {}


def _bank(cut, half, phases):
    """The interpolation filters: a Kaiser-windowed sinc for each of `phases` fractional positions."""
    key = (round(cut, 6), half, phases)
    if key not in _BANKS:
        k = np.arange(-half + 1, half + 1)
        frac = np.arange(phases) / phases
        d = frac[:, None] - k[None, :]
        w = np.i0(8.0 * np.sqrt(np.clip(1 - (d / half) ** 2, 0, 1))) / np.i0(8.0)
        _BANKS[key] = (cut * np.sinc(cut * d) * w).astype(np.float32)
    return _BANKS[key]


def resample(x, r0, r1, half=16, phases=2048):
    """(channels, n) from rate r0 to r1 by band-limited interpolation: every output sample is a
    Kaiser-windowed sinc over the 2 * half nearest inputs, its cut-off just under the lower Nyquist,
    taken from a table of `phases` fractional positions. Numpy only, in blocks."""
    if r0 == r1:
        return x
    x = np.atleast_2d(np.asarray(x, np.float32))
    ratio = r1 / r0
    bank = _bank(0.94 * min(1.0, ratio), half, phases)
    n_out = int(round(x.shape[1] * ratio))
    xp = np.pad(x, ((0, 0), (half, half + 1)))
    k = np.arange(-half + 1, half + 1)
    out = np.empty((x.shape[0], n_out), np.float32)
    blk = 1 << 16
    for a in range(0, n_out, blk):
        pos = np.arange(a, min(n_out, a + blk), dtype=np.float64) / ratio
        i = np.floor(pos).astype(np.int64)
        ph = np.minimum(np.round((pos - i) * phases).astype(np.int64), phases - 1)
        h = bank[ph]
        idx = i[:, None] + k[None, :] + half
        for c in range(x.shape[0]):
            out[c, a:a + len(pos)] = np.einsum('ij,ij->i', xp[c][idx], h)
    return out


def trim(x, db=-55.0):
    """Silence off both ends."""
    a = np.abs(x).max(axis=0)
    thr = 10 ** (db / 20) * max(a.max(), 1e-9)
    idx = np.nonzero(a > thr)[0]
    if not len(idx):
        return x
    return x[:, max(0, idx[0] - 32):idx[-1] + 1]


def peak_normalize(x, peak=0.89):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x


def to_adp(x, rate=44100, progress=None, max_seconds=None, fade=True):
    """Stereo float -> .adp bytes (mono, 44.1 kHz), its tail faded if cut to max_seconds."""
    mono = x.mean(axis=0)
    if max_seconds and len(mono) > max_seconds * rate:
        n = int(max_seconds * rate)
        mono = mono[:n].copy()
        if fade:
            f = n // 4
            mono[-f:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, f))).astype(np.float32)
    pcm = np.clip(np.round(mono * 32767), -32768, 32767).astype(np.int64)
    return adpcm.encode(pcm, rate, progress)


def adp_preview(data):
    """What RIPPS2 will play: the .adp decoded back, as stereo float at 44.1 kHz."""
    pcm, r = adpcm.decode(data)
    x = pcm.astype(np.float32) / 32768.0
    if r != 44100:
        x = resample(x[None, :], r, 44100)[0]
    return np.vstack([x, x])


def write_music(x, dst_noext, rate=44100):
    """Music for RIPPS2: Ogg Vorbis at 192 kbps without tags, or 16-bit WAV without ffmpeg. -> path."""
    ff = ffmpeg_path()
    pcm = (np.clip(x, -1, 1).T * 32767).astype('<i2')
    if ff:
        dst = str(dst_noext) + '.ogg'
        p = subprocess.run([ff, '-v', 'error', '-y', '-f', 's16le', '-ar', str(rate), '-ac', '2', '-i', '-',
                            '-map_metadata', '-1', '-c:a', 'libvorbis', '-b:a', '192k', dst],
                           input=pcm.tobytes(), capture_output=True)
        if p.returncode == 0:
            return dst
    dst = str(dst_noext) + '.wav'
    with wave.open(dst, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
    return dst


def loudness_match(x, target_db=-17.0):
    """A plain gain toward a typical menu-music level (an RMS estimate of loudness, gated)."""
    m = x.mean(axis=0)
    blk = 4410
    n = len(m) // blk
    if n < 4:
        return x
    r = np.sqrt((m[:n * blk].reshape(n, blk) ** 2).mean(axis=1) + 1e-12)
    rdb = 20 * np.log10(r)
    gate = rdb > rdb.max() - 25
    lev = 20 * np.log10(np.sqrt((r[gate] ** 2).mean()))
    g = 10 ** ((target_db - 3.0 - lev) / 20)
    y = x * g
    pk = np.abs(y).max()
    return y * (0.95 / pk) if pk > 0.95 else y
