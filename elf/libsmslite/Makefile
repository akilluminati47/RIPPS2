.SILENT:

include $(PS2SDK)/Defs.make

# ---------------------------------------------------------------------
# libsmslite
#
# Build variants (see include/smslite_config.h):
#
#   make                -> lib/libsmslite.a                (full)
#   make video          -> lib/libsmslite-video.a          (no audio)
#   make preview        -> lib/libsmslite-preview.a        (no fullscreen)
#   make preview-video  -> lib/libsmslite-preview-video.a  (neither)
#   make all-variants   -> all four
#
#   Any variant + "-debug" builds it with -DSMSLITE_DEBUG:
#   make debug, make preview-video-debug, ...
#
#   make test           -> bin/smslite_test.elf (links the full debug lib)
#
# What the switches drop:
#   AUDIO=0       the MP3 decoder (SMS_MP123 + core asm)  ~126 KB off the .a
#   FULLSCREEN=0  the threaded player + GS display path, and the four
#                 64 KB thread stacks                     ~262 KB of BSS
#
# A host that only needs the non-blocking preview (e.g. wOPL, which owns
# its own display) wants preview-video: smallest code AND smallest RAM.
# ---------------------------------------------------------------------

EE_SRC_DIR := src
EE_INC_DIR := include
EE_LIB_DIR := lib
EE_BIN_DIR := bin

SMSLITE_TEST_PATH ?= mass0:/video/test.avi
IRX_SRC_DIR := $(PS2SDK)/iop/irx

EE_INCS += \
	-I$(EE_INC_DIR) \
	-I$(EE_SRC_DIR) \
	-I$(PS2SDK)/ee/include \
	-I$(PS2SDK)/ee/rpc/filexio/include \
	-I$(PS2SDK)/common/include \
	-I$(PS2SDK)/ports/include \
	-I$(PS2SDK)/sbv/include

EE_LDFLAGS += -Wl,--gc-sections

EE_CFLAGS += \
	-Dmemset=mips_memset \
	-Dmemcpy=mips_memcpy \
	-D_EE \
	-DNEWLIB_PORT_AWARE \
	-Dfio_dirent_t=io_dirent_t \
	-std=gnu89 \
	-O2 \
	-G0 \
	-mno-abicalls \
	-fno-pic \
	-ffunction-sections \
	-fdata-sections \
	-Wall \
	-mno-check-zero-division

# RIPPS2: extra flags from the host build (elf/build.sh passes -DSMSLITE_DEBUG for a DEBUG=1 build)
EE_CFLAGS += $(SMSLITE_CFLAGS)

# --- object lists -----------------------------------------------------

CORE_OBJS := \
	smslite.o \
	demux/container.o \
	demux/avi.o \
	codec/codec.o \
	codec/video/mpeg4.o \
	codec/video/mpeg.o \
	codec/video/mpeginit.o \
	codec/video/h263.o \
	codec/video/vlc.o \
	codec/video/dsp.o \
	codec/video/dsp_mmi.o \
	codec/video/dsp_qpel.o \
	ps2/ipu.o \
	ps2/ipu_asm.o \
	ps2/gs.o \
	ps2/gs_asm.o \
	ps2/videobuffer.o \
	ps2/ringbuffer.o \
	ps2/dma.o \
	ps2/ee.o \
	ps2/utils.o \
	ps2/vu0.o

# only when SMSLITE_ENABLE_AUDIO=1
AUDIO_OBJS := codec/audio/mp123.o codec/audio/mp123core.o

# Nothing is fullscreen-exclusive at the OBJECT level: gs.c holds g_GSCtx
# and gs_asm.S holds GS_Params/GS_XYZ/g_XShift, which the IPU colour-space
# path needs in EVERY build (the preview seeds g_GSCtx and calls
# IPU_InitContext). Only GSContext_Init - the display takeover - is
# fullscreen-only, and that is #if'd inside gs.c.
FULLSCREEN_OBJS :=

# --- variant plumbing -------------------------------------------------
# Each variant compiles into its own obj dir so the -D flags never leak.
# $(1)=lib name  $(2)=AUDIO  $(3)=FULLSCREEN  $(4)=extra CFLAGS

define VARIANT

OBJDIR_$(1) := obj/$(1)

OBJS_$(1) := $$(CORE_OBJS)
ifeq ($(2),1)
OBJS_$(1) += $$(AUDIO_OBJS)
endif
ifeq ($(3),1)
OBJS_$(1) += $$(FULLSCREEN_OBJS)
endif

FULL_$(1) := $$(OBJS_$(1):%=$$(OBJDIR_$(1))/%)

CF_$(1) := $$(EE_CFLAGS) -DSMSLITE_ENABLE_AUDIO=$(2) -DSMSLITE_ENABLE_FULLSCREEN=$(3) $(4)

$$(OBJDIR_$(1))/%.o: $$(EE_SRC_DIR)/%.c
	mkdir -p $$(dir $$@)
	echo CC [$(1)] $$<
	$$(EE_CC) $$(CF_$(1)) $$(EE_INCS) -c $$< -o $$@

