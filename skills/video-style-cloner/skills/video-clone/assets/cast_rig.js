// cast.js: the two original characters of this video, their props, and the shared flower motif.
//   阿旺 wang(): a teal egg with a towering ink pompadour, a red flower-print shirt band, noodle arms, two stubby legs.
//   小花 hua():  a peach-pink dumpling with a plum bob and one big red flower on her head (the motif).
// Both take the same option objects as clawd() (so feel() / emotions() / take() / jump() drive them), and reuse the
// kit's painted eyes(), mouth(), blush() and emote(). (x, y) is the ground point between the feet; u is the size unit.
// Front-view body space: eyes at (±2.5u, -6u), mouth near (0, -4.3u), body roughly -4.4u..4.4u wide.

const FLOWER = { petal: '#D8394E', petalLt: '#F07A7F', mid: '#F4B63A' };

// The motif: a five-petal red flower. k = bloom 0..1 (petals open), rot = spin, droop = 0..1 (petals sag).
function flowerHead(x, y, r, o = {}) {
  const k = o.k ?? 1, rot = o.rot || 0, sw = o.sw ?? clamp(r / 22, .35, 1.6), droop = o.droop || 0;
  if (k < .02) return;
  push(); translate(x, y); rotate(rot); scale(backOut(k));
  for (let i = 0; i < 5; i++) {
    const a = i / 5 * TAU - Math.PI / 2 + .2, sag = droop * (Math.sin(a) + 1) * .35 * r;
    const cx = Math.cos(a) * r * .62, cy = Math.sin(a) * r * .62 + sag;
    paint(ellPts(cx, cy, r * .52, r * .44, 14, 0, a), { wash: o.col || FLOWER.petal, fill: FLOWER.petalLt, fillOp: 70, tex: .6, ink: PAL.ink, sw });
  }
  paint(ellPts(0, droop * .2 * r, r * .32, r * .32, 12), { wash: FLOWER.mid, ink: PAL.ink, sw: sw * .8 });
  pop();
}

// Noodle arm from a shoulder at (px, py), dir ±1 (which side), raise angle a (0 = out, + = up), length L (in u).
// hook(u, sw) is called at the hand, in arm space (+x outward), so a held prop follows the hand.
function noodleArm(px, py, dir, a, u, col, sw, hook, L = 3) {
  push(); translate(px, py); rotate(dir < 0 ? a : -a); if (dir < 0) scale(-1, 1);
  const bend = .35 * u;
  paint(ribbon([[0, 0], [L * u * .5, -bend], [L * u, 0]], .95 * u, .8 * u), { wash: col, ink: PAL.ink, sw: sw * .8 });
  paint(ellPts(L * u, 0, .62 * u, .6 * u, 12), { wash: col, ink: PAL.ink, sw: sw * .7 });
  if (hook) { translate(L * u, 0); hook(u, sw); }
  pop();
}

function stubLegs(u, o, sw, col, shoe, rs) {
  [-1.6, 1.6].forEach((lx, i) => {
    rs('leg' + i);
    let h = 1.6, sx = 0;
    if (o.walk != null) { const ph = (o.walk + (i ? .5 : 0)) * TAU; sx = Math.sin(ph) * .5; h = 1.6 - Math.max(0, Math.cos(ph)) * .6; }
    paint(rectPts((lx + sx - .45) * u, -1.9 * u, .9 * u, h * u + .3 * u, u * .04), { wash: col, ink: PAL.ink, sw: sw * .7 });
    paint(ellPts((lx + sx + .25) * u, (-1.9 + h + .3) * u - .25 * u, .85 * u, .42 * u, 12), { wash: shoe, ink: PAL.ink, sw: sw * .7 });
  });
}

