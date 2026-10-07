# libsmslite

Lightweight PS2 fullscreen AVI playback, extracted from the SMS
(Simple Media System) decode core. One container (AVI), one video
codec family (MPEG-4 ASP: XviD / DivX4+), one audio codec family
(MPEG-1 layer II/III AVI+MP3 pairing) played through
audsrv. Uses the same multi-threaded read/decode/render pipeline as
stock SMS (reader + video-decode + audio-decode threads feeding a
vsync-paced renderer), minus all the GUI, playlist, subtitle and OSD
machinery - just init, play one file, shut down.

## Build

    make            # lib/libsmslite.a
    make test       # + bin/smslite_test.elf (needs PS2SDK set)
    make test SMSLITE_TEST_PATH=mass0:/video/test.avi

## Use

    #include "smslite.h"

    smsLiteInit();
    smsLitePlayFullscreen("mass0:/video/test.avi");
    smsLiteShutdown();

Requirements before calling into the library:
- SifInitRpc / fileXio must be up (the library reads the video and
  rom0:ROMVER through fileXio), and for sound libsd.irx + audsrv.irx
  must be loaded (audio is best effort: no audsrv or a non-MP2/MP3
  stream just means video-only playback). See test/main.c for a
  complete example including module loading.
- Link with: -laudsrv -lfileXio -ldebug -lpatches -lc -lkernel and
  -Wl,--gc-sections (the library relies on section GC to drop unused
  SMS code paths).

The playback call blocks until end of stream, takes over the GS
(PAL/NTSC auto-detected from rom0:ROMVER), letterboxes to the video
aspect ratio, and paces frames by vsync from container timestamps.
Internally it spawns reader/video-decode/audio-decode threads and
runs the renderer on the calling thread; all are torn down before it
returns.

For embedding a non-blocking video preview (e.g. a game-info page),
use the preview API instead of smsLitePlayFullscreen(): smsLitePreviewOpen()
starts a background decode, smsLitePreviewUpdate() / smsLitePreviewFrameReady()
poll for the next frame, smsLitePreviewFrame() returns it for the host to
draw, and smsLitePreviewClose() tears down. See include/smslite.h.

Note on emulators: the display is set up in interlaced field mode
(as stock SMS does). Some PCSX2 versions mishandle this and show a
vertically-doubled/zoomed image - turning off interlacing in the
emulator's display settings corrects it. Real hardware is unaffected.

Media prep example (25 fps PAL, SD, XviD):

    ffmpeg -i in.mp4 -c:v libxvid -vf scale=640:-2 -r 25 \
           -c:a libmp3lame -ar 48000 -b:a 128k out.avi

48 kHz is the SPU2's native rate; other common MP3 rates work too
(audsrv resamples).

Decode core (c) Eugene Plotnikov and contributors,
Academic Free License v2.0 - see the individual source headers.
