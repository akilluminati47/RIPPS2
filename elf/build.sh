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

# Build 103: the RiptOPL upstream RIPPS2 has merged (elf/RIPTOPL_UPSTREAM: its commit, then its revision, the
# commit count + 2 RiptOPL's Makefile numbers a build by). The pin stays 65d4b89 and upstream arrives as patches,
# so this is what the version names. Vendored sources upstream carries whole come straight from that commit,
# untouched, instead of through a patch: mbedTLS (the RA edition's HTTPS game-ID lookup, Apache-2.0).
read -r UP_COMMIT UP_REV < "$HERE/RIPTOPL_UPSTREAM"
git -C "$SRC" fetch -q --depth 1 origin "$UP_COMMIT"
git -C "$SRC" checkout -q FETCH_HEAD -- third_party/mbedtls
UP_HASH="$(printf '%s' "$UP_COMMIT" | cut -c1-7)"
echo "RiptOPL upstream merged: $UP_HASH (revision $UP_REV)"

# build 76: --prepare-only stops here, with RiptOPL and every patch applied, for the host tests
# (.github/workflows/build-elf.yml runs them on a plain Ubuntu runner, which has no ps2dev toolchain)
if [ "${1:-}" = "--prepare-only" ]; then
  echo "Prepared $SRC (patches applied)"
  exit 0
fi

# Embedded RIPPS2 assets: our layout becomes the built-in theme, and the menu font
# is compiled in (patch 0001 loads it as builtin:ripps2)
cp -f "$HERE/theme/conf_theme.cfg" "$SRC/misc/conf_theme_OPL.cfg"
cp -f "$ROOT/assets/master.ttf" "$SRC/misc/ripps2_font.ttf"
cp -f "$HERE/theme/fonts/ripps2_sleek.ttf" "$SRC/misc/ripps2_sleek.ttf"
cp -f "$HERE/theme/fonts/ripps2_sleek_bold.ttf" "$SRC/misc/ripps2_sleekbold.ttf"
cp -f "$HERE/theme/fonts/ripps2_sleek_case.ttf" "$SRC/misc/ripps2_sleekcase.ttf"
cp -f "$HERE/theme/fonts/ripps2_one.ttf" "$SRC/misc/ripps2_one.ttf"
# RIPFLOW's and Settings' font (build 114): Roboto Condensed 3.015, variable (weights 400 to 700), cut to Latin-1,
# SIL OFL 1.1 (theme/fonts/ROBOTO-OFL.txt); made by theme/tools/make_roboto.py
cp -f "$HERE/theme/fonts/ripps2_roboto.ttf" "$SRC/misc/ripps2roboto.ttf"
# build 115: Planet N Condensed by Iconian Fonts, Adapt's list face, built in (builtin:ripps2condensed) so the theme carries
# no font file
cp -f "$HERE/theme/fonts/ripps2_condensed.ttf" "$SRC/misc/ripps2_condensed.ttf"
# build 114: the compiled-in fonts without what FreeType never reads (glyph names, extra name records, signatures,
# substitution tables); outlines, hinting and kerning stay, and a font whose outlines would change is left whole
python3 -c "import fontTools" 2>/dev/null || pip3 install --quiet --break-system-packages fonttools || true
python3 "$HERE/theme/tools/strip_fonts.py" "$SRC"/misc/ripps2_font.ttf "$SRC"/misc/ripps2_sleek*.ttf "$SRC"/misc/ripps2_one.ttf "$SRC"/misc/ripps2roboto.ttf "$SRC"/misc/ripps2_condensed.ttf || true
# The Memory Files ELF, compiled in and launched from RAM (patch 0004)
# Built-in textures: glass info panel and PS2 selector mark (patch 0006)
cp -f "$HERE"/theme/gfx/*.png "$SRC/gfx/"
# BIBLE (patch 0069; build 134: BIBLE f31c8d5, built on El Isra's PS2BBL, signed for RIPPS2), carried as data (GPL-3; see
# elf/bible/README.md for its licence and source)
cp -f "$HERE/bible/SYSTEM.XLF" "$SRC/misc/bible_system.xlf"
cp -f "$HERE/bible/MX4SIO/SYSTEM.XLF" "$SRC/misc/bible_mx4sio_system.xlf"
# build 136: BIBLE's MMCE build (reads mmce0:/mmce1:), signed with the others on 11/03
cp -f "$HERE/bible/MMCE/SYSTEM.XLF" "$SRC/misc/bible_mmce_system.xlf"
# build 138: KELFBinder's IOPRP image (GPL-3, elf/kelfbinder/README.md), which BIBLE's bind boots as it is
cp -f "$HERE/kelfbinder/IOPRP.img" "$SRC/misc/bind_ioprp.img"
# BIBLE on the HDD (build 73): its HDD build, HSYSTEM.XLF (build 134: BIBLE's, signed with the card builds)
cp -f "$HERE/bible/HSYSTEM.XLF" "$SRC/misc/bible_hdd_system.xlf"
# Ember and POPSTARTER are the user's own from build 113, found and launched, not carried (elf/ember, elf/popstarter)
# build 135: Neutrino is no longer carried (elf/neutrino/README.md); RIPPS2 finds the user's own
# The build number shown in About: the number of the last patch (build N is patch N); beta from build 100
LAST="$(ls "$HERE"/patches/0*.patch | tail -n1)"
NUM="$(basename "$LAST" | cut -c1-4 | sed 's/^0*//')"
# Build 103: and the version, the build number's digits (102: v1.0.2-beta, 110: v1.1.0-beta)
STAGE="${RIPPS2_STAGE:-BETA}"
VER="v$((NUM / 100)).$(((NUM / 10) % 10)).$((NUM % 10))-$(printf '%s' "$STAGE" | tr 'A-Z' 'a-z')"
printf '#define RIPPS2_BUILD %s\n#define RIPPS2_STAGE "%s"\n#define RIPPS2_VERSION "%s"\n' "$NUM" "$STAGE" "$VER" > "$SRC/include/ripps2_build.h"
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

