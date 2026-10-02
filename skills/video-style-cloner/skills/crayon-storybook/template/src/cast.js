// cast.js: the picture-book characters. Coloured-pencil outlines, crayon-scribble fills, boiling linework.
//
//   lulu(x, y, u, o)   a small girl in a butter-yellow raincoat and sky-blue boots, with a cocoa bob and a star clip.
//                      About 11u tall and 5u wide. (x, y) = the ground point between her feet.
//   kuri(x, y, u, o)   Lulu's companion, a round hedgehog: a cocoa spiky ball with a cream face and a button nose.
//                      About 5u tall and 6u wide. (x, y) = the ground point between his feet.
// Size guide at 1920×1080: wide shot u ≈ 14–20 (Lulu), medium 30–45, close-up 60–90. Kuri reads best at u ≥ 12.
//
// Both take the same options (all optional) and return { head, top, handL, handR, feet } in world coordinates:
//   pose:  dx, dy (in u, negative = up), sq (squash; negative stretches), rot (pivots at the feet), flip, sx, sy
//          aL, aR   arm angles: 0 = straight out sideways, + = up, − = down (±1.5 vertical). Rest ≈ −1.2.
//                   In side view 0 points forward (the way the character faces).
//          bL, bR   elbow bend (Lulu): + folds the forearm up/in (hand to chest ≈ 2, hand to chin ≈ 2.3), − back (hips)
//          walk     leg phase (1 = a full stride cycle); null = standing. See walkCycle().
//          hair     Lulu's hair/hem lag in u (+ = flicks up, e.g. while falling after a jump; use spring())
//   view:  'front' | 'q' (3/4, facing right) | 'side' (profile, facing right) | 'back'. flip: true faces left.
//   face:  eyes, mouth, brows, lookX / lookY (−1..1), squint 0..1, blush 0..1, seed (blink timing), noBlink
//          eyes: normal, wide, happy, closed, squeeze, sad, cry, teary, angry, heart, sleepy, shine, look, scared, x,
//                wink — or a pair ['normal', 'happy'] for mismatched eyes
//          mouth: smile, grin, laugh, o, O, frown, wobble, flat, wail, cat, tongue, pout
//          brows: up, worried, angry, flat (or null)
//   extras: emote + emoteK (0..1 pop) + emoteAge, draw(u, sw) (body-local, front coordinates, drawn last),
//          armL/armR(u, sw) called at the hand in ARM space (+x along the forearm), holdL/holdR(u, sw) called at the
//          hand UPRIGHT (props that stay level: an apple, a cup, a balloon string), propFront: draw props over the hand.
//   boil:  boilKey (a stable id for its boil seeds; default: call order — set it if characters come and go mid-shot)
//   col:   Lulu: coat, boots, hair colours via coat / boots / hairCol; Kuri: spikes, face via spikes / faceCol
//
// Moods: feel(name, t) and emotions(t, keys) (below) give the face, blush, emote and the idle body motion together:
//   lulu(x, y, 36, { ...emotions(t, [[0, 'curious'], [1.4, 'surprised'], [1.9, 'happy']]), view: 'q' })

// ---------- shared helpers ----------
const U = (u, pts) => pts.map(([x, y]) => [x * u, y * u]);
const OPEN_EYES = ['normal', 'wide', 'look', 'sad', 'angry', 'scared', 'shine', 'teary'];
function blinkK(o) {   // 1 while the eyes are shut for a blink (0.12 s every ~3–4.5 s, per seed)
  if (o.noBlink) return 0;
  const s = o.seed || 0, per = 3.1 + hash(s + 11) * 1.4, ph = (T + hash(s + 5) * 7) % per;
  return ph < .12 ? 1 : 0;
}
// local → world, for returned anchor points (mirrors the push/translate/rotate/scale the characters do)
function xform(x, y, rot, sx, sy) {
  const c = Math.cos(rot || 0), s = Math.sin(rot || 0);
  return (lx, ly) => [x + c * lx * sx - s * ly * sy, y + s * lx * sx + c * ly * sy];
}

// A two-segment arm (upper + fore), as one tapered sleeve with a mitten hand. Draws in the current body space.
// dirx: −1 left, +1 right (in side view +1 = forward). Returns the hand position (body space) and forearm angle.
function arm2(px, py, a, b, dirx, L1, L2, w0, w1, col, handCol, line, sw, u, hooks, gap) {
  const e = [px + dirx * Math.cos(a) * L1, py - Math.sin(a) * L1], a2 = a + b;
  const h = [e[0] + dirx * Math.cos(a2) * L2, e[1] - Math.sin(a2) * L2];
  const th = Math.atan2(h[1] - e[1], h[0] - e[0]);
  // slightly past the elbow the path gets a middle point so the bend reads as an elbow, not a kink
  colorIn(limbPts([px, py], e, h, w0, (w0 + w1) / 2, w1), { col, gap, ang: th + 1.3, w: clamp(u / 40, .45, 1.1), line, lw: sw * .85, curv: .25 });
  const hand = () => colorIn(ellPts(h[0] + Math.cos(th) * u * .12, h[1] + Math.sin(th) * u * .12, u * .42, u * .4, 14), { col: handCol, fill: 'flat', line, lw: sw * .8 });
  const props = () => {
    if (hooks.hold) { push(); translate(h[0], h[1]); hooks.hold(u, sw); pop(); }
    if (hooks.arm) { push(); translate(h[0], h[1]); rotate(th); if (dirx < 0) scale(1, -1); hooks.arm(u, sw); pop(); }
  };
  if (hooks.front) { hand(); props(); } else { props(); hand(); }
  return { h, th };
}
// One closed outline for a bent limb (root → elbow → tip) with a clamped miter at the elbow, so tight bends never spike.
function limbPts(A, E, Hh, wA, wE, wH) {
  const nrm = (p, q) => { const dx = q[0] - p[0], dy = q[1] - p[1], d = Math.hypot(dx, dy) || 1; return [-dy / d, dx / d]; };
  const n1 = nrm(A, E), n2 = nrm(E, Hh); let m = [n1[0] + n2[0], n1[1] + n2[1]]; const ml = Math.hypot(m[0], m[1]);
  m = ml < .2 ? n1 : [m[0] / ml, m[1] / ml]; const k = Math.min(1.6, 1 / Math.max(.4, m[0] * n1[0] + m[1] * n1[1]));
  const off = (p, n, w, s) => [p[0] + n[0] * w / 2 * s, p[1] + n[1] * w / 2 * s];
  const dir = [Hh[0] - E[0], Hh[1] - E[1]], dl = Math.hypot(dir[0], dir[1]) || 1, cap = [Hh[0] + dir[0] / dl * wH * .45, Hh[1] + dir[1] / dl * wH * .45];
  return [off(A, n1, wA, 1), off(E, m, wE * k, 1), off(Hh, n2, wH, 1), cap, off(Hh, n2, wH, -1), off(E, m, wE * k, -1), off(A, n1, wA, -1)];
}
const shadowUnder = (x, y, w, h, lift) => smudge(ellPts(x, y, w * (1 - Math.min(.5, lift * .06)), h * (1 - Math.min(.5, lift * .06)), 20), PAL.inkSoft, { op: 70, tex: .3 });

