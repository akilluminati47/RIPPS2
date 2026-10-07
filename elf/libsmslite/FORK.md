# RIPPS2's libsmslite

RIPPS2 (build 93) plays AVI video from Memory Files with libsmslite, the SMS (Simple Media System) playback
core cut down to one container (AVI), one video codec family (MPEG-4 ASP: XviD, DivX 4 and up) and one audio
family (MPEG-1 layer II and III). The copy here is RIPPS2's fork of it.

## Licences

- The SMS core (smslite.c, the AVI demuxer, the PS2 display, IPU and VU code): (c) Eugene Plotnikov and
  contributors, Academic Free License 2.0, as each file's header says.
- The MPEG-4 decoder (codec/video, from ffmpeg) and the MP3 decoder (codec/audio/mp123.c, from mpg123): GNU
  Lesser General Public License 2.1 or later, as their headers say. RIPPS2 builds this folder as its own
  library (libsmslite.a, by elf/build.sh) and links it into RIPPS2.ELF; RIPPS2's whole source is public, so
  anyone can change this library and link it again.

## RIPPS2's changes

- smsLitePause(int on): holds the picture and stops feeding the sound until called with 0; the host reads the
  pad itself (START pauses, the cancel button or SELECT stops), so nothing in the player takes input.
- smsLiteClearDecodeInfo / smsLiteClearDecoderInfo / smsLiteClearPacketInfo: called by smsLiteInit and
  smsLitePlayFullscreen but defined nowhere in this copy; RIPPS2 gives them empty bodies (nothing to reset).
- A stop stops at once: smsLiteStop() ended only the reading, and every frame already decoded was still
  shown, each held against the sound's clock, which stops moving once the sound runs out (up to 200
  vsyncs a frame). Now the decoding threads end on the stop and the frames left are let go unshown, each
  given back to the decoder the way IPU_Display gives a shown one back (m_FrameType = -1).
- After the last frame the player waited for its audio threads by rotating their ready queue, from a
  thread one priority above them, so they never ran: after a stop it spun for ever. It sleeps now.
