/* typical use:
     smsLiteInit();
     smsLitePlayFullscreen("mass0:/video/test.avi");
     smsLiteShutdown();
 */

#include "smslite.h"
#include <timer.h>

#include "smslite_config.h"
#include "smslite_debug.h"

#include <fileXio_rpc.h>
#include <io_common.h>
#include <kernel.h>
#include <malloc.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/file.h"
#include "demux/container.h"
#include "demux/avi.h"
#include "ps2/ringbuffer.h"
#include "codec/codec.h"
#include "codec/video/mpeg.h"
#include "codec/video/mpeg4.h"
#include "ps2/videobuffer.h"
#include "core/config.h"
#include "ps2/gs.h"
#include "ps2/ipu.h"
#include "ps2/ee.h"
#include "core/sms.h"
#include "ps2/dma.h"

#if SMSLITE_ENABLE_AUDIO
#include <audsrv.h>
#endif

static volatile int s_smsLitePaused = 0; /* RIPPS2: smsLitePause() */

static void smsLiteVU0Sync(void)
{
    DMA_Wait(DMAC_VIF0);
}

#define SMSLITE_FILE_BUFFER_SIZE          (32 * 1024)
#define SMSLITE_PACKET_BUFFER_SIZE        (256 * 1024)
#define SMSLITE_VIDEO_OUTPUT_BUFFER_SIZE  4096
#define SMSLITE_AUDIO_OUTPUT_BUFFER_SIZE  (256 * 1024)
#define SMSLITE_VIDEO_PROBE_TEST_FRAMES   5
#define SMSLITE_DEFAULT_FRAME_MS          40

static int s_smsLiteInitialized = 0;

#if SMSLITE_ENABLE_AUDIO
static int s_smsLiteAudsrvReady = 0;
#endif

static unsigned char s_smsLiteFileBuffer[SMSLITE_FILE_BUFFER_SIZE] __attribute__((aligned(64)));
static iox_stat_t s_smsLiteStat __attribute__((aligned(64)));

SMSConfig g_Config __attribute__((section(".data")));

static void smsLiteInitConfig(void)
{
    memset(&g_Config, 0, sizeof(g_Config));

    g_Config.m_DisplayMode      = GSVideoMode_Default;
    g_Config.m_ColorDepth       = 0;
    g_Config.m_PlayerFlags      = 0;
    g_Config.m_ImgOffs          = 0;

    g_Config.m_PlayerBrightness = 12;

    /* stock pixel aspect ratios (0x3F6EEEEF / 0x3F888889) */
    *((unsigned int*)&g_Config.m_PAR[0]) = 0x3F6EEEEF;
    *((unsigned int*)&g_Config.m_PAR[1]) = 0x3F888889;

    g_Config.m_DispWH[0][0] =  640; /* NTSC     */
    g_Config.m_DispWH[0][1] =  448;
    g_Config.m_DispWH[1][0] =  640; /* PAL      */
    g_Config.m_DispWH[1][1] =  512;
    g_Config.m_DispWH[2][0] =  640; /* DTV480p  */
    g_Config.m_DispWH[2][1] =  512;
    g_Config.m_DispWH[3][0] =  640; /* DTV576p  */
    g_Config.m_DispWH[3][1] =  512;
    g_Config.m_DispWH[4][0] = 1216; /* DTV720p  */
    g_Config.m_DispWH[4][1] =  676;
    g_Config.m_DispWH[5][0] = 1820; /* DTV1080i */
    g_Config.m_DispWH[5][1] = 1018;
    g_Config.m_DispWH[6][0] =  640; /* VESA60Hz */
    g_Config.m_DispWH[6][1] =  480;
    g_Config.m_DispWH[7][0] =  640; /* VESA75Hz */
    g_Config.m_DispWH[7][1] =  480;

    g_Config.m_SyncPar[0][0] =   0; /* NTSC     */
    g_Config.m_SyncPar[0][1] = 248;
    g_Config.m_SyncPar[0][2] = 248;
    g_Config.m_SyncPar[1][0] =   0; /* PAL      */
    g_Config.m_SyncPar[1][1] = 304;
    g_Config.m_SyncPar[1][2] = 304;
    g_Config.m_SyncPar[2][0] =   0; /* DTV480p  */
    g_Config.m_SyncPar[2][1] = 464;
    g_Config.m_SyncPar[2][2] = 480;
    g_Config.m_SyncPar[3][0] =   0; /* DTV576p  */
    g_Config.m_SyncPar[3][1] = 464;
    g_Config.m_SyncPar[3][2] = 480;
    g_Config.m_SyncPar[4][0] =   0; /* DTV720p  */
    g_Config.m_SyncPar[4][1] = 660;
    g_Config.m_SyncPar[4][2] = 648;
    g_Config.m_SyncPar[5][0] =   0; /* DTV1080i */
    g_Config.m_SyncPar[5][1] = 412;
    g_Config.m_SyncPar[5][2] = 480;
    g_Config.m_SyncPar[6][0] =   0; /* VESA60Hz */
    g_Config.m_SyncPar[6][1] = 448;
    g_Config.m_SyncPar[6][2] = 480;
    g_Config.m_SyncPar[7][0] =   0; /* VESA75Hz */
    g_Config.m_SyncPar[7][1] = 448;
    g_Config.m_SyncPar[7][2] = 460;
}

static char* smsLiteStrDup(const char* str)
{
    char* ret;
    unsigned int len;

    len = strlen(str) + 1;
    ret = (char*)malloc(len);

    if (ret)
        memcpy(ret, str, len);

    return ret;
}

static unsigned int smsLiteReadLE32(const unsigned char* data)
{
    return ((unsigned int)data[0]) | ((unsigned int)data[1] << 8) | ((unsigned int)data[2] << 16) | ((unsigned int)data[3] << 24);
}

typedef struct SMSLiteStreamInfo {
    int          videoIndex;      /* -1 = none */
    int          audioIndex;      /* -1 = none */
    unsigned int frameRate;
    unsigned int frameRateBase;
    int          sampleRate;
    int          channels;
} SMSLiteStreamInfo;

static SMSLiteStreamInfo s_streams = { -1, -1, 0, 0, 0, 0 };

static void smsLiteResetStreams(void)
{
    s_streams.videoIndex = -1;
    s_streams.audioIndex = -1;

    s_streams.frameRate = 0;
    s_streams.frameRateBase = 0;

    s_streams.sampleRate = 0;
    s_streams.channels = 0;
}

static int smsLiteFileRead(FileContext* ctx, void* buffer, unsigned int size)
{
    int fd;
    int ret;

    fd = (int)ctx->m_pData;

    fileXioLseek(fd, ctx->m_CurPos, FIO_SEEK_SET);

    ret = fileXioRead(fd, buffer, size);

    if (ret > 0) {
        ctx->m_CurPos += ret;
        ctx->m_Pos = ctx->m_CurPos;
        ctx->m_pPos = ctx->m_pBuff[0];
        ctx->m_pEnd = ctx->m_pBuff[0];
    }

    return ret;
}

static int smsLiteFileSeek(FileContext* ctx, unsigned int pos)
{
    int fd;
    int ret;

    fd = (int)ctx->m_pData;

    ret = fileXioLseek(fd, pos, FIO_SEEK_SET);

    if (ret >= 0) {
        ctx->m_CurPos = pos;
        ctx->m_Pos = pos;
        ctx->m_pPos = ctx->m_pBuff[0];
        ctx->m_pEnd = ctx->m_pBuff[0];
    }

    return ret;
}

static int smsLiteFileFill(FileContext* ctx)
{
    int fd;
    int ret;
    unsigned int readSize;

    if (ctx->m_CurPos >= ctx->m_Size)
        return 0;

    fd = (int)ctx->m_pData;

    readSize = ctx->m_BufSize;
    if (readSize > ctx->m_Size - ctx->m_CurPos)
        readSize = ctx->m_Size - ctx->m_CurPos;

    fileXioLseek(fd, ctx->m_CurPos, FIO_SEEK_SET);

    ret = fileXioRead(fd, ctx->m_pBuff[0], readSize);

    if (ret > 0) {
        ctx->m_CurBufSize = ret;
        ctx->m_pPos = ctx->m_pBuff[0];
        ctx->m_pEnd = ctx->m_pBuff[0] + ret;
    }

    return ret;
}

static int smsLiteFileStream(FileContext* ctx, unsigned int start, unsigned int size)
{
    (void)ctx;
    (void)start;
    (void)size;

    return 0;
}

static void smsLiteFileDestroy(FileContext* ctx)
{
    int fd;

    if (!ctx)
        return;

    fd = (int)ctx->m_pData;

    if (fd >= 0)
        fileXioClose(fd);

    if (ctx->m_pPath)
        free(ctx->m_pPath);

    free(ctx);
}