// ---------- faces (shared) ----------
// s = size unit; (x, y) = the eye's centre. Pupils follow lookX / lookY.
function eyeMark(kind, x, y, s, o, side, sw) {
  const lx = (o.lookX || 0) * s * .12, ly = (o.lookY || 0) * s * .1, sq = clamp(o.squint || 0), col = PAL.ink;
  if (sq > .6 && OPEN_EYES.includes(kind)) kind = 'closed';
  const dot = (rx, ry, hl = true) => {
    paint(ellPts(x + lx, y + ly, rx, ry * (1 - sq * .7), 14), { wash: col, ink: null });
    if (hl && rx > 3) paint(ellPts(x + lx - rx * .3, y + ly - ry * .35, rx * .32, rx * .32, 8), { wash: PAL.cream, ink: null });
  };
  const arc = (up, w = .3) => pencilLine([[x - s * w, y + (up ? s * .08 : -s * .06)], [x, y + (up ? -s * .14 : s * .1)], [x + s * w, y + (up ? s * .08 : -s * .06)]], sw * .9, col, .5);
  switch (kind) {
    case 'wide': paint(ellPts(x, y, s * .34, s * .4, 16), { wash: PAL.cream, ink: col, sw: sw * .6 }); dot(s * .16, s * .2); break;
    case 'scared': paint(ellPts(x, y, s * .34, s * .42, 16), { wash: PAL.cream, ink: col, sw: sw * .6 }); paint(ellPts(x + lx + jit(s * .02), y + ly, s * .08, s * .09, 8), { wash: col, ink: null }); break;
    case 'happy': arc(true); break;
    case 'closed': arc(false, .27); break;
    case 'squeeze': pencilLine([[x - side * s * .26, y - s * .18], [x + side * s * .18, y], [x - side * s * .26, y + s * .18]], sw * .9, col, 0); break;
    case 'sad': dot(s * .15, s * .2); pencilLine([[x - side * s * .3, y - s * .34], [x + side * s * .2, y - s * .22]], sw * .7, col, 0); break;
    case 'teary': dot(s * .17, s * .23); paint(ellPts(x + side * s * .12, y + s * .3, s * .09, s * .12, 10), { wash: PAL.sky, ink: PAL.skyDk, sw: sw * .4 }); break;
    case 'cry': {
      arc(true, .28);
      const ph = (T * 1.6 + (side > 0 ? .5 : 0)) % 1;
      paint(ribbon([[x + side * s * .1, y + s * .12], [x + side * s * .22, y + s * .6], [x + side * s * .16, y + s * 1.05]], s * .16, s * .26), { wash: PAL.skyLt, ink: PAL.skyDk, sw: sw * .5 });
      paint(ellPts(x + side * s * .2, y + s * (.3 + ph * 1.1), s * .09, s * .12, 10), { wash: PAL.sky, ink: null });
      break;
    }
    case 'angry': dot(s * .16, s * .2); pencilLine([[x - side * s * .32, y - s * .34], [x + side * s * .24, y - s * .12]], sw, col, 0); break;
    case 'heart': heartProp(x, y, s * .3, PAL.roseDk); break;
    case 'sleepy': pencilLine([[x - s * .28, y], [x + s * .28, y]], sw * .9, col, 0); paint(ellPts(x, y + s * .07, s * .12, s * .07, 8), { wash: col, ink: null }); break;
    case 'shine': dot(s * .2, s * .26, false); paint(ellPts(x + lx - s * .07, y + ly - s * .09, s * .08, s * .08, 8), { wash: PAL.cream, ink: null }); paint(ellPts(x + lx + s * .07, y + ly + s * .08, s * .04, s * .04, 6), { wash: PAL.cream, ink: null }); break;
    case 'x': pencilLine([[x - s * .2, y - s * .2], [x + s * .2, y + s * .2]], sw * .9, col, 0); pencilLine([[x + s * .2, y - s * .2], [x - s * .2, y + s * .2]], sw * .9, col, 0); break;
    case 'look': dot(s * .15, s * .21); break;
    default: dot(s * .15, s * .21);
  }
}
function mouthMark(kind, x, y, s, sw) {
  const col = PAL.ink, tong = PAL.rose, dark = '#8E4B4B';
  switch (kind) {
    case 'smile': pencilLine([[x - s * .32, y - s * .06], [x, y + s * .14], [x + s * .32, y - s * .06]], sw, col, .6); break;
    case 'grin': colorIn([[x - s * .38, y - s * .1], [x + s * .38, y - s * .1], [x + s * .22, y + s * .2], [x, y + s * .27], [x - s * .22, y + s * .2]], { col: dark, fill: 'flat', line: col, lw: sw * .8, curv: .5 }); break;
    case 'laugh': colorIn([[x - s * .45, y - s * .15], [x + s * .45, y - s * .15], [x + s * .3, y + s * .28], [x, y + s * .4], [x - s * .3, y + s * .28]], { col: dark, fill: 'flat', line: col, lw: sw * .8, curv: .5 });
      paint(ellPts(x, y + s * .24, s * .2, s * .1, 10), { wash: tong, ink: null }); break;
    case 'o': paint(ellPts(x, y + s * .04, s * .1, s * .12, 10), { wash: dark, ink: col, sw: sw * .7 }); break;
    case 'O': paint(ellPts(x, y + s * .08, s * .2, s * .28, 14), { wash: dark, ink: col, sw: sw * .8 }); paint(ellPts(x, y + s * .22, s * .12, s * .07, 8), { wash: tong, ink: null }); break;
    case 'frown': pencilLine([[x - s * .3, y + s * .12], [x, y - s * .06], [x + s * .3, y + s * .12]], sw, col, .6); break;
    case 'wobble': pencilLine([[x - s * .32, y + s * .04], [x - s * .16, y - s * .04], [x, y + s * .04], [x + s * .16, y - s * .04], [x + s * .32, y + s * .04]], sw * .9, col, .4); break;
    case 'flat': pencilLine([[x - s * .24, y], [x + s * .24, y + s * .01]], sw * .9, col, 0); break;
    case 'wail': colorIn([[x - s * .34, y - s * .12], [x + s * .34, y - s * .12], [x + s * .24, y + s * .42], [x - s * .24, y + s * .42]], { col: dark, fill: 'flat', line: col, lw: sw * .8, curv: .4 });
      paint(ellPts(x, y + s * .34, s * .16, s * .07, 8), { wash: tong, ink: null }); break;
    case 'cat': pencilLine([[x - s * .3, y], [x - s * .15, y + s * .1], [x, y], [x + s * .15, y + s * .1], [x + s * .3, y]], sw * .9, col, .5); break;
    case 'tongue': pencilLine([[x - s * .3, y - s * .04], [x, y + s * .12], [x + s * .3, y - s * .04]], sw, col, .6); paint(ellPts(x + s * .08, y + s * .17, s * .12, s * .11, 10), { wash: tong, ink: col, sw: sw * .5 }); break;
    case 'pout': pencilLine([[x - s * .12, y + s * .02], [x, y - s * .05], [x + s * .12, y + s * .02]], sw * .9, col, .5); break;
  }
}
function browMarks(kind, xs, y, s, sw) {
  if (!kind) return;
  for (const [x, side] of xs) {
    const P = { up: [[-.24, .04], [0, -.08], [.24, .02]], worried: [[-.24, -.12], [.24, .06]], angry: [[-.24, .1], [.24, -.08]], flat: [[-.22, 0], [.22, 0]] }[kind];
    if (!P) continue;
    // P is written for the right eye (inner end = −x); mirror it for the left one
    pencilLine(P.map(([px, py]) => [x + px * s * side, y + py * s]), sw * .8, PAL.ink, .5);
  }
}
function cheeks(xs, y, r, k, sw) {
  if (k <= .02) return;
  for (const x of xs) { smudge(ellPts(x, y, r, r * .75, 14), PAL.rose, { op: 70 + 110 * k, tex: .4 }); if (k > .5) for (let i = 0; i < 3; i++) pencilLine([[x - r * .5 + i * r * .4, y + r * .25], [x - r * .3 + i * r * .4, y - r * .25]], sw * .5, PAL.roseDk, 0); }
}

