#!/usr/bin/env bash
# Determinism gate: render the composition twice and compare decoded frame hashes.
# Same time must give the same frame, so any differing frame is a race (loading, clock, randomness).
# The second render runs under CPU load by default: a paint/decode race can stay hidden on an idle machine
# (seen on this project: two idle renders matched, an idle vs loaded pair differed in 111 frames).
# usage (from a HyperFrames project root): bash tools/determinism-check.sh [scratch-dir]   (LOAD=0 to skip the load)
set -euo pipefail
OUT="${1:-$(mktemp -d)}"; mkdir -p "$OUT"
HOGS=()
nproc_count() {
  nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4
}
stop_hogs() { for p in "${HOGS[@]:-}"; do [ -n "$p" ] && kill "$p" 2>/dev/null || true; done; HOGS=(); }
trap stop_hogs EXIT
for run in a b; do
  if [ "$run" = b ] && [ "${LOAD:-1}" = 1 ]; then
    for _ in $(seq "$(nproc_count)"); do python3 -c 'while True: pass' & HOGS+=("$!"); done
  fi
  npx --yes hyperframes@"${HF_VERSION:-0.8.92}" render -f 30 -q delivery -o "$OUT/run-$run.mp4" >"$OUT/run-$run.log" 2>&1 || { echo "render $run failed, see $OUT/run-$run.log"; tail -5 "$OUT/run-$run.log"; exit 2; }
  stop_hogs
  ffmpeg -hide_banner -loglevel error -y -i "$OUT/run-$run.mp4" -map 0:v -f framemd5 "$OUT/run-$run.md5"
done
python3 - "$OUT" <<'PY'
import sys

d = sys.argv[1]


def rd(f):
    with open(f) as fp:
        return [line.split(",")[-1] for line in fp if not line.startswith("#")]


a = rd(d + "/run-a.md5")
b = rd(d + "/run-b.md5")
bad = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
if len(a) != len(b):
    print(f"FAIL: frame counts differ ({len(a)} vs {len(b)})")
    sys.exit(1)
if bad:
    print(f"FAIL: {len(bad)}/{len(a)} frames differ, first {bad[0]}, last {bad[-1]}")
    sys.exit(1)
print(f"PASS: {len(a)}/{len(a)} frames bit-identical across two renders")
PY
