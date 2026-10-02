// crayon.js: the CRAYON-STORYBOOK look. Brushes (crayon, coloured pencil, pastel, graphite), fills (scribble, hatch,
// cross-hatch, smudge), the paper and its tooth, the page finish (grain, vignette, picture-book border), the page turn,
// scenery and props, emotes and storybook captions.
//
// How the crayon look is made:
//   1. Shapes are coloured in: a pale flat base (so a character is opaque), then directional crayon scribble or hatching
//      on top in the full colour, then a coloured-pencil outline (colorIn).
//   2. Everything is drawn on cream paper (paperG) and, after the frame is drawn, the paper's TOOTH is laid over it: a
//      fixed speckle mask in the paper colour. Where the paper has a pit, pigment skips, exactly like wax crayon on
//      drawing paper. Pure paper is unchanged (paper over paper), so only drawn marks break up. The tooth is the same
//      pattern everywhere, so every stroke breaks consistently; it shifts a little with each boil drawing (PROJECT.toothBoil,
//      default on) so a moving camera doesn't "swim" through a fixed texture.
//   3. Linework boils at 8 drawings/s (BOIL in core.js) through boilSeed(), like frames re-drawn by hand.
// Textures (paper, tooth, grain, vignette) are built once in lookSetup() and only blitted per frame.

// ---------- brushes ----------
// Names: 'crayon' (wide, waxy), 'crayonFine' (crayon for details and small lines), 'cpen' (coloured pencil: thin,
// grainy — the default outline), 'pastel' (soft, powdery), 'graphite' (sketch), 'chalk' (dry, broken, bigger than pastel).
// p5.brush built-ins still work: '2B', 'HB', 'charcoal', 'cpencil', 'marker', 'spray' …
function defineBrushes() {
  brush.add('crayon', { type: 'default', weight: 8, scatter: .7, sharpness: .45, grain: 5, opacity: 150, spacing: .22, pressure: [1.05, .95], rotate: 'natural', noise: .35 });
  brush.add('crayonFine', { type: 'default', weight: 4.2, scatter: .4, sharpness: .55, grain: 7, opacity: 165, spacing: .2, pressure: [1.1, .9], rotate: 'natural', noise: .3 });
  brush.add('cpen', { type: 'default', weight: 3.0, scatter: .35, sharpness: .7, grain: 9, opacity: 205, spacing: .15, pressure: [1.15, .8], rotate: 'natural', noise: .2 });
  brush.add('pastel', { type: 'default', weight: 20, scatter: 3, sharpness: .12, grain: 3, opacity: 60, spacing: .35, pressure: [1, .8], rotate: 'random', noise: .5 });
  brush.add('chalk', { type: 'default', weight: 12, scatter: 1.6, sharpness: .25, grain: 2.5, opacity: 120, spacing: .28, pressure: [1, .85], rotate: 'random', noise: .5 });
  brush.add('graphite', { type: 'default', weight: 1.8, scatter: .3, sharpness: .6, grain: 22, opacity: 150, spacing: .15, pressure: [1.2, .7], rotate: 'natural', noise: .3 });
}

// ---------- lines ----------
const pencilLine = (pts, sw = 1, col = PAL.ink, curv = .5) => inkLine(pts, sw, col, 'cpen', curv);
const crayonLine = (pts, sw = 1, col = PAL.ink, curv = .5) => inkLine(pts, sw, col, sw < .7 ? 'crayonFine' : 'crayon', curv);
const pastelLine = (pts, sw = 1, col = PAL.rose, curv = .5) => inkLine(pts, sw, col, 'pastel', curv);
const sketchLine = (pts, sw = 1, col = PAL.inkSoft, curv = .5) => inkLine(pts, sw, col, 'graphite', curv);

