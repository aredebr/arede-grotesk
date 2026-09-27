#!/usr/bin/env bash
# Builds Arede Grotesk from sources/ into fonts/.
# Requires: pip install -r requirements.txt
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="sources/AredeGrotesk-Regular.ufo"
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
