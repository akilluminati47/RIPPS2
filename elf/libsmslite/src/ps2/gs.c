/*
#     ___  _ _      ___
#    |    | | |    |
# ___|    |   | ___|    PS2DEV Open Source Project.
#----------------------------------------------------------
# (c) 2006-2007 Eugene Plotnikov <e-plotnikov@operamail.com>
# (c) 2007      Petr Otoupal (HDTV support)
# Licenced under Academic Free License version 2.0
# Review ps2sdk README & LICENSE files for further details.
#
*/
#include "core/sms.h"
#include "smslite_config.h"
#include "ps2/gs.h"
#include "ps2/dma.h"
#include "ps2/vif.h"
#include "ps2/intc.h"
#include "core/config.h"

#include <kernel.h>
#include <malloc.h>

extern int g_XShift;

GSContext g_GSCtx = {
 .m_Width    = 640U,
 .m_Height   = 480U,
 .m_PWidth   = 640U,
 .m_OffsetX  =    0,
 .m_OffsetY  =    0,
 .m_BkColor  =    0UL,
 .m_CodePage = GSCodePage_WinLatin1
};

#if SMSLITE_ENABLE_FULLSCREEN
static GSLoadImage  s_CLUTLoadImage __attribute__(  (  aligned( 64 )  )   );
static unsigned int s_CLUT[ 16 ]    __attribute__(  (  aligned( 64 )  )   );
#endif

#if SMSLITE_ENABLE_FULLSCREEN
void GSContext_Init ( GSVideoMode aMode, GSZTest aZTest, GSDoubleBuffer aDblBuf ) {

 unsigned int lSize;
 int          lPixSize;
 int          lColorDepth;
 int          lf16  = g_Config.m_ColorDepth;
 GSParams*    lpPar = GS_Params ();

 lpPar -> m_PARNTSC = g_Config.m_PAR[ 0 ];
 lpPar -> m_PARPAL  = g_Config.m_PAR[ 1 ];

 if ( aMode == GSVideoMode_Default ) aMode = GSVideoMode_NTSC;

 lSize = GS_VMode2Index ( aMode );

 g_GSCtx.m_PWidth     = g_Config.m_DispWH[ lSize ][ 0 ];
 g_GSCtx.m_Width      = g_Config.m_DispWH[ lSize ][ 0 ];
 g_GSCtx.m_PHeight    = g_Config.m_DispWH[ lSize ][ 1 ];
 g_GSCtx.m_Height     = g_Config.m_DispWH[ lSize ][ 1 ];
 g_GSCtx.m_DrawDelay  = g_Config.m_SyncPar[ lSize ][ aDblBuf ];
 g_GSCtx.m_DrawDelay2 = g_Config.m_SyncPar[ lSize ][ 2 ];

 if ( aMode == GSVideoMode_NTSC || aMode == GSVideoMode_PAL )
  g_GSCtx.m_Height = 480;
 else if ( aMode == GSVideoMode_DTV_1920x1080I ) {
  lf16             = aDblBuf;
  g_GSCtx.m_PWidth = g_GSCtx.m_PWidth >> !aDblBuf;
 }  /* end if */

 if ( lf16 ) {
  lColorDepth = GSPixelFormat_PSMCT16;
  lPixSize    = 2;
 } else {
  lColorDepth = GSPixelFormat_PSMCT24;
  lPixSize    = 3;
 }  /* end if */

 g_GSCtx.m_OffsetY -= g_GSCtx.m_OffsetY & 1;

 GS_Reset ( GSInterlaceMode_On, aMode, GSFieldMode_Field );
 GS_InitDC ( &g_GSCtx.m_DispCtx, lColorDepth, g_GSCtx.m_PWidth, g_GSCtx.m_PHeight, g_GSCtx.m_OffsetX, g_GSCtx.m_OffsetY );

 GIF_MODE() = 0;

 lSize = g_GSCtx.m_PWidth;

 while ( 1 ) {
  int lVal = lSize * lPixSize;
  if (  !( lVal & 15 ) && !( lVal % lPixSize )  ) break;
  ++lSize;
 }  /* end while */

 g_GSCtx.m_LWidth  = lSize;
 g_GSCtx.m_PixSize = lPixSize;

 lSize = GS_InitGC ( 0, &g_GSCtx.m_DrawCtx[ 0 ], lColorDepth, g_GSCtx.m_PWidth, g_GSCtx.m_PHeight, aZTest );
         GS_InitGC ( 1, &g_GSCtx.m_DrawCtx[ 1 ], lColorDepth, g_GSCtx.m_PWidth, g_GSCtx.m_PHeight, aZTest );
 GS_InitClear ( &g_GSCtx.m_ClearPkt, 0, 0, g_GSCtx.m_Width << 1, g_GSCtx.m_Height << 1, g_GSCtx.m_BkColor, aZTest );

 SyncDCache (   &g_GSCtx, (  ( unsigned char* )&g_GSCtx  ) + sizeof ( GSContext )   );

 g_GSCtx.m_VRAMPtr = g_GSCtx.m_VRAMPtr2 = g_GSCtx.m_DrawCtx[ 0 ].m_ZBUFVal.ZBP;

 if ( g_GSCtx.m_pDBuf ) {
  free ( g_GSCtx.m_pDBuf );
  g_GSCtx.m_pDBuf = NULL;
 }  /* end if */

 GS_SetDC (  &g_GSCtx.m_DispCtx, ( aMode <= GSVideoMode_PAL ) || ( aMode == GSVideoMode_DTV_1920x1080I )  );
 GS_SetGC ( &g_GSCtx.m_DrawCtx[ 0 ] );
 GS_SetGC ( &g_GSCtx.m_DrawCtx[ 1 ] );
 GS_Clear ( &g_GSCtx.m_ClearPkt     );

 if ( aZTest == GSZTest_On )

  g_GSCtx.m_VRAMPtr += lSize;

 else if ( aDblBuf && !g_GSCtx.m_pDBuf ) {

  g_GSCtx.m_pDBuf = ( unsigned char* )memalign (
   64, lSize = (  ( g_GSCtx.m_LWidth * g_GSCtx.m_PHeight * lPixSize + 63 ) & ~63  )
  );
  InvalidDCache ( g_GSCtx.m_pDBuf, g_GSCtx.m_pDBuf + lSize );

 }  /* end else */

 g_GSCtx.m_VRAMPtr <<= 5;

 GS_InitLoadImage (  UNCACHED_SEG( &s_CLUTLoadImage ), 0, 1, GSPixelFormat_PSMCT32, 0, 0, 8, 2  );


 if ( lColorDepth == GSPixelFormat_PSMCT16 )
  g_GSCtx.m_VRAMFontPtr = g_GSCtx.m_VRAMPtr;
 else g_GSCtx.m_VRAMFontPtr = 0;

 if ( g_GSCtx.m_pDisplayList[ 0 ] ) free ( g_GSCtx.m_pDisplayList[ 0 ] );
 if ( g_GSCtx.m_pDisplayList[ 1 ] ) free ( g_GSCtx.m_pDisplayList[ 1 ] );

 g_GSCtx.m_pDisplayList[ 0 ] = NULL;
 g_GSCtx.m_pDisplayList[ 1 ] = NULL;
 g_GSCtx.m_nAlloc      [ 0 ] = 0;
 g_GSCtx.m_nAlloc      [ 1 ] = 0;
 g_GSCtx.m_PutIndex    [ 0 ] = 0;
 g_GSCtx.m_PutIndex    [ 1 ] = 0;

}  /* end GSContext_Init */
#endif