// ---------- fills ----------
// Scanlines through a polygon at angle `ang` (radians), `gap` px apart → rows of [x0, x1] segments in rotated space.
function scanRows(pts, ang, gap, off = .5) {
  const c = Math.cos(-ang), s = Math.sin(-ang), R = pts.map(([x, y]) => [x * c - y * s, x * s + y * c]);
  let y0 = Infinity, y1 = -Infinity; for (const p of R) { if (p[1] < y0) y0 = p[1]; if (p[1] > y1) y1 = p[1]; }
  const rows = [], n = R.length;
  for (let y = y0 + gap * off; y < y1; y += gap) {
    const xs = [];
    for (let i = 0; i < n; i++) {
      const a = R[i], b = R[(i + 1) % n];
      if ((a[1] <= y) !== (b[1] <= y)) xs.push(a[0] + (y - a[1]) / (b[1] - a[1]) * (b[0] - a[0]));
    }
    xs.sort((p, q) => p - q);
    const segs = []; for (let i = 0; i + 1 < xs.length; i += 2) if (xs[i + 1] - xs[i] > 1) segs.push([xs[i], xs[i + 1]]);
    rows.push({ y, segs });
  }
  return { rows, back: (x, y) => [x * c + y * s, -x * s + y * c] };
}
// Scribble fill: back-and-forth crayon zigzags inside the shape, the way a child (or an illustrator) colours in.
//   o.ang   direction of the strokes in radians (default ~ -0.5, a comfortable right-handed diagonal)
//   o.gap   px between passes (smaller = denser; default 11)       o.w  brush weight (default 1)
//   o.br    brush (default 'crayon')                                o.op colour opacity is in the brush; use a paler col
//   o.over  px the turns overshoot (+) or stop short (-) of the edge (default 1: a tiny, natural overshoot)
//   o.loose 0..1 how wobbly the turns are (default .35)             o.run rows per stroke before lifting (default 7)
function scribbleFill(pts, col, o = {}) {
  if (pts.length < 3) return;
  centred(pts, P => {
    const gap = o.gap ?? 13, ang = o.ang ?? -.5, over = o.over ?? 1, loose = o.loose ?? .35, run = o.run ?? 7;
    const { rows, back } = scanRows(P, ang + jit(.03), gap, .35 + random() * .3);
    // chain each row's segments to an overlapping segment of the row before, so a zigzag follows the shape
    const chains = [];
    let open = [];
    for (const r of rows) {
      const next = [];
      for (const s of r.segs) {
        const ch = open.find(c => !c.used && c.last[0] < s[1] && c.last[1] > s[0] && c.rows.length < run);
        if (ch) { ch.used = true; ch.rows.push([r.y, s]); ch.last = s; next.push(ch); }
        else { const c = { rows: [[r.y, s]], last: s }; chains.push(c); next.push(c); }
      }
      next.forEach(c => c.used = false); open = next;
    }
    brush.noFill(); brush.noWash(); brush.noHatch(); brush.set(o.br || 'crayon', col, o.w ?? 1);
    for (const c of chains) {
      const Q = [];
      c.rows.forEach(([y, [a, b]], k) => {
        const len = b - a, inA = Math.min(len * .3, -over + jit(gap * loose)), inB = Math.min(len * .3, -over + jit(gap * loose));
        const ya = y + jit(gap * .18), yb = y + jit(gap * .18);
        const mid = back((a + b) / 2 + jit(len * .08), (ya + yb) / 2 + jit(gap * .35));
        if (k % 2 === 0) Q.push(back(a + inA, ya), mid, back(b - inB, yb)); else Q.push(back(b - inB, yb), mid, back(a + inA, ya));
      });
      brush.spline(Q, .4);
    }
  });
}
// Hatch fill: parallel strokes (p5.brush's hatch, clipped to the shape). cross: true adds a second direction.
//   o.ang (radians, default .6), o.gap (default 12), o.br ('crayonFine'), o.w (1), o.rand (.25), o.grad (0: even; up to 1 fades)
function hatchFill(pts, col, o = {}) {
  const one = (a) => paint(pts, { hatch: { d: o.gap ?? 12, a, o: { rand: o.rand ?? .25, gradient: o.grad || false }, b: o.br || 'crayonFine', c: col, w: o.w ?? 1 }, ink: null });
  one(o.ang ?? .6);
  if (o.cross) one((o.ang ?? .6) + (o.crossAng ?? 1.25));
}
const crossHatch = (pts, col, o = {}) => hatchFill(pts, col, { ...o, cross: true });
// Smudge: soft, powdery pastel colour with no hard edge (skies, cheeks, shadows, glows on paper, distant hills).
//   o.op (default 110), o.tex (default .55), o.bleed (default .12)
function smudge(pts, col, o = {}) {
  paint(pts, { fill: col, fillOp: o.op ?? 110, bleed: o.bleed ?? .12, tex: o.tex ?? .55, border: o.border ?? .08, ink: null });
}
// The workhorse: colour a shape in, picture-book style.
//   col      the colour (crayon strokes use it; the base under them is a paler version)
//   fill     'scribble' (default) | 'hatch' | 'cross' | 'smudge' | 'flat' | 'none'
//   pale     how much paler the base is (0 = same as col, default .45); base: an explicit base colour; baseOp (255)
//   tone     stroke colour (default: col, a touch deeper)   ang, gap, w, br, over, loose: passed to the fill
//   line     outline colour (default: a deep tint of col; null = no outline)  lw: outline weight (default 1)
//   lbr      outline brush (default 'cpen')   curv: 0..1 smooth the outline through the points
//   shade    { pts, col, ang, gap }: an extra scribble pass (a shadow side), drawn over the fill
function colorIn(pts, o = {}) {
  if (pts.length < 3) return;
  const col = o.col || PAL.butter, base = o.base || mixCol(col, PAL.paper, o.pale ?? .6);
  const fill = o.fill || 'scribble', tone = o.tone || col;
  if (fill !== 'none') paint(pts, { wash: base, washOp: o.baseOp ?? 255, ink: null, curv: o.curv });
  if (fill === 'scribble') scribbleFill(pts, tone, o);
  else if (fill === 'hatch') hatchFill(pts, tone, o);
  else if (fill === 'cross') hatchFill(pts, tone, { ...o, cross: true });
  else if (fill === 'smudge') smudge(pts, tone, o);
  if (o.shade) scribbleFill(o.shade.pts, o.shade.col || mixCol(col, PAL.ink, .3), { ang: o.shade.ang ?? (o.ang ?? -.5) + .5, gap: o.shade.gap ?? 9, br: 'crayonFine', w: .9 });
  const line = o.line === undefined ? mixCol(col, PAL.ink, .72) : o.line;
  if (line) paint(pts, { ink: line, sw: o.lw ?? 1, br: o.lbr || 'cpen', curv: o.curv });
}
// A round dab of colour (cheeks, dots, berries, polka dots): a little crayon spiral.
function dab(x, y, r, col, w = .8) {
  const P = []; for (let a = 0; a < TAU * 2.3; a += .5) { const q = r * (.2 + .8 * a / (TAU * 2.3)); P.push([x + Math.cos(a) * q + jit(r * .08), y + Math.sin(a) * q * .9 + jit(r * .08)]); }
  inkLine(P, w, col, 'crayonFine', .5);
}

