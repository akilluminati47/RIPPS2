/*
#     ___  _ _      ___
#    |    | | |    |
# ___|    |   | ___|    PS2DEV Open Source Project.
#----------------------------------------------------------
# (c) 2005-2008 Eugene Plotnikov <e-plotnikov@operamail.com>
# (c) 2006 hjx (widescreen support)
# Licenced under Academic Free License version 2.0
# Review ps2sdk README & LICENSE files for further details.
#
*/
#include <kernel.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "ps2/intc.h"
#include "ps2/dma.h"
#include "core/config.h"
#include "ps2/ipu.h"
#include "ps2/gs.h"
#include "ps2/ee.h"
#include "core/sms.h"
#include "ps2/videobuffer.h"
#include "ps2/vsync.h"

#define IPUF_WS 0x00000001
#define IPUF_PG 0x00000002
#define IPUF_FL 0x00000040

IPUContext        g_IPUCtx;
u64               s_DMAVIFDraw[ 16 ] __attribute__(   (  aligned( 64 )  )   );
u64               s_DMAGIFDraw[ 22 ] __attribute__(   (  aligned( 64 )  )   );

static int              s_SyncS;
       u64              s_VIFQueue[ 16 ];
       unsigned char    s_QIdx;

static void IPU_SyncNop ( void ) {

}  /* end IPU_SyncNop */

static void IPU_DestroyContext ( void ) {

 DeleteSema ( s_SyncS );

 IPU_RESET();

}  /* end IPU_DestroyContext */

void IPU_Flush ( void );
__asm__(
 ".set noreorder\n\t"
 ".set nomacro\n\t"
 ".text\n\t"
 "IPU_Flush:\n\t"
 "lbu      $a0, s_QIdx\n\t"
 "lui      $v0, 0x2000\n\t"
 "beqz     $a0, 2f\n\t"
 "la       $a1, s_VIFQueue\n\t"
 "la       $a2, s_DMAVIFDraw\n\t"
 "la       " ASM_REG_T0 ", s_DMAVIFDraw\n\t"
 "or       $a2, $a2, $v0\n\t"
 "1:\n\t"
 "ld       $v0, 0($a1)\n\t"
 "addiu    $a1, $a1, 8\n\t"
 "addiu    $a0 , $a0, -8\n\t"
 "lui      $v1, 0x1001\n\t"
 "sd       $v0, 0($a2)\n\t"
 "bnez     $a0, 1b\n\t"
 "addiu    $a2, $a2, 16\n\t"
 "sh       $zero, -14($a2)\n\t"
 "1:\n\t"
 "lw       $v0, -0x7000($v1)\n\t"
 "nop\n\t"
 "nop\n\t"
 "andi     $v0, $v0, 256\n\t"
 "nop\n\t"
 "bne      $v0, $zero, 1b\n\t"
 "addiu    $v0, $zero, 261\n\t"
 "sw       $zero, -0x6FE0($v1)\n\t"
 "sw       " ASM_REG_T0 ",   -0x6FD0($v1)\n\t"
 "sw       $v0,   -0x7000($v1)\n\t"
 "sb       $zero, s_QIdx\n\t"
 "2:\n\t"
 "jr       $ra\n\t"
 "nop\n\t"
 ".set macro\n\t"
 ".set reorder\n\t"
);

static void IPU_SetTEX ( void ) {

 u64*           lpDMA = UNCACHED_SEG( g_IPUCtx.m_DMAGIFTX );

 lpDMA[ 0 ] = GIF_TAG( 3, 1, 0, 0, 0, 1 );
 lpDMA[ 1 ] = GIFTAG_REGS_AD;
 lpDMA[ 2 ] = GS_SET_TEX1( 0, 0, 1, 1, 0, 0, 0 );
 lpDMA[ 3 ] = GS_TEX1_1;
 lpDMA[ 4 ] = GS_SET_FRAME_2( g_IPUCtx.m_VRAM >> 5, g_IPUCtx.m_TBW, g_IPUCtx.m_TexFmt, 0 );
 lpDMA[ 5 ] = GS_FRAME_2;
 lpDMA[ 6 ] = GS_SET_SCISSOR_2( 0, g_IPUCtx.m_Width, 0, g_IPUCtx.m_Height );
 lpDMA[ 7 ] = GS_SCISSOR_2;
 __asm__ __volatile__( "sync.l\n\t" );
 DMA_Send ( DMAC_GIF, g_IPUCtx.m_DMAGIFTX, 4 );

}  /* end IPU_SetTEX */