static FileContext* smsLiteOpenFileContext(const char* path)
{
    FileContext* ctx;
    int fd;
    int statResult;

    fd = fileXioOpen(path, FIO_O_RDONLY);


    if (fd < 0)
        return NULL;

    ctx = (FileContext*)calloc(1, sizeof(FileContext));
    if (!ctx) {
        fileXioClose(fd);
        return NULL;
    }

    ctx->m_pPath = smsLiteStrDup(path);
    if (!ctx->m_pPath) {
        fileXioClose(fd);
        free(ctx);
        return NULL;
    }

    statResult = fileXioGetStat(path, &s_smsLiteStat);


    ctx->m_Size = statResult >= 0 ? s_smsLiteStat.size : 0;
    ctx->m_StreamSize = ctx->m_Size;
    ctx->m_BufSize = sizeof(s_smsLiteFileBuffer);
    ctx->m_pBuff[0] = s_smsLiteFileBuffer;
    ctx->m_pPos = s_smsLiteFileBuffer;
    ctx->m_pEnd = s_smsLiteFileBuffer;
    ctx->m_pData = (void*)fd;

    ctx->Read = smsLiteFileRead;
    ctx->Seek = smsLiteFileSeek;
    ctx->Fill = smsLiteFileFill;
    ctx->Stream = smsLiteFileStream;
    ctx->Destroy = smsLiteFileDestroy;


    return ctx;
}

static void smsLiteSelectStreams(SMS_Container* container)
{
    unsigned int i;
    SMS_Stream* stream;
    SMS_CodecContext* codec;

    smsLiteResetStreams();

    if (!container)
        return;

    for (i = 0; i < container->m_nStm && i < SMS_MAX_STREAMS; i++) {
        stream = container->m_pStm[i];

        if (!stream)
            continue;

        codec = stream->m_pCodec;

        if (s_streams.videoIndex < 0 &&
            ((stream->m_Flags & SMS_STRM_FLAGS_VIDEO) ||
             (codec && codec->m_Type == SMS_CodecTypeVideo))) {
            s_streams.videoIndex = i;

            if (codec) {
                s_streams.frameRate = codec->m_FrameRate;
                s_streams.frameRateBase = codec->m_FrameRateBase;
            }

            if (!s_streams.frameRate)
                s_streams.frameRate = stream->m_RealFrameRate;

            if (!s_streams.frameRateBase)
                s_streams.frameRateBase = stream->m_RealFrameRateBase;
        }

        if (s_streams.audioIndex < 0 &&
            ((stream->m_Flags & SMS_STRM_FLAGS_AUDIO) ||
             (codec && codec->m_Type == SMS_CodecTypeAudio))) {
            s_streams.audioIndex = i;

            if (codec) {
                s_streams.sampleRate = codec->m_SampleRate;
                s_streams.channels = codec->m_Channels;
            }
        }
    }
}

static SMS_AVPacket* smsLiteAllocPacket(SMS_RingBuffer* packetBuffer, int size)
{
    static SMS_AVPacket s_emptyPacket;
    SMS_AVPacket* packet;


    packet = size ? (SMS_AVPacket*)SMS_RingBufferAlloc(packetBuffer, size + 64) : &s_emptyPacket;

    if (packet) {
        packet->m_PTS = SMS_NOPTS_VALUE;
        packet->m_DTS = SMS_NOPTS_VALUE;
        packet->m_StmIdx = 0;
        packet->m_Flags = 0;
        packet->m_Duration = 0;
        packet->m_pData = ((unsigned char*)packet) + 64;
        packet->m_Size = size;

    }

    return packet;
}

static int smsLiteInitPacketBuffers(SMS_Container* container, void* buffers[SMS_MAX_STREAMS])
{
    unsigned int i;
    SMS_Stream* stream;

    for (i = 0; i < SMS_MAX_STREAMS; i++)
        buffers[i] = NULL;

    if (!container)
        return 0;

    for (i = 0; i < container->m_nStm && i < SMS_MAX_STREAMS; i++) {
        stream = container->m_pStm[i];

        if (!stream)
            continue;

        buffers[i] = memalign(64, SMSLITE_PACKET_BUFFER_SIZE);
        if (!buffers[i])
            return 0;

        stream->m_pPktBuf = SMS_RingBufferInit(buffers[i], SMSLITE_PACKET_BUFFER_SIZE);
        if (!stream->m_pPktBuf)
            return 0;
    }

    return 1;
}

typedef struct SMSLitePlayback {
    FileContext* fileCtx;
    SMS_Container container;
    SMS_Stream* videoStream;
    SMS_CodecContext* codec;
    SMS_RingBuffer* outputBuffer;
    IPUContext* ipuCtx;
    void* packetBuffers[SMS_MAX_STREAMS];
    void* outputMemory;

    SMS_CodecContext* audioCodec;
    SMS_RingBuffer* audioBuffer;
    void* audioMemory;
    int audioStreamIndex;
    int audioActive;
    int audioFmtSet;
    int audioByteRate;
    u64 audioBytesOut;

    volatile s64 audioTimeMs;

    int videoStreamIndex;
    int packetsRead;
    int framesDisplayed;
    int hwActive;
    int codecOpened;

    volatile int stopRequested;   /* set by smsLiteStop() to abort */
    volatile int eof;
    int previewMode;              /* 1 = preview: pump must NOT display frames */
    volatile int videoDone;
    volatile int audioDone;
    volatile int audioRenderDone;

    /* vsync-based pacing */
    int vsyncHz;
    int callerPrio;               /* the host's priority on entry */
    int frameMs;
    unsigned int vsyncsElapsed;
    s64 nextDueMs;
    s64 lastPTS;
    int havePTS;
} SMSLitePlayback;

static void smsLitePlaybackClear(SMSLitePlayback* playback)
{
    memset(playback, 0, sizeof(*playback));
    playback->videoStreamIndex = -1;
    playback->audioStreamIndex = -1;
    playback->frameMs = SMSLITE_DEFAULT_FRAME_MS;
    playback->vsyncHz = 50;
}

#if SMSLITE_ENABLE_AUDIO
static void smsLiteAudioFrameCB(SMS_RingBuffer* apRB)
{
    SMS_RingBufferPost(apRB);
}

#ifdef SMSLITE_DUMP_PCM
#ifndef SMSLITE_DUMP_PATH
#define SMSLITE_DUMP_PATH "mass0:/smslite_pcm.txt"
#endif
#ifndef SMSLITE_DUMP_WAV_PATH
#define SMSLITE_DUMP_WAV_PATH "mass0:/smslite_pcm.wav"
#endif

#define SMSLITE_DUMP_MAXCH   2
#define SMSLITE_DUMP_FIRSTN  32   /* first N interleaved shorts captured */

typedef struct {
    u64 n;
    s64 sum;
    u64 sumsq;
    u64 sumabs;
    u64 sumabsdiff;
    int mn;
    int mx;
    int prev;
    int havePrev;
} SMSDumpChan;

static SMSDumpChan  s_dumpCh[SMSLITE_DUMP_MAXCH];
static int          s_dumpNCh;
static int          s_dumpRate;
static short        s_dumpFirst[SMSLITE_DUMP_FIRSTN];
static int          s_dumpFirstN;
static u64          s_dumpTotalBytes;

#define SMSLITE_DUMP_WAV_BYTES  (48000 * 2 * 2 * 10)
static unsigned char s_dumpPcm[SMSLITE_DUMP_WAV_BYTES];
static int           s_dumpPcmLen;
static int           s_dumpWritten;
static u64           s_dumpRenderEmpty;

static void smsDumpWrite(void);

static void smsDumpReset(void)
{
    int c;
    for (c = 0; c < SMSLITE_DUMP_MAXCH; c++) {
        s_dumpCh[c].n = s_dumpCh[c].sumsq = s_dumpCh[c].sumabs = 0;
        s_dumpCh[c].sumabsdiff = 0;
        s_dumpCh[c].sum = 0;
        s_dumpCh[c].mn  =  0x7FFFFFFF;
        s_dumpCh[c].mx  = -0x7FFFFFFF;
        s_dumpCh[c].prev = s_dumpCh[c].havePrev = 0;
    }
    s_dumpNCh = 0;
    s_dumpRate = 0;
    s_dumpFirstN = 0;
    s_dumpTotalBytes = 0;
    s_dumpPcmLen = 0;
    s_dumpWritten = 0;
    s_dumpRenderEmpty = 0;
}