$$(OBJDIR_$(1))/%.o: $$(EE_SRC_DIR)/%.s
	mkdir -p $$(dir $$@)
	echo AS [$(1)] $$<
	$$(EE_AS) $$(EE_ASFLAGS) $$< -o $$@

$$(OBJDIR_$(1))/%.o: $$(EE_SRC_DIR)/%.S
	mkdir -p $$(dir $$@)
	echo CC [$(1)] $$<
	$$(EE_CC) $$(CF_$(1)) $$(EE_INCS) -c $$< -o $$@

$$(EE_LIB_DIR)/lib$(1).a: $$(FULL_$(1)) | $$(EE_LIB_DIR)
	$$(EE_AR) rcs $$@ $$(FULL_$(1))
	mkdir -p $$(EE_LIB_DIR)/include-$(1)
	sed -e 's|^#define SMSLITE_ENABLE_AUDIO 1|#define SMSLITE_ENABLE_AUDIO $(2)|' \
	    -e 's|^#define SMSLITE_ENABLE_FULLSCREEN 1|#define SMSLITE_ENABLE_FULLSCREEN $(3)|' \
	    $$(EE_INC_DIR)/smslite_config.h > $$(EE_LIB_DIR)/include-$(1)/smslite_config.h
	cp $$(EE_INC_DIR)/smslite.h $$(EE_INC_DIR)/smslite_debug.h $$(EE_LIB_DIR)/include-$(1)/
	echo "Built $$@  (headers: $$(EE_LIB_DIR)/include-$(1)/)"

endef

#                  name                        AUD FS  extra
$(eval $(call VARIANT,smslite,1,1,))
$(eval $(call VARIANT,smslite-video,0,1,))
$(eval $(call VARIANT,smslite-preview,1,0,))
$(eval $(call VARIANT,smslite-preview-video,0,0,))
$(eval $(call VARIANT,smslite-debug,1,1,-DSMSLITE_DEBUG -DSMSLITE_DUMP_PCM))
$(eval $(call VARIANT,smslite-video-debug,0,1,-DSMSLITE_DEBUG))
$(eval $(call VARIANT,smslite-preview-debug,1,0,-DSMSLITE_DEBUG))
$(eval $(call VARIANT,smslite-preview-video-debug,0,0,-DSMSLITE_DEBUG))

# --- targets ----------------------------------------------------------

all:                 $(EE_LIB_DIR)/libsmslite.a
video:               $(EE_LIB_DIR)/libsmslite-video.a
preview:             $(EE_LIB_DIR)/libsmslite-preview.a
preview-video:       $(EE_LIB_DIR)/libsmslite-preview-video.a

debug:               $(EE_LIB_DIR)/libsmslite-debug.a
video-debug:         $(EE_LIB_DIR)/libsmslite-video-debug.a
preview-debug:       $(EE_LIB_DIR)/libsmslite-preview-debug.a
preview-video-debug: $(EE_LIB_DIR)/libsmslite-preview-video-debug.a

all-variants: all video preview preview-video

$(EE_LIB_DIR):
	mkdir -p $@

$(EE_BIN_DIR):
	mkdir -p $@

# --- test harness (links the full debug lib) --------------------------

IRX_EMBED_C := obj/embedded_irx.c
IRX_EMBED_O := obj/embedded_irx.o
EE_TEST_BIN := $(EE_BIN_DIR)/smslite_test.elf

$(IRX_EMBED_C): tools/bin2c.py
	mkdir -p obj
	python3 tools/bin2c.py $@ \
		iomanx_irx=$(IRX_SRC_DIR)/iomanX.irx \
		filexio_irx=$(IRX_SRC_DIR)/fileXio.irx \
		usbd_irx=$(IRX_SRC_DIR)/usbd.irx \
		usbhdfsd_irx=$(IRX_SRC_DIR)/usbhdfsd.irx \
		libsd_irx=$(IRX_SRC_DIR)/libsd.irx \
		audsrv_irx=$(IRX_SRC_DIR)/audsrv.irx

$(IRX_EMBED_O): $(IRX_EMBED_C)
	echo CC $<
	$(EE_CC) $(EE_CFLAGS) -DSMSLITE_DEBUG $(EE_INCS) -c $< -o $@

test: $(EE_LIB_DIR)/libsmslite-debug.a $(IRX_EMBED_O) | $(EE_BIN_DIR)
	echo LINK $(EE_TEST_BIN)
	$(EE_CC) $(EE_CFLAGS) -DSMSLITE_DEBUG $(EE_INCS) \
		-DSMSLITE_TEST_PATH=\"$(SMSLITE_TEST_PATH)\" \
		test/main.c \
		$(IRX_EMBED_O) \
		$(EE_LIB_DIR)/libsmslite-debug.a \
		$(EE_LDFLAGS) \
		-L$(PS2SDK)/ee/lib \
		-o $(EE_TEST_BIN) \
		-laudsrv -lfileXio -ldebug -lpatches -lc -lkernel
	echo "Built $(EE_TEST_BIN)"

clean:
	rm -rf obj $(EE_LIB_DIR) $(EE_BIN_DIR)

rebuild: clean all

.PHONY: all video preview preview-video \
        debug video-debug preview-debug preview-video-debug \
        all-variants test clean rebuild
