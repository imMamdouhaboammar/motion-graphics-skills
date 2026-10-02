// core.js: the runtime. Constants, timing and motion helpers, camera, paint wrapper, compositing and the render hooks.
// Derived from painted-animation's core.js (ClaudeAnimationBase, MIT © John Heibel; see LICENSE). The render contract
// (window.ready / renderAt / renderSheet) is unchanged, so the same render.mjs drives it. The LOOK (brushes, paper,
// tooth, fills, finishing) lives in crayon.js; the characters in cast.js.
// Length and rhythm come from PROJECT in config.js.
const W = 1920, H = 1080;
const BPM = PROJECT.bpm, BEAT = 60 / BPM, OFF = PROJECT.offset || 0, DUR = PROJECT.duration;
// Linework boils at BOIL drawings a second. 8 reads as "re-drawn by hand": slow, calm, storybook.
const BOIL = PROJECT.boil || 8;
const TAU = Math.PI * 2;
// The storybook palette: soft crayon colours on cream paper. No pure black or white: PAL.ink is a cocoa pencil,
// PAL.cream the lightest light. Dk/Lt variants are for shading scribbles and highlights.
const PAL = {
  paper: '#F7EFDD', cream: '#FFF9EC', ink: '#4A3631', inkSoft: '#7A5C52',
  butter: '#F7D774', butterDk: '#E8B64A', sky: '#9ECBEA', skyDk: '#6FA6D6', skyLt: '#CFE6F5',
  rose: '#F09AAB', roseDk: '#D9687F', sage: '#AECB98', sageDk: '#7FA56E', leaf: '#8DBB78',
  lilac: '#C3AEE0', lilacDk: '#9A82C4', peach: '#F9CFA8', peachDk: '#EBA57E', coral: '#EE8A6E',
  cocoa: '#8C5E48', bark: '#A77657', night: '#5C6BA8', dusk: '#8E86C7',
  // aliases kept so older helpers (karaoke.js, brushWipe) still work
  clay: '#EE8A6E', clayDk: '#C8694F', clayLt: '#F6B59C', ochre: '#EDB84F', sap: '#8DBB78', teal: '#7FB9B1',
  violet: '#9A82C4', indigo: '#5C6BA8'
};

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, x) => a + (b - a) * x;
const ease = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const backOut = x => { x = clamp(x); const s = 1.9; return 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2); };
const hash = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
// seeded stream for one element, the same every frame: const r = rnd('tree' + i); r() → 0..1
function rnd(key) { let h = 2166136261; for (const c of String(key)) h = Math.imul(h ^ c.charCodeAt(0), 16777619); let s = h >>> 0 || 1; return () => (s = Math.imul(s ^ (s >>> 15), 2246822519) >>> 0, s = (s ^ (s >>> 13)) >>> 0, (s % 1000003) / 1000003); }
const bpOf = t => (t - OFF) / BEAT;
// Seeded by the boil frame, so linework "boils" at BOIL fps like hand-drawn animation.
const jit = a => (random() * 2 - 1) * a;
// Each boil drawing holds for several frames, so whatever isn't moving must draw the same until the next one. But a moving
// thing uses a different amount of randomness each frame, which shifts the stream for everything drawn after it and makes
// that re-boil every frame (jitter). boilSeed(key) restarts the stream from the boil frame and a key (any string or
// number) that's the same every frame: call it before each separate element. The cast does this for itself and its parts.
let BOILN = 0, CAST_N = 0;
const boilSeed = key => { let h = 2166136261; for (const c of key + '|' + BOILN) h = Math.imul(h ^ c.charCodeAt(0), 16777619); randomSeed(h >>> 0); };