extern void PowerOf2 ( int, int, int*, int* );

static void IPU_Display ( void* apFB, s64  aVideoPTS ) {

 SMS_FrameBuffer* lpFrame   = ( SMS_FrameBuffer* )apFB;
 u64*             lpGIFPack = ( u64*             )(  ( unsigned int )&g_IPUCtx.m_DMAGIFPack[ 0 ] | 0x20000000  );

 SMS_CSCSync ();

 lpGIFPack[ 0 ] = DMA_TAG(  0, 0, DMATAG_ID_CALL, 0, ( unsigned int )lpFrame -> m_pData, 0  );

 __asm__ __volatile__( "sync.l\n\t" );

 DMA_SendChain ( DMAC_GIF, g_IPUCtx.m_DMAGIFPack );
 DMA_Wait ( DMAC_GIF );

 lpFrame -> m_FrameType = -1;
 g_IPUCtx.m_VideoPTS    = aVideoPTS;

}  /* end IPU_Display */


static void _ipu_compute_fields ( unsigned int anIdx, unsigned int aWidth ) {

 float lAR    = ( float )aWidth / ( float )g_IPUCtx.m_Height;
 int   lDelta = ( g_IPUCtx.m_Width - aWidth ) / 2;
 int   lShift = g_XShift;

 if ( g_IPUCtx.m_fWS && anIdx < 4 ) lAR += ( 16.0F / 9.0F - 4.0F / 3.0F );

 g_IPUCtx.m_TxtLeft  [ anIdx ] = ( lDelta << 4 ) + 8;
 g_IPUCtx.m_TxtTop   [ anIdx ] = 8;
 g_IPUCtx.m_TxtRight [ anIdx ] = ( aWidth << 4 ) + g_IPUCtx.m_TxtLeft[ anIdx ] - 6;
 g_IPUCtx.m_TxtBottom[ anIdx ] = ( g_IPUCtx.m_Height << 4 ) - 6;

 if ( g_GSCtx.m_Width < g_GSCtx.m_Height * lAR ) {

  int lH;
  int lTop;
  int lBottom;

  if ( anIdx > 4 ) lAR *= 3.0F / 4.0F;

  lH      = ( int )( g_GSCtx.m_Width / lAR );
  lTop    = ( g_GSCtx.m_Height > lH ? g_GSCtx.m_Height - lH : lH - g_GSCtx.m_Height ) >> 1;
  lBottom = lTop + lH;

  __asm__ __volatile__(
   ".set noreorder\n\t"
   "pcpyld  $ra, $ra, $ra\n\t"
   "dsll32  %3, %3, 0\n\t"
   "move    $a0, $zero\n\t"
   "move    $a1, %2\n\t"
   "move    $a2, $zero\n\t"
   "jal     GS_XYZ\n\t"
   "or      $a1, $a1, %3\n\t"
   "srl     %0, $v0, 16\n\t"
   "dsrl32  %1, $a1, 16\n\t"
   "pcpyud  $ra, $ra, $ra\n\t"
   ".set reorder\n\t"
   : "=r"( lTop ), "=r"( lBottom )
   :  "r"( lTop ),  "r"( lBottom )
   : "a0", "a1", "a2", "v0", "v1"
  );

  g_IPUCtx.m_ImgLeft  [ anIdx ] = 0;
  g_IPUCtx.m_ImgRight [ anIdx ] = (  ( g_GSCtx.m_Width << 4 ) >> lShift  ) - 6;
  g_IPUCtx.m_ImgTop   [ anIdx ] = lTop;
  g_IPUCtx.m_ImgBottom[ anIdx ] = lBottom - 15;

 } else {

  int lW = ( int )(  ( float )g_GSCtx.m_Height * lAR + 0.5F  );

  g_IPUCtx.m_ImgTop   [ anIdx ] = 0;
  g_IPUCtx.m_ImgBottom[ anIdx ] = g_IPUCtx.m_ScrBottom - 15;
  g_IPUCtx.m_ImgLeft  [ anIdx ] = (   (  ( g_GSCtx.m_Width - lW ) >> 1  ) << 4   ) >> lShift;
  g_IPUCtx.m_ImgRight [ anIdx ] = ( g_IPUCtx.m_ImgLeft[ anIdx ] + (  ( lW << 4 ) >> lShift  ) ) - 15;

 }  /* end else */

}  /* end _ipu_compute_fields */


