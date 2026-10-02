// patch_brush.mjs (runs on `npm install`): writes node_modules/p5.brush/dist/p5.brush.crayon.js, a copy of p5.brush
// with its stroke "darkening" turned off. p5.brush darkens a stroke's pigment wherever overlapping stamps push the mask
// past 0.7 — right for ink and graphite, wrong for wax crayon, which stays bright: butter-yellow scribbles came out
// mustard. The patch only raises that threshold; everything else in p5.brush is unchanged.
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
const src = 'node_modules/p5.brush/dist/p5.brush.js', dst = 'node_modules/p5.brush/dist/p5.brush.crayon.js';
if (!existsSync(src)) { console.error('patch_brush: ' + src + ' not found (run npm install)'); process.exit(0); }
const s = readFileSync(src, 'utf8'), out = s.replace(/DARKEN_THRESHOLD\s*=\s*0\.7/g, 'DARKEN_THRESHOLD=9.0');
if (out === s) console.warn('patch_brush: DARKEN_THRESHOLD not found — p5.brush changed; crayon colours may darken');
writeFileSync(dst, out);
console.log('patch_brush: wrote ' + dst);