// ---------- timing helpers (everything is a pure function of t; no state survives between frames) ----------
const seg = (t, a, b) => clamp((t - a) / (b - a));                 // 0..1 progress of t through [a, b]
const frac = x => x - Math.floor(x);
const beatN = t => Math.floor(bpOf(t));                            // integer beat index
const pulse = (t, k = 6) => Math.exp(-frac(bpOf(t)) * k);          // 1 exactly on each beat, decays after
const pulse2 = (t, k = 6) => Math.exp(-frac(bpOf(t) * 2) * k);     // same on eighth notes
const wob = (t, f = 1, ph = 0) => Math.sin((t * f + ph) * TAU);
const easeIn = x => Math.pow(clamp(x), 3);
const elasticOut = x => { x = clamp(x); return x === 0 || x === 1 ? x : Math.pow(2, -10 * x) * Math.sin((x * 10 - .75) * (TAU / 3)) + 1; };
// keyframes: kf(t, [[t0, v0], [t1, v1], ...], easeFn). Values may be numbers or arrays of numbers.
function kf(t, keys, e = ease) {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    if (t < keys[i][0]) {
      const [a, va] = keys[i - 1], [b, vb] = keys[i], k = e((t - a) / (b - a));
      return Array.isArray(va) ? va.map((v, j) => lerp(v, vb[j], k)) : lerp(va, vb, k);
    }
  }
  return keys[keys.length - 1][1];
}
// hex color mix
function mixCol(a, b, k) {
  const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16), c = i => Math.round(lerp((pa >> i) & 255, (pb >> i) & 255, clamp(k)));
  return '#' + ((1 << 24) + (c(16) << 16) + (c(8) << 8) + c(0)).toString(16).slice(1);
}
// small deterministic camera shake, changes at 24 fps
const shakeXY = (t, amt) => { const f = Math.floor(t * 24); return [(hash(f * 1.7) - .5) * 2 * amt, (hash(f * 2.3 + 9) - .5) * 2 * amt]; };

// ---------- motion principles, as pure functions of t ----------
// Damped spring kicked at t0: 0 before, then a wobble that dies away (settles, jiggles, hair after a landing).
const spring = (t, t0, k = 6, w = 18) => t < t0 ? 0 : Math.exp(-k * (t - t0)) * Math.sin(w * (t - t0));
const ring = (t, evs, k = 6, w = 18) => evs.reduce((s, e) => s + spring(t, e, k, w), 0);    // one kick per event time
// Hold each drawing for two frames (12 drawings a second), like hand-drawn animation "on twos". Wrap a shot's t in it.
const onTwos = t => Math.floor(t * 12 + 1e-6) / 12;
const onStep = (t, n) => Math.floor(t * n + 1e-6) / n;
// Point on a thrown or jumping arc from p0 to p1, peaking h px above the straight line; k = 0..1 along the flight.
const arcPt = (p0, p1, h, k) => [lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k) - h * 4 * k * (1 - k)];
// A hop that takes off at t0 and lands at t1, h body units high: crouch (anticipation), stretch on takeoff,
// round at the top, squash on landing and spring back. Returns { dy, sq } to add into a character's pose.
function jump(t, t0, t1, h = 3) {
  if (t < t0 - .16) return { dy: 0, sq: 0 };
  if (t < t0) return { dy: 0, sq: .2 * ease(seg(t, t0 - .16, t0)) };
  if (t < t1) { const k = (t - t0) / (t1 - t0); return { dy: -h * 4 * k * (1 - k), sq: -.16 * Math.abs(1 - 2 * k) }; }
  const a = t - t1; return { dy: 0, sq: .24 * Math.exp(-8 * a) * Math.cos(20 * a) };
}
// A surprise "take" peaking at t0: a quick squash, then a big stretch up that springs back. amt scales it.
function take(t, t0, amt = 1) {
  if (t < t0 - .1) return { sq: 0, dy: 0 };
  if (t < t0) return { sq: .12 * amt * ease(seg(t, t0 - .1, t0)), dy: 0 };
  const a = t - t0; return { sq: -.26 * amt * Math.exp(-6 * a) * Math.cos(16 * a), dy: -1.2 * amt * Math.exp(-7 * a) * Math.max(0, Math.cos(9 * a)) };
}
// Walk from x0 to x1 (px) between t0 and t1 for a character of unit u, taking steps of `stride` u: eases in and out,
// faces the way it's going, and faces front when it stops. Returns { x, walk, view, flip, dy } for the cast.
function stroll(t, t0, t1, x0, x1, u, stride = 3, view = 'side') {
  const x = lerp(x0, x1, ease(seg(t, t0, t1))), d = Math.abs(x - x0) / (stride * u), moving = t > t0 && t < t1;
  return { x, walk: moving ? d : null, view: moving ? view : 'front', flip: x1 < x0, dy: moving ? -Math.abs(Math.sin(d * Math.PI)) * .35 : 0 };
}