// ---------- Lulu ----------
const LULU = { coat: PAL.butter, coatDk: PAL.butterDk, boots: PAL.sky, hair: '#8A5A44', skin: '#F8D2B4', clip: PAL.rose };
function lulu(x, y, u, o = {}) {
  const id = o.boilKey ?? 'l' + (++CAST_N), rs = part => boilSeed(`lulu ${id} ${part}`);
  const view = o.view || 'front', side = view === 'side', q = view === 'q', back = view === 'back';
  const coat = o.coat || LULU.coat, boots = o.boots || LULU.boots, hairC = o.hairCol || LULU.hair, skin = LULU.skin;
  const dy = (o.dy || 0) * u, sq = o.sq || 0, sw = clamp(u / 21, .5, 2.6), line = PAL.ink, gap = clamp(u * .3, 5, 18), cw = clamp(u / 38, .45, 1.2);
  x += (o.dx || 0) * u;
  const fx = (o.flip ? -1 : 1) * (o.sx ?? 1) * (1 + sq * .5), fy = (o.sy ?? 1) * (1 - sq);
  rs('shadow'); if (!o.noShadow) shadowUnder(x, y + u * .1, u * (side ? 2 : 2.6), u * .55, Math.abs(o.dy || 0));
  push(); translate(x, y + dy); if (o.rot) rotate(o.rot); scale(fx, fy);
  const hairLag = (o.hair || 0);

  // --- arms (defined here, drawn at the right layer) ---
  const aL = o.aL ?? -1.2, aR = o.aR ?? -1.2, bL = o.bL ?? .2, bR = o.bR ?? .2;
  const hands = {};
  const drawArm = (which, far) => {
    rs('arm' + which);
    const a = which === 'L' ? aL : aR, b = which === 'L' ? bL : bR;
    const hooks = { arm: which === 'L' ? o.armL : o.armR, hold: which === 'L' ? o.holdL : o.holdR, front: o.propFront };
    let px, dirx;
    if (side) { px = far ? -.15 : .15; dirx = 1; }
    else if (q) { px = which === 'L' ? -1.05 : 1.3; dirx = which === 'L' ? -1 : 1; }
    else { px = which === 'L' ? -1.15 : 1.15; dirx = which === 'L' ? -1 : 1; }
    if (back) dirx = -dirx, px = -px;
    const c = far ? mixCol(coat, PAL.inkSoft, .25) : coat, hc = far ? mixCol(skin, PAL.inkSoft, .2) : skin;
    const r = arm2(px * u, -5.25 * u, a, b, dirx, 1.3 * u, 1.2 * u, .95 * u, .72 * u, c, hc, line, sw, u, hooks, gap);
    hands[which] = r.h;
  };

  // --- back hair (behind everything above the shoulders) ---
  rs('hairback');
  const hx = q ? .12 : 0;
  if (!back && !side) {
    const P = [];
    for (let i = 0; i <= 16; i++) { const a = Math.PI + i / 16 * Math.PI; P.push([hx + Math.cos(a) * 2.95, -8.3 + Math.sin(a) * 2.8]); }
    const fl = hairLag * .6;
    P.push([hx + 3.05, -6.9], [hx + 3.3 + fl * .2, -6.15 - fl], [hx + 2.4, -6.35 - fl * .4], [hx + 1.2, -6.5], [hx - 1.2, -6.5], [hx - 2.4, -6.35 - fl * .4], [hx - 3.3 - fl * .2, -6.15 - fl], [hx - 3.05, -6.9]);
    colorIn(U(u, P), { col: hairC, gap, ang: 1.2, w: cw, line, lw: sw, curv: .4 });
  }
  // far arm (side / 3/4): behind the body
  if (side) drawArm('L', true); if (q) drawArm('L', true);

  // --- legs + boots ---
  const legs = side ? [[-.32, 1], [.32, 0]] : q ? [[-.55, 1], [.75, 0]] : [[-.62, 0], [.62, 0]];
  legs.forEach(([lx, far], i) => {
    rs('leg' + i);
    let ang = 0, lift = 0;
    if (o.walk != null) {
      const ph = (o.walk + (i ? .5 : 0)) * TAU;
      if (side || q) { ang = Math.sin(ph) * .5; lift = Math.max(0, Math.cos(ph)) * .35; }
      else lift = Math.max(0, Math.sin(ph)) * .55;
    }
    push(); translate(lx * u, -2.5 * u); rotate(-ang);
    const len = (2.05 - lift) * u, lc = far ? mixCol(skin, PAL.inkSoft, .2) : skin, bc = far ? mixCol(boots, PAL.inkSoft, .25) : boots;
    colorIn(rectPts(-.3 * u, 0, .6 * u, len - .5 * u), { col: lc, fill: 'flat', line, lw: sw * .8 });
    const toe = side || q ? .42 : (lx < 0 ? -.12 : .12);
    colorIn(rrPts((-.5 + toe) * u, len - .9 * u, 1.0 * u, .95 * u, .35 * u), { col: bc, gap: gap * .8, ang: .3, w: cw * .8, line, lw: sw * .85 });
    pop();
  });

  // --- coat ---
  rs('coat');
  const cs = side ? .72 : q ? .95 : 1, hem = hairLag * .15;
  const C = [[-.55, -5.8], [-1.35 * cs, -5.45], [-1.7 * cs, -4.4], [-2.3 * cs, -2.2 - hem]];
  for (let i = 1; i < 6; i++) C.push([lerp(-2.3 * cs, 2.3 * cs, i / 6), -2.2 - hem + (i % 2 ? .22 : -.02)]);   // scalloped hem
  C.push([2.3 * cs, -2.2 - hem], [1.7 * cs, -4.4], [1.35 * cs, -5.45], [.55, -5.8]);
  const CP = U(u, C.map(([cx, cy]) => [cx + (q ? .12 : 0), cy]));
  colorIn(CP, { col: coat, gap, ang: -.55, w: cw, line, lw: sw, curv: .25, shade: { pts: U(u, [[.9 * cs, -5.2], [2.1 * cs, -2.4], [.9 * cs, -2.4]]), col: mixCol(coat, LULU.coatDk, .55), gap: gap * 1.3, ang: .4 } });
  if (!back) {   // buttons + collar
    const bx = side ? .75 : q ? .55 : 0;
    for (const by of [-4.6, -3.5]) paint(ellPts(bx * u, by * u, .17 * u, .17 * u, 10), { wash: PAL.coral, ink: line, sw: sw * .5 });
    if (!side) colorIn(U(u, [[-.95 + (q ? .2 : 0), -5.85], [(q ? .25 : 0), -5.05], [.95 + (q ? .2 : 0), -5.85], [(q ? .2 : 0), -5.6]]), { col: PAL.cream, fill: 'flat', line, lw: sw * .7 });
  } else pencilLine(U(u, [[0, -5.5], [0, -2.5]]), sw * .6, LULU.coatDk, 0);
  if (back) { drawArm('L', false); drawArm('R', false); }

  // --- head ---
  rs('head');
  const HX = side ? .25 : q ? .2 : 0, HY = -8.1;
  let head;
  if (side) {   // profile: one outline with a little button nose
    head = []; for (let i = 0; i < 40; i++) { const a = i / 40 * TAU, d = ((a + Math.PI) % TAU - Math.PI - .28) / .13, bump = .3 * Math.exp(-d * d); head.push([(HX + Math.cos(a) * (2.45 + bump)) * u, (HY + Math.sin(a) * (2.35 + bump * .4)) * u]); }
  } else head = ellPts(HX * u, HY * u, 2.55 * u, 2.35 * u, 26);
  colorIn(head, { col: skin, gap: gap * 1.1, ang: .9, w: cw * .8, line, lw: sw, pale: .35, tone: mixCol(skin, PAL.peachDk, .45), curv: .3 });

  // --- face ---
  if (!back) {
    rs('face');
    const eyes = Array.isArray(o.eyes) ? o.eyes : [o.eyes || 'normal', o.eyes || 'normal'];
    const blink = blinkK(o), E = k => blink && OPEN_EYES.includes(k) ? 'closed' : k;
    const fc = side ? 1.45 : q ? .7 : 0, sp = side ? 0 : q ? .78 : .98;
    const ex = side ? [[fc + .05, 1]] : [[fc - sp, -1], [fc + sp, 1]];
    ex.forEach(([ex1, s1], i) => eyeMark(E(eyes[side ? 1 : i]), ex1 * u, -7.75 * u, u * 1.3, o, s1, sw));
    browMarks(o.brows, ex.map(([e1, s1]) => [e1 * u, s1]), -8.55 * u, u, sw);
    cheeks(side ? [(fc + .15) * u] : [(fc - sp - .6) * u, (fc + sp + .6) * u], -7.0 * u, .45 * u, .35 + .65 * (o.blush || 0), sw);
    mouthMark(o.mouth === undefined ? 'smile' : o.mouth, (fc + (side ? .55 : q ? .15 : 0)) * u, -6.8 * u, u, sw);
  }

  // --- bangs / back of the hair ---
  rs('hairfront');
  if (back) {
    const P = []; for (let i = 0; i <= 20; i++) { const a = Math.PI + i / 20 * TAU * .5; P.push([Math.cos(a) * 2.9, -8.2 + Math.sin(a) * 2.75]); }
    P.push([3.1, -6.6], [3.3, -6.1 - hairLag * .6], [0, -6.25], [-3.3, -6.1 - hairLag * .6], [-3.1, -6.6]);
    colorIn(U(u, P), { col: hairC, gap, ang: 1.3, w: cw, line, lw: sw, curv: .4 });
  } else {
    const bx = side ? .55 : q ? .38 : 0, P = [];
    if (!side) {
    const a0 = side ? 1.05 * Math.PI : Math.PI * 1.02, a1 = side ? 1.97 * Math.PI : Math.PI * 1.98;
    for (let i = 0; i <= 12; i++) { const a = lerp(a0, a1, i / 12); P.push([bx + Math.cos(a) * 2.65, -8.2 + Math.sin(a) * 2.55]); }
    const x0 = P[P.length - 1][0], xs = P[0][0];
    for (let i = 1; i <= 3; i++) { const xx = lerp(x0, xs, i / 3), xm = lerp(x0, xs, (i - .5) / 3); P.push([xm, -8.75], [xx, -9.05]); }
    colorIn(U(u, P), { col: hairC, gap: gap * .9, ang: -1.1, w: cw, line, lw: sw, curv: .35 });
    } else {   // profile: one hair shape — fringe at the front, over the crown, down the back to the flick, and back up behind the ear
      const Q = [[2.15, -8.85]];
      for (let i = 0; i <= 14; i++) { const a = lerp(-.35 * Math.PI, -1.05 * Math.PI, i / 14); Q.push([.2 + Math.cos(a) * 2.72, -8.2 + Math.sin(a) * 2.62]); }
      Q.push([-2.75, -6.9], [-3.1 - hairLag * .2, -6.1 - hairLag * .6], [-2.2, -6.3 - hairLag * .4], [-1.0, -6.5], [-.35, -7.2], [-.1, -8.2], [.7, -8.75], [1.4, -8.95]);
      colorIn(U(u, Q), { col: hairC, gap, ang: 1.2, w: cw, line, lw: sw, curv: .35 });
    }
    rs('clip');
    starProp((bx + 1.65) * u, -9.85 * u, .55 * u, PAL.butter, .2);
  }
  // arms in front (3/4: near arm; side: near arm)
  if (side) drawArm('R', false); if (q) drawArm('R', false);
  if (!side && !q && !back) { drawArm('L', false); drawArm('R', false); }   // front: arms over everything, so raised arms show
  rs('draw'); if (o.draw) o.draw(u, sw);
  pop();

  rs('emote');
  const dir = o.flip ? -1 : 1;
  if (o.emote) emote(o.emote, x + dir * 3.2 * u, y + dy - 11.2 * u * (1 - sq), u * .9, o.emoteK ?? 1, o.emoteAge ?? T);
  rs('after');
  const W2 = xform(x, y + dy, o.rot, fx, fy);
  return { head: W2(0, -8.1 * u), top: W2(0, -10.9 * u), handL: hands.L ? W2(...hands.L) : null, handR: hands.R ? W2(...hands.R) : null, feet: [x, y] };
}

