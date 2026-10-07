#include "core/sms.h"
#include "ps2/ee.h"

#include <kernel.h>
#include <limits.h>
#include <malloc.h>

#define MUL64( a, b ) (  ( u64 )( u32 )( a ) * ( u64 )( u32 )( b )  )

unsigned char* g_pSPRTop;
void*          g_pSynthBuffer;

__asm__(
 ".set noreorder\n\t"
 ".set nomacro\n\t"
 ".set noat\n\t"
 ".globl SMS_EEDIntr\n\t"
 ".text\n\t"
 "SMS_EEDIntr:\n\t"
 "_di:\n\t"
 "mfc0  $v1, $12\n\t"
 "lui   $at, 0x0001\n\t"
 "and   $v1, $v1, $at\n\t"
 "beql  $v1, $zero, 1f\n\t"
 "xor   $v0, $v0, $v0\n\t"
 "2:\n\t"
 "di\n\t"
 "sync.p\n\t"
 "mfc0  $v1, $12\n\t"
 "and   $v1, $v1, $at\n\t"
 "bne   $v1, $zero, 2b\n\t"
 "nor   $v0, $zero, $zero\n\t"
 "1:\n\t"
 "jr    $ra\n\t"
 "nop\n\t"
);

void* SMS_Realloc ( void* apData, unsigned int* apSize, unsigned int aMinSize ) {

 if ( aMinSize < *apSize ) return apData;

 *apSize = 17 * aMinSize / 16 + 32;

 return realloc ( apData, *apSize );

}  /* SMS_Realloc */

s64  SMS_Rescale ( s64  anA, s64  aB, s64  aC ){

 int           i;
 u64           lA0, lA1, lB0, lB1, lT1, lT1a;
 s64           lR;

 if ( anA < 0 ) return -SMS_Rescale ( -anA, aB, aC );

 lR = aC >> 1;

 if ( aB <= INT_MAX && aC <= INT_MAX ) {
  if ( anA <= INT_MAX )
   return ( anA * aB + lR ) / aC;
  else return anA / aC * aB + ( anA % aC * aB + lR ) / aC;
 }  /* end if */

 lA0  = anA & 0xFFFFFFFF;
 lA1  = anA >> 32;
 lB0  = aB  & 0xFFFFFFFF;
 lB1  = aB  >> 32;
 lT1  = MUL64 ( lA0, lB1 ) + MUL64 ( lA1, lB0 );
 lT1a = lT1 << 32;
 lA0  = MUL64 ( lA0, lB0 ) + lT1a;
 lA1  = MUL64 ( lA1, lB1 ) + ( lT1 >> 32 ) + ( lA0 < lT1a );
 lA0 += lR;
 lA1 += lA0 < lR;

 for ( i = 63; i >= 0; --i ) {

  lA1 += lA1 + (  ( lA0 >> i ) & 1  );
  lT1 += lT1;

  if ( aC <= lA1 ){
   lA1 -= aC;
   ++lT1;
  }  /* end if */

 }  /* end for */

 return lT1;

}  /* end SMS_Rescale */
