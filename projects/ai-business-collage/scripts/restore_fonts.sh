#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -f assets/fonts/thmanyahserifdisplay-Regular.woff2 && -f assets/fonts/thmanyahserifdisplay-Bold.woff2 && -f assets/fonts/thmanyahserifdisplay-Black.woff2 ]]; then exit 0; fi
font_source_path="${1:-../../motion-graphics-skills}"
if [[ ! -f "$font_source_path/projects/jedar-lesh-majani/assets/fonts/thmanyahserifdisplay-Bold.woff2" ]]; then
 font_source_path="$(mktemp -d)"; git clone --depth 1 https://github.com/imMamdouhaboammar/motion-graphics-skills "$font_source_path"
fi
mkdir -p assets/fonts
for weight in Bold Regular Black; do cp "$font_source_path/projects/jedar-lesh-majani/assets/fonts/thmanyahserifdisplay-$weight.woff2" assets/fonts/; done