// ---------- paper, tooth, grain ----------
function lcg(seed) { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; }
let toothC = null, grainC = null, pageA = null, pageAX = null, TOOTH_PAD = 96;
function lookSetup() {
  paperG = makePaper(); toothC = makeTooth(); grainC = makeGrain();
  pageA = document.createElement('canvas'); pageA.width = W; pageA.height = H; pageAX = pageA.getContext('2d');
}
function makePaper() {
  const g = createGraphics(W, H); g.pixelDensity(1); const c = g.drawingContext, r = lcg(11);
  c.fillStyle = PAL.paper; c.fillRect(0, 0, W, H);
  // soft uneven warmth, like real drawing paper under a lamp
  for (let i = 0; i < 60; i++) { const x = r() * W, y = r() * H, rr = 140 + r() * 420, gr = c.createRadialGradient(x, y, 0, x, y, rr), a = .035 * r(); gr.addColorStop(0, `rgba(190,150,100,${a})`); gr.addColorStop(1, 'rgba(190,150,100,0)'); c.fillStyle = gr; c.fillRect(x - rr, y - rr, 2 * rr, 2 * rr); }
  // fibres
  c.lineWidth = 1;
  for (let i = 0; i < 1600; i++) { const x = r() * W, y = r() * H, l = 5 + r() * 20, a = r() * TAU; c.strokeStyle = `rgba(140,110,80,${.03 + r() * .05})`; c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + Math.cos(a + .6) * l * .5, y + Math.sin(a + .6) * l * .5, x + Math.cos(a) * l, y + Math.sin(a) * l); c.stroke(); }
  return g;
}
// value noise on a lattice, bilinear
function noiseField(w, h, cell, r) {
  const gw = Math.ceil(w / cell) + 2, gh = Math.ceil(h / cell) + 2, g = new Float32Array(gw * gh); for (let i = 0; i < g.length; i++) g[i] = r();
  return (x, y) => { const fx = x / cell, fy = y / cell, ix = fx | 0, iy = fy | 0, tx = fx - ix, ty = fy - iy, sx = tx * tx * (3 - 2 * tx), sy = ty * ty * (3 - 2 * ty), i = iy * gw + ix;
    return lerp(lerp(g[i], g[i + 1], sx), lerp(g[i + gw], g[i + gw + 1], sx), sy); };
}
// The tooth: paper-coloured speckles whose alpha is how deep the pit is. Laid over the drawn frame, pigment skips there.
function makeTooth() {
  const TW = W + TOOTH_PAD, TH = H + TOOTH_PAD, cv = document.createElement('canvas'); cv.width = TW; cv.height = TH;
  const c = cv.getContext('2d'), id = c.createImageData(TW, TH), d = id.data, r = lcg(7);
  const n1 = noiseField(TW, TH, 2.3, r), n2 = noiseField(TW, TH, 6.5, r), n3 = noiseField(TW, TH, 38, r);
  const pc = parseInt(PAL.paper.slice(1), 16), pr = (pc >> 16) & 255, pg = (pc >> 8) & 255, pb = pc & 255;
  for (let y = 0, i = 0; y < TH; y++) for (let x = 0; x < TW; x++, i += 4) {
    // fine pits + a medium weave + large patches where the paper is rougher (crayon breaks more there)
    const v = .55 * n1(x, y * 1.35) + .3 * n2(x * 1.2, y) + .15 * r() + .12 * (n3(x, y) - .5);
    const a = clamp((v - .5) / .22);
    d[i] = pr + 4; d[i + 1] = pg + 3; d[i + 2] = pb + 2; d[i + 3] = 255 * a * a * .92;
  }
  c.putImageData(id, 0, 0);
  return cv;
}
// Static grain multiplied over the frame, so pigment sits "in" the paper.
function makeGrain() {
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H; const c = cv.getContext('2d'), r = lcg(5);
  const id = c.createImageData(W, H), d = id.data;
  for (let i = 0; i < d.length; i += 4) { const v = 255 - (r() < .5 ? r() * r() * 26 : 0); d[i] = v; d[i + 1] = v - 1; d[i + 2] = v - 3; d[i + 3] = 255; }
  c.putImageData(id, 0, 0);
  return cv;
}

// ---------- stage: per-frame finishing options (reset every frame; set them from a shot) ----------
// vignette(k): soft warm darkening at the corners (default .3; 0 = off).
// bookPage(k, o): the picture-book framing: a cream page border around the illustration. k 0..1 (animate it in/out),
//   o.m margin px (default 64), o.r corner radius (default 26), o.line: draw the pencil frame line (default true).
// tooth(k): how strongly the paper tooth breaks the crayon (default 1).
let STAGE = {};
function stageReset() { STAGE = { vig: .3, page: 0, pageM: 64, pageR: 26, pageLine: true, tooth: 1, turn: null }; }
stageReset();
const vignette = k => { STAGE.vig = k; };
const bookPage = (k = 1, o = {}) => { STAGE.page = clamp(k); STAGE.pageM = o.m ?? 64; STAGE.pageR = o.r ?? 26; STAGE.pageLine = o.line ?? true; };
const tooth = k => { STAGE.tooth = k; };

