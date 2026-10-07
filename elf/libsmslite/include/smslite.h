#ifndef SMSLITE_H
#define SMSLITE_H

#include "smslite_config.h"

#ifdef __cplusplus
extern "C" {
#endif

#define SMSLITE_OK              0
#define SMSLITE_ERR_INIT        -1
#define SMSLITE_ERR_OPEN        -2
#define SMSLITE_ERR_UNSUPPORTED -3
#define SMSLITE_ERR_PLAY        -4
#define SMSLITE_ERR_FORMAT      -5
#define SMSLITE_ERR_READ        -6
#define SMSLITE_ERR_CONTAINER   -7
#define SMSLITE_ERR_PACKET      -8
#define SMSLITE_ERR_CODEC       -9
#define SMSLITE_ERR_DECODE      -10

const char* smsLiteVersion(void);

int smsLiteInit(void);
void smsLiteShutdown(void);

#if SMSLITE_ENABLE_FULLSCREEN
int smsLitePlayFullscreen(const char* path);
#endif

/* Request an in progress smsLitePlayFullscreen() to stop early.. safe to call from another thread.. no op if nothing is playing. */
void smsLiteStop(void);

/* RIPPS2: hold (1) or carry on (0) an in progress smsLitePlayFullscreen(): the frame on screen stays and the
   sound stops being fed, so picture and sound pick up together. Safe from another thread (the host reads the
   pad itself: the player takes no input). Cleared when a playback starts or ends. */
void smsLitePause(int on);

/* Open flags */
#define SMSLITE_PREVIEW_AUDIO       0x0000  /* decode + play audio (audsrv) */
#define SMSLITE_PREVIEW_VIDEO_ONLY  0x0001  /* skip audio entirely */
#define SMSLITE_PREVIEW_LOOP        0x0002  /* restart at end instead of EOF */

/* Update / status return codes */
#define SMSLITE_PREVIEW_OK      0   /* advanced; check smsLitePreviewFrameReady */
#define SMSLITE_PREVIEW_EOF     1   /* end of stream (no LOOP flag) */
#define SMSLITE_PREVIEW_ERROR  -1   /* decode/IO error; close the preview */

/* Pixel format of the exposed frame buffer. */
#define SMSLITE_PIXFMT_RGBA32   0   /* 32 bpp, 8-8-8-8, GS PSMCT32 layout */
#define SMSLITE_PIXFMT_RGBA16   1   /* 16 bpp, 5-5-5-1, GS PSMCT16 layout */
#define SMSLITE_PIXFMT_RGB24    2   /* 32-bit stride, 8-8-8, GS PSMCT24 (no alpha) */

typedef struct SMSLitePreviewFrame {
    const void*  pixels;   /* linear pixel data, host uploads this   */
    int          width;    /* frame width in pixels                  */
    int          height;   /* frame height in pixels                 */
    int          stride;   /* bytes per row                          */
    int          format;   /* SMSLITE_PIXFMT_*                       */
    unsigned int serial;   /* increments each new frame (for change  */
                           /* detection - only re-upload when it     */
                           /* differs from the last value you saw)   */
} SMSLitePreviewFrame;

/* Open a clip for previewing.. flags is a bitwise-OR of SMSLITE_PREVIEW_*.
   Returns SMSLITE_OK on success or a negative SMSLITE_ERR_* code. Does
   NOT touch the GS.. the host keeps its own display. */
int smsLitePreviewOpen(const char* path, int flags);

/* Advance decoding.. Call once per host frame (or as needed). Non blocking.
   Returns SMSLITE_PREVIEW_OK / _EOF / _ERROR. When it returns
   OK, a new decoded frame may be available.. check smsLitePreviewFrameReady. */
int smsLitePreviewUpdate(void);

/* Non zero if a new frame is ready to upload since the last time you consumed one (i.e. serial changed) */
int smsLitePreviewFrameReady(void);

/* The current decoded frame. Valid until the next smsLitePreviewUpdate or smsLitePreviewClose
   Returns NULL if no frame has been decoded yet..
   The host should upload pixels to a texture and can then draw that texture at any position/size */
const SMSLitePreviewFrame* smsLitePreviewFrame(void);

/* Stop previewing and release everything.. safe to call anytime after Open (even mid-stream) and safe to call more than once */
void smsLitePreviewClose(void);

#ifdef __cplusplus
}
#endif

#endif
