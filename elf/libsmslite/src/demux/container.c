/*
#     ___  _ _      ___
#    |    | | |    |
# ___|    |   | ___|    PS2DEV Open Source Project.
#----------------------------------------------------------
# (c) 2005-2007 Eugene Plotnikov <e-plotnikov@operamail.com>
# Licenced under Academic Free License version 2.0
# Review ps2sdk README & LICENSE files for further details.
#
*/
#include "demux/container.h"
#include "demux/avi.h"


static SMS_AVPacket* _AllocPacket ( SMS_RingBuffer* apRB, int aSize ) {

 static SMS_AVPacket s_EmptyPacket;

 SMS_AVPacket* lpPkt = aSize ? SMS_RingBufferAlloc ( apRB, aSize + 64 ) : &s_EmptyPacket;

 if ( lpPkt ) {

  lpPkt -> m_PTS      = SMS_NOPTS_VALUE;
  lpPkt -> m_DTS      = SMS_NOPTS_VALUE;
  lpPkt -> m_StmIdx   = 0;
  lpPkt -> m_Flags    = 0;
  lpPkt -> m_Duration = 0;
  lpPkt -> m_pData    = (  ( unsigned char* )lpPkt  ) + 64;
  lpPkt -> m_Size     = aSize;

 }  /* end if */

 return lpPkt;

}  /* end _AllocPacket */

void SMS_DestroyContainer ( SMS_Container* apCont, int afAll ) {

 uint32_t i;

 for ( i = 0; i < apCont -> m_nStm; ++i ) {

  SMS_Stream* lpStm = apCont -> m_pStm[ i ];

  if ( !lpStm ) continue;

  apCont -> m_pStm[ i ] = NULL;

  if ( lpStm -> Destroy ) lpStm -> Destroy ( lpStm );

  SMS_CodecDestroy ( lpStm -> m_pCodec );

  if ( lpStm -> m_pName   ) free ( lpStm -> m_pName );
  if ( lpStm -> m_pPktBuf ) SMS_RingBufferDestroy ( lpStm -> m_pPktBuf );

  free ( lpStm );

 }  /* end for */

 if ( apCont -> m_pCtx ) {
  free ( apCont -> m_pCtx );
  apCont -> m_pCtx = NULL;
 }  /* end if */


 if ( afAll ) {

  if ( apCont -> m_pFileCtx  ) apCont -> m_pFileCtx -> Destroy ( apCont -> m_pFileCtx );

  free ( apCont );

 }  /* end if */

}  /* end SMS_DestroyContainer */

void SMSContainer_SetPTSInfo ( SMS_Stream* apStm, int aPTSNum, int aPTSDen ) {

 apStm -> m_TimeBase.m_Num = aPTSNum;
 apStm -> m_TimeBase.m_Den = aPTSDen;

}  /* end SMSContainer_SetPTSInfo */

