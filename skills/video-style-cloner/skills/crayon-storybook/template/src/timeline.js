// timeline.js: the shot list, standalone loops and the timeline-level transitions (page turn).
//
// shots([[t0, fn], [t1, fn, opts], ...]) registers shots in time order. Each fn(t, lt, dur) is called with t = video
// time, lt = time since the shot started, dur = the shot's length. It paints the WHOLE frame, background included, and
// must be a pure function of t: frames render in parallel and out of order, so nothing may carry over between frames.
//
// opts.turn = seconds: the shot arrives by a PAGE TURN. For that long after t1 the previous shot keeps playing
// (called with lt > its dur, so let its motion settle rather than end abruptly) on the page that curls away, revealing
// this shot underneath. opts.turnDir = 1 (default: the page turns right → left, like a book) or -1.

const SHOTS = [];
function shots(list) { SHOTS.push(...list); SHOTS.sort((a, b) => a[0] - b[0]); }

// Standalone loops (model sheets, GIFs, tests), outside the main timeline: window.LOOP = LOOPS[name] swaps the whole
// frame for that function, called with loop time. Give each a length: LOOPS.x = t => { ... }; LOOPS.x.len = 4;
const LOOPS = {};

function drawWorld(t) {
  if (window.LOOP) window.LOOP(t);
  else if (!SHOTS.length) placeholder(t);
  else {
    let i = 0; while (i + 1 < SHOTS.length && t >= SHOTS[i + 1][0]) i++;
    const t0 = SHOTS[i][0], end = i + 1 < SHOTS.length ? SHOTS[i + 1][0] : DUR, opt = SHOTS[i][2] || {};
    if (opt.turn && i > 0 && t - t0 < opt.turn) {
      // page turn: paint the previous shot, keep it as the turning page, then paint this one underneath
      const [p0, pfn] = SHOTS[i - 1];
      stageReset(); pfn(t, t - p0, t0 - p0); CAM = null; flushLetters();
      snapshotPage();
      const keep = { ...STAGE };
      clearToPaper(); stageReset(); boilSeed('frame');
      STAGE.turn = { p: (t - t0) / opt.turn, dir: opt.turnDir || 1, prevStage: keep };
    }
    SHOTS[i][1](t, t - t0, end - t0);
    CAM = null;
  }
  flushLetters();
}

function placeholder(t) {
  paperWash(t);
  const k = feel('happy', t);
  lulu(820, 860, 44, k); kuri(1120, 860, 40, { ...feel('happy', t + .3), seed: 2 });
}

// ---------- crayon wipe ----------
// Fat crayon zigzags scribble across to cover the frame (p 0 → .5), then are scribbled away (p .5 → 1).
// Cut to the next shot at p = .5, under full cover. Call it last in both shots, in screen space (outside a camera):
//   end of shot A:   if (lt > dur - .35) crayonWipe((lt - (dur - .35)) / .7);
//   start of shot B: if (lt < .35) crayonWipe(.5 + lt / .7);
function crayonWipe(p, cols = [PAL.butter, PAL.rose, PAL.sky]) {
  if (p <= 0 || p >= 1) return;
  boilSeed('wipe');
  const n = 4, bh = (H + 300) / n;
  for (let i = 0; i < n; i++) {
    const d = [0, .12, .05, .16][i];
    const q = p < .5 ? easeOut(clamp((p * 2 - d) / (1 - d))) : ease(clamp(((p - .5) * 2 - d) / (1 - d)));
    const x0 = p < .5 ? -200 : lerp(-200, W + 300, q), x1 = p < .5 ? lerp(-200, W + 300, q) : W + 300;
    if (x1 - x0 < 30) continue;
    const y0 = -150 + i * bh, col = cols[i % cols.length];
    paint(rectPts(x0, y0 - 10, x1 - x0, bh + 20, 6), { wash: mixCol(col, PAL.paper, .25), ink: null });
    scribbleFill(rectPts(x0, y0 - 10, x1 - x0, bh + 20), mixCol(col, PAL.ink, .12), { ang: 1.35 + i * .15, gap: 26, w: 1.2, over: 0 });
  }
}
// kept for compatibility with painted-animation scene code
const brushWipe = (p, cols) => crayonWipe(p, cols);