// ---------- Kuri ----------
const KURI = { spikes: '#9C6B50', spikesDk: '#6E4A39', face: '#F6DFC2', feet: '#E9B996', nose: '#4A3631' };
function kuri(x, y, u, o = {}) {
  const id = o.boilKey ?? 'k' + (++CAST_N), rs = part => boilSeed(`kuri ${id} ${part}`);
  const view = o.view || 'front', side = view === 'side', q = view === 'q', back = view === 'back';
  const spk = o.spikes || KURI.spikes, faceC = o.faceCol || KURI.face, line = PAL.ink;
  const dy = (o.dy || 0) * u, sq = o.sq || 0, sw = clamp(u / 17, .5, 2.6), gap = clamp(u * .55, 5, 16), cw = clamp(u / 30, .45, 1.2);
  x += (o.dx || 0) * u;
  const fx = (o.flip ? -1 : 1) * (o.sx ?? 1) * (1 + sq * .6), fy = (o.sy ?? 1) * (1 - sq);
  rs('shadow'); if (!o.noShadow) shadowUnder(x, y + u * .1, u * 2.9, u * .55, Math.abs(o.dy || 0) * .5);
  push(); translate(x, y + dy); if (o.rot) rotate(o.rot); scale(fx, fy);
  const hands = {};
  const drawArm = (which, far) => {
    rs('arm' + which);
    const a = which === 'L' ? (o.aL ?? -1.1) : (o.aR ?? -1.1), b = which === 'L' ? (o.bL ?? .3) : (o.bR ?? .3);
    const hooks = { arm: which === 'L' ? o.armL : o.armR, hold: which === 'L' ? o.holdL : o.holdR, front: o.propFront };
    let px, py = -1.45, dirx;
    if (side) { px = far ? .2 : .5; py = -1.0; dirx = 1; } else if (q) { px = which === 'L' ? -1.25 : 2.1; py = which === 'L' ? -1.45 : -1.1; dirx = which === 'L' ? -1 : 1; }
    else { px = which === 'L' ? -1.75 : 1.75; dirx = which === 'L' ? -1 : 1; }
    if (back) dirx = -dirx, px = -px;
    const c = far ? mixCol(KURI.feet, PAL.inkSoft, .25) : KURI.feet;
    const r = arm2(px * u, py * u, a, b, dirx, .6 * u, .55 * u, .62 * u, .5 * u, c, c, line, sw * .9, u * .8, hooks, gap);
    hands[which] = r.h;
  };
  // feet
  const feet = side ? [[-.5, 1], [.7, 0]] : q ? [[-.6, 1], [1.1, 0]] : [[-.95, 0], [.95, 0]];
  feet.forEach(([fxp, far], i) => {
    rs('foot' + i);
    let lift = 0, sx = 0;
    if (o.walk != null) { const ph = (o.walk + (i ? .5 : 0)) * TAU; lift = Math.max(0, Math.sin(ph)) * .45; if (side || q) sx = Math.cos(ph) * .45; }
    colorIn(ellPts((fxp + sx) * u, (-.28 - lift) * u, .62 * u, .34 * u, 14), { col: far ? mixCol(KURI.feet, PAL.inkSoft, .25) : KURI.feet, fill: 'flat', line, lw: sw * .8 });
  });
  if (side || q) drawArm('L', true);
  // spikes: a spiky ball, coloured with radiating strokes
  rs('spikes');
  const cx = side ? -.35 : q ? -.3 : 0, cy = -2.35, S = [];
  const N = back ? 26 : 22;
  for (let i = 0; i < N * 2; i++) {
    const a = i / (N * 2) * TAU - Math.PI / 2, down = Math.sin(a);
    let r = (i % 2 ? 2.55 : 3.2 + .12 * Math.sin(i * 1.7));
    if (!back && down > .55) r = 2.35;                        // no spikes underneath
    if (side && Math.cos(a) > .45 && down > -.2) r = 2.3;     // nor in front of the face in profile
    if (q && Math.cos(a) > .7 && down > -.1) r = 2.3;
    S.push([cx + Math.cos(a) * r * 1.05, cy + Math.sin(a) * r * .92 + (i % 2 ? 0 : -.08 * (1 - Math.abs(Math.cos(a))) * (o.hair || 0))]);
  }
  colorIn(U(u, S), { col: spk, gap: gap * .7, ang: 1.2, w: cw, line, lw: sw, pale: .3, tone: KURI.spikesDk });
  for (let i = 0; i < 9; i++) {   // a few long spike strokes radiating out, for texture
    const a = -Math.PI + (i + .5) / 9 * Math.PI + (side ? -.4 : 0), r0 = 1.4, r1 = 2.7;
    crayonLine(U(u, [[cx + Math.cos(a) * r0, cy + Math.sin(a) * r0 * .9], [cx + Math.cos(a) * r1, cy + Math.sin(a) * r1 * .9]]), cw * .7, KURI.spikesDk, 0);
  }
  if (!back) {
    // ears
    rs('ears');
    const ears = side ? [[.55, -4.05]] : q ? [[-.55, -4.05], [1.55, -3.95]] : [[-1.4, -4.0], [1.4, -4.0]];
    ears.forEach(([ex, ey]) => { colorIn(ellPts(ex * u, ey * u, .5 * u, .48 * u, 12), { col: KURI.feet, fill: 'flat', line, lw: sw * .8 }); dab(ex * u, ey * u + .05 * u, .2 * u, PAL.rose, cw * .6); });
    // face / belly
    rs('face');
    const F = side ? ellPts(1.05 * u, -2.0 * u, 1.75 * u, 1.65 * u, 22) : q ? ellPts(.55 * u, -1.85 * u, 2.0 * u, 1.75 * u, 22) : ellPts(0, -1.85 * u, 2.15 * u, 1.8 * u, 22);
    colorIn(F, { col: faceC, gap: gap * .9, ang: .5, w: cw * .8, line, lw: sw, pale: .3, tone: mixCol(faceC, PAL.peachDk, .35) });
    // snout + nose
    const nx = side ? 3.1 : q ? 1.35 : 0, ny = side ? -1.85 : -1.7;
    if (side) colorIn(ellPts(2.3 * u, -1.9 * u, .9 * u, .5 * u, 18, 0, .12), { col: faceC, fill: 'flat', line, lw: sw * .85 });   // snout
    paint(ellPts(nx * u, ny * u, .34 * u, .26 * u, 12), { wash: KURI.nose, ink: line, sw: sw * .6 });
    paint(ellPts((nx - .1) * u, (ny - .09) * u, .1 * u, .07 * u, 8), { wash: PAL.cream, ink: null });
    const eyes = Array.isArray(o.eyes) ? o.eyes : [o.eyes || 'normal', o.eyes || 'normal'];
    const blink = blinkK(o), E = k => blink && OPEN_EYES.includes(k) ? 'closed' : k;
    const ex = side ? [[1.7, 1]] : q ? [[-.05, -1], [1.35, 1]] : [[-.78, -1], [.78, 1]];
    ex.forEach(([e1, s1], i) => eyeMark(E(eyes[side ? 1 : i]), e1 * u, -2.5 * u, u * 1.25, o, s1, sw));
    browMarks(o.brows, ex.map(([e1, s1]) => [e1 * u, s1]), -3.2 * u, u, sw);
    cheeks(side ? [1.4 * u] : q ? [-.5 * u, 1.95 * u] : [-1.4 * u, 1.4 * u], -1.75 * u, .38 * u, .35 + .65 * (o.blush || 0), sw);
    mouthMark(o.mouth === undefined ? 'cat' : o.mouth, (side ? 2.5 : nx) * u, (side ? -1.45 : -1.1) * u, u * .8, sw);
  } else {
    rs('ears');
    [[-1.4, -4.0], [1.4, -4.0]].forEach(([ex, ey]) => colorIn(ellPts(ex * u, ey * u, .45 * u, .42 * u, 12), { col: mixCol(KURI.feet, PAL.inkSoft, .2), fill: 'flat', line, lw: sw * .8 }));
  }
  if (side || q) drawArm('R', false); else { drawArm('L', false); drawArm('R', false); }
  rs('draw'); if (o.draw) o.draw(u, sw);
  pop();
  rs('emote');
  if (o.emote) emote(o.emote, x + (o.flip ? -1 : 1) * 2.6 * u, y + dy - 5.4 * u * (1 - sq), u * .85, o.emoteK ?? 1, o.emoteAge ?? T);
  rs('after');
  const W2 = xform(x, y + dy, o.rot, fx, fy);
  return { head: W2(0, -2.3 * u), top: W2(0, -5.2 * u), handL: hands.L ? W2(...hands.L) : null, handR: hands.R ? W2(...hands.R) : null, feet: [x, y] };
}