static void smsDumpAccum(const short* pcm, int byteLen, int nCh, int rate)
{
    int nShorts = byteLen / 2;
    int i;

    if (nCh < 1) nCh = 1;
    if (nCh > SMSLITE_DUMP_MAXCH) nCh = SMSLITE_DUMP_MAXCH;
    s_dumpNCh  = nCh;
    s_dumpRate = rate;
    s_dumpTotalBytes += (u64)byteLen;

    for (i = 0; i < nShorts && s_dumpFirstN < SMSLITE_DUMP_FIRSTN; i++)
        s_dumpFirst[s_dumpFirstN++] = pcm[i];

    /* copy raw bytes for the WAV.. up to the cap */
    if (s_dumpPcmLen < (int)sizeof(s_dumpPcm)) {
        int room = (int)sizeof(s_dumpPcm) - s_dumpPcmLen;
        int cpy  = byteLen < room ? byteLen : room;
        memcpy(s_dumpPcm + s_dumpPcmLen, pcm, cpy);
        s_dumpPcmLen += cpy;

        if (s_dumpPcmLen >= (int)sizeof(s_dumpPcm) && !s_dumpWritten)
            smsDumpWrite();
    }

    for (i = 0; i < nShorts; i++) {
        int c = i % nCh;
        int s = pcm[i];               /* signed 16 bit */
        SMSDumpChan* ch = &s_dumpCh[c];
        int a = s < 0 ? -s : s;

        ch->n++;
        ch->sum    += s;
        ch->sumsq  += (u64)((s64)s * s);
        ch->sumabs += (u64)a;
        if (s < ch->mn) ch->mn = s;
        if (s > ch->mx) ch->mx = s;
        if (ch->havePrev) {
            int d = s - ch->prev;
            if (d < 0) d = -d;
            ch->sumabsdiff += (u64)d;
        }
        ch->prev = s;
        ch->havePrev = 1;
    }
}

static u64 smsDumpISqrt(u64 v)
{
    u64 x, x1;
    if (v == 0) return 0;
    x  = v;
    x1 = (x + 1) / 2;
    while (x1 < x) { x = x1; x1 = (x + v / x) / 2; }
    return x;
}

static void smsDumpWrite(void)
{
    static char buf[3072] __attribute__((aligned(64)));
    int  o = 0;
    int  fd, c, i;

    if (s_dumpWritten) return;
    s_dumpWritten = 1;

    o += snprintf(buf + o, sizeof(buf) - o,
        "smslite decoded-PCM signature\n"
        "rate=%d ch=%d total_pcm_bytes=%llu\n"
        "render_empty_polls=%llu (~%llu ms PCM-ring-empty)\n\n",
        s_dumpRate, s_dumpNCh, (unsigned long long)s_dumpTotalBytes,
        (unsigned long long)s_dumpRenderEmpty,
        (unsigned long long)(s_dumpRenderEmpty / 2));

    for (c = 0; c < s_dumpNCh; c++) {
        SMSDumpChan* ch = &s_dumpCh[c];
        s64 dc       = ch->n ? ch->sum / (s64)ch->n : 0;
        u64 meanabs  = ch->n ? ch->sumabs / ch->n : 0;
        u64 ms       = ch->n ? ch->sumsq / ch->n : 0;
        u64 rms      = smsDumpISqrt(ms);
        u64 meandiff = ch->n ? ch->sumabsdiff / ch->n : 0;
        u64 hf       = ch->sumabs ? (ch->sumabsdiff * 1000) / ch->sumabs : 0;

        o += snprintf(buf + o, sizeof(buf) - o,
            "ch%d: n=%llu min=%d max=%d dc=%lld mean_abs=%llu rms=%llu "
            "mean_absdiff=%llu hf_ratio_x1000=%llu\n",
            c, (unsigned long long)ch->n, ch->mn, ch->mx,
            (long long)dc, (unsigned long long)meanabs,
            (unsigned long long)rms, (unsigned long long)meandiff,
            (unsigned long long)hf);
    }

    o += snprintf(buf + o, sizeof(buf) - o, "\nfirst %d interleaved shorts:\n",
        s_dumpFirstN);
    for (i = 0; i < s_dumpFirstN; i++) {
        o += snprintf(buf + o, sizeof(buf) - o, "%d%s",
            (int)s_dumpFirst[i],
            ((i & 7) == 7 || i == s_dumpFirstN - 1) ? "\n" : " ");
    }

    fd = fileXioOpen(SMSLITE_DUMP_PATH, FIO_O_WRONLY | FIO_O_CREAT | FIO_O_TRUNC, 0666);
    if (fd >= 0) {
        fileXioWrite(fd, buf, o);
        fileXioClose(fd);
    }
    smsLiteDbg("pcm dump: fd=%d bytes=%d -> %s\n", fd, o, SMSLITE_DUMP_PATH);

    {
        static unsigned char hdr[44] __attribute__((aligned(64)));
        int rate = s_dumpRate    ? s_dumpRate : 48000;
        int ch   = s_dumpNCh     ? s_dumpNCh  : 2;
        int data = s_dumpPcmLen;
        int riff = 36 + data;
        int byteRate = rate * ch * 2;
        int wfd, off, left;

        memcpy(hdr +  0, "RIFF", 4);
        hdr[ 4]=riff&0xFF; hdr[ 5]=(riff>>8)&0xFF; hdr[ 6]=(riff>>16)&0xFF; hdr[ 7]=(riff>>24)&0xFF;
        memcpy(hdr +  8, "WAVE", 4);
        memcpy(hdr + 12, "fmt ", 4);
        hdr[16]=16; hdr[17]=0; hdr[18]=0; hdr[19]=0;      /* fmt chunk size 16 */
        hdr[20]=1;  hdr[21]=0;                            /* PCM */
        hdr[22]=(unsigned char)ch; hdr[23]=0;
        hdr[24]=rate&0xFF; hdr[25]=(rate>>8)&0xFF; hdr[26]=(rate>>16)&0xFF; hdr[27]=(rate>>24)&0xFF;
        hdr[28]=byteRate&0xFF; hdr[29]=(byteRate>>8)&0xFF; hdr[30]=(byteRate>>16)&0xFF; hdr[31]=(byteRate>>24)&0xFF;
        hdr[32]=(unsigned char)(ch*2); hdr[33]=0;         /* block align */
        hdr[34]=16; hdr[35]=0;                            /* bits */
        memcpy(hdr + 36, "data", 4);
        hdr[40]=data&0xFF; hdr[41]=(data>>8)&0xFF; hdr[42]=(data>>16)&0xFF; hdr[43]=(data>>24)&0xFF;

        wfd = fileXioOpen(SMSLITE_DUMP_WAV_PATH, FIO_O_WRONLY | FIO_O_CREAT | FIO_O_TRUNC, 0666);
        if (wfd >= 0) {
            fileXioWrite(wfd, hdr, 44);
            off = 0; left = data;
            while (left > 0) {
                int w = fileXioWrite(wfd, s_dumpPcm + off, left);
                if (w <= 0) break;
                off += w; left -= w;
            }
            fileXioClose(wfd);
        }
        fileXioSync("mass0:", 0);
        smsLiteDbg("wav dump: fd=%d pcm=%d -> %s\n", wfd, data, SMSLITE_DUMP_WAV_PATH);
    }
}
#endif

static void smsLiteAudioSetFormat(SMSLitePlayback* playback, int aRate, int aChannels)
{
    struct audsrv_fmt_t fmt;

    if (aRate <= 0 || aChannels <= 0)
        return;

    fmt.freq     = aRate;
    fmt.bits     = 16;
    fmt.channels = aChannels;

    {
        int fr = audsrv_set_format(&fmt);
        smsLiteDbg("a fmt %d %d/%d\n", fr, aRate, aChannels);
        if (fr != 0)
            return;
    }

    audsrv_set_volume(MAX_VOLUME);

    playback->audioByteRate = aRate * aChannels * 2;
    playback->audioFmtSet   = 1;
}

static void smsLiteAudioDrain(SMSLitePlayback* playback)
{
    unsigned char* slot;
    int len;

    while (playback->audioBuffer &&
           SMS_RingBufferCount(playback->audioBuffer) > 0) {

        slot = (unsigned char*)SMS_RingBufferWait(playback->audioBuffer);
        len  = *(int*)(slot + 64);

        if (!playback->audioFmtSet)
            smsLiteAudioSetFormat(
                playback,
                playback->audioCodec->m_SampleRate,
                playback->audioCodec->m_Channels
            );



        if (len > 0 && playback->audioFmtSet) {
#ifdef SMSLITE_DUMP_PCM
            smsDumpAccum((const short*)(slot + 80), len,
                (int)playback->audioCodec->m_Channels,
                (int)playback->audioCodec->m_SampleRate);
#endif
            const char* p        = (const char*)(slot + 80);
            int         left     = len;
            int         accepted;

            while (left > 0) {
                int sent;
                audsrv_wait_audio(left);
                sent = audsrv_play_audio(p, left);
                if (sent <= 0)
                    break;
                p    += sent;
                left -= sent;
            }

            accepted = len - left;

            playback->audioBytesOut += accepted;

            if (playback->audioByteRate > 0)
                playback->audioTimeMs =
                    ((s64)playback->audioBytesOut * 1000) /
                    playback->audioByteRate;

        }

        SMS_RingBufferFree(playback->audioBuffer, len + 80);
    }
}

