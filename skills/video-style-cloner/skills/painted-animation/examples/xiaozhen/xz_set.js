// xz_set.js: the one world of 小镇姑娘, a small-town railway station, in three lights (dusk now, the sepia
// memory, night now), plus the cast and props every shot shares. Shots live in xz_shots.js.

const RAIL = 790;            // the rail line: trains stand on it, behind the platform
const PLAT = 765;            // the platform's back edge (it hides the bottom of the wheels)
const LOOK = {
  dusk:  { sky: '#8C6CA8', sky2: '#E9A08C', glow: '#F6C58A', far: '#7A6394', near: '#5B5A86', house: '#6A557E', roof: '#A8574A', win: '#F6C86A', winOn: .6,
           top: '#9E8F95', face: '#6C5E6E', edge: '#E8C46A', ballast: '#5A4A5C', rail: '#2B2233', train: '#2F7470', trainDk: '#1E4A4A', trim: '#E8AA38', stars: 0 },
  sepia: { sky: '#EFDDB6', sky2: '#F7E9C8', glow: '#FFF3D6', far: '#D6BF97', near: '#C2A57C', house: '#B39670', roof: '#93674A', win: '#E7D2A8', winOn: 0,
           top: '#D5C29E', face: '#AE9572', edge: '#E9D9B2', ballast: '#9C8262', rail: '#5E4838', train: '#8E5E48', trainDk: '#5E3C2E', trim: '#D6B36E', stars: 0, sepia: true },
  night: { sky: '#1F2550', sky2: '#2F3C7A', glow: '#3E4C8C', far: '#2C3468', near: '#232A57', house: '#2E2C58', roof: '#553252', win: '#F2B84E', winOn: 1,
           top: '#4B4A6C', face: '#33314F', edge: '#C9A64E', ballast: '#27253C', rail: '#15131F', train: '#2F7470', trainDk: '#1E4A4A', trim: '#E8AA38', stars: 1 },
};
const SEP = '#B99468';
const ME = { col: PAL.clay, dk: PAL.clayDk, lt: '#F5B394' };
const HER = { col: '#EE9AAE', dk: '#C0637B', lt: '#FBD0DA' };
const sepiaOf = c => ({ col: mixCol(c.col, SEP, .38), dk: mixCol(c.dk, SEP, .38), lt: mixCol(c.lt, SEP, .38) });

// ---------- characters ----------
// Me (Clawd) and her (a rosy Clawd with a flower on her head; the flower is how you know her in every form).
// Mood colour tints are dropped in favour of each character's own colours, which stay on model.
function me(x, y, u, o = {}, L = LOOK.dusk) { clawd(x, y, u, { ...o, ...(L.sepia ? sepiaOf(ME) : ME), tint: null }); }
function her(x, y, u, o = {}, L = LOOK.dusk) {
  const tie = o.tie;
  clawd(x, y, u, { ...o, ...(L.sepia ? sepiaOf(HER) : HER), tint: null, hat: 'flower', draw: tie ? (uu, sw) => { necktie(uu, sw); o.draw && o.draw(uu, sw); } : o.draw });
}
function necktie(u, sw) {   // body-local, front view: a white collar and a navy tie
  paint([[-1.6 * u, -3.9 * u], [0, -3.1 * u], [-.5 * u, -2.4 * u]], { wash: PAL.cream, ink: PAL.ink, sw: sw * .5 });
  paint([[1.6 * u, -3.9 * u], [0, -3.1 * u], [.5 * u, -2.4 * u]], { wash: PAL.cream, ink: PAL.ink, sw: sw * .5 });
  paint([[-.35 * u, -3.4 * u], [.35 * u, -3.4 * u], [.45 * u, -2.3 * u], [0, -1.8 * u], [-.45 * u, -2.3 * u]], { wash: '#34488A', ink: PAL.ink, sw: sw * .55 });
  paint(ellPts(0, -3.35 * u, .32 * u, .26 * u, 8), { wash: '#34488A', ink: PAL.ink, sw: sw * .5 });
}
// Suitcase, standing on (x, y) = bottom centre. s ≈ the owner's u.
function suitcase(x, y, s, L = LOOK.dusk) {
  const col = L.sepia ? '#9A7250' : '#8B5A3C';
  inkLine([[x - 1 * s, y - 3.1 * s], [x - .8 * s, y - 3.9 * s], [x + .8 * s, y - 3.9 * s], [x + 1 * s, y - 3.1 * s]], s * .09, PAL.ink, 'ink', .4);
  paint(rrPts(x - 2.4 * s, y - 3.2 * s, 4.8 * s, 3.2 * s, .45 * s, s * .05), { wash: col, fill: mixCol(col, PAL.ink, .3), fillOp: 60, tex: .5, ink: PAL.ink, sw: clamp(s / 22, .5, 1.3) });
  for (const k of [-1, 1]) paint(rectPts(x + k * 1.3 * s - .25 * s, y - 3.2 * s, .5 * s, 3.2 * s), { wash: mixCol(col, PAL.cream, .35), ink: null });
  paint(ellPts(x + 1.6 * s, y - 2.3 * s, .35 * s, .3 * s, 10), { wash: PAL.ochre, ink: PAL.ink, sw: .5 });
}