void SMSContainer_CalcPktFields ( SMS_Stream* apStm, SMS_AVPacket* apPkt ) {

 int               lNum, lDen;
 SMS_CodecContext* lpCodecCtx = apStm -> m_pCodec;

 if ( lpCodecCtx -> m_Type == SMS_CodecTypeVideo ) {

  lNum = lpCodecCtx -> m_FrameRateBase;
  lDen = lpCodecCtx -> m_FrameRate;

 } else if ( lpCodecCtx -> m_Type == SMS_CodecTypeAudio ) {

  lNum = lpCodecCtx -> m_FrameSize <= 1 ? ( apPkt -> m_Size * 8 * lpCodecCtx -> m_SampleRate ) / lpCodecCtx -> m_BitRate
                                        : lpCodecCtx -> m_FrameSize;
  lDen = lpCodecCtx -> m_SampleRate;

 } else return;

 if ( lDen && lNum )

  apPkt -> m_Duration = ( int )SMS_Rescale (
   1, lNum * ( int64_t )apStm -> m_TimeBase.m_Den, lDen * ( int64_t )apStm -> m_TimeBase.m_Num
  );

 if ( apPkt -> m_PTS == SMS_NOPTS_VALUE ) {

  if ( apPkt -> m_DTS == SMS_NOPTS_VALUE ) {

   apPkt -> m_PTS = apStm -> m_CurDTS;
   apPkt -> m_DTS = apStm -> m_CurDTS;

  } else {

   apStm -> m_CurDTS = apPkt -> m_DTS;
   apPkt -> m_PTS    = apPkt -> m_DTS;

  }  /* end else */

 } else {

  apStm -> m_CurDTS = apPkt -> m_PTS;
  apPkt -> m_DTS    = apPkt -> m_PTS;

 }  /* end else */

 apStm -> m_CurDTS += apPkt -> m_Duration;

 if ( apPkt -> m_PTS != SMS_NOPTS_VALUE )
  apPkt -> m_PTS = SMS_Rescale (  apPkt -> m_PTS, SMS_TIME_BASE * ( int64_t )apStm -> m_TimeBase.m_Num, apStm -> m_TimeBase.m_Den  );

 if ( apPkt -> m_DTS != SMS_NOPTS_VALUE )
  apPkt -> m_DTS = SMS_Rescale ( apPkt -> m_DTS, SMS_TIME_BASE * ( int64_t )apStm -> m_TimeBase.m_Num, apStm -> m_TimeBase.m_Den );

 apPkt -> m_Duration = ( int )SMS_Rescale (  apPkt -> m_Duration, SMS_TIME_BASE * ( int64_t )apStm -> m_TimeBase.m_Num, apStm -> m_TimeBase.m_Den  );

}  /* end SMSContainer_CalcPktFields */



void SMSContainer_GetWAVHeader ( FileContext* apFileCtx, SMS_CodecContext* apCodecCtx, int aSize ) {

 int lID = File_GetUShort ( apFileCtx );

 apCodecCtx -> m_Type          = SMS_CodecTypeAudio;
 apCodecCtx -> m_Tag           = lID;
 apCodecCtx -> m_Channels      = File_GetUShort ( apFileCtx );
 apCodecCtx -> m_SampleRate    = File_GetUInt ( apFileCtx );
 apCodecCtx -> m_BitRate       = File_GetUInt ( apFileCtx ) * 8;
 apCodecCtx -> m_BlockAlign    = File_GetUShort ( apFileCtx );
 apCodecCtx -> m_BitsPerSample = aSize == 14 ? 8 : File_GetUShort ( apFileCtx );
 apCodecCtx -> m_ID            = SMS_CodecGetID ( SMS_CodecTypeAudio, lID );

 if ( aSize > 16 ) {
  int lLen = File_GetUShort ( apFileCtx );
  if ( lLen > 0 ) {
   if ( lLen > aSize - 18 ) lLen = aSize - 18;
   apCodecCtx -> m_pUserData   = malloc (  ( lLen + 15 ) & ~15  );
   apFileCtx -> Read ( apFileCtx, apCodecCtx -> m_pUserData, lLen );
   apCodecCtx -> m_UserDataLen = lLen;
  }  /* end if */
  if ( aSize - lLen - 18 > 0 ) apFileCtx -> Seek ( apFileCtx, apFileCtx -> m_CurPos + aSize - lLen - 18 );
 }  /* end if */

}  /* end SMSContainer_GetWAVHeader */

static int SMS_INLINE _id3_match ( const uint8_t* apBuf ) {

 return apBuf[ 0 ] == 'I'  && apBuf[ 1 ] == 'D'  && apBuf[ 2 ] == '3' &&
        apBuf[ 3 ] != 0xFF && apBuf[ 4 ] != 0xFF &&
        ( apBuf[ 6 ] & 0x80 ) == 0 && ( apBuf[ 7 ] & 0x80 ) == 0 &&
        ( apBuf[ 8 ] & 0x80 ) == 0 && ( apBuf[ 9 ] & 0x80 ) == 0;

}  /* end _id3_match */