// Draw a finished page into c: the drawn frame, the tooth, the grain, the vignette and the page border.
function finishPage(c, src, t, st = STAGE) {
  c.save(); c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1;
  c.drawImage(src, 0, 0, W, H);
  if (st.tooth > 0) {
    const bn = PROJECT.toothBoil === false ? 0 : Math.floor(t * BOIL + 1e-6), ox = Math.floor(hash(bn * 3.7 + 1) * TOOTH_PAD), oy = Math.floor(hash(bn * 5.3 + 2) * TOOTH_PAD);
    c.globalAlpha = clamp(st.tooth); c.drawImage(toothC, -ox, -oy); c.globalAlpha = 1;
  }
  c.globalCompositeOperation = 'multiply'; c.drawImage(grainC, 0, 0);
  if (st.vig > 0) {
    const g = c.createRadialGradient(W / 2, H / 2, H * .42, W / 2, H / 2, H * 1.08);
    g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(1, `rgba(150,112,82,${.55 * st.vig})`);
    c.fillStyle = g; c.fillRect(0, 0, W, H);
  }
  c.globalCompositeOperation = 'source-over';
  if (st.page > 0) pageBorder(c, st);
  c.restore();
}
function pageBorder(c, st) {
  const m = st.pageM * easeOut(st.page), r = st.pageR, x0 = m, y0 = m * .85, x1 = W - m, y1 = H - m * .85;
  c.save();
  c.beginPath(); c.rect(-10, -10, W + 20, H + 20); c.roundRect(x0, y0, x1 - x0, y1 - y0, r);
  c.fillStyle = PAL.paper; c.fill('evenodd');
  c.clip('evenodd'); c.drawImage(paperG.elt || paperG.canvas, 0, 0); c.restore();
  if (st.pageLine && st.page > .3) {   // a hand-drawn frame line, drawn twice, slightly off (boils with the linework)
    c.save(); c.globalAlpha = .55 * seg(st.page, .3, 1); c.strokeStyle = PAL.ink; c.lineJoin = 'round';
    for (let k = 0; k < 2; k++) {
      const j = n => (hash(BOILN * 7 + n + k * 31) - .5) * 3.5, e = 5 + k * 2;
      c.lineWidth = k ? 1.4 : 2.4; c.beginPath();
      c.moveTo(x0 - e + j(1), y0 + r + j(2)); c.quadraticCurveTo(x0 - e + j(3), y0 - e + j(4), x0 + r + j(5), y0 - e + j(6));
      c.lineTo(x1 - r + j(7), y0 - e + j(8)); c.quadraticCurveTo(x1 + e + j(9), y0 - e + j(10), x1 + e + j(11), y0 + r + j(12));
      c.lineTo(x1 + e + j(13), y1 - r + j(14)); c.quadraticCurveTo(x1 + e + j(15), y1 + e + j(16), x1 - r + j(17), y1 + e + j(18));
      c.lineTo(x0 + r + j(19), y1 + e + j(20)); c.quadraticCurveTo(x0 - e + j(21), y1 + e + j(22), x0 - e + j(23), y1 - r + j(24));
      c.closePath(); c.stroke();
    }
    c.restore();
  }
}

// ---------- page turn ----------
// Registered per shot in shots(): [t, shotFn, { turn: .9 }]. The previous page is snapshotted (finished with ITS stage
// settings), then composited over the new one, curling away from the bottom-right corner with its back showing.
function snapshotPage() { flushBrush(); finishPage(pageAX, drawingContext.canvas, T, STAGE); }
function clipHalf(poly, F, n, keepPos) {   // Sutherland–Hodgman against the line through F with normal n
  const out = [], s = p => ((p[0] - F[0]) * n[0] + (p[1] - F[1]) * n[1]) * (keepPos ? 1 : -1);
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length], sa = s(a), sb = s(b);
    if (sa >= 0) out.push(a);
    if ((sa >= 0) !== (sb >= 0)) { const k = sa / (sa - sb); out.push([lerp(a[0], b[0], k), lerp(a[1], b[1], k)]); }
  }
  return out;
}
function pageTurnComposite(c, turn, t) {
  const e = ease(turn.p), dir = turn.dir;
  // fold line: its bottom end leads (the corner is lifted first), its top end follows
  const xb = lerp(W + 30, -90, e), xt = xb + 420 * Math.sin(Math.PI * Math.min(1, e * 1.1)) + 40 * (1 - e);
  const mx = x => dir > 0 ? x : W - x;
  const F0 = [mx(xb), H + 30], F1 = [mx(xt), -30], dx = F1[0] - F0[0], dy = F1[1] - F0[1], L = Math.hypot(dx, dy);
  let n = [dy / L, -dx / L]; if ((mx(W + 999) - F0[0]) * n[0] + (H / 2 - F0[1]) * n[1] < 0) n = [-n[0], -n[1]];   // n points to the revealed side
  const rect = [[0, 0], [W, 0], [W, H], [0, H]], keep = clipHalf(rect, F0, n, false), gone = clipHalf(rect, F0, n, true);
  const sq = .72, refl = p => { const d = (p[0] - F0[0]) * n[0] + (p[1] - F0[1]) * n[1]; return [p[0] - (1 + sq) * d * n[0], p[1] - (1 + sq) * d * n[1]]; };
  const flap = gone.map(refl);
  const path = P => { c.beginPath(); P.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); };
  c.save();
  // the new page gets a soft shadow along the fold
  if (gone.length > 2) {
    path(gone); c.save(); c.clip();
    const g = c.createLinearGradient(F0[0], F0[1], F0[0] + n[0] * 140, F0[1] + n[1] * 140);
    g.addColorStop(0, 'rgba(90,60,40,.32)'); g.addColorStop(1, 'rgba(90,60,40,0)'); c.fillStyle = g; c.fillRect(0, 0, W, H); c.restore();
  }
  // the old page, what's left of it
  if (keep.length > 2) { path(keep); c.save(); c.clip(); c.drawImage(pageA, 0, 0); c.restore(); }
  // the flap: the page's back, curling over, with a drop shadow
  if (flap.length > 2) {
    c.save(); path(flap); c.shadowColor = 'rgba(70,45,30,.38)'; c.shadowBlur = 36; c.shadowOffsetX = -n[0] * 10; c.shadowOffsetY = -n[1] * 10 + 6;
    c.fillStyle = PAL.paper; c.fill(); c.restore();
    c.save(); path(flap); c.clip();
    c.drawImage(paperG.elt || paperG.canvas, 0, 0);
    // a ghost of the picture showing through the paper, mirrored
    const k = 1 + sq, M = [1 - k * n[0] * n[0], -k * n[0] * n[1], -k * n[0] * n[1], 1 - k * n[1] * n[1]], dF = F0[0] * n[0] + F0[1] * n[1];
    c.globalAlpha = .09; c.setTransform(M[0], M[1], M[2], M[3], k * dF * n[0], k * dF * n[1]); c.drawImage(pageA, 0, 0); c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1;
    // curl shading: bright along the fold, warmer towards the lifted edge
    const g = c.createLinearGradient(F0[0], F0[1], F0[0] - n[0] * 520, F0[1] - n[1] * 520);
    g.addColorStop(0, 'rgba(255,252,242,.5)'); g.addColorStop(.25, 'rgba(255,252,242,0)'); g.addColorStop(1, 'rgba(150,110,80,.22)');
    c.fillStyle = g; c.fillRect(0, 0, W, H);
    c.restore();
    c.save(); path(flap); c.strokeStyle = 'rgba(74,54,49,.45)'; c.lineWidth = 2; c.lineJoin = 'round'; c.stroke(); c.restore();
  }
  c.restore();
}