# RIPPS2 build 93: libsmslite (AVI video in Memory Files), RIPPS2's fork in elf/libsmslite, built as its own
# library: its core is AFL 2.0, its MPEG-4 and MP3 decoders LGPL 2.1 (elf/libsmslite/FORK.md)
rm -rf "$SRC/thirdparty/libsmslite"
mkdir -p "$SRC/thirdparty"
cp -r "$HERE/libsmslite" "$SRC/thirdparty/libsmslite"
# a DEBUG=1 build (RIPPS2_MAKE_FLAGS) gets the player's own log lines too
case "${RIPPS2_MAKE_FLAGS:-}" in *DEBUG=1*) SMS_CF=-DSMSLITE_DEBUG ;; *) SMS_CF= ;; esac
make -C "$SRC/thirdparty/libsmslite" all SMSLITE_CFLAGS="$SMS_CF"
case "${RIPPS2_MAKE_FLAGS:-}" in
  *RIPPS2_NO_SMSLITE=1*) # build 95: a test build without the player, to tell its link apart from everything else
    rm -f "$SRC/lib/libsmslite.a"
    echo "libsmslite: left out (RIPPS2_NO_SMSLITE=1)" ;;
  *)
    cp -f "$SRC/thirdparty/libsmslite/lib/libsmslite.a" "$SRC/lib/libsmslite.a"
    echo "libsmslite: $(du -k "$SRC/lib/libsmslite.a" | cut -f1) KB" ;;