// ---------- the world ----------
function skyBg(L, t) {
  boilSeed('sky');
  paint(rectPts(-900, -1600, W + 1800, 3200), { wash: L.sky, ink: null });
  paint(ellPts(W / 2, 760, 1500, 380, 30, 10), { fill: L.sky2, fillOp: 150, bleed: .3, tex: .5, ink: null });
  paint(ellPts(W * .62, 660, 700, 140, 24, 8), { fill: L.glow, fillOp: 90, bleed: .3, tex: .4, ink: null });
  if (L.stars) for (let i = 0; i < 60; i++) {
    boilSeed('st' + i);
    const x = hash(i) * (W + 1200) - 600, y = hash(i + 50) * 1900 - 1300, tw = .55 + .45 * Math.sin(t * (1.5 + 2 * hash(i + 9)) + i);
    paint(starPts(x, y, (3 + 5 * hash(i + 3)) * tw, .35, 4), { wash: PAL.cream, washOp: 130 + 110 * tw, ink: null });
  }
  for (let i = 0; i < 3; i++) {   // soft drifting clouds
    boilSeed('cl' + i);
    const x = ((hash(i + 20) * 2400 + t * (8 + 6 * i)) % 2800) - 450, y = 180 + i * 150 - (L.stars ? 400 : 0);
    paint(lumpy(x, y, 200 + 60 * i, 46, 20 + i), { fill: mixCol(L.sky2, PAL.cream, L.stars ? .1 : .35), fillOp: 110, bleed: .25, tex: .5, ink: null });
  }
}
function lumpy(cx, cy, rx, ry, seed, n = 22) {   // cloud / smoke outline: one shape, wobbly edge
  const p = []; for (let k = 0; k < n; k++) { const a = k / n * TAU, w = 1 + .13 * Math.sin(a * 5 + seed) + .07 * Math.sin(a * 9 + seed * 2); p.push([cx + Math.cos(a) * rx * w, cy + Math.sin(a) * ry * w]); }
  return p;
}
function townBg(L, t) {
  boilSeed('hillfar');
  paint(ellPts(500, 820, 1100, 250, 36, 3), { wash: L.far, fill: mixCol(L.far, L.sky, .3), fillOp: 80, tex: .5, ink: PAL.ink, sw: .6 });
  paint(ellPts(1650, 830, 1000, 200, 36, 3), { wash: L.far, fill: mixCol(L.far, L.sky, .3), fillOp: 80, tex: .5, ink: PAL.ink, sw: .6 });
  for (let i = 0; i < 9; i++) {   // the little town on the hill line
    boilSeed('house' + i);
    const x = -250 + i * 290 + 60 * hash(i), w = 110 + 50 * hash(i + 4), h = 80 + 60 * hash(i + 8), y = 700 + 30 * hash(i + 2);
    paint(rectPts(x, y - h, w, h, 1.5), { wash: L.house, ink: PAL.ink, sw: .6 });
    paint([[x - 14, y - h], [x + w / 2, y - h - 55 - 20 * hash(i)], [x + w + 14, y - h]], { wash: L.roof, ink: PAL.ink, sw: .6 });
    const lit = L.winOn > 0 && hash(i + 31) < .75;
    paint(rectPts(x + w * .35, y - h * .7, w * .3, h * .3), { wash: lit ? L.win : mixCol(L.house, PAL.ink, .3), ink: null });
    if (lit && L.stars) glow(x + w * .5, y - h * .55, 50, '#FFC766', .35);
  }
  boilSeed('hillnear');
  paint(ellPts(W / 2, 900, 1600, 170, 40, 3), { wash: L.near, fill: mixCol(L.near, PAL.ink, .2), fillOp: 70, tex: .5, ink: PAL.ink, sw: .7 });
}
function trackBed(L) {
  boilSeed('track');
  paint(rectPts(-900, RAIL - 30, W + 1800, 70), { wash: L.ballast, ink: null });
  inkLine([[-900, RAIL - 4], [W / 2, RAIL - 5], [W + 900, RAIL - 4]], 1.6, L.rail, 'ink', 0);
}
// The platform: a lit top surface from the back edge (PLAT) to the front edge, then the front face.
function platform(L) {
  boilSeed('plat');
  paint([[-900, PLAT], [W + 900, PLAT], [W + 900, 975], [-900, 975]], { wash: L.top, fill: mixCol(L.top, PAL.ink, .25), fillOp: 50, tex: .6, bleed: .03, ink: PAL.ink, sw: 1 });
  paint([[-900, PLAT + 6], [W + 900, PLAT + 6], [W + 900, PLAT + 20], [-900, PLAT + 20]], { wash: L.edge, washOp: 230, ink: null });
  for (let i = -3; i < 14; i++) inkLine([[i * 190, PLAT + 22], [i * 190 - 60, 975]], .6, mixCol(L.top, PAL.ink, .45), 'inkfine', 0);
  paint([[-900, 975], [W + 900, 975], [W + 900, 1500], [-900, 1500]], { wash: L.face, fill: mixCol(L.face, PAL.ink, .3), fillOp: 60, tex: .6, ink: PAL.ink, sw: 1 });
}
function lampPost(x, L, on = 1) {
  boilSeed('lamp' + x);
  const top = 430, col = mixCol(L.rail, L.face, .3);
  paint(rectPts(x - 9, top, 18, 930 - top), { wash: col, ink: PAL.ink, sw: .8 });
  paint(rectPts(x - 24, 918, 48, 16), { wash: col, ink: PAL.ink, sw: .8 });
  inkLine([[x, top + 20], [x + 40, top - 10], [x + 70, top + 10]], 3, col, 'ink', .6);
  paint([[x + 48, top + 8], [x + 92, top + 8], [x + 84, top + 60], [x + 56, top + 60]], { wash: on ? '#FFE3A0' : mixCol(L.face, PAL.cream, .3), ink: PAL.ink, sw: .8 });
  paint([[x + 44, top + 2], [x + 96, top + 2], [x + 70, top - 18]], { wash: col, ink: PAL.ink, sw: .8 });
  if (on) glow(x + 70, top + 36, 170 * on, '#FFC766', .9 * on);
}
function bench(x, y, L) {
  boilSeed('bench' + x);
  const wood = L.sepia ? '#A07A52' : '#8A5E48';
  paint(rectPts(x - 170, y - 150, 340, 26, 1.5), { wash: wood, ink: PAL.ink, sw: .8 });
  paint(rectPts(x - 170, y - 110, 340, 26, 1.5), { wash: wood, ink: PAL.ink, sw: .8 });
  paint(rectPts(x - 180, y - 62, 360, 22, 1.5), { wash: mixCol(wood, PAL.cream, .15), ink: PAL.ink, sw: .8 });
  for (const k of [-1, 1]) paint(rectPts(x + k * 140 - 8, y - 150, 16, 150), { wash: mixCol(wood, PAL.ink, .4), ink: PAL.ink, sw: .7 });
}