// ---------- scenery ----------
// Plain page: nothing but the paper with a whisper of colour. sky(top, bottom): a soft pastel sky, smudged and stroked.
function paperWash(t, col = PAL.skyLt) { boilSeed('paperwash'); smudge(rectPts(-100, -100, W + 200, H + 200), col, { op: 60 }); }
function sky(top = PAL.sky, bottom = PAL.cream, o = {}) {
  boilSeed('sky');
  const x0 = o.x0 ?? -400, x1 = o.x1 ?? W + 400, y0 = o.y0 ?? -300, y1 = o.y1 ?? H * .75;
  paint(rectPts(x0, y0, x1 - x0, y1 - y0), { wash: mixCol(top, bottom, .55), ink: null });
  smudge(rectPts(x0, y0, x1 - x0, (y1 - y0) * .6, 20), top, { op: 120 });
  // long, loose horizontal pastel strokes: the sky is coloured in, not printed
  for (let i = 0; i < (o.strokes ?? 9); i++) {
    const y = lerp(y0 + 60, y1 - 100, (i + .5) / (o.strokes ?? 9)) + jit(10), xa = lerp(x0, x1, hash(i + 3) * .3), xb = lerp(x0, x1, .7 + hash(i + 9) * .3);
    inkLine([[xa, y], [(xa + xb) / 2, y + jit(8)], [xb, y + jit(6)]], 1.6, mixCol(top, PAL.cream, .15 + i / 14), 'crayon', .5);
  }
}
// A crayon sun: a butter disc coloured in circles, with wobbly rays that turn slowly.
function sun(x, y, r, t = T, o = {}) {
  boilSeed('sun' + (o.key || ''));
  if (o.glow !== false) glow(x, y, r * 3.2, '#FFE2A0', .35);
  const rays = o.rays ?? 12, rot = t * .15;
  for (let i = 0; i < rays; i++) {
    const a = rot + i / rays * TAU, l = r * (i % 2 ? 1.55 : 1.8);
    crayonLine([[x + Math.cos(a) * r * 1.2, y + Math.sin(a) * r * 1.2], [x + Math.cos(a + .05) * (r * 1.2 + l * .5), y + Math.sin(a + .05) * (r * 1.2 + l * .5)], [x + Math.cos(a) * (r * .9 + l), y + Math.sin(a) * (r * .9 + l)]], .9, PAL.butterDk);
  }
  colorIn(ellPts(x, y, r, r, 26, r * .02), { col: PAL.butter, gap: 10, ang: .3, line: PAL.butterDk, lw: 1.1 });
  if (o.face) { dab(x - r * .32, y - r * .08, r * .08, PAL.ink, .6); dab(x + r * .32, y - r * .08, r * .08, PAL.ink, .6); pencilLine([[x - r * .25, y + r * .25], [x, y + r * .38], [x + r * .25, y + r * .25]], .9, PAL.ink, .6); dab(x - r * .55, y + r * .2, r * .13, PAL.rose); dab(x + r * .55, y + r * .2, r * .13, PAL.rose); }
}
// A puffy cloud of scallops, lightly coloured.
function cloud(x, y, s = 1, o = {}) {
  boilSeed('cloud' + (o.key ?? Math.round(x)));
  const P = [], n = 40;
  for (let i = 0; i < n; i++) {   // an ellipse with round bumps on top and a flatter, softer underside
    const a = i / n * TAU, top = Math.sin(a) < 0, bump = top ? .22 * Math.abs(Math.sin(a * 3.5 + .4)) : .03 * Math.abs(Math.sin(a * 5));
    P.push([x + Math.cos(a) * 190 * s * (1 + bump * .6), y + Math.sin(a) * (top ? 78 : 40) * s * (1 + bump * 1.4)]);
  }
  colorIn(P, { col: o.col || PAL.cream, base: o.base || '#FFFCF3', fill: 'hatch', ang: .1, gap: 22 * s, tone: o.tone || PAL.skyLt, line: o.line || PAL.skyDk, lw: .8, curv: .5 });
}
// A hill: a big soft mound, coloured in long strokes that follow its slope.
function hill(cx, cy, rx, ry, col = PAL.sage, o = {}) {
  boilSeed('hill' + cx + ':' + cy);
  colorIn(ellPts(cx, cy, rx, ry, 44, 2), { col, gap: o.gap ?? 40, ang: o.ang ?? -.12, w: 1.5, run: 12, pale: .35, line: o.line ?? mixCol(col, PAL.ink, .55), lw: 1 });
}
const hillY = (x, cx, cy, rx, ry) => cy - ry * Math.sqrt(Math.max(0, 1 - ((x - cx) / rx) ** 2));
// A ground strip from y down, coloured in, with a pencil horizon.
function ground(y, col = PAL.sage, o = {}) {
  boilSeed('ground' + y);
  const x0 = o.x0 ?? -400, x1 = o.x1 ?? W + 400;
  colorIn(rectPts(x0, y, x1 - x0, (o.depth ?? H + 250 - y)), { col, gap: o.gap ?? 44, ang: -.05, w: 1.6, pale: .3, line: null, run: 12 });
  inkLine([[x0, y + 4], [(x0 + x1) / 2, y - 4], [x1, y + 3]], 1, mixCol(col, PAL.ink, .6), 'cpen', .5);
}
// Grass tufts that sway (key them so they don't re-boil).
function tufts(x0, x1, yf, n, col = PAL.sageDk, t = T, key = 'tufts') {
  boilSeed(key);
  for (let i = 0; i < n; i++) {
    const x = lerp(x0, x1, (i + hash(i + 7) * .6) / n), y = yf(x), sw = wob(t, .45, hash(i) * 3) * 5;
    for (const k of [-1, 0, 1]) inkLine([[x + k * 6, y], [x + k * 10 + sw, y - 20 - 10 * hash(i * 3 + k)]], .8, col, 'crayonFine', .4);
  }
}
// A round storybook tree: a scribbled crown of greens on a crayon trunk. o.fruit: [[dx, dy], …] apples (in crown units).
function tree(x, y, s = 1, o = {}) {
  boilSeed('tree' + Math.round(x));
  colorIn([[x - 26 * s, y], [x - 18 * s, y - 210 * s], [x - 44 * s, y - 260 * s], [x + 40 * s, y - 262 * s], [x + 20 * s, y - 210 * s], [x + 30 * s, y]], { col: PAL.bark, ang: 1.45, gap: 9, line: mixCol(PAL.bark, PAL.ink, .6) });
  const crown = [];
  for (let i = 0; i < 16; i++) { const a = i / 16 * TAU, rr = (1 + .1 * Math.sin(i * 2.7)) * 190 * s; crown.push([x + Math.cos(a) * rr, y - 360 * s + Math.sin(a) * rr * .82]); }
  colorIn(through([...crown, crown[0]], 3), { col: o.col || PAL.leaf, gap: 13, ang: -.7, w: 1.1, pale: .35, line: mixCol(o.col || PAL.leaf, PAL.ink, .55), shade: { pts: ellPts(x + 50 * s, y - 300 * s, 120 * s, 90 * s, 18), col: PAL.sageDk } });
  for (let i = 0; i < 6; i++) { const a = hash(i + x) * TAU, q = hash(i * 3 + x) * 130 * s; dab(x + Math.cos(a) * q, y - 380 * s + Math.sin(a) * q * .7, 10 * s, PAL.sageDk, .7); }
}
// A little flower on a stem, nodding in the breeze.
function flower(x, y, s = 1, col = PAL.rose, t = T, o = {}) {
  boilSeed('flower' + Math.round(x) + ':' + Math.round(y));
  const sw = Math.sin(t * 1.6 + x * .01) * 6 * s, hx = x + sw, hy = y - 60 * s;
  crayonLine([[x, y], [x + sw * .4, y - 30 * s], [hx, hy]], .55, PAL.sageDk, .5);
  for (let i = 0; i < 5; i++) { const a = i / 5 * TAU + .3; paint(ellPts(hx + Math.cos(a) * 12 * s, hy + Math.sin(a) * 12 * s, 10 * s, 10 * s, 10), { wash: mixCol(col, PAL.paper, .15), ink: mixCol(col, PAL.ink, .5), sw: .55 * s, br: 'cpen' }); }
  paint(ellPts(hx, hy, 7 * s, 7 * s, 10), { wash: PAL.butter, ink: PAL.butterDk, sw: .5 * s, br: 'cpen' });
}
// A storybook cottage.
function house(x, y, s = 1, o = {}) {
  boilSeed('house' + Math.round(x));
  const w = 300 * s, h = 220 * s;
  colorIn(rectPts(x - w / 2, y - h, w, h, 2), { col: o.wall || PAL.peach, gap: 11, ang: 1.4, line: PAL.ink });
  colorIn([[x - w / 2 - 30 * s, y - h + 6], [x, y - h - 170 * s], [x + w / 2 + 30 * s, y - h + 6]], { col: o.roof || PAL.coral, gap: 10, ang: -.9, line: PAL.ink });
  colorIn(rrPts(x - 40 * s, y - 120 * s, 80 * s, 120 * s, 30 * s), { col: PAL.sky, gap: 8, ang: 1.5, line: PAL.ink });
  colorIn(rectPts(x + 60 * s, y - 180 * s, 60 * s, 60 * s), { col: PAL.butter, gap: 8, ang: .2, line: PAL.ink });
  pencilLine([[x + 90 * s, y - 180 * s], [x + 90 * s, y - 120 * s]], .7); pencilLine([[x + 60 * s, y - 150 * s], [x + 120 * s, y - 150 * s]], .7);
}