static void smsLiteAudioOpen(SMSLitePlayback* playback)
{
    SMS_Stream* stream;
    SMS_CodecContext* codec;
    int idx;

    idx = s_streams.audioIndex;

    if (idx < 0 || idx >= (int)playback->container.m_nStm)
        return;

    stream = playback->container.m_pStm[idx];
    if (!stream || !stream->m_pCodec)
        return;

    codec = stream->m_pCodec;

    /* one audio codec by design.. MPEG-1 layer II/III */
    if (codec->m_ID != SMS_CodecID_MP3 && codec->m_ID != SMS_CodecID_MP2)
        return;

    SMS_CodecOpen(codec);

    if (!codec->m_pCodec || !codec->m_pCodec->Decode)
        return;

    if (codec->m_pCodec->Init)
        codec->m_pCodec->Init(codec);

    playback->audioMemory = memalign(64, SMSLITE_AUDIO_OUTPUT_BUFFER_SIZE);
    if (!playback->audioMemory)
        return;

    playback->audioBuffer = SMS_RingBufferInit(
        playback->audioMemory,
        SMSLITE_AUDIO_OUTPUT_BUFFER_SIZE
    );

    if (!playback->audioBuffer)
        return;

    playback->audioBuffer->UserCB = smsLiteAudioFrameCB;

    if (!s_smsLiteAudsrvReady) {
        int ir = audsrv_init();
        smsLiteDbg("a init %d\n", ir);
        if (ir != 0)
            return;
        s_smsLiteAudsrvReady = 1;
    }

    smsLiteAudioSetFormat(
        playback,
        s_streams.sampleRate,
        s_streams.channels
    );

    playback->audioStreamIndex = idx;
    playback->audioCodec       = codec;
    playback->audioActive      = 1;

    smsLiteDbg("audio mp3 s%d\n", idx);
}

#else

static void smsLiteAudioOpen(SMSLitePlayback* playback)  { (void)playback; }
static void smsLiteAudioDrain(SMSLitePlayback* playback) { (void)playback; }

#endif

static void smsLitePlaybackClose(SMSLitePlayback* playback)
{
    unsigned int i;


    if (!playback)
        return;

    if (playback->codec && playback->codec->HWCtl && !playback->hwActive)
        playback->codec->HWCtl = NULL;

    SMS_DestroyContainer(&playback->container, 0);

    playback->codec = NULL;
    playback->videoStream = NULL;
    playback->hwActive = 0;

    for (i = 0; i < SMS_MAX_STREAMS; i++) {
        if (playback->packetBuffers[i]) {
            free(playback->packetBuffers[i]);
            playback->packetBuffers[i] = NULL;
        }
    }

#if SMSLITE_ENABLE_AUDIO
    if (playback->audioActive) {
        audsrv_stop_audio();
        playback->audioActive = 0;
    }
#endif

    if (playback->audioBuffer) {
        SMS_RingBufferDestroy(playback->audioBuffer);
        playback->audioBuffer = NULL;
    }

    if (playback->audioMemory) {
        free(playback->audioMemory);
        playback->audioMemory = NULL;
    }

    if (playback->outputBuffer) {
        SMS_RingBufferDestroy(playback->outputBuffer);
        playback->outputBuffer = NULL;
    }

    if (playback->outputMemory) {
        free(playback->outputMemory);
        playback->outputMemory = NULL;
    }

    if (playback->ipuCtx) {
        playback->ipuCtx->Destroy();
        playback->ipuCtx = NULL;
    }

    if (playback->fileCtx) {
        playback->fileCtx->Destroy(playback->fileCtx);
        playback->fileCtx = NULL;
    }
}

static GSVideoMode smsLiteDetectVideoMode(void)
{
    char romver[16];
    int fd;
    int ret;

    fd = fileXioOpen("rom0:ROMVER", FIO_O_RDONLY);
    if (fd < 0)
        return GSVideoMode_PAL;

    ret = fileXioRead(fd, romver, sizeof(romver));

    fileXioClose(fd);

    if (ret >= 5 && romver[4] != 'E')
        return GSVideoMode_NTSC;

    return GSVideoMode_PAL;
}

#if SMSLITE_ENABLE_FULLSCREEN
static int smsLitePlaybackInitDisplay(SMSLitePlayback* playback)
{
    unsigned short crtMode;

    smsLiteDbg("pb display init\n");

    GS_VSync();
    GSContext_Init(smsLiteDetectVideoMode(), GSZTest_Off, GSDoubleBuffer_Off);
    GS_VSync();

    playback->ipuCtx = IPU_InitContext(
        playback->codec->m_Width,
        playback->codec->m_Height,
        NULL,
        playback->codec->m_fWS
    );

    if (!playback->ipuCtx ||
        !playback->ipuCtx->Display ||
        !playback->ipuCtx->Sync)
        return SMSLITE_ERR_DECODE;

    crtMode = GS_Params()->m_GSCRTMode;

    playback->vsyncHz = (crtMode == GSVideoMode_PAL ||
                         crtMode == GSVideoMode_DTV_640x576P) ? 50 : 60;

    return SMSLITE_OK;
}
#endif

#if SMSLITE_ENABLE_FULLSCREEN
static void smsLitePlaybackShowFrame(SMSLitePlayback* playback, SMS_FrameBuffer* frame)
{
    s64 pts = frame->m_StartPTS;
    s64 delta;

    if (playback->havePTS && pts != SMS_NOPTS_VALUE) {
        delta = pts - playback->lastPTS;

        if (delta > 0 && delta <= 1000)
            playback->frameMs = (int)delta;
    }

    if (pts != SMS_NOPTS_VALUE) {
        playback->lastPTS = pts;
        playback->havePTS = 1;
    }

    if (playback->audioActive && pts != SMS_NOPTS_VALUE) {
        int guard = 0;

        while (playback->audioTimeMs > 0 &&
               pts - playback->audioTimeMs > 80) {
            GS_VSync();
            if (++guard > 200)
                break;
        }
    } else {
        while ((s64)playback->vsyncsElapsed * 1000 <
               playback->nextDueMs * playback->vsyncHz) {
            GS_VSync();
            playback->vsyncsElapsed++;
        }
        playback->nextDueMs += playback->frameMs;
    }

    /* RIPPS2: paused, the last frame stays up; the vsync count is left alone, so the pacing carries on
       from here when the pause ends */
    while (s_smsLitePaused && !playback->stopRequested)
        GS_VSync();

    playback->ipuCtx->Display(frame, pts);

    playback->framesDisplayed++;
}
#endif

#if SMSLITE_ENABLE_FULLSCREEN
static void smsLitePlaybackDrainOutput(SMSLitePlayback* playback)
{
    void* outputSlot;
    SMS_FrameBuffer* decodedFrame;

    while (playback->outputBuffer &&
           SMS_RingBufferCount(playback->outputBuffer) > 0) {

        outputSlot = SMS_RingBufferWait(playback->outputBuffer);

        decodedFrame = outputSlot ? *((SMS_FrameBuffer**)outputSlot) : NULL;

        if (decodedFrame)
            smsLitePlaybackShowFrame(playback, decodedFrame);

        SMS_RingBufferFree(playback->outputBuffer, 4);
    }
}
#endif

/* Only the fullscreen player uses this..
   preview has its own open path.. smsLitePreviewOpenInternal */
#if SMSLITE_ENABLE_FULLSCREEN
static int smsLitePlaybackOpen(SMSLitePlayback* playback, const char* path)
{
    int ret;
    int initOK;

    smsLitePlaybackClear(playback);

    smsLiteDbg("pb open file\n");

    playback->fileCtx = smsLiteOpenFileContext(path);
    if (!playback->fileCtx)
        return SMSLITE_ERR_OPEN;

    playback->container.m_pFileCtx = playback->fileCtx;
    playback->container.AllocPacket = smsLiteAllocPacket;

    smsLiteDbg("pb parse avi\n");
    
    ret = SMS_GetContainerAVI(&playback->container);

    smsLiteDbg("pb parsed %d\n", ret);


    if (ret && playback->container.m_nStm > 0)
        smsLiteSelectStreams(&playback->container);

    if (!ret || playback->container.m_nStm == 0 || !playback->container.ReadPacket)
        return SMSLITE_ERR_CONTAINER;

    if (s_streams.videoIndex < 0 ||
        s_streams.videoIndex >= (int)playback->container.m_nStm)
        return SMSLITE_ERR_CODEC;

    playback->videoStreamIndex = s_streams.videoIndex;
    playback->videoStream = playback->container.m_pStm[playback->videoStreamIndex];

    if (!playback->videoStream || !playback->videoStream->m_pCodec)
        return SMSLITE_ERR_CODEC;

    playback->codec = playback->videoStream->m_pCodec;

    smsLiteDbg("pb codec id %d\n", playback->codec->m_ID);


    if (playback->codec->m_ID != SMS_CodecID_MPEG4) {
        return SMSLITE_ERR_UNSUPPORTED;
    }

    SMS_Codec_MPEG4_Open(playback->codec);

    playback->codecOpened = playback->codec->m_pCodec != NULL;


    if (!playback->codec->m_pCodec || !playback->codec->m_pCodec->Decode)
        return SMSLITE_ERR_CODEC;

    if (s_streams.frameRate && s_streams.frameRateBase) {
        int ms = (int)(((s64)s_streams.frameRateBase * 1000) /
                       s_streams.frameRate);

        if (ms > 0 && ms <= 1000)
            playback->frameMs = ms;
    }

    smsLiteDbg("pb codec init\n");

    g_pSPRTop = SMS_SPR_FREE;

    initOK = playback->codec->m_pCodec->Init ? playback->codec->m_pCodec->Init(playback->codec) : 0;

    smsLiteDbg("pb codec init ret %d\n", initOK);

    if (!initOK)
        return SMSLITE_ERR_CODEC;

    playback->outputMemory = memalign(64, SMSLITE_VIDEO_OUTPUT_BUFFER_SIZE);
    if (!playback->outputMemory)
        return SMSLITE_ERR_DECODE;

    playback->outputBuffer = SMS_RingBufferInit(
        playback->outputMemory,
        SMSLITE_VIDEO_OUTPUT_BUFFER_SIZE
    );

    if (!playback->outputBuffer)
        return SMSLITE_ERR_DECODE;

    if (!smsLiteInitPacketBuffers(&playback->container, playback->packetBuffers))
        return SMSLITE_ERR_PACKET;

    ret = smsLitePlaybackInitDisplay(playback);
    if (ret != SMSLITE_OK)
        return ret;

    if (playback->codec->HWCtl) {
        playback->codec->HWCtl(playback->codec, SMS_HWC_Init);
        playback->hwActive = 1;
    } else {
        return SMSLITE_ERR_CODEC;
    }

    FlushCache(0);

    smsLiteAudioOpen(playback);

    return SMSLITE_OK;
}
#endif

