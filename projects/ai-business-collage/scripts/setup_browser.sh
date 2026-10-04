#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .browser
node --input-type=module <<'JS'
import{readFileSync,writeFileSync,chmodSync}from'node:fs';import{brotliDecompressSync}from'node:zlib';import{execFileSync}from'node:child_process';
for(const name of ['chromium','swiftshader.tar','fonts.tar']){const b=brotliDecompressSync(readFileSync(`node_modules/@sparticuz/chromium/bin/${name}.br`));writeFileSync(`.browser/${name}`,b);if(name==='chromium')chmodSync('.browser/chromium',0o755);else execFileSync('tar',['--no-same-owner','-xf',`.browser/${name}`,'-C','.browser']);}
JS