// ---------- props (draw them in a hand hook, or free in the scene) ----------
// Each takes a centre and a size r and draws around it, so a hand hook can call prop(0, 0, u * 1.2) directly.
function apple(x, y, r, o = {}) {
  const P = []; for (let i = 0; i < 24; i++) { const a = i / 24 * TAU, dent = .12 * Math.exp(-((a - 1.5 * Math.PI) ** 2) * 6); P.push([x + Math.cos(a) * r * 1.02, y + Math.sin(a) * r * (.95 - dent)]); }
  colorIn(P, { col: o.col || '#E8655E', gap: Math.max(4, r * .22), ang: .8, w: clamp(r / 40, .45, 1), line: '#8E3B3A', lw: clamp(r / 35, .4, 1), curv: .5 });
  paint(ellPts(x - r * .38, y - r * .3, r * .16, r * .24, 10, 0, -.5), { wash: '#FFE8DA', washOp: 200, ink: null });
  crayonLine([[x, y - r * .8], [x + r * .08, y - r * 1.25]], clamp(r / 50, .4, .9), PAL.cocoa, .4);
  colorIn([[x + r * .08, y - r * 1.05], [x + r * .5, y - r * 1.35], [x + r * .75, y - r * 1.1], [x + r * .35, y - r * .95]], { col: PAL.leaf, fill: 'flat', line: PAL.sageDk, lw: clamp(r / 50, .35, .8), curv: .5 });
}
function leafProp(x, y, r, rot = 0, col = PAL.leaf) {
  push(); translate(x, y); rotate(rot);
  colorIn([[-r, 0], [-r * .3, -r * .45], [r * .5, -r * .38], [r, 0], [r * .5, r * .38], [-r * .3, r * .45]], { col, gap: Math.max(4, r * .25), ang: .6, w: clamp(r / 40, .4, 1), curv: .6, lw: clamp(r / 40, .4, 1) });
  pencilLine([[-r * .95, 0], [r * .9, 0]], clamp(r / 50, .3, .8), mixCol(col, PAL.ink, .6));
  pop();
}
function starProp(x, y, r, col = PAL.butter, rot = 0) { colorIn(starPts(x, y, r, .5, 5, -Math.PI / 2 + rot), { col, gap: Math.max(4, r * .22), ang: .4, w: clamp(r / 40, .4, 1), lw: clamp(r / 40, .4, 1) }); }
function heartProp(x, y, r, col = PAL.rose) { colorIn(heartPts(x, y, r), { col, gap: Math.max(4, r * .22), ang: .7, w: clamp(r / 40, .4, 1), lw: clamp(r / 40, .4, 1) }); }
// A balloon on a string. (x, y) is the string's end (the hand); the balloon floats `len` above, swaying.
function balloon(x, y, r, len, col = PAL.rose, t = T) {
  const sw = Math.sin(t * 1.3) * r * .25, bx = x + sw, by = y - len;
  pencilLine([[x, y], [x + sw * .3, y - len * .4], [bx - sw * .2, y - len * .75], [bx, by + r * 1.05]], .6, PAL.inkSoft, .5);
  colorIn(ellPts(bx, by, r * .9, r, 24), { col, gap: Math.max(5, r * .2), ang: .5, curv: .5 });
  paint(ellPts(bx - r * .35, by - r * .35, r * .14, r * .22, 10, 0, -.5), { wash: PAL.cream, washOp: 220, ink: null });
  paint([[bx - r * .12, by + r * .98], [bx + r * .12, by + r * .98], [bx, by + r * 1.12]], { wash: col, ink: mixCol(col, PAL.ink, .6), sw: .5 });
}

