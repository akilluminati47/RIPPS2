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

cd "$SRC"
sh .github/scripts/install_coherent_mmce.sh
make clean
make LOCALVERSION=RIPPS2 release

mkdir -p "$OUT"
ELF="$(ls RIPTOPL-*.ELF | head -n1)"
cp -f "$ELF" "$OUT/RIPPS2.elf"
echo "Built $ELF -> out/RIPPS2.elf"
ls -la "$OUT"
