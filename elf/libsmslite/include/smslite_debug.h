#ifndef SMSLITE_DEBUG_H
#define SMSLITE_DEBUG_H

#ifdef SMSLITE_DEBUG

#include <stdio.h>

#ifdef SMSLITE_FULLDEBUG
#define smsLiteDbg(fmt, args...) \
    printf("(%s:%s:%i): " fmt, __FILE__, __FUNCTION__, __LINE__, ## args)
#else
#define smsLiteDbg(fmt, args...) printf(fmt, ## args)
#endif

#else

#define smsLiteDbg(fmt, args...) do { } while (0)

#endif

#endif