// ---------- the train ----------
// A little steam train, side view, heading right. xF = the front of the locomotive; the carriage hangs behind it.
// dist = distance travelled (px) for the wheels. o.door 0..1 opens the carriage door; o.window(x, y, w, h) paints a
// window's contents (a face) before its frame; o.lit lights the windows.
const TRAIN = { chimney: -160, door: -1250 };   // chimney top and carriage door centre, relative to xF
function train(xF, L, dist = 0, o = {}) {
  boilSeed('train');
  const C = L.train, D = L.trainDk, y = RAIL;
  const wheel = (cx, r) => {
    paint(ellPts(cx, y - r, r, r, 20, 1), { wash: mixCol(D, PAL.ink, .4), ink: PAL.ink, sw: .9 });
    const a = dist / r;
    for (let k = 0; k < 3; k++) { const q = a + k * Math.PI / 3; inkLine([[cx - Math.cos(q) * r * .85, y - r - Math.sin(q) * r * .85], [cx + Math.cos(q) * r * .85, y - r + Math.sin(q) * r * .85]], .8, L.trim, 'inkfine', 0); }
    paint(ellPts(cx, y - r, r * .2, r * .2, 10), { wash: L.trim, ink: null });
  };
  // carriage: from xF-1680 to xF-680
  const c0 = xF - 1680, c1 = xF - 690;
  paint(rrPts(c0, y - 360, c1 - c0, 280, 26, 2), { wash: C, fill: D, fillOp: 60, tex: .5, ink: PAL.ink, sw: 1.2 });
  paint([[c0 - 10, y - 360], [c1 + 10, y - 360], [c1 - 10, y - 395], [c0 + 10, y - 395]], { wash: D, ink: PAL.ink, sw: 1 });
  paint(rectPts(c0, y - 150, c1 - c0, 18), { wash: L.trim, washOp: 220, ink: null });
  for (let i = 0; i < 5; i++) {
    const wx = c0 + 40 + i * 115 + (i > 1 ? 330 : 0), wy = y - 320, ww = 90, wh = 110;
    paint(rrPts(wx, wy, ww, wh, 12), { wash: o.lit ? '#FFE3A0' : mixCol(L.sky2, PAL.cream, .4), fill: o.lit ? L.trim : L.sky, fillOp: 60, ink: PAL.ink, sw: .9 });
    if (o.window) o.window(wx, wy, ww, wh, i);
    inkLine([[wx + 18, wy + 70], [wx + 50, wy + 22]], .7, PAL.cream, 'inkfine', 0);
  }
  const dx = xF + TRAIN.door, dw = 170, open = clamp(o.door || 0);
  paint(rectPts(dx - dw / 2, y - 340, dw, 240), { wash: mixCol(D, PAL.ink, .5), ink: null });     // the dark doorway
  if (o.inDoor) {
    // whoever stands in the doorway is drawn here, then the wall beside the door is painted back over them, so
    // nothing of them shows outside the doorway, and last the sliding door closes over them
    o.inDoor(dx, y - 100);
    boilSeed('jamb');
    for (const s of [-1, 1]) {
      const x0 = s < 0 ? dx - dw / 2 - 70 : dx + dw / 2, jw = 70;
      paint(rectPts(x0, y - 358, jw, 276), { wash: C, fill: D, fillOp: 60, tex: .5, ink: null });
      paint(rectPts(x0, y - 150, jw, 18), { wash: L.trim, washOp: 220, ink: null });
    }
    inkLine([[dx - dw / 2 - 70, y - 81], [dx + dw / 2 + 70, y - 81]], 1.2, PAL.ink, 'ink', 0);
  }
  paint(rectPts(dx - dw / 2 + dw * open * .92, y - 340, dw * (1 - open * .92), 240), { wash: mixCol(C, D, .3), ink: PAL.ink, sw: 1 });   // the sliding door
  paint(rectPts(dx - dw / 2, y - 340, dw, 240), { ink: PAL.ink, sw: 1.1 });
  for (const wx of [c0 + 170, c1 - 170]) { wheel(wx - 50, 42); wheel(wx + 50, 42); }
  paint(rectPts(c1 - 10, y - 150, 60, 16), { wash: PAL.ink, ink: null });   // coupling
  // locomotive
  const L0 = xF - 660;
  paint(rectPts(L0, y - 130, 620, 34), { wash: D, ink: PAL.ink, sw: 1 });
  paint(rrPts(xF - 520, y - 310, 420, 180, 70, 2), { wash: C, fill: D, fillOp: 70, tex: .5, ink: PAL.ink, sw: 1.2 });
  for (const bx of [-440, -330, -220]) inkLine([[xF + bx, y - 305], [xF + bx, y - 133]], .8, L.trim, 'inkfine', 0);
  paint(rrPts(xF - 130, y - 300, 70, 170, 20), { wash: D, ink: PAL.ink, sw: 1 });
  paint(ellPts(xF - 70, y - 270, 22, 22, 14), { wash: o.lit ? '#FFE3A0' : L.trim, ink: PAL.ink, sw: .9 });
  if (o.lit) glow(xF - 50, y - 270, 160, '#FFD27A', .8);
  paint([[xF + TRAIN.chimney - 28, y - 310], [xF + TRAIN.chimney + 28, y - 310], [xF + TRAIN.chimney + 20, y - 400], [xF + TRAIN.chimney + 40, y - 430], [xF + TRAIN.chimney - 40, y - 430], [xF + TRAIN.chimney - 20, y - 400]], { wash: D, ink: PAL.ink, sw: 1 });
  paint(ellPts(xF - 330, y - 318, 44, 32, 14), { wash: L.trim, ink: PAL.ink, sw: .9 });
  paint(rrPts(L0, y - 430, 190, 300, 14), { wash: C, fill: D, fillOp: 60, tex: .5, ink: PAL.ink, sw: 1.2 });
  paint(rectPts(L0 - 12, y - 450, 214, 26), { wash: D, ink: PAL.ink, sw: 1 });
  paint(rrPts(L0 + 40, y - 395, 100, 90, 10), { wash: o.lit ? '#FFE3A0' : mixCol(L.sky2, PAL.cream, .4), ink: PAL.ink, sw: .9 });
  paint([[xF - 60, y - 96], [xF + 10, y - 96], [xF + 40, y - 8], [xF - 60, y - 8]], { wash: D, ink: PAL.ink, sw: 1 });
  wheel(xF - 460, 72); wheel(xF - 290, 72); wheel(xF - 130, 42);
  inkLine([[xF - 460 + Math.cos(dist / 72) * 40, y - 72 + Math.sin(dist / 72) * 40], [xF - 290 + Math.cos(dist / 72) * 40, y - 72 + Math.sin(dist / 72) * 40]], 2.2, L.trim, 'ink', 0);
}
// Steam: a puff leaves the chimney on every beat while `on(te)`; it drifts up and back and swells as it ages.
// chimAt(te) = [x, y] of the chimney top at emission time te. Pure in t: each puff is recomputed from its own clock.
function steam(t, chimAt, L, o = {}) {
  const life = o.life ?? 3.2, b1 = beatN(t), each = o.each ?? .5, grow = o.grow ?? 1;
  for (let k = Math.floor((b1 - life / BEAT) / each) * each; k <= b1 + 1e-6; k += each) {
    const te = OFF + k * BEAT, age = t - te;
    if (age < 0 || age > life || (o.on && !o.on(te))) continue;
    const [cx, cy] = chimAt(te), q = age / life, r = (40 + 190 * easeOut(q)) * grow * (.85 + .3 * hash(k * 3.1));
    const x = cx - age * (o.wind ?? 70) + 30 * Math.sin(age * 2 + k), y = cy - 50 - age * 120 * (1 - q * .4);
    boilSeed('puff' + k);
    const col = L.sepia ? '#F4E8D0' : L.stars ? '#C9C6DA' : '#EDE3E6';
    paint(lumpy(x, y, r, r * .8, k * 1.7), { wash: col, washOp: 255 * (1 - easeIn(q)), fill: mixCol(col, L.far, .5), fillOp: 90 * (1 - q), tex: .5, bleed: .1, ink: q < .7 ? PAL.ink : null, sw: .8 });
  }
}