// shared rig for both characters: shadow, squash/flip/rotate transform, arms, legs, body(u, sw, V) and face.
function rig(x, y, u, o, spec) {
  const id = o.boilKey ?? ('c' + (++CLAWD_N)), rs = part => boilSeed(`${spec.name} ${id} ${part}`);
  x += (o.dx || 0) * u;
  const dy = (o.dy || 0) * u, sq = (o.sq || 0), sw = clamp(u / 15, .45, 2.4);
  const tc = tintCols({ col: spec.col, dk: spec.dk, lt: spec.lt, tint: o.tint, tintK: o.tintK });
  const col = (o.ownCol && o.col) || tc.col, dk = (o.ownCol && o.dk) || tc.dk, lt = (o.ownCol && o.lt) || tc.lt;   // emotions() blends from clay: ignore unless ownCol
  const q = o.view === 'q' || o.view === 'side';
  rs('shadow');
  if (!o.noShadow) { const f = 1 - Math.min(.5, Math.abs(o.dy || 0) * .06); paint(ellPts(x, y + u * .15, u * 4.6 * f, u * .8 * f, 22), { fill: PAL.ink, fillOp: 90, bleed: .25, tex: .3, border: .1, ink: null }); }
  push(); translate(x, y + dy); if (o.rot) rotate(o.rot);
  scale((o.flip ? -1 : 1) * (o.sx ?? 1) * (1 + sq * .6), (o.sy ?? 1) * (1 - sq));
  const aL = o.aL ?? .2, aR = o.aR ?? .2, sh = spec.shoulder;
  // far arm (behind) in 3/4 view, then legs, body, face, near arm
  if (q) { rs('armfar'); noodleArm(-sh[0] * u * .8, sh[1] * u, -1, aL, u, mixCol(col, dk, .45), sw, o.armL, spec.armL); }
  else { rs('armL'); noodleArm(-sh[0] * u, sh[1] * u, -1, aL, u, col, sw, o.armL, spec.armL); }
  if (!o.noLegs) stubLegs(u, o, sw, dk, spec.shoe, rs);
  rs('body'); spec.body(u, sw, { col, dk, lt, q, o });
  rs('face');
  if (!o.noFace) {
    push(); translate(q ? 1.3 * u : 0, spec.faceY * u); scale(q ? .8 : 1, 1);
    if (o.blush) blush(u, sw, { bx: 3.1, sides: [-1, 1] }, o.blush === true ? 1 : o.blush);
    rs('eyes'); eyes(u, o, sw, [-1, 1], 0); rs('mouth'); mouth(u, o.mouth, sw);
    pop();
  }
  rs('top'); if (spec.top) spec.top(u, sw, { col, dk, lt, q, o });
  rs('armR'); noodleArm(sh[0] * u * (q ? 1.05 : 1), sh[1] * u, 1, aR, u, col, sw, o.armR, spec.armL);
  rs('draw'); if (o.draw) o.draw(u, sw);
  pop();
  rs('emote');
  if (o.emote) {
    const top = EMOTE_TOP.includes(o.emote), d = o.flip ? -1 : 1;
    emote(o.emote, x + d * (top ? 0 : 5.2 * u), y + dy + (top ? -14 : spec.emoteY) * u * (1 - sq), u * .9, o.emoteK ?? 1, o.emoteAge ?? T);
  }
  rs('after');
}

// 阿旺. Extra options: hairUp (0..1 pompadour boing stretch), hairRot, flower (0..1: 小花's flower tucked in his quiff),
// shades (0..1: sunglasses sliding down the nose, 1 = on).
const WANG = { col: '#4F97B8', dk: '#2E6488', lt: '#A9D6E8' };
function wang(x, y, u, o = {}) {
  rig(x, y, u, o, {
    name: 'wang', ...WANG, shoe: '#5B3A2E', shoulder: [4.1, -4.4], armL: 2.8, faceY: .2, emoteY: -12,
    body: (u, sw, c) => {
      const body = ellPts(0, -5.4 * u, 4.4 * u, 4.5 * u, 30, u * .05);
      paint(body, { wash: c.col, ink: null });
      paint(ellPts(-1.5 * u, -7.4 * u, 2.2 * u, 1.3 * u, 16, u * .08, -.3), { fill: c.lt, fillOp: 120, bleed: .2, tex: .8, border: .8, ink: null });
      // flower-print shirt band across the belly, clipped to the egg by drawing it as the egg's lower slice
      const band = []; for (let i = 0; i <= 16; i++) { const a = .12 * Math.PI + i / 16 * .76 * Math.PI; band.push([Math.cos(a) * 4.4 * u, -5.4 * u + Math.sin(a) * 4.5 * u]); }
      band.push([-4.05 * u, -3.2 * u], [0, -2.7 * u], [4.05 * u, -3.2 * u]);
      paint(band, { wash: '#E0674E', fill: '#B8453A', fillOp: 60, tex: .6, ink: null });
      for (const [fx, fy] of [[-2.2, -2.1], [.4, -1.6], [2.6, -2.3]]) paint(ellPts(fx * u, fy * u, .42 * u, .42 * u, 8), { wash: PAL.cream, ink: null });
      paint(body, { ink: PAL.ink, sw });
    },
    top: (u, sw, c) => {
      const o = c.o, up = o.hairUp || 0;
      push(); translate(-.4 * u, -8.6 * u); rotate((o.hairRot || 0) - up * .15); scale(1 - up * .1, 1 + up * .8);
      const quiff = [[-3.6, .4], [-3.4, -1.6], [-1.8, -3.3], [.8, -4.1], [3.6, -3.7], [5.3, -2.5], [5.6, -1.4], [4.4, -1.7], [3.8, -.6], [3.4, .6]].map(([a, b]) => [a * u, b * u]);
      paint(quiff, { wash: '#3A2E4A', fill: '#5A4A70', fillOp: 70, tex: .5, ink: PAL.ink, sw, curv: .6 });
      inkLine([[-2 * u, -2.2 * u], [0, -3.2 * u], [2.8 * u, -3.1 * u]], sw * .7, '#8E82B0', 'inkfine', .6);   // gloss
      inkLine([[-.6 * u, -1.2 * u], [1.4 * u, -2.1 * u], [3.8 * u, -2 * u]], sw * .5, '#8E82B0', 'inkfine', .6);
      if ((o.flower || 0) > .01) flowerHead(3.9 * u, -3.3 * u, 1.35 * u, { k: o.flower, rot: .3, sw: sw * .7 });
      pop();
      const sh = o.shades || 0;
      if (sh > .01 && !c.q) {   // sunglasses, sliding down the nose as sh goes 1 → 0
        push(); translate(0, (.2 + (1 - sh) * 1.1) * u); translate(0, 0);
        if (sh > .05) eyes(u, { eyes: 'shades' }, sw, [-1, 1], 0);
        pop();
      }
    }
  });
}