static void IPU_ChangeMode ( unsigned int anIdx ) {

 if ( anIdx < 8 ) {

  int lImgTop = g_IPUCtx.m_ImgTop   [ anIdx ];
  int lImgBtm = g_IPUCtx.m_ImgBottom[ anIdx ];
  int lDelta  = g_Config.m_ImgOffs << 4;

  if ( lImgTop + lDelta < 0 )
   lDelta -= lImgTop + lDelta;
  else if ( lImgBtm + lDelta > g_IPUCtx.m_ScrBottom )
   lDelta -= ( lImgBtm + lDelta ) - g_IPUCtx.m_ScrBottom;

  lImgTop += lDelta;
  lImgBtm += lDelta;

  g_IPUCtx.m_ModeIdx = anIdx;

  SMS_EEDIntr ();
   s_DMAGIFDraw[  0 ] = GIF_TAG( 1, 0, 0, 0, 1, 6 );
   s_DMAGIFDraw[  1 ] = ( GS_TEX0_1 <<  0 ) | ( GS_PRIM <<  4 ) |
                        ( GS_UV     <<  8 ) | ( GS_XYZ2 << 12 ) |
                        ( GS_UV     << 16 ) | ( GS_XYZ2 << 20 );
   s_DMAGIFDraw[  2 ] = GS_SET_TEX0(
                         g_IPUCtx.m_VRAM, g_IPUCtx.m_TBW, g_IPUCtx.m_TexFmt,
                         g_IPUCtx.m_TW, g_IPUCtx.m_TH, 0, 1, 0, 0, 0, 0, 0
                        );
   s_DMAGIFDraw[  3 ] = GS_SET_PRIM( GS_PRIM_PRIM_SPRITE, 0, 1, 0, 0, 0, 1, 0, 0 );
   s_DMAGIFDraw[  4 ] = GS_SET_UV( g_IPUCtx.m_TxtLeft  [ anIdx ], g_IPUCtx.m_TxtTop   [ anIdx ] );
   s_DMAGIFDraw[  5 ] = GS_SET_XYZ( g_IPUCtx.m_ImgLeft [ anIdx ], lImgTop, 0 );
   s_DMAGIFDraw[  6 ] = GS_SET_UV( g_IPUCtx.m_TxtRight [ anIdx ], g_IPUCtx.m_TxtBottom[ anIdx ] );
   s_DMAGIFDraw[  7 ] = GS_SET_XYZ( g_IPUCtx.m_ImgRight[ anIdx ], lImgBtm, 0 );
   s_DMAGIFDraw[  8 ] = GIF_TAG( 3, 0, 0, 0, 0, 1 );
   s_DMAGIFDraw[  9 ] = GIFTAG_REGS_AD;
   s_DMAGIFDraw[ 10 ] = GS_SET_TEX1( 0, 0, 1, 1, 0, 0, 0 );
   s_DMAGIFDraw[ 11 ] = GS_TEX1_1;
   s_DMAGIFDraw[ 12 ] = GS_SET_PRIM( GS_PRIM_PRIM_SPRITE, 0, 0, 0, 0, 0, 0, 0, 0 );
   s_DMAGIFDraw[ 13 ] = GS_PRIM;
   s_DMAGIFDraw[ 14 ] = GS_SET_RGBAQ( 0x00, 0x00, 0x00, 0x00, 0x00 );
   s_DMAGIFDraw[ 15 ] = GS_RGBAQ;
   s_DMAGIFDraw[ 16 ] = GIF_TAG( 2, 1, 0, 0, 1, 2 );
   s_DMAGIFDraw[ 17 ] = GS_XYZ2 | ( GS_XYZ2 << 4 );
   s_DMAGIFDraw[ 18 ] = GS_SET_XYZ( 0, 0, 0 );
   if ( !g_IPUCtx.m_ImgLeft[ anIdx ] ) {
    s_DMAGIFDraw[ 19 ] = GS_SET_XYZ( g_IPUCtx.m_ScrRight, lImgTop, 0 );
    s_DMAGIFDraw[ 20 ] = GS_SET_XYZ( 0, lImgBtm, 0 );
    s_DMAGIFDraw[ 21 ] = GS_SET_XYZ( g_IPUCtx.m_ScrRight, g_IPUCtx.m_ScrBottom, 0 );
   } else {
    s_DMAGIFDraw[ 19 ] = GS_SET_XYZ( g_IPUCtx.m_ImgLeft [ anIdx ], g_IPUCtx.m_ScrBottom, 0 );
    s_DMAGIFDraw[ 20 ] = GS_SET_XYZ( g_IPUCtx.m_ImgRight[ anIdx ], 0, 0 );
    s_DMAGIFDraw[ 21 ] = GS_SET_XYZ( g_IPUCtx.m_ScrRight, g_IPUCtx.m_ScrBottom, 0 );
   }  /* end else */
   SyncDCache ( s_DMAGIFDraw, &s_DMAGIFDraw[ 22 ] );
  SMS_EEIntr ( 1 );

 }  /* end if */

}  /* end IPU_ChangeMode */