// ---------- her other forms: the koi, the star ----------
// The koi (锦鲤): gold with red patches, her flower on its head, and (optionally) her tie. (x, y) = body centre,
// s = half its length, ang = heading. t drives the swim wave.
function koi(x, y, s, ang, t, o = {}) {
  boilSeed(o.key || 'koi');
  push(); translate(x, y); rotate(ang); if (Math.cos(ang) < 0) scale(1, -1);
  const wave = k => Math.sin(t * 9 - k * 3) * s * .09 * k;          // tail swings more than the head
  const spine = []; for (let i = 0; i <= 10; i++) { const k = i / 10; spine.push([s * (1 - 2 * k), wave(k)]); }
  const wid = k => s * .36 * Math.pow(Math.sin(Math.PI * Math.min(1, k * .92 + .08)), .7) * (1 - .45 * k);
  const top = [], bot = [];
  for (let i = 0; i <= 10; i++) { const k = i / 10; top.push([spine[i][0], spine[i][1] - wid(k)]); bot.push([spine[i][0], spine[i][1] + wid(k)]); }
  const tb = spine[10], tw = Math.sin(t * 9 - 3.4) * .5;
  // tail fan and fins behind the body
  paint(through([[tb[0] + s * .05, tb[1]], [tb[0] - s * .45, tb[1] - s * .42 + tw * s * .2], [tb[0] - s * .32, tb[1] + tw * s * .1], [tb[0] - s * .45, tb[1] + s * .42 + tw * s * .2], [tb[0] + s * .05, tb[1] + 2]]), { wash: '#F2A23A', fill: '#D9463B', fillOp: 110, tex: .6, ink: PAL.ink, sw: clamp(s / 120, .5, 1.3) });
  paint(ellPts(s * .15, s * .33, s * .2, s * .09, 12, 0, .6 + .3 * Math.sin(t * 7)), { wash: '#F6C25A', fill: '#D9463B', fillOp: 70, ink: PAL.ink, sw: clamp(s / 150, .4, 1) });
  // body
  const body = top.concat(bot.reverse());
  paint(body, { wash: '#F4B63A', fill: '#FFE08A', fillOp: 110, tex: .6, bleed: .1, ink: null, curv: .5 });
  for (const [k, r, dy] of [[.3, .17, -.1], [.55, .13, .08], [.75, .09, -.05]]) {   // red patches along the back
    const p = spine[Math.round(k * 10)]; paint(ellPts(p[0], p[1] + dy * s, s * r * 1.3, s * r * .8, 12, s * .01), { wash: '#D9463B', washOp: 230, ink: null });
  }
  paint(body, { ink: PAL.ink, sw: clamp(s / 110, .6, 1.6), curv: .5 });
  for (let i = 3; i < 9; i++) { const p = spine[i]; inkLine([[p[0] + s * .04, p[1] - wid(i / 10) * .5], [p[0] - s * .04, p[1]], [p[0] + s * .04, p[1] + wid(i / 10) * .5]], .5, mixCol('#F4B63A', PAL.ink, .5), 'inkfine', .5); }   // scales
  // face: eye, smile, whiskers
  const hx = s * .72;
  paint(ellPts(hx, -s * .08, s * .065, s * .075, 10), { wash: PAL.ink, ink: null });
  paint(ellPts(hx + s * .02, -s * .1, s * .02, s * .02, 6), { wash: PAL.cream, ink: null });
  inkLine([[s * .9, s * .07], [s * .95, s * .1], [s * .99, s * .06]], clamp(s / 150, .5, 1.2), PAL.ink, 'ink', .6);
  inkLine([[s * .96, s * .12], [s * 1.08, s * .22 + Math.sin(t * 5) * s * .03], [s * 1.15, s * .2]], .7, PAL.ink, 'inkfine', .6);
  paint(ellPts(hx - s * .1, s * .08, s * .06, s * .03, 8), { fill: PAL.rose, fillOp: 150, ink: null });
  if (o.tie) {   // collar and tie under the chin
    const tx = s * .5;
    paint([[tx - s * .06, s * .2], [tx + s * .06, s * .2], [tx + s * .08, s * .42], [tx, s * .5], [tx - s * .08, s * .42]], { wash: '#34488A', ink: PAL.ink, sw: .8 });
  }
  flower(s * .55, -s * .33, s * .13);
  pop();
}
function flower(x, y, r) {   // her flower: five petals around an ochre centre (matches the 'flower' hat)
  for (let i = 0; i < 5; i++) { const a = i / 5 * TAU - Math.PI / 2; paint(ellPts(x + Math.cos(a) * r * .75, y + Math.sin(a) * r * .75, r * .55, r * .55, 10), { wash: '#F7F0E6', ink: PAL.ink, sw: clamp(r / 30, .35, .8) }); }
  paint(ellPts(x, y, r * .45, r * .45, 10), { wash: PAL.ochre, ink: PAL.ink, sw: clamp(r / 30, .35, .8) });
}
// Her star: a warm five-point star with a little face and her flower. k = brightness 0..1, smile 0..1, wink 0..1.
function starHer(x, y, r, t, o = {}) {
  boilSeed(o.key || 'starher');
  const k = o.k ?? 1, tw = 1 + .05 * Math.sin(t * 7);
  glow(x, y, r * (2.2 + 1.6 * k) * tw, '#FFD96A', .5 + .5 * k);
  push(); translate(x, y); rotate(o.rot || .06 * Math.sin(t * 1.3));
  paint(starPts(0, 0, r * tw, .5, 5), { wash: '#FFE27A', fill: PAL.cream, fillOp: 90, ink: PAL.ink, sw: clamp(r / 45, .5, 1.3) });
  const e = r * .15, sm = o.smile ?? 1, wink = o.wink || 0;
  if (o.face !== false) {
    for (const s of [-1, 1]) {
      if (s > 0 && wink > .5) inkLine([[s * e * 1.9 - e * .6, -e * .1], [s * e * 1.9, -e * .5], [s * e * 1.9 + e * .6, -e * .1]], clamp(r / 60, .4, 1), PAL.ink, 'ink', .6);
      else paint(ellPts(s * e * 1.9, -e * .3, e * .42, e * .56 * (sm > .5 ? .8 : 1), 10), { wash: PAL.ink, ink: null });
    }
    inkLine([[-e * 1.1, e * 1], [0, e * (1 + .8 * sm)], [e * 1.1, e * 1]], clamp(r / 60, .4, 1), PAL.ink, 'ink', .6);
    for (const s of [-1, 1]) paint(ellPts(s * e * 3, e * 1.1, e * .6, e * .3, 10), { fill: PAL.rose, fillOp: 160, ink: null });
  }
  flower(-r * .42, -r * .5, r * .2);
  pop();
}