// ---------- camera ----------
// camBegin(cx, cy, zoom, rot): world point (cx, cy) lands at screen centre. Letters queued while a camera is
// active are placed through it automatically (pass {screen:true} to opt out). One level only: always pair with camEnd().
// LAST_CAM stays set after camEnd(), until the next frame: renderSheet's crops that follow a world point use it.
let CAM = null, LAST_CAM = null;
function camBegin(cx = W / 2, cy = H / 2, zoom = 1, rot = 0) { push(); translate(W / 2, H / 2); rotate(rot); scale(zoom); translate(-cx, -cy); CAM = LAST_CAM = { cx, cy, zoom, rot }; }
function camEnd() { pop(); CAM = null; }
function toScreen(x, y, cam = CAM) {
  if (!cam) return [x, y];
  const c = Math.cos(cam.rot), s = Math.sin(cam.rot), dx = (x - cam.cx) * cam.zoom, dy = (y - cam.cy) * cam.zoom;
  return [W / 2 + dx * c - dy * s, H / 2 + dx * s + dy * c];
}

// ---------- full-frame effects (call outside a camera, in screen space) ----------
function flash(k, col = PAL.cream) { if (k > .01) paint(rectPts(-60, -60, W + 120, H + 120), { wash: col, washOp: 255 * clamp(k), ink: null }); }
// Light: glow(x, y, r, col, a) ADDS a soft halo of light (sun, lamp, fireflies, magic). p5.brush mixes colour like
// pigment, so light can't be painted; this is the one non-crayon mark in the kit. It lands on what's drawn so far,
// under anything drawn after it, and follows the camera. On cream paper it shows only as a gentle warm bloom.
function glow(x, y, r, col = '#FFD98A', a = 1) {
  if (a <= 0 || r < 1) return;
  flushBrush();
  const c = color(col), rr = r * (1 + jit(.03));
  push(); blendMode(ADD); tint(red(c), green(c), blue(c), 150 * clamp(a)); image(glowTex, x - rr, y - rr, 2 * rr, 2 * rr); noTint(); blendMode(BLEND); pop();
}
function makeGlowTex() {
  const g = createGraphics(256, 256); g.pixelDensity(1); const c = g.drawingContext, gr = c.createRadialGradient(128, 128, 0, 128, 128, 128);
  [[0, 1], [.18, .8], [.45, .32], [.75, .08], [1, 0]].forEach(([s, a]) => gr.addColorStop(s, `rgba(255,255,255,${a})`));
  c.fillStyle = gr; c.fillRect(0, 0, 256, 256);
  return g;
}
// Paint everything OUTSIDE a star-shaped hole (irises, keyholes, heart-shaped reveals).
function irisShape(pts, col = PAL.ink, far = 4000) {
  const n = pts.length; let cx = 0, cy = 0; for (const p of pts) { cx += p[0]; cy += p[1]; } cx /= n; cy /= n;
  const out = p => { const dx = p[0] - cx, dy = p[1] - cy, d = Math.hypot(dx, dy) || 1; return [cx + dx / d * far, cy + dy / d * far]; };
  for (let i = 0; i < n; i++) {
    const a = pts[i], b = pts[(i + 1) % n], ex = (b[0] - a[0]) * .06, ey = (b[1] - a[1]) * .06;
    const a2 = [a[0] - ex, a[1] - ey], b2 = [b[0] + ex, b[1] + ey];
    paint([a2, b2, out(b2), out(a2)], { wash: col, washOp: 255, ink: null });
  }
}
function iris(cx, cy, r, col = PAL.ink) { if (r < 4) paint(rectPts(-60, -60, W + 120, H + 120), { wash: col, ink: null }); else irisShape(ellPts(cx, cy, r, r, 40), col); }

let T = 0, paperG = null, glowTex = null, letG = null, outC = null, outX = null;
let LETTERS = [];

