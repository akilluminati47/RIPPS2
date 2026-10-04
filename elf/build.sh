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
# The Memory Files ELF, compiled in and launched from RAM (patch 0004)
# Built-in textures: glass info panel and PS2 selector mark (patch 0006)
cp -f "$HERE"/theme/gfx/*.png "$SRC/gfx/"

cd "$SRC"
sh .github/scripts/install_coherent_mmce.sh
make clean
# DIRTY= : the tree is RiptOPL plus our patches by design, so the version never says -dirty
# RIPPS2_MAKE_FLAGS: extra make flags, e.g. DEBUG=1 EESIO_DEBUG=1 for a build that logs over EE SIO
make LOCALVERSION=RIPPS2 DIRTY= ${RIPPS2_MAKE_FLAGS:-} release

mkdir -p "$OUT"
ELF="$(ls RIPTOPL-*.ELF | head -n1)"
cp -f "$ELF" "$OUT/RIPPS2.elf"
echo "Built $ELF -> out/RIPPS2.elf"
ls -la "$OUT"