static void smsLitePreviewDrain(SMSLitePlayback* playback);

static int smsLitePlaybackPump(SMSLitePlayback* playback)
{
    SMS_Stream* packetStream;
    SMS_AVPacket* skipPacket;
    int packetRet;
    int streamIndex;
    int decodeRet;

#if SMSLITE_ENABLE_FULLSCREEN
    if (!playback->previewMode)
        smsLitePlaybackDrainOutput(playback);
    else
#endif
        smsLitePreviewDrain(playback);

    streamIndex = -1;
    packetRet = playback->container.ReadPacket(&playback->container, &streamIndex);

    if (packetRet <= 0)
        return 0;

    playback->packetsRead++;


    if (streamIndex < 0 || streamIndex >= (int)playback->container.m_nStm)
        return 1;

    packetStream = playback->container.m_pStm[streamIndex];
    if (!packetStream || !packetStream->m_pPktBuf)
        return 1;

    SMS_RingBufferPost(packetStream->m_pPktBuf);

    if (playback->audioActive && streamIndex == playback->audioStreamIndex) {
        skipPacket = (SMS_AVPacket*)SMS_RingBufferWait(packetStream->m_pPktBuf);

        if (skipPacket) {
            smsLiteVU0Sync();

            while (playback->audioCodec->m_pCodec->Decode(
                       playback->audioCodec,
                       playback->audioBuffer,
                       packetStream->m_pPktBuf
                   ) > 0)
                smsLiteAudioDrain(playback);

            smsLiteAudioDrain(playback);

            SMS_RingBufferFree(packetStream->m_pPktBuf, skipPacket->m_Size + 64);
        }

        return 1;
    }

    if (streamIndex != playback->videoStreamIndex) {
        skipPacket = (SMS_AVPacket*)SMS_RingBufferWait(packetStream->m_pPktBuf);

        if (skipPacket) {
            SMS_RingBufferFree(packetStream->m_pPktBuf, skipPacket->m_Size + 64);
        } else {
            SMS_RingBufferFree(packetStream->m_pPktBuf, packetRet + 64);
        }

        return 1;
    }


    smsLiteDbg("PUMP video decode start\n");

    decodeRet = playback->codec->m_pCodec->Decode(
        playback->codec,
        playback->outputBuffer,
        playback->videoStream->m_pPktBuf
    );

    smsLiteDbg("PUMP video decode ret=%d\n", (int)decodeRet);

#if SMSLITE_ENABLE_FULLSCREEN
    if (!playback->previewMode)
        smsLitePlaybackDrainOutput(playback);
#endif

    return 1;
}

extern void* _gp;

#define SMSLITE_THREAD_PRIO   SMS_THREAD_PRIORITY
#define SMSLITE_STACK_SIZE    0x10000

#if SMSLITE_ENABLE_FULLSCREEN
static unsigned char s_smsLiteReaderStack[SMSLITE_STACK_SIZE] __attribute__((aligned(64)));
static unsigned char s_smsLiteVideoStack [SMSLITE_STACK_SIZE] __attribute__((aligned(64)));
#if SMSLITE_ENABLE_AUDIO
static unsigned char s_smsLiteAudioStack [SMSLITE_STACK_SIZE] __attribute__((aligned(64)));
static unsigned char s_smsLiteAudioRStack[SMSLITE_STACK_SIZE] __attribute__((aligned(64)));
#endif
#endif

static SMSLitePlayback* s_smsLiteActive;

#if SMSLITE_ENABLE_FULLSCREEN
static void smsLiteReaderThread(void* apParam)
{
    SMSLitePlayback* pb = (SMSLitePlayback*)apParam;
    int streamIndex;
    int ret;

    smsLiteDbg("thr reader go\n");

    for (;;) {
        if (pb->stopRequested)
            break;

        streamIndex = -1;
        ret = pb->container.ReadPacket(&pb->container, &streamIndex);

        if (ret <= 0)
            break;

        pb->packetsRead++;

        if (streamIndex < 0 || streamIndex >= (int)pb->container.m_nStm)
            continue;

        {
            SMS_Stream* stream = pb->container.m_pStm[streamIndex];
            int wanted;

            if (!stream || !stream->m_pPktBuf)
                continue;

            wanted = (streamIndex == pb->videoStreamIndex) ||
                     (pb->audioActive && streamIndex == pb->audioStreamIndex);

            if (!wanted) {
                SMS_AVPacket* drop;

                SMS_RingBufferPost(stream->m_pPktBuf);
                drop = (SMS_AVPacket*)SMS_RingBufferWait(stream->m_pPktBuf);

                if (drop)
                    SMS_RingBufferFree(stream->m_pPktBuf, drop->m_Size + 64);
                else
                    SMS_RingBufferFree(stream->m_pPktBuf, ret + 64);

                continue;
            }

            SMS_RingBufferPost(stream->m_pPktBuf);
        }
    }

    pb->eof = 1;
}
#endif

#if SMSLITE_ENABLE_FULLSCREEN
static void smsLiteVideoThread(void* apParam)
{
    SMSLitePlayback* pb = (SMSLitePlayback*)apParam;

    smsLiteDbg("thr video go\n");

    for (;;) {
        while (SMS_RingBufferCount(pb->videoStream->m_pPktBuf) == 0) {
            if (pb->eof)
                goto videoExit;
            RotateThreadReadyQueue(SMSLITE_THREAD_PRIO);
        }

        if (pb->codec->m_pCodec->Decode(
                pb->codec, pb->outputBuffer, pb->videoStream->m_pPktBuf))
            RotateThreadReadyQueue(SMSLITE_THREAD_PRIO);
    }

videoExit:
    pb->videoDone = 1;

    {
        SMS_FrameBuffer** slot =
            (SMS_FrameBuffer**)SMS_RingBufferAlloc(pb->outputBuffer, 4);

        if (slot) {
            *slot = NULL;
            SMS_RingBufferPost(pb->outputBuffer);
        } else {
            /* ring full the renderer is already awake and will drain it.. then see videoDone on its next pass */
        }
    }
}
#endif

#if SMSLITE_ENABLE_FULLSCREEN
static void smsLiteAudioThread(void* apParam)
{
    SMSLitePlayback* pb = (SMSLitePlayback*)apParam;
    SMS_Stream* stream;
    SMS_AVPacket* pkt;

    stream = pb->container.m_pStm[pb->audioStreamIndex];

    smsLiteDbg("thr audio go\n");

    for (;;) {
        while (SMS_RingBufferCount(stream->m_pPktBuf) == 0) {
            if (pb->eof)
                goto audioExit;
            RotateThreadReadyQueue(SMSLITE_THREAD_PRIO);
        }

        pkt = (SMS_AVPacket*)SMS_RingBufferWait(stream->m_pPktBuf);
        if (!pkt)
            break;

        smsLiteVU0Sync();

        while (pb->audioCodec->m_pCodec->Decode(pb->audioCodec, pb->audioBuffer, stream->m_pPktBuf) > 0);

        SMS_RingBufferFree(stream->m_pPktBuf, pkt->m_Size + 64);
    }

audioExit:
    pb->audioDone = 1;
}
#endif

#if SMSLITE_ENABLE_FULLSCREEN
static void smsLiteAudioRenderThread(void* apParam)
{
    SMSLitePlayback* pb = (SMSLitePlayback*)apParam;

    smsLiteDbg("thr arender go\n");

    for (;;) {
        while (s_smsLitePaused && !pb->stopRequested) /* RIPPS2: paused, nothing more goes to audsrv */
            DelayThread(10000);
        while (SMS_RingBufferCount(pb->audioBuffer) == 0) {
            if (pb->audioDone)
                goto arExit;

            DelayThread(500);
#ifdef SMSLITE_DUMP_PCM
            ++s_dumpRenderEmpty;
#endif
        }

        smsLiteAudioDrain(pb);
    }

arExit:
    pb->audioRenderDone = 1;
}
#endif

