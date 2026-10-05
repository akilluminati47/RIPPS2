#!/bin/sh
# Builds RIPPS2.elf: RiptOPL at the pinned commit + our patches + embedded assets.
# Runs inside the ps2dev container (see .github/workflows/build-elf.yml).
set -eu

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
REF="$(tr -d ' \r\n' < "$HERE/RIPTOPL_REF")"
SRC="$ROOT/riptopl"
OUT="$ROOT/out"

echo "RiptOPL ref: $REF"
rm -rf "$SRC"
git init -q "$SRC"
git -C "$SRC" remote add origin https://github.com/NathanNeurotic/Open-PS2-Loader.git
git -C "$SRC" fetch -q --depth 1 origin "$REF"
git -C "$SRC" checkout -q FETCH_HEAD
git config --global --add safe.directory "$SRC"

# Our changes, applied in name order
for p in "$HERE"/patches/*.patch; do
  [ -e "$p" ] || continue
  echo "Applying $(basename "$p")"
  git -C "$SRC" apply --whitespace=nowarn "$p"
done

# Embedded RIPPS2 assets: our layout becomes the built-in theme, and the menu font
# is compiled in (patch 0001 loads it as builtin:ripps2)
cp -f "$HERE/theme/conf_theme.cfg" "$SRC/misc/conf_theme_OPL.cfg"
cp -f "$ROOT/assets/master.ttf" "$SRC/misc/ripps2_font.ttf"
cp -f "$HERE/theme/fonts/ripps2_sleek.ttf" "$SRC/misc/ripps2_sleek.ttf"
cp -f "$HERE/theme/fonts/ripps2_sleek_bold.ttf" "$SRC/misc/ripps2_sleekbold.ttf"
cp -f "$HERE/theme/fonts/ripps2_sleek_case.ttf" "$SRC/misc/ripps2_sleekcase.ttf"
cp -f "$HERE/theme/fonts/ripps2_one.ttf" "$SRC/misc/ripps2_one.ttf"
# Ember (build 71): Gageformer's PS1 emulator, carried unmodified (gzip here, inflated byte for byte
# when RIPPS2 installs it) with its licence (elf/ember/LICENSE-BETA.txt)
gzip -9 -n -c "$HERE/ember/ember.elf" > "$SRC/misc/ember_elf.gz"
cp -f "$HERE/ember/LICENSE-BETA.txt" "$SRC/misc/ember_licence.txt"
# RIPFLOW's fonts (build 70): Roboto Condensed and Bold Condensed, Apache-2.0 (theme/fonts/ROBOTO-LICENSE.txt)
cp -f "$HERE/theme/fonts/ripflow.ttf" "$SRC/misc/ripflow.ttf"
cp -f "$HERE/theme/fonts/ripflow_bold.ttf" "$SRC/misc/ripflowbold.ttf"
# The Memory Files ELF, compiled in and launched from RAM (patch 0004)
# Built-in textures: glass info panel and PS2 selector mark (patch 0006)
cp -f "$HERE"/theme/gfx/*.png "$SRC/gfx/"
# BIBLE (patch 0069): PS2BBL 1.2.0 by El Isra, signed and unchanged, carried as data (GPL-3; see
# elf/bible/README.md for its licence and source)
cp -f "$HERE/bible/SYSTEM.XLF" "$SRC/misc/bible_system.xlf"
cp -f "$HERE/bible/MX4SIO/SYSTEM.XLF" "$SRC/misc/bible_mx4sio_system.xlf"
# BIBLE on the HDD (build 73): PS2BBL 1.2.0's HDD build, HSYSTEM.XLF from the same release, unchanged
cp -f "$HERE/bible/HSYSTEM.XLF" "$SRC/misc/bible_hdd_system.xlf"
# POPSTARTER (build 73): krHACKen's PS1 launcher, carried as released (elf/popstarter/README.md); RIPPS2
# writes it to a drive's POPS folder only when the user has no POPSTARTER of their own
cp -f "$HERE/popstarter/POPSTARTER.ELF" "$SRC/misc/popstarter_elf.bin"
# The build number shown in About: the number of the last patch (build N is patch N)
LAST="$(ls "$HERE"/patches/0*.patch | tail -n1)"
NUM="$(basename "$LAST" | cut -c1-4 | sed 's/^0*//')"
printf '#define RIPPS2_BUILD %s\n#define RIPPS2_STAGE "%s"\n' "$NUM" "${RIPPS2_STAGE:-ALPHA}" > "$SRC/include/ripps2_build.h"
# A private sound pack baked into this build only (never set by the public workflow: RIPPS2 carries
# no one else's sounds). A folder of <event>.adp files, from elf/theme/tools/make_sound_pack.py.
if [ -n "${RIPPS2_SOUND_PACK:-}" ]; then
  python3 "$HERE/theme/tools/bake_sound_pack.py" "$RIPPS2_SOUND_PACK" "$SRC/src/ripps2sfxpack.c"
fi

# BearSSL 0.6 (build 73: the cover art download's HTTPS), Thomas Pornin, MIT (elf/bearssl), as
# lib/libbearssl.a. Its 32-bit code paths: the R5900 has no 64-bit multiply.
tar xzf "$HERE/bearssl/bearssl-0.6.tar.gz" -C "$SRC"
mkdir -p "$SRC/lib" "$SRC/bearssl-obj"
BR_CC="${PS2DEV:-/usr/local/ps2dev}/ee/bin/mips64r5900el-ps2-elf-gcc"
BR_AR="${PS2DEV:-/usr/local/ps2dev}/ee/bin/mips64r5900el-ps2-elf-ar"
find "$SRC/bearssl-0.6/src" -name '*.c' | while read -r f; do
  o="$SRC/bearssl-obj/$(echo "${f#$SRC/bearssl-0.6/src/}" | tr '/' '_' | sed 's/\.c$/.o/')"
  "$BR_CC" -O2 -G0 -D_EE -I"$SRC/bearssl-0.6/inc" -I"$SRC/bearssl-0.6/src" \
    -DBR_64=0 -DBR_INT128=0 -DBR_UMUL128=0 -DBR_USE_URANDOM=0 -DBR_USE_GETENTROPY=0 -DBR_USE_UNIX_TIME=0 \
    -DBR_USE_WIN32_RAND=0 -DBR_USE_WIN32_TIME=0 -DBR_RDRAND=0 -c "$f" -o "$o"
done
"$BR_AR" rcs "$SRC/lib/libbearssl.a" "$SRC"/bearssl-obj/*.o
echo "BearSSL: $(ls "$SRC"/bearssl-obj/*.o | wc -l) objects"

cd "$SRC"
sh .github/scripts/install_coherent_mmce.sh
make clean
# DIRTY= : the tree is RiptOPL plus our patches by design, so the version never says -dirty
# RIPPS2_MAKE_FLAGS: extra make flags, e.g. DEBUG=1 EESIO_DEBUG=1 for a build that logs over EE SIO
# RETROACHIEVEMENTS=1 (build 70, SpiritofRA): RiptOPL's RetroAchievements flavour, the shipping loader
# plus achievements; telemetry stays off until the user turns it on (Achievements in the main menu)
make LOCALVERSION=RIPPS2 DIRTY= RETROACHIEVEMENTS=1 ${RIPPS2_MAKE_FLAGS:-} release

mkdir -p "$OUT"
ELF="$(ls RIPTOPL-*.ELF | head -n1)"
cp -f "$ELF" "$OUT/RIPPS2.elf"
echo "Built $ELF -> out/RIPPS2.elf"
ls -la "$OUT"