static void IPU_Reset ( void ) {

 float lHeight = g_IPUCtx.m_fWS ? ( float )g_IPUCtx.m_Height * ( 3.0F / 4.0F ) : ( float )g_IPUCtx.m_Height;
 float lAR     = (  ( float )g_GSCtx.m_Width  ) / (  ( float )g_GSCtx.m_Height  );
 int   lWP     = ( int )( lHeight * lAR );
 int   lDelta  = (  ( int )g_IPUCtx.m_Width - lWP  ) / 3;

 _ipu_compute_fields ( 0, g_IPUCtx.m_Width );  /* letterbox  */

 if ( lDelta > 0 ) {

  _ipu_compute_fields ( 1, g_IPUCtx.m_Width - lDelta          );  /* pan-scan 1 */
  _ipu_compute_fields ( 2, g_IPUCtx.m_Width - lDelta - lDelta );  /* pan-scan 2 */
  _ipu_compute_fields ( 3, lWP                                );  /* pan-scan 3 */

 } else {

 _ipu_compute_fields ( 1, g_IPUCtx.m_Width );  /* pan-scan 1 */
 _ipu_compute_fields ( 2, g_IPUCtx.m_Width );  /* pan-scan 2 */
 _ipu_compute_fields ( 3, g_IPUCtx.m_Width );  /* pan-scan 3 */

 }  /* end else */

 g_IPUCtx.m_TxtLeft  [ 4 ] = 8;
 g_IPUCtx.m_TxtTop   [ 4 ] = 8;
 g_IPUCtx.m_TxtRight [ 4 ] = ( g_IPUCtx.m_Width  << 4 ) - 16;
 g_IPUCtx.m_TxtBottom[ 4 ] = ( g_IPUCtx.m_Height << 4 ) - 16;

 g_IPUCtx.m_ImgLeft  [ 4 ] = 0;
 g_IPUCtx.m_ImgTop   [ 4 ] = 0;
 g_IPUCtx.m_ImgRight [ 4 ] = g_GSCtx.m_PWidth  << 4;
 g_IPUCtx.m_ImgBottom[ 4 ] = g_GSCtx.m_PHeight << 4;

 lAR    = 16.0F / 9.0F;
 lWP    = ( int )(  ( float )g_IPUCtx.m_Height * lAR  );
 lDelta = (  ( int )g_IPUCtx.m_Width - lWP  ) / 2;

 _ipu_compute_fields ( 5, g_IPUCtx.m_Width );  /* widescreen  */

 if ( lDelta > 0 ) {
  _ipu_compute_fields ( 6, g_IPUCtx.m_Width - lDelta );  /* widescreen pan-scan 1 */
  _ipu_compute_fields ( 7, lWP                       );  /* widescreen pan-scan 2 */
 } else {
  _ipu_compute_fields ( 6, g_IPUCtx.m_Width );  /* widescreen pan-scan 3 */
  _ipu_compute_fields ( 7, g_IPUCtx.m_Width );  /* widescreen pan-scan 3 */
 }  /* end else */

 IPU_ChangeMode ( g_Config.m_PlayerFlags >> 28 );

}  /* end IPU_Reset */