#if SMSLITE_ENABLE_FULLSCREEN
static int smsLitePlaybackRunThreaded(SMSLitePlayback* playback)
{
    ee_thread_t thread;
    int readerTID, videoTID, audioTID, audioRenderTID;

    playback->stopRequested   = 0;
    s_smsLitePaused           = 0; /* RIPPS2 */
    playback->eof             = 0;
    playback->videoDone       = 0;
    playback->audioDone       = 0;
    playback->audioRenderDone = 0;

#ifdef SMSLITE_DUMP_PCM
    smsDumpReset();
#endif

    s_smsLiteActive = playback;

    {
        ee_thread_status_t st;
        if (ReferThreadStatus(GetThreadId(), &st) >= 0)
            playback->callerPrio = st.current_priority;
        else
            playback->callerPrio = SMSLITE_THREAD_PRIO;
    }

    ChangeThreadPriority(GetThreadId(), SMSLITE_THREAD_PRIO - 1);

    memset(&thread, 0, sizeof(thread));

    /* video decode thread */
    thread.stack_size       = SMSLITE_STACK_SIZE;
    thread.stack            = s_smsLiteVideoStack;
    thread.initial_priority = SMSLITE_THREAD_PRIO;
    thread.gp_reg           = &_gp;
    thread.func             = smsLiteVideoThread;
    videoTID = CreateThread(&thread);

    audioTID = -1;
    audioRenderTID = -1;
#if SMSLITE_ENABLE_AUDIO
    if (playback->audioActive) {
        thread.stack_size       = SMSLITE_STACK_SIZE;
        thread.stack            = s_smsLiteAudioStack;
        thread.initial_priority = SMSLITE_THREAD_PRIO;
        thread.gp_reg           = &_gp;
        thread.func             = smsLiteAudioThread;
        audioTID = CreateThread(&thread);

        thread.stack_size       = SMSLITE_STACK_SIZE;
        thread.stack            = s_smsLiteAudioRStack;

        thread.initial_priority = SMSLITE_THREAD_PRIO - 2;
        thread.gp_reg           = &_gp;
        thread.func             = smsLiteAudioRenderThread;
        audioRenderTID = CreateThread(&thread);

        if (audioTID < 0 || audioRenderTID < 0) {
            smsLiteDbg("audio thread create failed (%d/%d) - video only\n", audioTID, audioRenderTID);

            if (audioTID >= 0)
                DeleteThread(audioTID);
            if (audioRenderTID >= 0)
                DeleteThread(audioRenderTID);

            audioTID       = -1;
            audioRenderTID = -1;

            playback->audioActive     = 0;
            playback->audioDone       = 1;
            playback->audioRenderDone = 1;
        }
    }
#endif

    /* reader thread */
    thread.stack_size       = SMSLITE_STACK_SIZE;
    thread.stack            = s_smsLiteReaderStack;
    thread.initial_priority = SMSLITE_THREAD_PRIO;
    thread.gp_reg           = &_gp;
    thread.func             = smsLiteReaderThread;
    readerTID = CreateThread(&thread);

    smsLiteDbg("tids v%d a%d ar%d r%d\n", videoTID, audioTID, audioRenderTID, readerTID);

    if (videoTID < 0 || readerTID < 0) {
        smsLiteDbg("thread create failed (v%d r%d) - unwinding\n", videoTID, readerTID);

        if (videoTID >= 0)
            DeleteThread(videoTID);
        if (readerTID >= 0)
            DeleteThread(readerTID);
        if (audioTID >= 0)
            DeleteThread(audioTID);
        if (audioRenderTID >= 0)
            DeleteThread(audioRenderTID);

        s_smsLiteActive = NULL;
        ChangeThreadPriority(GetThreadId(), playback->callerPrio);

        return SMSLITE_ERR_DECODE;
    }

    if (StartThread(videoTID, playback) < 0 ||
        (audioTID >= 0       && StartThread(audioTID, playback) < 0) ||
        (audioRenderTID >= 0 && StartThread(audioRenderTID, playback) < 0) ||
        StartThread(readerTID, playback) < 0) {

        smsLiteDbg("StartThread failed - unwinding\n");

        TerminateThread(readerTID);
        TerminateThread(videoTID);
        if (audioTID >= 0)
            TerminateThread(audioTID);
        if (audioRenderTID >= 0)
            TerminateThread(audioRenderTID);

        DeleteThread(readerTID);
        DeleteThread(videoTID);
        if (audioTID >= 0)
            DeleteThread(audioTID);
        if (audioRenderTID >= 0)
            DeleteThread(audioRenderTID);

        s_smsLiteActive = NULL;
        ChangeThreadPriority(GetThreadId(), playback->callerPrio);

        return SMSLITE_ERR_DECODE;
    }

    smsLiteDbg("thr render go\n");

    for (;;) {
        void* slot;
        SMS_FrameBuffer* frame;

        if (playback->stopRequested)
            playback->eof = 1;

        slot = SMS_RingBufferWait(playback->outputBuffer);
        if (!slot)
            break;

        frame = *((SMS_FrameBuffer**)slot);

        SMS_RingBufferFree(playback->outputBuffer, 4);

        if (!frame)
            break;

        if (playback->framesDisplayed == 0)
            smsLiteDbg("first frame\n");

        smsLitePlaybackShowFrame(playback, frame);
    }

    while (playback->audioActive &&
           (!playback->audioDone || !playback->audioRenderDone))
        RotateThreadReadyQueue(SMSLITE_THREAD_PRIO);

    TerminateThread(readerTID);
    TerminateThread(videoTID);
    if (audioTID >= 0)
        TerminateThread(audioTID);
    if (audioRenderTID >= 0)
        TerminateThread(audioRenderTID);
    DeleteThread(readerTID);
    DeleteThread(videoTID);
    if (audioTID >= 0)
        DeleteThread(audioTID);
    if (audioRenderTID >= 0)
        DeleteThread(audioRenderTID);

    ChangeThreadPriority(GetThreadId(), playback->callerPrio);

    s_smsLiteActive = NULL;

#ifdef SMSLITE_DUMP_PCM
    smsDumpWrite();
#endif

    return playback->framesDisplayed > 0 ? SMSLITE_OK : SMSLITE_ERR_DECODE;
}
#endif

#if SMSLITE_ENABLE_FULLSCREEN
static int smsLitePlaybackRun(SMSLitePlayback* playback, int targetFrames, int maxPackets)
{
    if (targetFrames <= 0)
        return smsLitePlaybackRunThreaded(playback);

    while (playback->packetsRead < maxPackets) {
        if (playback->framesDisplayed >= targetFrames)
            break;

        if (!smsLitePlaybackPump(playback))
            break;
    }

    smsLitePlaybackDrainOutput(playback);

    return playback->framesDisplayed >= targetFrames ? SMSLITE_OK
                                                     : SMSLITE_ERR_DECODE;
}
#endif

/* ------------------------------------------------------------------ */
/* Public API                                                         */
/* ------------------------------------------------------------------ */

const char* smsLiteVersion(void)
{
    return "libsmslite 0.2";
}

int smsLiteInit(void)
{
    if (!s_smsLiteInitialized)
        smsLiteInitConfig();

    s_smsLiteInitialized = 1;

    smsLiteResetStreams();
    smsLiteClearPacketInfo();
    smsLiteClearDecoderInfo();
    smsLiteClearDecodeInfo();

    return SMSLITE_OK;
}

void smsLiteShutdown(void)
{
    s_smsLiteInitialized = 0;
}

void smsLiteStop(void)
{
    SMSLitePlayback* active = s_smsLiteActive;

    if (active)
        active->stopRequested = 1;
}

void smsLitePause(int on) /* RIPPS2 */
{
    s_smsLitePaused = on ? 1 : 0;
}

/* ------------------------------------------------------------------ */
/* Fullscreen playback                                                */
/* ------------------------------------------------------------------ */