// 小花. Extra options: flowerK (0..1 her flower's bloom; 0 = she has given it away), flowerAt (hook to draw it elsewhere).
const HUA = { col: '#F2A7A6', dk: '#C66F78', lt: '#FFD8D2' };
function hua(x, y, u, o = {}) {
  rig(x, y, u, o, {
    name: 'hua', ...HUA, shoe: '#7A3B4E', shoulder: [3.8, -4.1], armL: 2.6, faceY: .3, emoteY: -11,
    body: (u, sw, c) => {
      const body = through([[-4.1, -1.2], [-4.3, -4.2], [-3.2, -7.4], [0, -8.7], [3.2, -7.4], [4.3, -4.2], [4.1, -1.2], [2, -.9], [-2, -.9], [-4.1, -1.2]].map(([a, b]) => [a * u, b * u]), 4);
      paint(body, { wash: c.col, ink: null });
      paint(ellPts(-1.4 * u, -6.6 * u, 2 * u, 1.2 * u, 16, u * .08, -.3), { fill: c.lt, fillOp: 130, bleed: .2, tex: .8, border: .8, ink: null });
      // apron: cream, with a pocket
      paint(through([[-2.8, -3.6], [2.8, -3.6], [3.2, -1.1], [-3.2, -1.1], [-2.8, -3.6]].map(([a, b]) => [a * u, b * u]), 3), { wash: PAL.cream, fill: '#F1DCC2', fillOp: 80, tex: .5, ink: PAL.ink, sw: sw * .6 });
      paint(rrPts(-1 * u, -2.7 * u, 2 * u, 1.1 * u, .3 * u), { ink: mixCol(PAL.ink, PAL.cream, .4), sw: sw * .45 });
      paint(body, { ink: PAL.ink, sw });
    },
    top: (u, sw, c) => {
      const o = c.o;
      // plum bob: a cap over the top of the head with a fringe
      const cap = [[-4.5, -3.2], [-4.4, -6.2], [-3.3, -8.3], [0, -9.3], [3.3, -8.3], [4.4, -6.2], [4.5, -3.2], [3.6, -3.6], [3.4, -6.4], [1.8, -7.3], [.9, -6.8], [0, -7.4], [-1.2, -6.9], [-2.2, -7.4], [-3.4, -6.4], [-3.6, -3.6]].map(([a, b]) => [a * u, b * u]);
      paint(cap, { wash: '#6B3550', fill: '#8E4A6A', fillOp: 70, tex: .5, ink: PAL.ink, sw, curv: .35 });
      inkLine([[-2.4 * u, -8.3 * u], [0, -8.9 * u], [2 * u, -8.5 * u]], sw * .5, '#B07A98', 'inkfine', .6);
      if (o.bow) {   // bow hair clip (the 陽光宅男 version of her)
        for (const s of [-1, 1]) paint([[-3 * u, -8.5 * u], [(-3 + s * 1.5) * u, -9.6 * u], [(-3 + s * 1.5) * u, -7.5 * u]], { wash: '#F4B63A', fill: '#E8912A', fillOp: 60, ink: PAL.ink, sw: sw * .6, curv: .3 });
        paint(ellPts(-3 * u, -8.55 * u, .45 * u, .45 * u, 10), { wash: '#E8912A', ink: PAL.ink, sw: sw * .5 });
      } else {
        const k = o.flowerK ?? 1;
        if (k > .01) flowerHead(-3.1 * u, -8.4 * u, 1.55 * u, { k, rot: -.2 + .06 * Math.sin(T * 3), sw: sw * .7 });
      }
    }
  });
}