// ---------- geometry ----------
function rectPts(x, y, w, h, j = 0) {
  return [[x + jit(j), y + jit(j)], [x + w / 2 + jit(j), y + jit(j) * .5], [x + w + jit(j), y + jit(j)],
          [x + w + jit(j) * .5, y + h / 2], [x + w + jit(j), y + h + jit(j)], [x + w / 2 + jit(j), y + h + jit(j) * .5],
          [x + jit(j), y + h + jit(j)], [x + jit(j) * .5, y + h / 2]];
}
function ellPts(cx, cy, rx, ry, n = 28, j = 0, rot = 0) {
  const p = []; for (let i = 0; i < n; i++) { const a = rot + i / n * TAU; p.push([cx + Math.cos(a) * rx + jit(j), cy + Math.sin(a) * ry + jit(j)]); } return p;
}
function rrPts(x, y, w, h, r, j = 0) {
  const p = [], seg = 5, corner = (cx, cy, a0) => { for (let i = 0; i <= seg; i++) { const a = a0 + i / seg * Math.PI / 2; p.push([cx + Math.cos(a) * r + jit(j), cy + Math.sin(a) * r + jit(j)]); } };
  corner(x + w - r, y + r, -Math.PI / 2); corner(x + w - r, y + h - r, 0); corner(x + r, y + h - r, Math.PI / 2); corner(x + r, y + r, Math.PI);
  return p;
}
function starPts(cx, cy, r, inner = .38, n = 4, rot = -Math.PI / 2) {
  const p = []; for (let i = 0; i < n * 2; i++) { const a = rot + i * Math.PI / n, q = i % 2 ? r * inner : r; p.push([cx + Math.cos(a) * q, cy + Math.sin(a) * q]); } return p;
}
function heartPts(cx, cy, r, n = 22) {
  const p = []; for (let i = 0; i < n; i++) { const a = i / n * TAU, x = 16 * Math.pow(Math.sin(a), 3), y = 13 * Math.cos(a) - 5 * Math.cos(2 * a) - 2 * Math.cos(3 * a) - Math.cos(4 * a); p.push([cx + x * r / 16, cy - y * r / 16]); }
  return p;
}
// Smooth curve through the points (Catmull-Rom), n samples per span.
function through(P, n = 6) {
  if (P.length < 3) return P.slice();
  const out = [];
  for (let i = 0; i < P.length - 1; i++) {
    const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)];
    for (let k = 0; k < n; k++) {
      const u = k / n, u2 = u * u, u3 = u2 * u;
      out.push([0, 1].map(d => .5 * (2 * p1[d] + (p2[d] - p0[d]) * u + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * u2 + (3 * p1[d] - p0[d] - 3 * p2[d] + p3[d]) * u3)));
    }
  }
  out.push(P[P.length - 1]);
  return out;
}
// Tapered ribbon around a path (w0 wide at the start, w1 at the end), as one closed outline.
// Limbs, tails, scarves, stems: one shape with one outline, so nothing looks glued on.
function ribbon(P, w0, w1 = w0) {
  const C = through(P), n = C.length, L = [], R = [];
  for (let i = 0; i < n; i++) {
    const a = C[Math.max(0, i - 1)], b = C[Math.min(n - 1, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], d = Math.hypot(dx, dy) || 1, w = lerp(w0, w1, i / Math.max(1, n - 1)) / 2;
    L.push([C[i][0] - dy / d * w, C[i][1] + dx / d * w]); R.push([C[i][0] + dy / d * w, C[i][1] - dx / d * w]);
  }
  return L.concat(R.reverse());
}

// ---------- paint wrapper ----------
// One call = one shape: optional flat wash, optional watercolour-style fill, optional hatch, optional outline.
// It's the low-level primitive; the crayon look is built on it in crayon.js (colorIn, scribbleFill, hatchFill …).
// p5.brush 2.2.3 loses strokes drawn far from the origin under a zoomed camera, so every shape and line is drawn
// around its own centre.
function centred(pts, draw) {
  if (!pts.length) return;
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (const [x, y] of pts) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
  push(); translate(cx, cy); draw(pts.map(([x, y]) => [x - cx, y - cy])); pop();
}
function paint(pts, o = {}) { centred(pts, (P) => paintAt(P, o)); }
function paintAt(pts, o) {
  if (o.wash || o.fill || o.hatch) {
    if (o.wash) brush.wash(o.wash, o.washOp ?? 255); else brush.noWash();
    if (o.fill) { brush.fill(o.fill, o.fillOp ?? 170); brush.fillBleed(o.bleed ?? .1); brush.fillTexture(o.tex ?? .4, o.border ?? .35); } else brush.noFill();
    if (o.hatch) { brush.hatch(o.hatch.d, o.hatch.a, o.hatch.o || { rand: .15 }); brush.hatchStyle(o.hatch.b || 'cpen', o.hatch.c || PAL.ink, o.hatch.w || 1); } else brush.noHatch();
    brush.noStroke();
    if (o.curv) { brush.beginShape(o.curv); for (const p of pts) brush.vertex(p[0], p[1]); brush.endShape(true); }
    else brush.polygon(pts);
  }
  if (o.ink !== null) {
    brush.noWash(); brush.noFill(); brush.noHatch(); brush.set(o.br || 'cpen', o.ink || PAL.ink, o.sw ?? 1);
    brush.beginShape(o.curv || 0); for (const p of pts) brush.vertex(p[0], p[1]); brush.endShape(true);
  }
}
// An open line. The default brush is the coloured pencil ('cpen'); see crayon.js for the others.
function inkLine(pts, sw = 1, col = PAL.ink, br = 'cpen', curv = .5) {
  if (pts.length < 2) return;
  centred(pts, (P) => { brush.noFill(); brush.noWash(); brush.noHatch(); brush.set(br, col, sw); brush.spline(P, curv); });
}

// ---------- lettering in the scene (drawn on the 2D compositor, under the paper finish) ----------
// For a word that belongs IN the picture (a shop sign, a name on a mailbox). Captions go through captions() instead.
const HAND_FONT = '"LXGW WenKai TC", "Zen Maru Gothic", "Noto Serif TC", "Kaiti TC", serif';
function letter(txt, x, y, size, color, o = {}) {
  if (CAM && !o.screen) { [x, y] = toScreen(x, y); size *= CAM.zoom; o = { ...o, rot: (o.rot || 0) + CAM.rot }; }
  LETTERS.push({ txt, x, y, size, color, ...o });
}
// Comic sound effect: pops in at age 0, wobbles, fades by `life` seconds.
function sfx(txt, x, y, size, color, age, o = {}) {
  const life = o.life ?? 1.2; if (age < 0 || age > life) return;
  letter(txt, x, y, size, color, { pop: age * 5, rot: (o.rot ?? -.08) + Math.sin(age * 20) * .03 * (1 - age / life), alpha: 1 - seg(age, life - .25, life), ...o });
}
function drawLetters(c) {
  for (const L of LETTERS) {
    const k = L.pop != null ? backOut(L.pop) : 1; if (k <= .01) continue;
    c.save(); c.translate(L.x, L.y); c.rotate(L.rot || 0); c.scale(k, k); c.globalAlpha = L.alpha ?? 1;
    c.font = L.font || `700 ${L.size}px ${HAND_FONT}`;
    c.textAlign = L.align || 'center'; c.textBaseline = 'middle';
    if (L.stroke) { c.lineJoin = 'round'; c.lineWidth = L.size * .12; c.strokeStyle = L.stroke; c.strokeText(L.txt, 0, 0); }
    c.fillStyle = L.color; c.fillText(L.txt, 0, 0);
    c.restore();
  }
}

// p5.brush defers washes and strokes into a mask layer; a (tiny, off-screen) fill forces it to composite now, so
// everything drawn before this call really lands under whatever p5 draws next (letters, glow, snapshots).
function flushBrush() {
  push(); resetMatrix(); translate(-W / 2, -H / 2);
  brush.noStroke(); brush.noHatch(); brush.noWash(); brush.fill('#000000', 1); brush.fillBleed(0); brush.fillTexture(0, 0);
  brush.polygon([[-50, -50], [-40, -50], [-40, -40]]); brush.noFill(); pop();
}
// Paint the queued lettering into the scene itself, so later layers (wipes) cover it. drawWorld calls this after each shot.
function flushLetters() {
  if (!LETTERS.length) return;
  letG.clear(); drawLetters(letG.drawingContext); LETTERS = [];
  flushBrush();
  push(); resetMatrix(); translate(-W / 2, -H / 2); image(letG, 0, 0); pop();
}
// Wipe the canvas back to blank paper (used between the two pages of a page turn).
function clearToPaper() { flushBrush(); push(); resetMatrix(); translate(-W / 2, -H / 2); image(paperG, 0, 0); pop(); }

// ---------- frame ----------
async function setup() {
  createCanvas(W, H, WEBGL); pixelDensity(1); noLoop();
  brush.scaleBrushes(5); defineBrushes();                     // crayon.js
  lookSetup();                                                // crayon.js: paper, tooth, grain, page textures (cached)
  glowTex = makeGlowTex(); letG = createGraphics(W, H); letG.pixelDensity(1);
  outC = document.getElementById('out'); outX = outC.getContext('2d');
  await Promise.all([document.fonts.load(`700 80px ${HAND_FONT}`, '從前有一隻小刺蝟 Once upon a time'), ...(window.EXTRA_FONTS || []).map(([f, txt]) => document.fonts.load(f, txt))]);
  window.ready = true;
  if (!location.search.includes('render')) devUI();
}
function draw() {
  if (!window.ready) return;
  LETTERS = []; CAM = LAST_CAM = null; stageReset();
  push(); translate(-W / 2, -H / 2);
  BOILN = Math.floor(T * BOIL + 1e-6); CAST_N = 0; boilSeed('frame'); noiseSeed(77);
  image(paperG, 0, 0);
  drawWorld(T);
  pop();
}
function composite(t) {
  const c = outX;
  c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1;
  finishPage(c, drawingContext.canvas, t);                    // crayon.js: tooth, grain, vignette, page border
  if (STAGE.turn) pageTurnComposite(c, STAGE.turn, t);       // crayon.js: the previous page curling away
  drawLetters(c);
  c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1;
  if (window.overlayHook && !window.LOOP) window.overlayHook(c, t);   // crisp 2D overlay on top (captions: see captions() in crayon.js)
}
window.renderAt = async (t, type = 'image/png', q = .92) => { T = t; await redraw(); composite(t); return outC.toDataURL(type, q); };
// Contact sheet of several times, for visual checks: returns { url, ms[] }. crop = [x, y, w, h] fills each cell with just
// that region of the frame, at full resolution. at = [x, y, w, h] instead crops w × h around the WORLD point (x, y),
// wherever each frame's camera put it; x and y may be expressions evaluated in the page.
window.renderSheet = async (times, cols = 3, w = 640, crop = null, at = null) => {
  if (at) at = at.map((v) => typeof v === 'string' ? (0, eval)(v) : v);
  const [, , cw, ch] = at || crop || [0, 0, W, H], h = Math.round(w * ch / cw), rows = Math.ceil(times.length / cols), sc = document.createElement('canvas');
  sc.width = cols * w; sc.height = rows * h; const c = sc.getContext('2d'), ms = [];
  for (let i = 0; i < times.length; i++) {
    const t0 = performance.now(); T = times[i]; await redraw(); composite(times[i]); ms.push(Math.round(performance.now() - t0));
    const x = (i % cols) * w, y = Math.floor(i / cols) * h;
    const [cx, cy] = at ? toScreen(at[0], at[1], LAST_CAM).map((v, j) => v - (j ? ch : cw) / 2) : crop || [0, 0];
    c.drawImage(outC, cx, cy, cw, ch, x, y, w, h); c.fillStyle = 'rgba(0,0,0,.65)'; c.fillRect(x, y, 84, 24); c.fillStyle = '#fff'; c.font = '15px sans-serif'; c.fillText(times[i].toFixed(2) + 's', x + 6, y + 17);
  }
  return { url: sc.toDataURL('image/jpeg', .9), ms };
};
window.gpuInfo = () => { const gl = drawingContext, e = gl.getExtension('WEBGL_debug_renderer_info'); return e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER); };

function devUI() {
  const s = document.getElementById('scrub'), lab = document.getElementById('tt'); s.max = window.LOOP ? window.LOOP.len : DUR;
  let busy = false, want = null;
  const go = async () => { if (busy) return; busy = true; while (want != null) { const t = want; want = null; const t0 = performance.now(); await window.renderAt(t); lab.textContent = `${t.toFixed(2)}s  ·  ${Math.round(performance.now() - t0)} ms/frame`; } busy = false; };
  s.addEventListener('input', () => { want = +s.value; go(); });
  want = +(new URLSearchParams(location.search).get('t') || 0); s.value = want; go();
}
