"""Build 131: the video player's pause goes silent on the held frame, and a video ends without its sound repeating.

Run dry, audsrv repeats what it holds (the stutter): paused, stopped or at the end, the player's sound thread fades
what it sends to 0 and feeds audsrv silence. Once the sound has ended, the last frames run on the bus clock instead
of waiting on the stopped sound clock. Static checks on elf/libsmslite and the patched tree."""
import os
import re
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
elf = Path(__file__).resolve().parents[1]
s = (elf / 'libsmslite' / 'src' / 'smslite.c').read_text(encoding='utf-8')
media = (root / 'src' / 'ripps2media.c').read_text(encoding='utf-8')
fail = []


def body(name):
    m = re.search(r'\n(?:static )?\w[\w\s\*]*\b' + name + r'\([^)]*\)\s*\{', s)
    if not m:
        return ''
    i, depth = m.end(), 1
    while depth and i < len(s):
        depth += {'{': 1, '}': -1}.get(s[i], 0)
        i += 1
    return s[m.end():i]


silence = body('smsLiteAudioSilence')
if 'audsrv_wait_audio' not in silence or 'audsrv_play_audio' not in silence or 'audioBytesOut' in silence:
    fail.append('smsLiteAudioSilence must feed audsrv zeros at its own pace, outside the clock the picture follows')
drain = body('smsLiteAudioDrain')
if 'canFade' not in drain or 's_smsLiteGain == 0' not in drain or 'smsLiteApplyGain((short*)(slot + 80), len / 2, quiet)' not in drain:
    fail.append('the drain must fade a piece at a time when paused or stopped, and stop once the sound is at 0')
render = body('smsLiteAudioRenderThread')
if (render.count('smsLiteAudioSilence(pb') < 3 or 'while (s_smsLitePaused && !pb->stopRequested)' not in render
        or 'SMS_RingBufferFree' not in render or 'pb->audioEnded = 1' not in render):
    fail.append('the sound thread must feed silence while paused, at a stop and at the end, and let a stopped queue go')
if 'DelayThread(10000);' in render:
    fail.append('a pause must not leave audsrv dry (the old DelayThread wait)')
if 'smsLiteAudioDrain(playback, 0)' not in s:
    fail.append('the preview pump keeps its old drain (no fade)')
clock = body('smsLiteClockMs')
if 'audioEnded' not in clock or 'GetTimerSystemTime' not in clock or 'pts - smsLiteClockMs(playback) > 80' not in s:
    fail.append('frames must follow the bus clock once the sound has ended')
if 'playback->audioEnded      = 0;' not in s:
    fail.append('each run (a skip, a loop) must start with the sound not ended')
if 'LOG("MEDIA: video %s\\n", paused ? "paused" : "resumed");' not in media:
    fail.append('the log must say when a video is paused and resumed')

print('\n'.join(fail) or 'build131: pause silent on the held frame, no repeated sound at a stop or the end, last frames on time OK')
sys.exit(1 if fail else 0)