// ---------- moods ----------
// Each emotion: a face (eyes, mouth, brows, blush), an emote, a take size, and an idle body motion locked to the beat.
const _b = t => { const bp = bpOf(t), s1 = Math.sin(bp * Math.PI); return { bp, s1, ab: Math.abs(s1), hit: pulse(t), s2: Math.sin(bp * TAU), f: frac(bp) }; };
const EMO = {
  neutral:    { eyes: 'normal', mouth: 'smile', take: .3, body: t => { const b = _b(t); return { dy: -.12 * b.ab, sq: .02 * b.hit, aL: -1.22 + .04 * b.s1, aR: -1.2 - .04 * b.s1 }; } },
  happy:      { eyes: 'happy', mouth: 'grin', blush: .4, take: .6, body: t => { const b = _b(t); return { dy: -.45 * b.ab, sq: .06 * b.hit, aL: -.95 + .2 * b.s1, aR: -.95 - .2 * b.s1, bL: .5, bR: .5 }; } },
  laugh:      { eyes: 'squeeze', mouth: 'laugh', blush: .6, take: .8, body: t => { const c = Math.abs(Math.sin(t * TAU * 4.5)); return { dy: -.25 * c, sq: .06 * c - .03, rot: -.05 + .03 * Math.sin(t * TAU * 4.5), aL: -1.3, aR: -1.3, bL: 1.7 + .15 * c, bR: 1.7 + .15 * c }; } },
  excited:    { eyes: 'shine', mouth: 'laugh', emote: 'spark', blush: .4, take: 1, body: t => { const b = _b(t), h = Math.abs(b.s2); return { dy: -1.1 * h, sq: .12 * pulse2(t) - .05 * h, aL: .9 + .35 * Math.sin(b.bp * TAU * 2), aR: .9 - .35 * Math.sin(b.bp * TAU * 2), bL: .2, bR: .2 }; } },
  love:       { eyes: 'heart', mouth: 'cat', blush: 1, emote: 'hearts', take: .7, body: t => { const b = _b(t), s = Math.sin(b.bp * Math.PI / 2); return { rot: .06 * s, dy: -.2 * b.ab, aL: -1.15, aR: -1.15, bL: 2.3, bR: 2.3 }; } },
  shy:        { eyes: 'look', mouth: 'pout', blush: 1, take: .3, body: t => { const b = _b(t), s = Math.sin(b.bp * Math.PI / 2); return { lookX: -.7, lookY: .8, sq: .04, rot: -.05 + .02 * s, aL: -1.35, aR: -1.35, bL: 1.1, bR: 1.1 }; } },
  proud:      { eyes: 'closed', mouth: 'grin', brows: 'up', blush: .3, emote: 'spark', take: .5, body: t => { const b = _b(t); return { sq: -.06 - .02 * b.ab, dy: -.1 * b.hit, aL: -.55, aR: -.55, bL: -1.8, bR: -1.8, rot: .02 * b.s1 }; } },
  curious:    { eyes: 'look', mouth: 'o', brows: 'up', emote: '?', take: .5, body: t => { const b = _b(t); return { lookX: .7, rot: .07 + .02 * b.s1, dy: -.08 * b.ab, aL: -1.25, aR: -1.05, bR: 2.25 }; } },
  thinking:   { eyes: 'look', mouth: 'flat', brows: 'worried', emote: 'dots', take: .4, body: t => { const b = _b(t); return { lookX: .4, lookY: -.8, rot: .04, aR: -1.05, bR: 2.35, aL: -1.25, dy: -.05 * b.ab }; } },
  idea:       { eyes: 'shine', mouth: 'grin', brows: 'up', emote: 'bulb', take: 1.1, body: t => { const b = _b(t); return { dy: -.5 * b.ab, sq: -.04 + .06 * b.hit, aR: 1.25 + .08 * b.s2, bR: .15, aL: -1.1 }; } },
  surprised:  { eyes: 'wide', mouth: 'O', brows: 'up', emote: '!', fade: true, take: 1.3, body: t => { const b = _b(t); return { sq: -.1, dy: -.2 - .1 * b.ab, aL: .35 + .05 * b.s2, aR: .35 - .05 * b.s2, bL: .6, bR: .6 }; } },
  scared:     { eyes: 'scared', mouth: 'wobble', brows: 'worried', emote: 'sweat', take: 1.1, body: t => ({ dx: .06 * Math.sin(t * TAU * 20), sq: .06, aL: -.35 + .06 * Math.sin(t * TAU * 17), aR: -.35 + .06 * Math.sin(t * TAU * 19), bL: 2.1, bR: 2.1, lookX: .6 * Math.sign(Math.sin(t * 2.3)) }) },
  sad:        { eyes: 'sad', mouth: 'frown', brows: 'worried', emote: 'cloud', take: .3, body: t => { const b = _b(t), s = Math.sin(b.bp * Math.PI / 4); return { sq: .07 + .02 * s, rot: .025 * s, aL: -1.42, aR: -1.42, bL: .05, bR: .05, lookY: .6 }; } },
  cry:        { eyes: 'cry', mouth: 'wail', brows: 'worried', blush: .5, take: .8, body: t => { const b = _b(t), sob = Math.sin(b.f * Math.PI) * Math.exp(-b.f * 2); return { sq: .1 * sob - .02, dy: -.35 * sob, aL: -.95, aR: -.95, bL: 2.45 + .1 * Math.sin(t * TAU * 5), bR: 2.45 - .1 * Math.sin(t * TAU * 5), rot: .03 * b.s1 }; } },
  angry:      { eyes: 'angry', mouth: 'frown', brows: 'angry', emote: 'anger', blush: .5, take: .8, body: t => { const b = _b(t); return { dx: .05 * Math.sin(t * TAU * 16), sq: .08 * b.hit, aL: -1.05, aR: -1.05, bL: -.25, bR: -.25 }; } },
  sleepy:     { eyes: 'sleepy', mouth: 'o', emote: 'zzz', take: .2, body: t => { const br = Math.sin(t * TAU * .3); return { sq: .04 + .04 * br, rot: .05 * Math.sin(t * .8), aL: -1.4, aR: -1.4, bL: .05, bR: .05 }; } },
  determined: { eyes: 'angry', mouth: 'flat', brows: 'angry', take: .7, body: t => { const b = _b(t), p = Math.sin(b.f * Math.PI); return { rot: .05, sq: -.03 + .05 * b.hit, dy: -.12 * b.ab, aL: -.65 + .3 * p, aR: -.65 + .3 * p, bL: 2.0, bR: 2.0 }; } },
  relieved:   { eyes: 'closed', mouth: 'smile', emote: 'sweat', take: .4, body: t => { const br = Math.sin(t * TAU * .35); return { sq: .04 + .04 * br, aL: -1.35, aR: -1.35, bL: .1, bR: .1 }; } },
};
function feel(name, t, over = {}) {
  const E = EMO[name] || EMO.neutral;
  return { eyes: E.eyes, mouth: E.mouth, brows: E.brows || null, blush: E.blush || 0, emote: E.emote, ...(E.body ? E.body(t) : {}), ...over };
}
// An emotion timeline with ACTED changes: keys = [[t0, 'neutral'], [t1, 'surprised'], [t2, 'happy', { emote: null }]].
// Before each change the eyes squeeze and the body squashes (anticipation); the face swaps under the squint; a take the
// size of the new emotion fires; the body settles into the new idle with overshoot; blush cross-fades; the emote pops.
function emotions(t, keys, o = {}) {
  let i = 0; while (i + 1 < keys.length && t >= keys[i + 1][0]) i++;
  const [tc, name, over] = keys[i], age = t - tc, cur = feel(name, t, over);
  const tn = i + 1 < keys.length ? keys[i + 1][0] : Infinity, tkS = o.take ?? 1;
  const E = EMO[name] || EMO.neutral;
  let squint = cur.squint || 0;
  if (tn - t < .1) squint = Math.max(squint, 1 - (tn - t) / .1);
  if (i > 0 && age < .14) squint = Math.max(squint, 1 - age / .14);
  const prev = i > 0 ? feel(keys[i - 1][1], t, keys[i - 1][2]) : null;
  if (prev && age < .5) {
    const base = { dy: 0, sq: 0, aL: -1.2, aR: -1.2, bL: .2, bR: .2, rot: 0, dx: 0, lookX: 0, lookY: 0 };
    const k = backOut(seg(age, 0, .4)), kc = ease(seg(age, 0, .3));
    for (const f in base) cur[f] = lerp(prev[f] ?? base[f], cur[f] ?? base[f], k);
    cur.blush = lerp(prev.blush || 0, cur.blush || 0, kc);
  }
  const t1 = prev ? take(t, tc, (E.take ?? .6) * tkS) : { sq: 0, dy: 0 };
  const En = i + 1 < keys.length ? EMO[keys[i + 1][1]] || EMO.neutral : null, t2 = En ? take(t, tn, (En.take ?? .6) * tkS) : { sq: 0, dy: 0 };
  cur.sq = (cur.sq || 0) + t1.sq * .7 + t2.sq * .7; cur.dy = (cur.dy || 0) + t1.dy * .6 + t2.dy * .6;
  cur.squint = squint;
  const same = prev && prev.emote === cur.emote;
  cur.emoteK = same ? 1 : seg(age, .06, .32) * (E.fade && !(over && over.emote) ? 1 - seg(age, 1.4, 1.8) : 1);
  cur.emoteAge = age;
  return cur;
}
// A walk cycle at phase ph (1 = one full stride): legs, arm swing, bob and a little sway. Spread it into a character.
// For side view pass side = true (arms swing forward/back instead of out/in).
function walkCycle(ph, side = true, amt = 1) {
  const s = Math.sin(ph * TAU), b = Math.abs(Math.sin(ph * TAU));
  return side ? { walk: ph, dy: -.28 * b * amt, aL: -1.35 + .55 * s * amt, aR: -1.35 - .55 * s * amt, bL: .35, bR: .35, rot: .03 * amt }
              : { walk: ph, dy: -.22 * b * amt, aL: -1.2 + .25 * s * amt, aR: -1.2 - .25 * s * amt, rot: .025 * s * amt };
}
// Merge poses: later ones win, except dy / sq / rot / dx, which add (so a mood's bounce and a jump combine).
function pose(...ps) {
  const out = {};
  for (const p of ps) for (const k in p) out[k] = ['dy', 'sq', 'rot', 'dx'].includes(k) ? (out[k] || 0) + (p[k] || 0) : p[k];
  return out;
}