esac
# build 95: symbols libsmslite defines that a library linked after it defines too. It comes first in EE_LIBS,
# so RIPPS2's own calls would take its version of any of these: the list must stay empty.
SMS_NM=$(command -v mips64r5900el-ps2-elf-nm || true)
if [ -n "$SMS_NM" ]; then
  "$SMS_NM" -g --defined-only "$SRC/thirdparty/libsmslite/lib/libsmslite.a" 2>/dev/null | awk 'NF==3 && $2 ~ /[TDBRW]/ {print $3}' | sort -u > "$SRC/sms_syms.txt"
  : > "$SRC/other_syms.txt"
  for L in "$PS2SDK"/ee/lib/*.a "$PS2SDK"/ports/lib/*.a "$GSKIT"/lib/*.a "$PS2DEV"/ee/mips64r5900el-ps2-elf/lib/libc.a "$PS2DEV"/ee/mips64r5900el-ps2-elf/lib/libm.a; do
    [ -f "$L" ] && "$SMS_NM" -g --defined-only "$L" 2>/dev/null | awk 'NF==3 && $2 ~ /[TDBRW]/ {print $3}' >> "$SRC/other_syms.txt"
  done
  sort -u "$SRC/other_syms.txt" -o "$SRC/other_syms.txt"
  echo "libsmslite symbols that shadow a later library: $(comm -12 "$SRC/sms_syms.txt" "$SRC/other_syms.txt" | wc -l)"
  comm -12 "$SRC/sms_syms.txt" "$SRC/other_syms.txt" | head -60 | sed 's/^/  shadows: /'
  if [ -n "$(comm -12 "$SRC/sms_syms.txt" "$SRC/other_syms.txt")" ]; then
    echo "::error::libsmslite defines symbols a later library defines (see above): RIPPS2 would call its versions"
    exit 1
  fi
fi

cd "$SRC"
sh .github/scripts/install_coherent_mmce.sh
# build 114: RiptOPL's own releases rebuild the SDK's exFAT/FAT driver with its fragment walker guard (#986: a corrupt
# chain fails the launch instead of handing the game's driver wrong sectors to write a VMC to) and the contiguous VMC
# reserve genvmc asks for. RIPPS2 shipped the stock driver until now (FifthFox's corrupted drives, 10/22)
python3 .github/scripts/install_safe_bdmfs.py
make clean
# DIRTY= : the tree is RiptOPL plus our patches by design, so the version never says -dirty
# RIPPS2_MAKE_FLAGS: extra make flags, e.g. DEBUG=1 EESIO_DEBUG=1 for a build that logs over EE SIO
# RETROACHIEVEMENTS=1 (build 70, SpiritofRA): RiptOPL's RetroAchievements flavour, the shipping loader
# plus achievements; telemetry stays off until the user turns it on (Achievements in the main menu)
# Build 103: REVISION and GIT_HASH name the upstream merged (RIPTOPL_UPSTREAM), not the one-commit clone of the pin
# (which made every RIPPS2 say v1.2.0-Beta-3-65d4b89)
make LOCALVERSION=RIPPS2 DIRTY= REVISION="$UP_REV" GIT_HASH="$UP_HASH" RETROACHIEVEMENTS=1 ${RIPPS2_MAKE_FLAGS:-} release || {
  # build 87: an ee_core over its stack floor still leaves its map: say by how much
  [ -f ee_core/ee_core.map ] && grep -E '(_end_bss|_stack_size|_stack) = ' ee_core/ee_core.map | sed 's/^ */ee_core: /'
  # build 103: and what each object takes (text, data, bss), to see where the room went
  for o in ee_core/obj/*.o; do mips64r5900el-ps2-elf-size "$o" 2>/dev/null | tail -n1 | sed 's/^/ee_core size: /'; done
  exit 1
}

# build 87: ee_core's room. Its stack is what ram84 leaves above .bss (ee_core/linkfile refuses under 3 KB);
# the log shows how much a change to the in-game code took
# (ee_core links stripped, so the numbers come from its map: _end_bss, and _stack_size up to 0x97000)
if [ -f ee_core/ee_core.map ]; then
  grep -E '(_end_bss|_stack_size|_stack) = ' ee_core/ee_core.map | sed 's/^ */ee_core: /' || true
fi

mkdir -p "$OUT"
ELF="$(ls RIPTOPL-*.ELF | head -n1)"
cp -f "$ELF" "$OUT/RIPPS2.elf"
echo "Built $ELF -> out/RIPPS2.elf"

# build 104: the language pack. `make release` made lng_src/ (Open PS2 Loader's translations with RiptOPL's lng_fork
# filled in); RIPPS2's own words come from elf/lang. Keyed by the English, so a pack keeps working in later builds.
python3 "$HERE/lang/ripps2lang.py" extract "$SRC" --check || echo "::warning::elf/lang/_strings.yml is out of date"
# fontTools cuts the big CJK font down to the letters a language uses (without it the pack carries it whole)
python3 -c "import fontTools" 2>/dev/null || pip3 install --quiet --break-system-packages fonttools || true
python3 "$HERE/lang/ripps2lang.py" pack "$SRC" "$OUT"

ls -la "$OUT"