static void IPU_SetBrightness ( unsigned int aBrightness ) {

 u64*           lpPtr = UNCACHED_SEG( &g_IPUCtx.m_DMAGIFBgtn[ 4 ] );

 if ( aBrightness == 128 )
  lpPtr[ 0 ] = g_IPUCtx.m_Alpha = GS_SET_ALPHA( 1, 2, 2, 2, 0x80 );
 else {
  u64           lAlpha;
  if ( aBrightness > 128 ) {
   float lVal = aBrightness - 128;
   lAlpha = GS_SET_ALPHA_2( 1, 2, 2, 0, 0x80 );
   aBrightness = ( unsigned int )( lVal * 0.7F );
  } else {
   aBrightness = 128 - aBrightness;
   lAlpha      = GS_SET_ALPHA_2( 1, 0, 2, 2, 0x80 );
  }  /* end else */
  lpPtr[ 0 ] = g_IPUCtx.m_Alpha  = lAlpha;
  lpPtr[ 5 ] = g_IPUCtx.m_BRGBAQ = GS_SET_RGBAQ( aBrightness, aBrightness, aBrightness, 0x00, 0x00 );
 }  /* end else */

}  /* end IPU_SetBrightness */


IPUContext* IPU_InitContext ( int aWidth, int aHeight, s64*  apAudioPTS, int afWS ) {

 ee_sema_t      lSema;
 unsigned short lCRTMode = GS_Params () -> m_GSCRTMode;

 lSema.init_count = 1;
 s_SyncS = CreateSema ( &lSema );

 s_QIdx = 0;


 g_IPUCtx.Destroy       = IPU_DestroyContext;
 g_IPUCtx.Sync          = IPU_SyncNop;
 g_IPUCtx.Flush         = IPU_Flush;
 g_IPUCtx.SetBrightness = IPU_SetBrightness;
 g_IPUCtx.m_pAudioPTS   = apAudioPTS;
 g_IPUCtx.m_Width       = aWidth;
 g_IPUCtx.m_Height      = aHeight;

 switch ( lCRTMode ) {
  case GSVideoMode_NTSC          :
  case GSVideoMode_PAL           :
  case GSVideoMode_DTV_1920x1080I: g_IPUCtx.m_fPG = 0; break;
  default                        : g_IPUCtx.m_fPG = 1; break;
 }  /* end switch */


 if ( aWidth && aHeight ) {

  unsigned int       lVRAM, lImgSize;
  u64*               lpGIFPack;
  unsigned int       lTBW = ( aWidth + 63 ) >> 6;
  int                lf16 = ( g_Config.m_PlayerFlags & SMS_PF_C16 ) && !( g_Config.m_PlayerFlags & SMS_PF_C32 );
retry:
  if ( lf16 ) {

   g_IPUCtx.m_PixFmt =
   g_IPUCtx.m_TexFmt = GSPixelFormat_PSMCT16;

  } else {

   g_IPUCtx.m_PixFmt = GSPixelFormat_PSMCT32;
   g_IPUCtx.m_TexFmt = GSPixelFormat_PSMCT24;

  }  /* end else */

  lImgSize = (   ( lTBW << 6 ) * (  ( aHeight + 31 ) & ~31  ) * ( 4 >> lf16 )   ) >> 8;
  lVRAM    = 0x4000 - lImgSize;
   
  if ( !lf16 && g_GSCtx.m_VRAMFontPtr && lVRAM < g_GSCtx.m_VRAMPtr ) {
   lf16 = 1;
   goto retry;
  }  /* end if */

  if (  !lf16 && !g_GSCtx.m_VRAMFontPtr && (
          lCRTMode == GSVideoMode_DTV_1920x1080I ||
          lCRTMode == GSVideoMode_DTV_1280x720P
         )
  ) lVRAM = ( g_GSCtx.m_VRAMPtr2 << 5 ) - lImgSize + 352;

  g_IPUCtx.m_ScrRight  = g_GSCtx.m_PWidth  << 4;
  g_IPUCtx.m_ScrBottom = g_GSCtx.m_PHeight << 4;
  g_IPUCtx.m_VRAM      = lVRAM;
  g_IPUCtx.m_TBW       = lTBW;
  g_IPUCtx.m_ModeIdx   = 0;
  g_IPUCtx.m_fWS       = afWS;
  PowerOf2 ( aWidth, aHeight, ( int * )&g_IPUCtx.m_TW, ( int * )&g_IPUCtx.m_TH );


  lpGIFPack = ( u64*               )(  ( unsigned int )&g_IPUCtx.m_DMAGIFPack[ 0 ] | 0x20000000  );
  lpGIFPack[ 2 ] = DMA_TAG(  8, 0, DMATAG_ID_REF,  0, ( unsigned int )g_IPUCtx.m_DMAGIFBgtn, 0  );
  lpGIFPack[ 4 ] = DMA_TAG( 11, 0, DMATAG_ID_REFE, 0, s_DMAGIFDraw,                          0  );

  g_IPUCtx.SetTEX     = IPU_SetTEX;
  g_IPUCtx.Reset      = IPU_Reset;

  g_IPUCtx.Display       = IPU_Display;

  g_IPUCtx.m_DMAGIFBgtn[  0 ] = GIF_TAG( 2, 0, 0, 0, 0, 1 );
  g_IPUCtx.m_DMAGIFBgtn[  1 ] = GIFTAG_REGS_AD;
  g_IPUCtx.m_DMAGIFBgtn[  2 ] = GS_SET_TEXFLUSH( 0 );
  g_IPUCtx.m_DMAGIFBgtn[  3 ] = GS_TEXFLUSH;
  g_IPUCtx.m_DMAGIFBgtn[  4 ] = g_IPUCtx.m_Alpha;
  g_IPUCtx.m_DMAGIFBgtn[  5 ] = GS_ALPHA_2;
  g_IPUCtx.m_DMAGIFBgtn[  6 ] = GIF_TAG( 1, 0, 0, 0, 1, 4 );
  g_IPUCtx.m_DMAGIFBgtn[  7 ] = GS_PRIM | ( GS_RGBAQ << 4 ) | ( GS_XYZ2 << 8 ) | ( GS_XYZ2 << 12 );
  g_IPUCtx.m_DMAGIFBgtn[  8 ] = GS_SET_PRIM( GS_PRIM_PRIM_SPRITE, 0, 0, 0, 1, 0, 0, 1, 0 );
  g_IPUCtx.m_DMAGIFBgtn[  9 ] = g_IPUCtx.m_BRGBAQ;
  g_IPUCtx.m_DMAGIFBgtn[ 10 ] = GS_SET_XYZ( 0, 0, 0 );
  g_IPUCtx.m_DMAGIFBgtn[ 11 ] = GS_SET_XYZ( aWidth << 4, aHeight << 4, 0 );
  g_IPUCtx.m_DMAGIFBgtn[ 12 ] = GIF_TAG( 1, 0, 0, 0, 0, 1 );
  g_IPUCtx.m_DMAGIFBgtn[ 13 ] = GIFTAG_REGS_AD;
  g_IPUCtx.m_DMAGIFBgtn[ 14 ] = GS_SET_ALPHA_2( 0, 1, 0, 1, 0 );
  g_IPUCtx.m_DMAGIFBgtn[ 15 ] = GS_ALPHA_2;
  SyncDCache ( g_IPUCtx.m_DMAGIFBgtn, &g_IPUCtx.m_DMAGIFBgtn[ 16 ] );

  g_IPUCtx.SetTEX ();
  DMA_Wait ( DMAC_GIF );

  IPU_SetBrightness (  ( unsigned int )( g_Config.m_PlayerBrightness * 10.625F + 0.5F )  );
  IPU_Reset ();

 } else return NULL;

 return &g_IPUCtx;

}  /* end IPU_InitContext */