// ---------- emotes: drawn marks that pop in by a head (never typed letters) ----------
// emote(kind, x, y, s, k = pop 0..1, age = seconds since it appeared). kinds: '!', '?', 'heart', 'hearts', 'sweat',
// 'spark', 'zzz', 'bulb', 'music', 'anger', 'cloud', 'tears', 'dots', 'swirl'
function emote(kind, x, y, s, k = 1, age = T) {
  if (k <= .01 || !kind) return;
  const p = backOut(k); push(); translate(x, y); scale(p);
  const lw = clamp(s / 22, .5, 1.3);
  switch (kind) {
    case '!': colorIn([[-s * .22, -s * 1.6], [s * .22, -s * 1.6], [s * .1, -s * .4], [-s * .1, -s * .4]], { col: PAL.coral, fill: 'flat', lw }); dab(0, -s * .05, s * .18, PAL.coral, lw); break;
    case '?': crayonLine([[-s * .4, -s * 1.1], [-s * .2, -s * 1.5], [s * .3, -s * 1.45], [s * .35, -s * 1], [0, -s * .75], [0, -s * .45]], lw * 1.1, PAL.skyDk, .5); dab(0, -s * .05, s * .16, PAL.skyDk, lw); break;
    case 'heart': heartProp(0, -s * .8, s * .7, PAL.rose); break;
    case 'hearts': for (let i = 0; i < 3; i++) { const a = (age * .8 + i / 3) % 1; heartProp(Math.sin(a * 6 + i) * s * .4 + (i - 1) * s * .5, -s * (.4 + a * 1.8), s * .38 * (1 - a * .5), PAL.rose); } break;
    case 'sweat': colorIn([[0, -s * 1.4], [s * .38, -s * .6], [0, -s * .3], [-s * .38, -s * .6]], { col: PAL.sky, fill: 'flat', lw, curv: .7 }); break;
    case 'spark': for (let i = 0; i < 3; i++) { const q = .7 + .3 * Math.sin(age * 8 + i * 2); starProp((i - 1) * s * .7, -s * (.6 + (i % 2) * .6), s * .35 * q, PAL.butter); } break;
    case 'zzz': for (let i = 0; i < 3; i++) { const a = (age * .5 + i / 3) % 1, z = s * (.3 + .25 * a), zx = s * (.2 + a * .9), zy = -s * (.3 + a * 1.6);
      crayonLine([[zx - z, zy - z], [zx + z, zy - z], [zx - z, zy + z], [zx + z, zy + z]], lw * .8, mixCol(PAL.lilacDk, PAL.paper, a * .6), 0); } break;
    case 'bulb': glow(0, -s * 1.2, s * 1.6, '#FFE3A0', .8); colorIn(ellPts(0, -s * 1.3, s * .5, s * .55, 18), { col: PAL.butter, fill: 'flat', lw }); colorIn(rectPts(-s * .22, -s * .82, s * .44, s * .3), { col: PAL.inkSoft, fill: 'flat', lw: lw * .7 });
      for (let i = 0; i < 5; i++) { const a = -Math.PI / 2 + (i - 2) * .55; crayonLine([[Math.cos(a) * s * .75, -s * 1.3 + Math.sin(a) * s * .75], [Math.cos(a) * s * 1.05, -s * 1.3 + Math.sin(a) * s * 1.05]], lw * .7, PAL.butterDk, 0); } break;
    case 'music': for (let i = 0; i < 2; i++) { const a = (age * .6 + i / 2) % 1, nx = (i - .5) * s * .9 + Math.sin(a * 5) * s * .2, ny = -s * (.5 + a * 1.3);
      paint(ellPts(nx, ny, s * .2, s * .15, 10, 0, -.4), { wash: PAL.lilacDk, ink: null }); crayonLine([[nx + s * .18, ny], [nx + s * .18, ny - s * .6], [nx + s * .4, ny - s * .45]], lw * .7, PAL.lilacDk, 0); } break;
    case 'anger': for (let q = 0; q < 4; q++) { const a = q * Math.PI / 2 + .78; crayonLine([[Math.cos(a) * s * .2, -s + Math.sin(a) * s * .2], [Math.cos(a) * s * .55 + Math.cos(a + 1.57) * s * .15, -s + Math.sin(a) * s * .55 + Math.sin(a + 1.57) * s * .15]], lw * .9, PAL.coral, .3); } break;
    case 'cloud': cloud(0, -s * 1.3, s * .0055, { key: 'emo', col: PAL.skyLt, base: '#DDE6EE', line: PAL.inkSoft }); for (let i = 0; i < 4; i++) { const a = (age * 1.4 + i / 4) % 1; crayonLine([[(i - 1.5) * s * .3, -s * (1 - a * .8)], [(i - 1.5) * s * .3 - s * .05, -s * (.8 - a * .8)]], lw * .6, PAL.skyDk, 0); } break;
    case 'dots': for (let i = 0; i < 3; i++) if ((age * 3) % 3 >= i) dab((i - 1) * s * .5, -s * .8, s * .12, PAL.inkSoft, lw); break;
    case 'swirl': { const P = []; for (let a = 0; a < TAU * 2; a += .4) P.push([Math.cos(a + age * 6) * s * .1 * a, -s + Math.sin(a + age * 6) * s * .1 * a]); crayonLine(P, lw * .8, PAL.lilacDk, .5); } break;
  }
  pop();
}