#if SMSLITE_ENABLE_FULLSCREEN
int smsLitePlayFullscreen(const char* path)
{
    SMSLitePlayback playback;
    int ret;
    int framesDisplayed;
    int packetsRead;

    if (!s_smsLiteInitialized)
        return SMSLITE_ERR_INIT;

    if (!path || !path[0])
        return SMSLITE_ERR_OPEN;

    smsLiteClearDecodeInfo();
    smsLiteClearDecoderInfo();
    smsLiteClearPacketInfo();
    smsLiteResetStreams();

    smsLiteDbg("play start\n");

    ret = smsLitePlaybackOpen(&playback, path);
    if (ret != SMSLITE_OK) {
        smsLitePlaybackClose(&playback);
        return ret;
    }

    ret = smsLitePlaybackRun(&playback, 0, 0x7FFFFFFF);

#ifdef SMSLITE_DEBUG
    {
        const short* lpIM = SMS_QM_INTRA;
        const short* lpNM = SMS_QM_NON_INTRA;
        smsLiteDbg(
            "vol mq %d qpel %d tib %d rm %d dp %d\n",
            g_MPEGCtx.m_MPEGQuant, g_MPEGCtx.m_QuarterSample,
            g_MPEGCtx.m_TimeIncBits, g_MPEGCtx.m_ResyncMarker,
            g_MPEGCtx.m_DataPartitioning
        );
        smsLiteDbg(
            "im %d %d %d %d %d %d %d %d\n",
            lpIM[0], lpIM[1], lpIM[2], lpIM[3],
            lpIM[4], lpIM[5], lpIM[6], lpIM[7]
        );
        smsLiteDbg(
            "im8 %d %d %d %d %d %d %d %d\n",
            lpIM[8], lpIM[9], lpIM[10], lpIM[11],
            lpIM[12], lpIM[13], lpIM[14], lpIM[15]
        );
        smsLiteDbg(
            "nm %d %d %d %d %d %d %d %d\n",
            lpNM[0], lpNM[1], lpNM[2], lpNM[3],
            lpNM[4], lpNM[5], lpNM[6], lpNM[7]
        );
        smsLiteDbg(
            "q %d cq %d ydc %d cdc %d\n",
            g_MPEGCtx.m_QScale, g_MPEGCtx.m_ChromaQScale,
            g_MPEGCtx.m_Y_DCScale, g_MPEGCtx.m_C_DCScale
        );
    }
#endif

    framesDisplayed = playback.framesDisplayed;
    packetsRead = playback.packetsRead;

    smsLitePlaybackClose(&playback);

    smsLiteDbg("play stopped\n");
    smsLiteDbg("frames %d\n", framesDisplayed);
    smsLiteDbg("packets %d\n", packetsRead);

    if (framesDisplayed > 0)
        return SMSLITE_OK;

    return SMSLITE_ERR_DECODE;
}
#endif

static SMSLitePlayback  s_smsLitePreview;
static int              s_smsLitePreviewOpen   = 0;
static int              s_smsLitePreviewFlags  = 0;
static int              s_smsLitePreviewEOF    = 0;

typedef struct SMSLitePreviewPace {
    int          active;      /* 0 until the first frame has decoded   */
    unsigned int lastTicks;   /* cpu_ticks() at the previous Update    */
    s64          elapsed;     /* ticks since the first frame           */
    s64          frameIndex;  /* frames decoded so far                 */
    s64          periodNum;   /* kBUSCLK * frameRateBase               */
    unsigned int periodDen;   /* frameRate (0 = pacing disabled)       */
} SMSLitePreviewPace;

static SMSLitePreviewPace s_pace;

static void smsLitePreviewPaceReset(void)
{
    memset(&s_pace, 0, sizeof(s_pace));

    if (s_streams.frameRate && s_streams.frameRateBase) {
        s_pace.periodNum = (s64)kBUSCLK * (s64)s_streams.frameRateBase;
        s_pace.periodDen = s_streams.frameRate;
    }
}

static int smsLitePreviewPaceDue(void)
{
    unsigned int now;
    unsigned int delta;
    s64 due;
    s64 lead;

    if (!s_pace.periodDen)
        return 1;

    if (!s_pace.active)
        return 1;

    now   = cpu_ticks();
    delta = now - s_pace.lastTicks;
    s_pace.lastTicks = now;
    s_pace.elapsed += (s64)delta;

    due = (s_pace.periodNum * s_pace.frameIndex) / (s64)s_pace.periodDen;

    if (s_pace.elapsed < due)
        return 0;

    lead = s_pace.elapsed - due;
    if (lead > (s_pace.periodNum * 4) / (s64)s_pace.periodDen)
        s_pace.elapsed = due;

    return 1;
}

static void smsLitePreviewPaceFrameDone(void)
{
    if (!s_pace.periodDen)
        return;

    if (!s_pace.active) {
        s_pace.active    = 1;
        s_pace.lastTicks = cpu_ticks();
        s_pace.elapsed   = 0;
    }

    s_pace.frameIndex++;
}

static SMSLitePreviewFrame s_smsLitePreviewFrame;

static unsigned char*   s_smsLitePreviewDetile     = 0;
static unsigned int     s_smsLitePreviewDetileSize = 0;
static unsigned int     s_smsLitePreviewSerial = 0;
static unsigned int     s_smsLitePreviewSeen   = 0;

static void smsLitePreviewCaptureFrame(SMSLitePlayback* playback, SMS_FrameBuffer* frame)
{
    int w = playback->codec->m_Width;
    int h = playback->codec->m_Height;
    int f16 = (g_IPUCtx.m_TexFmt == GSPixelFormat_PSMCT16);
    int bpp = f16 ? 2 : 4;
    unsigned int bytes;

    int aw = (w + 15) & ~15;
    int ah = (h + 15) & ~15;

    bytes = (unsigned int)aw * (unsigned int)ah * (unsigned int)bpp;

    smsLiteDbg("CAP pre CSCSync\n");
    SMS_CSCSync();
    smsLiteDbg("CAP post CSCSync\n");

    if (frame->m_pBase)
        SyncDCache(frame->m_pBase,
                   (void*)((unsigned char*)frame->m_pBase + bytes));

    {
        int mbw   = aw >> 4; /* macroblocks per row  */
        int mbh   = ah >> 4; /* macroblock rows      */
        int mbx, mby, row;
        unsigned int mbIncr   = (unsigned int)(16 * 16 * bpp);
        unsigned int tileRow  = (unsigned int)(16 * bpp);
        unsigned int dstStride = (unsigned int)w * (unsigned int)bpp;
        unsigned char* src = (unsigned char*)frame->m_pBase;
        unsigned char* dst;
        unsigned int need = dstStride * (unsigned int)h;

        if (s_smsLitePreviewDetileSize < need) {
            if (s_smsLitePreviewDetile)
                free(s_smsLitePreviewDetile);
            s_smsLitePreviewDetile = (unsigned char*)memalign(64, need);
            s_smsLitePreviewDetileSize =
                s_smsLitePreviewDetile ? need : 0;
        }

        dst = s_smsLitePreviewDetile;

        if (dst && src) {
            for (mby = 0; mby < mbh; ++mby) {
                for (mbx = 0; mbx < mbw; ++mbx) {
                    unsigned char* tile = src +
                        (unsigned int)(mby * mbw + mbx) * mbIncr;
                    int x0 = mbx * 16;
                    int y0 = mby * 16;
                    int cw = w - x0;
                    if (cw <= 0) continue;
                    if (cw > 16) cw = 16;

                    for (row = 0; row < 16; ++row) {
                        int y = y0 + row;
                        if (y >= h) break;
                        memcpy(dst + (unsigned int)y * dstStride + (unsigned int)x0 * (unsigned int)bpp, tile + (unsigned int)row * tileRow, (unsigned int)cw * (unsigned int)bpp);
                    }
                }
            }
        }

        if (!dst) {
            smsLiteDbg("CAP detile alloc failed (%u bytes) - frame dropped\n", need);
            frame->m_FrameType = -1;
            return;
        }

        SyncDCache(dst, (void*)(dst + need));

        s_smsLitePreviewFrame.pixels = dst;
    }

    s_smsLitePreviewFrame.width  = w;
    s_smsLitePreviewFrame.height = h;
    s_smsLitePreviewFrame.stride = w * bpp;

    s_smsLitePreviewFrame.format = (g_IPUCtx.m_PixFmt == GSPixelFormat_PSMCT16) ? SMSLITE_PIXFMT_RGBA16 : SMSLITE_PIXFMT_RGBA32;
    s_smsLitePreviewFrame.serial = ++s_smsLitePreviewSerial;

    frame->m_FrameType = -1;
}

static void smsLitePreviewDrain(SMSLitePlayback* playback)
{
    void* outputSlot;
    SMS_FrameBuffer* decodedFrame;
    int count;

    count = playback->outputBuffer ? SMS_RingBufferCount(playback->outputBuffer) : -1;
    smsLiteDbg("DRAIN enter count=%d\n", count);

    while (playback->outputBuffer &&
           SMS_RingBufferCount(playback->outputBuffer) > 0) {

        outputSlot = SMS_RingBufferWait(playback->outputBuffer);
        decodedFrame = outputSlot ? *((SMS_FrameBuffer**)outputSlot) : NULL;

        smsLiteDbg("DRAIN frame=%p\n", (void*)decodedFrame);

        if (decodedFrame)
            smsLitePreviewCaptureFrame(playback, decodedFrame);

        SMS_RingBufferFree(playback->outputBuffer, 4);
    }
    smsLiteDbg("DRAIN exit\n");
}

