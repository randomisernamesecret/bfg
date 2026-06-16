#!/bin/bash
# Pull localized App Store screenshots per website locale and write them as
# /assets/<slug>/<weblocale>/NN.webp (720px wide, matching the English shots).
# lang.js swaps to these on localized pages, falling back to English if missing.
# Usage: localize_screenshots.sh <slug> <appId>
set -uo pipefail
SITE="$HOME/Development/Website/bfg-site"
ASC="$HOME/Development/BFG/AppstoreConnect"
slug="$1"; appId="$2"

asc_for() { case "$1" in de) echo de-DE;; es) echo es-ES;; fr) echo fr-FR;; ja) echo ja;; zh-CN) echo zh-Hans;; esac; }

for web in de es fr ja zh-CN; do
  asc=$(asc_for "$web")
  tmp="/tmp/shots-$slug-$web"; rm -rf "$tmp"; mkdir -p "$tmp"
  node "$ASC/download_screenshots.mjs" "$appId" "$tmp" "$asc" >/dev/null 2>&1
  out="$SITE/assets/$slug/$web"; mkdir -p "$out"; n=0
  for img in "$tmp"/*.png; do
    [ -f "$img" ] || continue
    base=$(basename "$img" .png)
    cwebp -quiet -resize 720 0 -q 82 "$img" -o "$out/$base.webp" && n=$((n+1))
  done
  echo "$slug/$web: $n shots"
done