// ---------- captions: storybook text ----------
// captions([[t0, t1, 'text', { pos: 'bottom' | 'top', size, box }], …]) registers the lines and the overlay hook.
// The text is hand-lettered (a warm kai / rounded font with a slightly uneven baseline), writes itself on character by
// character, sits on a soft torn-paper label (box: false to put it straight on the picture), and is broken a little by
// the paper tooth like the rest of the drawing. Sized for phones: default 74 px (≈ 15 px on a 390 px-wide screen).
const CAPTION_FONT = HAND_FONT;
let CAPTIONS = [], capC = null;
function captions(list) {
  CAPTIONS = list;
  window.EXTRA_FONTS = [...(window.EXTRA_FONTS || []), [`700 74px ${CAPTION_FONT}`, list.map(l => l[2]).join('')]];
  window.overlayHook = (c, t) => { for (const L of CAPTIONS) if (t >= L[0] - .01 && t < L[1] + .4) storyCaption(c, L, t); };
}
function storyCaption(c, [a, b, txt, o = {}], t) {
  const size = o.size || 74, chars = [...txt], rate = o.rate || 16, age = t - a;
  const alpha = seg(age, 0, .15) * (1 - seg(t, b, b + .4));
  if (alpha <= 0) return;
  if (!capC) { capC = document.createElement('canvas'); capC.width = W; capC.height = 300; }
  const k = capC.getContext('2d'); k.setTransform(1, 0, 0, 1, 0, 0); k.clearRect(0, 0, W, 300);
  k.font = `700 ${size}px ${CAPTION_FONT}`; k.textBaseline = 'middle';
  const ws = chars.map(ch => k.measureText(ch).width), total = ws.reduce((s, v) => s + v, 0) + (chars.length - 1) * size * .04;
  const cy = 150, bn = Math.floor(t * BOIL + 1e-6);
  // label: a torn cream paper strip with a pencil edge
  if (o.box !== false) {
    const bw = total + size * 1.3, bh = size * 1.55, x0 = W / 2 - bw / 2, y0 = cy - bh / 2, j = n => (hash(n * 13.1 + 5) - .5) * size * .1;
    k.beginPath(); const N = 14;
    for (let i = 0; i <= N; i++) k.lineTo(x0 + bw * i / N, y0 + j(i));
    for (let i = 1; i <= 4; i++) k.lineTo(x0 + bw + j(40 + i), y0 + bh * i / 4);
    for (let i = N - 1; i >= 0; i--) k.lineTo(x0 + bw * i / N, y0 + bh + j(20 + i));
    for (let i = 3; i >= 1; i--) k.lineTo(x0 + j(60 + i), y0 + bh * i / 4);
    k.closePath(); k.fillStyle = 'rgba(255,250,236,.93)'; k.fill();
    k.strokeStyle = 'rgba(74,54,49,.35)'; k.lineWidth = 2.2; k.stroke();
  }
  // the letters, written on one by one, each a little off the line like hand lettering
  let x = W / 2 - total / 2;
  chars.forEach((ch, i) => {
    const ka = seg(age * rate, i, i + 2.2); if (ka <= 0) { x += ws[i] + size * .04; return; }
    const r = (hash(i * 7.3 + txt.length) - .5) * .09, dy = (hash(i * 3.1 + 2) - .5) * size * .07 + (1 - easeOut(ka)) * size * .25;
    k.save(); k.translate(x + ws[i] / 2, cy + dy); k.rotate(r); k.globalAlpha = easeOut(ka);
    k.lineJoin = 'round'; k.lineWidth = size * .16; k.strokeStyle = 'rgba(255,249,234,.95)'; k.textAlign = 'center';
    k.strokeText(ch, 0, 0); k.fillStyle = o.col || PAL.ink; k.fillText(ch, 0, 0); k.restore();
    x += ws[i] + size * .04;
  });
  // crayon-ish: the paper tooth nibbles the letters a little
  k.globalCompositeOperation = 'destination-out'; k.globalAlpha = .45;
  k.drawImage(toothC, -Math.floor(hash(bn * 3.7 + 1) * TOOTH_PAD), -Math.floor(hash(bn * 5.3 + 2) * TOOTH_PAD));
  k.globalCompositeOperation = 'source-over'; k.globalAlpha = 1;
  const y = o.pos === 'top' ? 150 : o.y ?? H - 140;
  c.save(); c.globalAlpha = alpha; c.drawImage(capC, 0, y - 150); c.restore();
}