// A little retro scooter facing right. (x, y) = ground under the middle. o.lamp 0..1 headlamp, o.shake for idling.
// seatPt(x, y, u) = where a rider sits (feet dangle); mirrorPt = the round mirror on the handlebar.
const scooterSeat = (x, y, u) => [x - 1.2 * u, y - 5.2 * u];
const scooterMirror = (x, y, u) => [x + 5.6 * u, y - 11.6 * u];
function scooter(x, y, u, o = {}) {
  const sw = clamp(u / 15, .45, 2.4), red = '#C8324A', cream = PAL.cream, P = pts => pts.map(([a, b]) => [x + a * u, y + b * u]);
  boilSeed('scooter ' + (o.key || ''));
  paint(ellPts(x, y + .15 * u, 8.5 * u, .9 * u, 22), { fill: PAL.ink, fillOp: 80, bleed: .25, ink: null });
  for (const wx of [-5.2, 5]) {   // wheels
    paint(ellPts(x + wx * u, y - 1.5 * u, 1.55 * u, 1.55 * u, 18), { wash: '#34303F', ink: PAL.ink, sw });
    paint(ellPts(x + wx * u, y - 1.5 * u, .6 * u, .6 * u, 10), { wash: '#B9B2C4', ink: null });
  }
  // rear body (rounded hump) and floorboard
  paint(P([[-7.6, -2.2], [-7.4, -4.6], [-5.4, -6.1], [-2, -5.6], [.2, -3.1], [3.2, -3], [3.4, -2.1], [-7.6, -2.2]]), { wash: red, fill: '#9E2238', fillOp: 60, tex: .5, ink: PAL.ink, sw, curv: .45 });
  paint(ellPts(x - 5.4 * u, y - 4.6 * u, 1.2 * u, .7 * u, 12, 0, -.3), { fill: '#F07A7F', fillOp: 110, bleed: .2, ink: null });
  // front leg shield + fender
  paint(P([[2.6, -2.2], [3.4, -8.2], [4.6, -8.6], [5.6, -3.4], [6.8, -2.4], [6.5, -1.6], [2.6, -2.2]]), { wash: red, fill: '#9E2238', fillOp: 60, tex: .5, ink: PAL.ink, sw, curv: .3 });
  paint(P([[3.1, -3.3], [3.7, -7.6], [4.3, -7.8]]), { ink: cream, sw: sw * .7 });
  // seat
  paint(P([[-4.8, -6], [-4.4, -6.9], [-.6, -6.9], [-.2, -6], [-4.8, -6]]), { wash: '#4A3040', ink: PAL.ink, sw, curv: .4 });
  // steering column, handlebar, mirror
  inkLine(P([[4.2, -8.3], [4.5, -10.2]]), sw * 1.4, PAL.ink, 'ink', 0);
  inkLine(P([[3.2, -10.2], [5.8, -10.4]]), sw * 1.6, PAL.ink, 'ink', 0);
  inkLine(P([[5.2, -10.3], [5.6, -11]]), sw, PAL.ink, 'inkfine', 0);
  const [mx, my] = scooterMirror(x, y, u);
  paint(ellPts(mx, my, .95 * u, .8 * u, 14), { wash: '#BFD7E6', fill: PAL.sky, fillOp: 60, ink: PAL.ink, sw: sw * .8 });
  inkLine([[mx - .45 * u, my - .15 * u], [mx - .05 * u, my - .5 * u]], sw * .5, PAL.cream, 'inkfine', 0);
  // headlamp
  const hl = [x + 4.7 * u, y - 9.2 * u];
  if ((o.lamp || 0) > .01) glow(hl[0] + 1.2 * u, hl[1], 6 * u, '#FFD98A', o.lamp);
  paint(ellPts(hl[0], hl[1], .9 * u, .75 * u, 12), { wash: '#FFE9A8', ink: PAL.ink, sw: sw * .8 });
}

