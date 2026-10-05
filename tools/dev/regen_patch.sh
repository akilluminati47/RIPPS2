#!/bin/bash
# Re-export the LAST patch in elf/patches from the RiptOPL clone's current working tree, so fixes made
# after a push fold into that build's patch. Usage: regen_patch.sh   (run from anywhere)
set -e
SP="${TMPDIR:-${TEMP:-/tmp}}"  # where the temporary git index goes
R="/c/Users/Mini PC/Desktop/Webpages - Projects/RiptOPL"
P="/c/Users/Mini PC/Desktop/Webpages - Projects/ps2-pillars/elf/patches"
PATCHES=("$P"/0*.patch)   # glob order is sorted
LAST="${PATCHES[${#PATCHES[@]}-1]}"
cd "$R"
git add -A
export GIT_INDEX_FILE="$SP/idx_regen"
git read-tree 65d4b89
for p in "${PATCHES[@]}"; do
  [ "$p" = "$LAST" ] && break
  git apply --cached --whitespace=nowarn "$p"
done
PREV=$(git write-tree)
unset GIT_INDEX_FILE
git diff-index --cached -p --binary "$PREV" > "$LAST"
# check: the whole series reproduces the index
export GIT_INDEX_FILE="$SP/idx_regen"
git read-tree 65d4b89
for p in "${PATCHES[@]}"; do git apply --cached --whitespace=nowarn "$p"; done
T=$(git write-tree)
unset GIT_INDEX_FILE
if [ -n "$(git diff-index --cached --name-only "$T")" ]; then echo "SERIES MISMATCH"; exit 1; fi
echo "regenerated $(basename "$LAST") ($(wc -l < "$LAST") lines); series reproduces the tree"