static int smsLitePreviewOpenInternal(SMSLitePlayback* playback, const char* path, int flags)
{
    int ret;

    memset(playback, 0, sizeof(*playback));

    playback->previewMode = 1;

    playback->fileCtx = smsLiteOpenFileContext(path);
    if (!playback->fileCtx)
        return SMSLITE_ERR_OPEN;

    playback->container.m_pFileCtx = playback->fileCtx;
    playback->container.AllocPacket = smsLiteAllocPacket;

#ifdef SMSLITE_DEBUG
    smsLiteDbg("prev: parsing container...\n");
#endif

    ret = SMS_GetContainerAVI(&playback->container);

#ifdef SMSLITE_DEBUG
    smsLiteDbg("prev: container ret=%d nstm=%d\n", ret, (int)playback->container.m_nStm);
#endif

    if (!ret || playback->container.m_nStm == 0 || !playback->container.ReadPacket)
        return SMSLITE_ERR_CONTAINER;

    smsLiteSelectStreams(&playback->container);

    if (s_streams.videoIndex < 0 || s_streams.videoIndex >= (int)playback->container.m_nStm)
        return SMSLITE_ERR_CODEC;

    playback->videoStreamIndex = s_streams.videoIndex;
    playback->videoStream = playback->container.m_pStm[playback->videoStreamIndex];

    if (!playback->videoStream || !playback->videoStream->m_pCodec)
        return SMSLITE_ERR_CODEC;

    playback->codec = playback->videoStream->m_pCodec;

    if (playback->codec->m_ID != SMS_CodecID_MPEG4)
        return SMSLITE_ERR_UNSUPPORTED;

    SMS_Codec_MPEG4_Open(playback->codec);

    if (!playback->codec->m_pCodec || !playback->codec->m_pCodec->Decode)
        return SMSLITE_ERR_CODEC;

#ifdef SMSLITE_DEBUG
    extern int smsLiteMpeg4InitCount(void);
    smsLiteDbg("mpeg4 s_Init(pre)=%d\n", smsLiteMpeg4InitCount());
#endif

    g_pSPRTop = SMS_SPR_FREE;

    if (playback->codec->m_pCodec->Init &&
        !playback->codec->m_pCodec->Init(playback->codec))
        return SMSLITE_ERR_CODEC;

    playback->outputMemory = memalign(64, SMSLITE_VIDEO_OUTPUT_BUFFER_SIZE);
    if (!playback->outputMemory)
        return SMSLITE_ERR_DECODE;

    playback->outputBuffer = SMS_RingBufferInit(
        playback->outputMemory,
        SMSLITE_VIDEO_OUTPUT_BUFFER_SIZE
    );
    if (!playback->outputBuffer)
        return SMSLITE_ERR_DECODE;

    if (!smsLiteInitPacketBuffers(&playback->container, playback->packetBuffers))
        return SMSLITE_ERR_PACKET;

    if (!g_GSCtx.m_PWidth) {
        g_GSCtx.m_PWidth  = 640;
        g_GSCtx.m_PHeight = 448;
        g_GSCtx.m_Width   = 640;
        g_GSCtx.m_Height  = 448;
        g_GSCtx.m_VRAMPtr    = 0x1200;
        g_GSCtx.m_VRAMPtr2   = 0x1200;
        g_GSCtx.m_VRAMFontPtr = 0;
    }

    if (!GS_Params()->m_GSCRTMode)
        GS_Params()->m_GSCRTMode = smsLiteDetectVideoMode();

    playback->ipuCtx = IPU_InitContext(playback->codec->m_Width, playback->codec->m_Height, NULL, playback->codec->m_fWS);

    if (!playback->ipuCtx)
        return SMSLITE_ERR_DECODE;

    if (playback->codec->HWCtl) {
        playback->codec->HWCtl(playback->codec, SMS_HWC_Init);
        playback->hwActive = 1;
    }

#ifdef SMSLITE_DEBUG
    smsLiteDbg("prev w=%d h=%d pixfmt=%d texfmt=%d\n", playback->codec->m_Width, playback->codec->m_Height, (int)g_IPUCtx.m_PixFmt, (int)g_IPUCtx.m_TexFmt);

    SMS_VideoBuffer* vb = (SMS_VideoBuffer*)playback->codec->m_pIntBuf;
    smsLiteDbg("intbuf=%p free=%p\n", (void*)vb, vb ? (void*)vb->m_pFree : (void*)0);
#endif

    if (!(flags & SMSLITE_PREVIEW_VIDEO_ONLY)) {
        smsLiteAudioOpen(playback);
    }

    return SMSLITE_OK;
}

int smsLitePreviewOpen(const char* path, int flags)
{
    int ret;

    if (!s_smsLiteInitialized)
        return SMSLITE_ERR_INIT;

    if (!path || !path[0])
        return SMSLITE_ERR_OPEN;

    if (s_smsLitePreviewOpen)
        smsLitePreviewClose();

    s_smsLitePreviewFlags  = flags;
    s_smsLitePreviewEOF    = 0;
    s_smsLitePreviewSerial = 0;
    s_smsLitePreviewSeen   = 0;
    memset(&s_smsLitePreviewFrame, 0, sizeof(s_smsLitePreviewFrame));

    ret = smsLitePreviewOpenInternal(&s_smsLitePreview, path, flags);
    if (ret != SMSLITE_OK) {
        smsLitePlaybackClose(&s_smsLitePreview);
        return ret;
    }

    s_smsLitePreviewOpen = 1;
#ifdef SMSLITE_DEBUG
    smsLiteDbg("prev: open OK, entering render loop\n");
#endif
    return SMSLITE_OK;
}

static int smsLitePreviewSeekToStart(SMSLitePlayback* pb)
{
    FileContext* fc = pb->fileCtx;
    unsigned int moviStart = smsLiteContainerMoviStart(&pb->container);

    if (!fc || !fc->Seek || moviStart == 0)
        return 0;

    fc->Seek(fc, moviStart);
    return 1;
}

int smsLitePreviewUpdate(void)
{
    SMSLitePlayback* pb = &s_smsLitePreview;
    unsigned int before;
    int guard;

    if (!s_smsLitePreviewOpen)
        return SMSLITE_PREVIEW_ERROR;

    if (s_smsLitePreviewEOF)
        return SMSLITE_PREVIEW_EOF;

    before = s_smsLitePreviewSerial;
    guard  = 0;

    smsLiteDbg("UPD enter serial=%d\n", (int)before);

    if (!smsLitePreviewPaceDue()) {
        smsLiteDbg("UPD early, holding frame\n");
        return SMSLITE_PREVIEW_OK;
    }

    while (++guard <= 512) {
        int pr;

        smsLiteDbg("UPD pump#%d\n", guard);
        pr = smsLitePlaybackPump(pb);
        smsLiteDbg("UPD pump#%d ret=%d\n", guard, pr);

        if (!pr) {
            smsLiteDbg("UPD eof, draining\n");
            smsLitePreviewDrain(pb);

            if (s_smsLitePreviewFlags & SMSLITE_PREVIEW_LOOP) {
                smsLiteDbg("UPD loop: seek to start\n");
                if (smsLitePreviewSeekToStart(pb)) {
                    pb->packetsRead = 0;
                    smsLiteDbg("UPD loop: seek ok, ret OK\n");
                    return SMSLITE_PREVIEW_OK;
                }
                smsLiteDbg("UPD loop: seek FAILED\n");
            }

            s_smsLitePreviewEOF = 1;
            smsLiteDbg("UPD ret EOF\n");
            return SMSLITE_PREVIEW_EOF;
        }

        smsLiteDbg("UPD drain#%d\n", guard);
        smsLitePreviewDrain(pb);

        if (s_smsLitePreviewSerial != before) {
            smsLitePreviewPaceFrameDone();
            smsLiteDbg("UPD got frame#%d guard=%d ret OK\n",
                               (int)s_smsLitePreviewSerial, guard);
            return SMSLITE_PREVIEW_OK;
        }
    }

    smsLiteDbg("UPD guard exhausted.. ret OK\n");
    return SMSLITE_PREVIEW_OK;
}

int smsLitePreviewFrameReady(void)
{
    if (!s_smsLitePreviewOpen)
        return 0;
    return s_smsLitePreviewSerial != s_smsLitePreviewSeen && s_smsLitePreviewFrame.pixels != NULL;
}

const SMSLitePreviewFrame* smsLitePreviewFrame(void)
{
    if (!s_smsLitePreviewOpen || !s_smsLitePreviewFrame.pixels)
        return NULL;

    s_smsLitePreviewSeen = s_smsLitePreviewSerial;
    return &s_smsLitePreviewFrame;
}

void smsLitePreviewClose(void)
{
    if (!s_smsLitePreviewOpen)
        return;

    smsLitePlaybackClose(&s_smsLitePreview);

    if (s_smsLitePreviewDetile) {
        free(s_smsLitePreviewDetile);
        s_smsLitePreviewDetile     = 0;
        s_smsLitePreviewDetileSize = 0;
    }

    memset(&s_pace, 0, sizeof(s_pace));

    s_smsLitePreviewOpen   = 0;
    s_smsLitePreviewEOF    = 0;
    s_smsLitePreviewSerial = 0;
    s_smsLitePreviewSeen   = 0;
    memset(&s_smsLitePreviewFrame, 0, sizeof(s_smsLitePreviewFrame));
}