// A round paper lantern hanging at (x, y); lit 0..1. Glow first, so the paint sits in the light.
function lantern(x, y, r, lit, sw = 1, col = '#D8394E') {
  if (lit > .01) glow(x, y, r * 4.2, '#FFB45A', lit * .9);
  paint(ellPts(x, y, r, r * 1.12, 16), { wash: mixCol('#7A2A38', col, .35 + .65 * lit), fill: lit > .3 ? '#FFB45A' : col, fillOp: 60 * lit + 20, tex: .5, ink: PAL.ink, sw });
  inkLine([[x, y - r * 1.1], [x, y + r * 1.1]], sw * .45, mixCol(PAL.ink, col, .3), 'inkfine', 0);
  paint(rectPts(x - r * .35, y - r * 1.3, r * .7, r * .25), { wash: '#3A2E3A', ink: null });
  paint(rectPts(x - r * .35, y + r * 1.05, r * .7, r * .25), { wash: '#3A2E3A', ink: null });
}

// 阿宅 (陽光宅男). A lilac-grey mochi in a hoodie, bed-head hair, big round glasses.
// Extra options: hood (0..1 hood up), pale (0..1 sun-shocked), glasses (default true), hatK (kit hat name via o.hat).
const ZHAI = { col: '#A89CC8', dk: '#6E6296', lt: '#D8D0EE' };
function zhai(x, y, u, o = {}) {
  rig(x, y, u, { ...o, tint: o.pale > .01 ? 'pale' : o.tint, tintK: o.pale > .01 ? o.pale : o.tintK }, {
    name: 'zhai', ...ZHAI, shoe: '#3E3A52', shoulder: [4.2, -4.2], armL: 2.7, faceY: .1, emoteY: -11.5,
    body: (u, sw, c) => {
      const body = through([[-4.4, -1.1], [-4.6, -4.6], [-3.6, -7.9], [0, -9.2], [3.6, -7.9], [4.6, -4.6], [4.4, -1.1], [0, -.8], [-4.4, -1.1]].map(([a, b]) => [a * u, b * u]), 4);
      paint(body, { wash: c.col, ink: null });
      paint(ellPts(-1.5 * u, -7 * u, 2.1 * u, 1.2 * u, 16, u * .08, -.3), { fill: c.lt, fillOp: 120, bleed: .2, tex: .8, border: .8, ink: null });
      // hoodie: a teal body-sleeve over the lower half, with a pouch pocket and two drawstrings
      const hood = through([[-4.5, -1.1], [-4.6, -3.9], [-2.4, -4.4], [0, -3.9], [2.4, -4.4], [4.6, -3.9], [4.5, -1.1], [0, -.8], [-4.5, -1.1]].map(([a, b]) => [a * u, b * u]), 3);
      paint(hood, { wash: '#3A9C98', fill: '#2A7470', fillOp: 70, tex: .6, ink: PAL.ink, sw: sw * .7 });
      paint(rrPts(-1.8 * u, -2.7 * u, 3.6 * u, 1.3 * u, .4 * u), { ink: mixCol(PAL.ink, '#3A9C98', .3), sw: sw * .5 });
      for (const s of [-.8, .8]) inkLine([[s * u, -3.9 * u], [s * u * 1.05, -2.9 * u]], sw * .5, PAL.cream, 'inkfine', 0);
      paint(body, { ink: PAL.ink, sw });
    },
    top: (u, sw, c) => {
      const o = c.o;
      if ((o.hood || 0) > .01) {   // hood pulled up over the head
        const k = o.hood, hp = [[-4.8, -3.8], [-4.9, -6.8], [-3.6, -9.4], [0, -10.4], [3.6, -9.4], [4.9, -6.8], [4.8, -3.8], [3.6, -4.4], [3.4, -7.4], [0, -8.4], [-3.4, -7.4], [-3.6, -4.4]].map(([a, b]) => [a * u, (b + (1 - k) * 4) * u]);
        paint(hp, { wash: '#3A9C98', fill: '#2A7470', fillOp: 80, tex: .5, ink: PAL.ink, sw, curv: .4 });
      } else if (!o.hat) {   // bed-head: a tuft cluster sticking out every which way
        const tufts = [[-2.6, -8.4, -.9], [-1, -9.1, -.35], [.7, -9.2, .2], [2.4, -8.6, .8], [3.6, -7.8, 1.25]];
        tufts.forEach(([tx, ty, a], i) => { push(); translate(tx * u, ty * u); rotate(a + .08 * Math.sin(T * 5 + i)); paint(ribbon([[0, 0], [.2 * u, -1.1 * u], [.7 * u, -1.9 * u]], .95 * u, .1 * u), { wash: '#4A3E66', ink: PAL.ink, sw: sw * .7 }); pop(); });
        paint(through([[-3.9, -6.2], [-3.4, -8.3], [0, -9.3], [3.4, -8.3], [3.9, -6.2], [2.2, -7.2], [0, -7.6], [-2.2, -7.2], [-3.9, -6.2]].map(([a, b]) => [a * u, b * u]), 3), { wash: '#4A3E66', fill: '#6A5A8E', fillOp: 60, ink: PAL.ink, sw: sw * .8 });
      }
      if (o.hat) { push(); translate(0, -.9 * u); hat(u, o.hat, sw); pop(); }
      if (o.glasses !== false && o.eyes !== 'shades' && !c.q) {   // big round glasses over the eyes
        for (const s of [-1, 1]) paint(ellPts(s * 2.5 * u, (-5.9 + .1) * u, 1.55 * u, 1.45 * u, 18), { wash: '#E8F4FF', washOp: 40, ink: PAL.ink, sw: sw * .8 });
        inkLine([[-.95 * u, -6 * u], [0, -6.3 * u], [.95 * u, -6 * u]], sw * .7, PAL.ink, 'ink', .5);
        if ((o.glint || 0) > .01) for (const s of [-1, 1]) inkLine([[(s * 2.5 - .9) * u, -6.4 * u], [(s * 2.5 - .3) * u, -7 * u]], sw * .6 * o.glint, PAL.cream, 'inkfine', 0);
      } else if (o.glasses !== false && o.eyes !== 'shades' && c.q) {
        push(); translate(1.3 * u, 0); scale(.8, 1);
        for (const s of [-1, 1]) paint(ellPts(s * 2.5 * u, -5.8 * u, 1.55 * u, 1.45 * u, 18), { wash: '#E8F4FF', washOp: 40, ink: PAL.ink, sw: sw * .8 });
        inkLine([[-.95 * u, -6 * u], [0, -6.3 * u], [.95 * u, -6 * u]], sw * .7, PAL.ink, 'ink', .5);
        pop();
      }
    }
  });
}

