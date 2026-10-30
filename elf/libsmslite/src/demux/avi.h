/*
#     ___  _ _      ___
#    |    | | |    |
# ___|    |   | ___|    PS2DEV Open Source Project.
#----------------------------------------------------------
# (c) 2005 Eugene Plotnikov <e-plotnikov@operamail.com>
# Licenced under Academic Free License version 2.0
# Review ps2sdk README & LICENSE files for further details.
#
*/
#ifndef __SMS_ContainerAVI_H
#define __SMS_ContainerAVI_H

#ifndef __SMS_Container_H
#include "demux/container.h"
#endif  /* __SMS_Container_H */

#ifdef __cplusplus
extern "C" {
#endif  /* __cplusplus */

int SMS_GetContainerAVI ( SMS_Container* );

uint32_t smsLiteContainerMoviStart ( SMS_Container* );

/* RIPPS2 build 125: a stream's key frame at frame aPos or the nearest one before it (aDir -1) or after it (aDir 1),
   -1 if there is none; and its scale / rate / frame count (0, or -1 when it has no index) */
int smsLiteAviKeyFrame ( SMS_Container*, int, int, int );
int smsLiteAviTiming ( SMS_Container*, int, int32_t*, int32_t*, uint32_t* );

#ifdef __cplusplus
}
#endif  /* __cplusplus */
#endif  /* __SMS_ContainerAVI_H */
