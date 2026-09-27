#!/usr/bin/env bash
# Prints the release notes for a version: its section of CHANGELOG.md followed by the
# fixed footer in .github/release-notes.md. Fails if CHANGELOG.md has no section for it.
# Usage: ./scripts/release_notes.sh 1.1.0
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION="${1:?usage: $0 <version>}"
VERSION="${VERSION#v}"

SECTION="$(awk -v v="$VERSION" '
  found && /^## / { exit }
  found {
    if ($0 ~ /^[[:space:]]*$/) { if (started) blank++ ; next }
    while (blank > 0) { print ""; blank-- }
    print; started = 1
  }
  $0 == "## " v || index($0, "## " v " ") == 1 { found = 1 }
' CHANGELOG.md)"

if [ -z "$SECTION" ]; then
  echo "error: CHANGELOG.md has no section for $VERSION (expected a heading like \"## $VERSION — YYYY-MM-DD\")" >&2
  exit 1
fi

printf '%s\n\n---\n\n' "$SECTION"
cat .github/release-notes.md