// ---------- full-frame devices (screen space) ----------
// Theatre curtains: k = 0 open (off the sides) → 1 closed at the centre.
function curtains(k, t) {
  boilSeed('curtain');
  const red = '#A3283A', dk = '#6E1726', w = W / 2 + 80, off = (1 - ease(k)) * (w + 40);
  for (const s of [-1, 1]) {
    const x0 = s < 0 ? -80 - off : W / 2 + off, sway = Math.sin(t * 3) * 10 * (1 - k);
    const P = [[x0, -40], [x0 + w, -40], [x0 + w + (s < 0 ? sway : -sway), H + 40], [x0, H + 40]];
    paint(P, { wash: red, fill: dk, fillOp: 90, tex: .7, bleed: .05, ink: PAL.ink, sw: 1.2 });
    for (let i = 1; i < 7; i++) { const fx = x0 + i * w / 7; inkLine([[fx, -40], [fx + 6 * Math.sin(i + t), H / 2], [fx, H + 40]], 1.2, dk, 'dry', .5); }
  }
  if (k <= .01) return;
  const vy = -170 * (1 - ease(k * 2));   // the valance drops in first
  push(); translate(0, vy);
  paint([[-80, -40], [W + 80, -40], [W + 80, 110], [W * .75, 140], [W / 2, 110], [W * .25, 140], [-80, 110]], { wash: dk, fill: red, fillOp: 90, tex: .6, ink: PAL.ink, sw: 1.2, curv: .3 });
  inkLine([[-80, 100], [W / 2, 124], [W + 80, 100]], 2, '#E8AA38', 'ink', .5);
  pop();
}
// Darkness everywhere outside a circle, at opacity a (0..1): a spotlight.
function spotDark(cx, cy, r, a, col = '#1A1424') {
  if (a <= .01) return;
  const pts = ellPts(cx, cy, r, r * .92, 36), far = 4000;
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i], q = pts[(i + 1) % pts.length], o = pp => { const dx = pp[0] - cx, dy = pp[1] - cy, d = Math.hypot(dx, dy) || 1; return [cx + dx / d * far, cy + dy / d * far]; };
    const e = [(q[0] - p[0]) * .08, (q[1] - p[1]) * .08], p2 = [p[0] - e[0], p[1] - e[1]], q2 = [q[0] + e[0], q[1] + e[1]];
    paint([p2, q2, o(q2), o(p2)], { wash: col, washOp: 255 * a, ink: null });
  }
}
// Smoke wipe: billows swell up to cover the frame (p 0 → .5), then thin and drift off (p .5 → 1).
function smokeWipe(p) {
  if (p <= 0 || p >= 1) return;
  const col = '#E4DCD8';
  const cover = p < .5 ? easeOut(p * 2) : 1 - ease((p - .5) * 2);
  for (let i = 0; i < 14; i++) {
    boilSeed('sw' + i);
    const x = (i % 5) * 480 - 40 + 60 * hash(i), y = Math.floor(i / 5) * 420 + 60 * hash(i + 7) + (p > .5 ? -(p - .5) * 500 : 0);
    const r = (120 + 380 * cover) * (.8 + .4 * hash(i + 3)) * clamp(cover * 2.5 - i * .04 + .2);
    if (r < 10) continue;
    paint(lumpy(x, y, r, r * .85, i * 2.3), { wash: col, washOp: 255 * clamp(cover * 1.6), fill: mixCol(col, '#9C8EA8', .4), fillOp: 70, tex: .5, ink: cover < .85 ? PAL.ink : null, sw: .9 });
  }
}
// Old-film look for the memory: a sepia veil at the edges, a couple of flickering scratches, dust.
function filmFX(t) {
  boilSeed('film');
  const f = BOILN;
  for (let i = 0; i < 2; i++) if (hash(f * 3 + i) < .55) { const x = hash(f * 7 + i) * W; inkLine([[x, -20], [x + 8 * (hash(f + i) - .5), H / 2], [x + 4, H + 20]], .5, '#FFF3D6', 'inkfine', .3); }
  for (let i = 0; i < 5; i++) { const x = hash(f * 11 + i) * W, y = hash(f * 13 + i) * H; paint(ellPts(x, y, 3 + 4 * hash(i + f), 2 + 3 * hash(i), 6), { wash: '#5E4838', washOp: 160, ink: null }); }
  spotDark(W / 2, H / 2, 1150, .22, '#8A6A48');
}