// A handheld game console held at an arm tip (arm space). glow 0..1 lights the screen.
function consoleProp(u, sw, col = '#E27A92', lit = 1) {
  paint(rrPts(-.4 * u, -1.1 * u, 3.2 * u, 2.2 * u, .5 * u), { wash: col, fill: mixCol(col, PAL.ink, .3), fillOp: 50, ink: PAL.ink, sw: sw * .7 });
  if (lit > .01) glow(1.2 * u, 0, 2.4 * u, '#9AF0E0', .6 * lit);
  paint(rrPts(.55 * u, -.65 * u, 1.3 * u, 1.3 * u, .15 * u), { wash: mixCol('#2A3A4A', '#9AF0E0', .6 * lit), ink: PAL.ink, sw: sw * .5 });
  paint(ellPts(0, 0, .28 * u, .28 * u, 8), { wash: PAL.ink, ink: null });
  paint(ellPts(2.3 * u, -.2 * u, .22 * u, .22 * u, 8), { wash: PAL.cream, ink: null });
}
// An umbrella held at the arm tip; open 0..1.
function umbrellaProp(u, sw, open = 1, col = '#3A2E4A') {
  inkLine([[0, 0], [0, -7 * u]], sw * 1.2, PAL.ink, 'ink', 0);
  const w = lerp(1, 6.5, open) * u, top = -7.6 * u, pts = [];
  for (let i = 0; i <= 14; i++) { const a = Math.PI + i / 14 * Math.PI; pts.push([Math.cos(a) * w, top + Math.sin(a) * 2.6 * u * (0.4 + .6 * open) + 2.2 * u]); }
  for (let i = 5; i >= 1; i--) pts.push([-w + i / 6 * 2 * w, top + 2.2 * u + (i % 2 ? .5 * u : 0)]);
  paint(pts, { wash: col, fill: '#5A4A70', fillOp: 70, tex: .5, ink: PAL.ink, sw: sw * .8 });
  inkLine([[0, 0], [.4 * u, .6 * u], [-.2 * u, 1 * u]], sw, PAL.ink, 'ink', .6);
}
