#!/usr/bin/env bash
# Builds Arede Grotesk from sources/ into fonts/.
# Requires: pip install -r requirements.txt
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="sources/AredeGrotesk-Regular.ufo"

# Reproducible builds: stamp the fonts with the date of the last commit that changed
# sources/ (falling back to the last commit, e.g. in a shallow clone) instead of the
# current time, so rebuilding unchanged sources gives byte-identical binaries.
if [ -z "${SOURCE_DATE_EPOCH:-}" ] && git rev-parse --git-dir >/dev/null 2>&1; then
  SOURCE_DATE_EPOCH="$(git log -1 --format=%ct -- sources/)"
  [ -n "$SOURCE_DATE_EPOCH" ] || SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
fi
[ -n "${SOURCE_DATE_EPOCH:-}" ] && export SOURCE_DATE_EPOCH

rm -rf fonts/otf fonts/ttf fonts/webfonts
mkdir -p fonts/otf fonts/ttf fonts/webfonts

echo "== OTF"
fontmake -u "$SRC" -o otf --output-dir fonts/otf --filter DecomposeTransformedComponentsFilter
echo "== TTF"
fontmake -u "$SRC" -o ttf --output-dir fonts/ttf --flatten-components --filter DecomposeTransformedComponentsFilter
python3 scripts/postprocess.py fonts/ttf/AredeGrotesk-Regular.ttf fonts/otf/AredeGrotesk-Regular.otf
echo "== WOFF2"
fonttools ttLib.woff2 compress -o fonts/webfonts/AredeGrotesk-Regular.woff2 fonts/ttf/AredeGrotesk-Regular.ttf
echo "== done"
ls -la fonts/otf fonts/ttf fonts/webfonts
