/* smslite_config.h compile time switches

   Set these on the compiler command line (the Makefile does it for
   you.. see the build variants below). Everything defaults to ON..
   so a plain `make` gives you the full library.

     SMSLITE_ENABLE_AUDIO      MP3/MP2 audio decoding (SMS_MP123).
                               Off  => the MP3 decoder is not linked
                               at all: ~107 KB smaller (24 KB code +
                               69 KB of tables). smsLitePreviewOpen()
                               then behaves as if SMSLITE_PREVIEW_
                               VIDEO_ONLY were always set.

     SMSLITE_ENABLE_FULLSCREEN smsLitePlayFullscreen() and the threaded
                               player + GS display path.
                               Off  => drops the 4x64 KB thread stacks
                               (256 KB of BSS) and the GS display code.
                               Only the non-blocking preview API is
                               built - which is all a host like wOPL
                               (which owns its own display) needs.

   Build variants produced by the Makefile:

     libsmslite.a                 audio=1 fullscreen=1   (full)
     libsmslite-video.a           audio=0 fullscreen=1
     libsmslite-preview.a         audio=1 fullscreen=0
     libsmslite-preview-video.a   audio=0 fullscreen=0   (smallest)

   ...each also available as a -debug build (adds -DSMSLITE_DEBUG, which turns smsLiteDbg() into printf.. see smslite_debug.h).*/

#ifndef SMSLITE_CONFIG_H
#define SMSLITE_CONFIG_H

#ifndef SMSLITE_ENABLE_AUDIO
#define SMSLITE_ENABLE_AUDIO 1
#endif

#ifndef SMSLITE_ENABLE_FULLSCREEN
#define SMSLITE_ENABLE_FULLSCREEN 1
#endif

/* audio inside the fullscreen player only matters if audio exists */
#if !SMSLITE_ENABLE_AUDIO && defined(SMSLITE_FORCE_AUDIO)
#error "SMSLITE_FORCE_AUDIO set but SMSLITE_ENABLE_AUDIO is 0"
#endif

#endif
