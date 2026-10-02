// xz_shots.js: the shots of 小镇姑娘 (see STORYBOARD.md), cut to the song: 154 BPM, one lyric line = 8 beats ≈ 3.1 s.
// Times in comments are clip times (song time − 146.887 s). The half-time pulse (BEAT = .778 s) lands on 0, .778, 1.556 …
(() => {
  const L0 = LOOK.dusk, LS = LOOK.sepia, LN = LOOK.night;
  const SEPW = ['#9A7250', '#D8BE8E'];                     // brush-wipe colours into the memory
  // a suitcase carried in one hand: undo the arm's rotation so it hangs straight down (side = side-view arm)
  const carry = (a, L, side) => (u, sw) => { push(); rotate(side ? a - .7 : a); suitcase(0, 3.9 * u * .55, u * .55, L); pop(); };

  // ---------- A · 0–3.02 · intro, dusk, now: me alone on the bench with my suitcase, looking down the empty line ----------
  function shotA(t, lt, dur) {
    camBegin(1080 + 30 * Math.sin(lt * .6), 650 - 10 * lt, 1.3 + .07 * lt);
    skyBg(L0, t); townBg(L0, t); trackBed(L0); platform(L0);
    lampPost(640, L0, .6 + .4 * seg(lt, .5, 1.1));
    bench(1160, 930, L0);
    suitcase(1400, 932, 22, L0);
    const m = emotions(lt, [[0, 'bored', { lookX: -.9, emote: null }], [1.56, 'sad', { lookX: -1, lookY: .2, emote: null }]], { take: .6 });
    me(1140, 868, 24, { ...m, view: 'q', flip: true }, L0);
    const at = toScreen(1140, 868 - 4 * 24);
    camEnd();
    if (lt < .6) iris(...at, lerp(0, 1500, easeIn(lt / .6)), PAL.night);
    boilSeed('wipe');
    if (lt > dur - .3) brushWipe((lt - (dur - .3)) / .6, SEPW);
  }

  // ---------- B · 3.02–6.07 · 还记得一年前站在火车站: the memory, she leaves on the train ----------
  const XF_B = 1620, DOOR_B = XF_B + TRAIN.door;           // the train stands still; its door is at x 370
  const herB = lt => emotions(lt, [[0, 'sad', { lookX: .6, emote: null }], [.62, 'determined', { lookX: -.5 }], [2.4, 'sad', { lookX: .8, eyes: 'teary', emote: null }]], { take: .7 });
  const herDoor = (lt, L) => (dx, fy) => her(dx, fy, 21, { ...herB(lt), ...turn(lt, 2.4, 2.58, -.25, 0), aL: -.6, armL: carry(-.6, L) }, L);
  function shotB(t, lt, dur) {
    camBegin(880 + 25 * Math.sin(lt * .5), 560, 1.02 + .03 * lt);
    skyBg(LS, t); townBg(LS, t); trackBed(LS);
    train(XF_B, LS, 0, { door: 1, inDoor: lt > 2.35 ? herDoor(lt, LS) : null });
    steam(t, () => [XF_B + TRAIN.chimney, RAIL - 430], LS, { each: 1, grow: .6, life: 2.4 });
    platform(LS); lampPost(1840, LS, 0);
    // her: face me → turn to the door → walk → hop up into the doorway
    if (lt < 2.35) {
      const m = herB(lt), w = stroll(lt, .92, 1.85, 620, 450, 24);
      let pose;
      if (lt < .75) pose = { view: 'q' };
      else if (lt < .92) pose = turn(lt, .75, .92, .125, -.25);
      else if (lt < 1.95) pose = { view: 'side', flip: true, walk: w.walk, dy: w.dy };
      else pose = { view: 'side', flip: true, ...jump(lt, 2.0, 2.35, 2.2) };
      const k = ease(seg(lt, 2.0, 2.35)), x = lt < 1.95 ? w.x : lerp(450, DOOR_B, k), y = lt < 2.0 ? 900 : lerp(900, RAIL - 100, k);
      const side = pose.view === 'side';
      her(x, y, lerp(24, 21, k), { ...m, ...pose, dy: (pose.dy || 0) + (lt < 1.95 ? (m.dy || 0) * .3 : 0), aL: side ? -.3 : -.6, armL: carry(side ? -.3 : -.6, LS, side) }, LS);
    }
    // me: watch her go, then step after her with a hand out
    const mm = emotions(lt, [[0, 'sad', { lookX: -.7, emote: null }], [.9, 'nervous', { lookX: -.9, emote: null }], [2.05, 'surprised', { lookX: -1, lookY: -.4 }]], { take: .8 });
    const w = stroll(lt, 2.1, 2.9, 880, 660, 24), reach = ease(seg(lt, 2.05, 2.35));
    me(w.x, 900, 24, { ...mm, view: 'q', flip: true, walk: w.walk, dy: (mm.dy || 0) + w.dy, aL: lerp(mm.aL ?? .2, 1.05, reach), aR: lerp(mm.aR ?? .2, -.4, reach) }, LS);
    camEnd();
    filmFX(t);
    boilSeed('wipe');
    if (lt < .3) brushWipe(.5 + lt / .6, SEPW);
  }

  // ---------- C · 6.07–9.08 · 看着自己的悲剧演完: the door shuts; a spotlight on me; the curtain falls ----------
  function shotC(t, lt, dur) {
    const push_ = ease(seg(lt, .5, 1.6));
    camBegin(lerp(880, 700, push_), lerp(560, 740, push_), lerp(1.08, 1.45, push_));
    skyBg(LS, t); townBg(LS, t); trackBed(LS);
    train(XF_B, LS, 0, { door: 1 - ease(seg(lt, .08, .45)), inDoor: lt < .6 ? herDoor(lt + 3.05, LS) : null });
    steam(t, () => [XF_B + TRAIN.chimney, RAIL - 430], LS, { each: 1, grow: .6, life: 2.4 });
    platform(LS);
    const m = emotions(lt, [[0, 'surprised', { lookX: -1, lookY: -.4, emote: null }], [.55, 'sad', { lookX: -.6, lookY: .3 }], [1.6, 'cry']], { take: .7 });
    const drop = ease(seg(lt, .4, .9));
    me(660, 900, 24, { ...m, view: 'q', flip: true, aL: lerp(1.05, m.aL ?? -.7, drop), aR: lerp(-.4, m.aR ?? -.7, drop) }, LS);
    const at = toScreen(660, 900 - 4 * 24);
    glow(660, 820, 260, '#FFF0C8', .5 * seg(lt, .7, 1.3));
    camEnd();
    spotDark(at[0], at[1] - 10, lerp(900, 360, ease(seg(lt, .6, 1.4))), .82 * seg(lt, .6, 1.3));
    filmFX(t);
    curtains(seg(lt, 1.95, 2.85), t);
  }

  // ---------- D · 9.08–12.38 · 透过玻璃窗看见你的泪满面: through the train window, her face full of tears ----------
  function shotD(t, lt, dur) {
    const slide = 1500 * easeIn(seg(lt, 2.3, 3.3)), shake = lt > 2.1 ? shakeXY(t, 3) : [0, 0];
    camBegin(960 + shake[0], 540 + shake[1], 1 + .03 * seg(lt, 0, 2.3));
    const wx = 560 + slide, wy = 170, ww = 800, wh = 660, C = LS.train, D = LS.trainDk;
    boilSeed('cabin');
    paint(rectPts(wx - 40, wy - 40, ww + 80, wh + 80), { wash: '#8A6A50', fill: '#5E4430', fillOp: 90, tex: .6, ink: null });
    paint(rrPts(wx + 60, wy + 330, 280, 360, 30), { wash: '#7A4E3A', ink: PAL.ink, sw: 1 });   // seat backs
    paint(rrPts(wx + ww - 330, wy + 330, 280, 360, 30), { wash: '#7A4E3A', ink: PAL.ink, sw: 1 });
    const m = emotions(lt, [[0, 'sad', { lookX: -.2, eyes: 'teary', emote: null }], [.85, 'cry']], { take: .6 });
    const press = ease(seg(lt, 1.6, 1.95));
    her(wx + ww / 2, wy + 740, 62, { ...m, aL: lerp(m.aL ?? .2, -.5, press), aR: lerp(m.aR ?? .2, 1.35, press) }, LS);
    if (press > .5) paint(ellPts(wx + ww / 2 + 330, wy + 250, 46, 40, 16), { fill: PAL.cream, fillOp: 70, bleed: .2, ink: null });   // her paw fogging the glass
    // my faint reflection in the glass (this is my point of view)
    boilSeed('refl');
    paint(rectPts(wx + ww - 230, wy + wh - 190, 190, 120, 3), { wash: PAL.clay, washOp: 45, ink: null });
    for (const ex of [-45, 45]) paint(rectPts(wx + ww - 135 + ex - 8, wy + wh - 165, 16, 34), { wash: PAL.ink, washOp: 60, ink: null });
    // glass glare
    paint([[wx + 80, wy], [wx + 190, wy], [wx + 20, wy + 240], [wx, wy + 240], [wx, wy + 120]], { fill: PAL.cream, fillOp: 70, bleed: .1, ink: null });
    paint([[wx + 560, wy + wh], [wx + 640, wy + wh], [wx + ww, wy + 380], [wx + ww, wy + 480]], { fill: PAL.cream, fillOp: 50, bleed: .1, ink: null });
    // the carriage wall around the window (and the next, empty window behind)
    boilSeed('wall');
    const wall = o => paint(o, { wash: C, fill: D, fillOp: 60, tex: .6, bleed: .03, ink: null });
    wall(rectPts(-3000, -200, W + 6000, wy + 200)); wall(rectPts(-3000, wy + wh, W + 6000, 600));
    wall(rectPts(wx + ww, wy - 10, W + 3000, wh + 20)); wall(rectPts(wx - 1300, wy - 10, 1300, wh + 20));
    paint(rectPts(wx - 2100 + 60, wy, 800 - 120, wh), { wash: '#8A6A50', fill: mixCol(LS.sky2, '#5E4430', .5), fillOp: 80, ink: PAL.ink, sw: 2 });
    wall(rectPts(-3000, wy - 10, wx - 2100 + 60 + 3000, wh + 20));
    paint(rrPts(wx, wy, ww, wh, 40), { ink: PAL.ink, sw: 2.4 });
    paint(rectPts(-3000, wy + wh + 60, W + 6000, 34), { wash: LS.trim, washOp: 220, ink: null });
    for (let i = -8; i < 8; i++) paint(ellPts(wx - 60 + i * 150, wy - 60, 7, 7, 8), { wash: D, ink: PAL.ink, sw: .5 });
    camEnd();
    filmFX(t);
    curtains(1 - seg(lt, 0, .6), t);
  }

  // ---------- E · 12.38–15.39 · 那车头依然吐着烟: the engine puffs away; I run after it; smoke swallows the frame ----------
  const T_E = 12.38, xfE = tt => XF_B + 80 + 200 * Math.pow(Math.max(0, tt - T_E + .6), 2);   // accelerating right
  function shotE(t, lt, dur) {
    camBegin(960 + 120 * ease(seg(lt, 0, 2.4)), 520, .92);
    skyBg(LS, t); townBg(LS, t); trackBed(LS);
    const xf = xfE(t);
    train(xf, LS, xf - XF_B, { door: 0, window: (x, y, w, h, i) => { if (i === 0 && lt < 1.5) her(x + w / 2, y + h + 70, 13, { ...feel('cry', t), noShadow: true }, LS); } });
    steam(t, te => [xfE(te) + TRAIN.chimney, RAIL - 430], LS, { each: .5, grow: 1.35, life: 3.0, wind: 110 });
    platform(LS);
    const run = seg(lt, .15, 1.4), x = lerp(640, 1220, ease(run)), running = lt > .15 && lt < 1.45;
    const m = emotions(lt, [[0, 'determined'], [1.45, 'sad', { emote: null, lookX: 1, lookY: -.3 }], [2.2, 'cry']], { take: .6 });
    const pose = running ? { view: 'side', walk: (x - 640) / 96, dy: -Math.abs(Math.sin((x - 640) / 96 * Math.PI)) * .7, rot: -.08, aL: .6 * Math.sin(lt * 16) } : { view: 'q', ...jump(lt, 1.38, 1.5, .4) };
    const wave = lt > 1.6 ? 1.25 + .45 * Math.sin((lt - 1.6) * 12) : null;
    me(x, 900, 24, { ...m, ...pose, sq: (m.sq || 0) + (pose.sq || 0), dy: (running ? 0 : m.dy || 0) + (pose.dy || 0), ...(wave != null ? { aR: wave } : {}) }, LS);
    camEnd();
    filmFX(t);
    if (lt > dur - 1.0) smokeWipe((lt - (dur - 1.0)) / 2.0);
  }

  // ---------- F · 15.39–19.4 · 听说现在的你成了大经理: the waiting-room TV. 大经理 → 大锦鲤 ----------
  // "经理" is sung at ≈ 17.6: the TV poofs her into a koi on that word, as the lyric gets struck through to 锦鲤.
  // The koi leaps out of the screen on the next line (18.64, 前途好比…).
  const SCR = { x: 1120, y: 190, w: 500, h: 420 }, SC = [SCR.x + SCR.w / 2, SCR.y + SCR.h / 2];
  const T_POOF = 17.5 - 15.39, T_LEAP = 18.64 - 15.39, LEAP = .76;
  function room(t) {
    boilSeed('room');
    paint(rectPts(-300, -300, W + 600, 1050), { wash: '#3A3462', fill: PAL.indigo, fillOp: 80, tex: .6, bleed: .05, ink: null });
    paint(rectPts(-300, 700, W + 600, 210), { wash: '#5A3F4E', fill: '#3E2A38', fillOp: 70, tex: .6, ink: PAL.ink, sw: 1 });
    for (let i = 0; i < 16; i++) inkLine([[-200 + i * 150, 705], [-200 + i * 150, 905]], .6, '#3E2A38', 'inkfine', 0);
    paint(rectPts(-300, 900, W + 600, 500), { wash: '#4A3A48', fill: '#2B2233', fillOp: 50, tex: .6, ink: PAL.ink, sw: 1 });
    // window: the night outside, the platform lamp
    paint(rectPts(110, 190, 400, 370, 2), { wash: LN.sky, fill: LN.sky2, fillOp: 90, tex: .5, ink: null });
    for (let i = 0; i < 8; i++) { boilSeed('ws' + i); paint(starPts(140 + hash(i) * 340, 220 + hash(i + 5) * 200, 4 + 4 * hash(i + 1), .35, 4), { wash: PAL.cream, washOp: 200, ink: null }); }
    boilSeed('win');
    glow(430, 300, 120, '#FFC766', .7);
    inkLine([[310, 190], [310, 560]], 2.2, '#2B2233', 'ink', 0); inkLine([[110, 375], [510, 375]], 2.2, '#2B2233', 'ink', 0);
    paint(rectPts(110, 190, 400, 370, 2), { ink: PAL.ink, sw: 2 });
    paint(rectPts(90, 555, 440, 24), { wash: '#6B4A3A', ink: PAL.ink, sw: 1 });
    // wall clock (late)
    paint(ellPts(760, 250, 62, 62, 24, 1), { wash: PAL.cream, fill: PAL.ochre, fillOp: 30, ink: PAL.ink, sw: 1.2 });
    inkLine([[760, 250], [760 + 30 * Math.sin(5.9), 250 - 30 * Math.cos(5.9)]], 1.6, PAL.ink, 'ink', 0);
    inkLine([[760, 250], [760 + 45 * Math.sin(t * .5), 250 - 45 * Math.cos(t * .5)]], 1, PAL.ink, 'ink', 0);
    // TV cabinet
    paint(rectPts(1090, 700, 700, 200, 2), { wash: '#6B4A3A', fill: '#4A3028', fillOp: 70, tex: .5, ink: PAL.ink, sw: 1 });
  }
  function tvScreen(t, lt) {
    const { x, y, w, h } = SCR;
    boilSeed('scr');
    if (lt > .4 && lt < .75) {   // a flick of static as the channel changes, behind the clearing smoke
      paint(rectPts(x, y, w, h), { wash: '#5E6C78', ink: null });
      for (let i = 0; i < 14; i++) { const yy = y + hash(i + BOILN * 3) * h; inkLine([[x, yy], [x + w, yy + jit(3)]], .8 + 1.5 * hash(i), hash(i + 1) > .5 ? PAL.cream : '#2B2233', 'dry', 0); }
      return;
    }
    // the award stage: red backdrop and a gold sunburst
    paint(rectPts(x, y, w, h), { wash: '#A8453E', ink: null });
    push(); translate(...SC); rotate(t * .3);
    for (let i = 0; i < 10; i++) { const a = i / 10 * TAU; paint([[0, 0], [Math.cos(a) * 250, Math.sin(a) * 250], [Math.cos(a + .3) * 250, Math.sin(a + .3) * 250]], { wash: '#E8AA38', washOp: 110, ink: null }); }
    pop();
    const koiOn = lt > T_POOF + .14;
    if (!koiOn) {
      paint(rectPts(SC[0] - 90, y + h - 120, 180, 120, 2), { wash: '#6B4A3A', fill: PAL.ochre, fillOp: 40, ink: PAL.ink, sw: .8 });   // podium
      paint(starPts(SC[0], y + h - 70, 22, .45, 5), { wash: PAL.ochre, ink: PAL.ink, sw: .5 });
      her(SC[0], y + h - 118, 19, { ...feel('proud', t), tie: true }, LN);
    } else if (lt < T_LEAP) {
      koi(SC[0], SC[1] - 20 + 12 * Math.sin(t * 3), 150, -.05 + .06 * Math.sin(t * 2.4), t, { tie: true });
    }
    // confetti (stage) or rising gold coins (koi)
    for (let i = 0; i < 18; i++) {
      boilSeed('cf' + i);
      const cx = x + hash(i) * w, ph = frac(t * (.5 + .3 * hash(i + 2)) + hash(i + 4));
      if (!koiOn) paint(rectPts(cx + 10 * Math.sin(t * 3 + i), y + ph * h, 12, 7), { wash: [PAL.rose, PAL.ochre, PAL.sky, PAL.cream][i % 4], ink: null });
      else if (i < 10) paint(ellPts(cx, y + h - ph * h, 11 * Math.abs(Math.cos(t * 4 + i)) + 2, 11, 10), { wash: '#F4C24A', ink: PAL.ink, sw: .4 });
    }
    // the crowd along the bottom: clapping for the manager, then bowing to the koi (on the beat)
    for (let i = 0; i < 6; i++) {
      const cx = x + 45 + i * 82, bow = koiOn ? Math.max(0, Math.sin((bpOf(t) + i * .08) * Math.PI)) : 0;
      clawd(cx, y + h + 14, 9, koiOn ? { eyes: 'closed', rot: bow * .5, sq: .1 * bow, aL: 1.3, aR: 1.3, noShadow: true, noLegs: true, view: 'back' }
                                     : { ...move('hop', t + i * .1), eyes: 'happy', view: 'back', noShadow: true, noLegs: true, aL: 1.2 + .3 * Math.sin(t * 20 + i), aR: 1.2 - .3 * Math.sin(t * 20 + i) });
    }
    // the poof
    if (lt > T_POOF - .05 && lt < T_POOF + .55) {
      boilSeed('poof');
      const a = lt - T_POOF, r = a < .14 ? lerp(40, 260, easeOut(a / .14)) : lerp(260, 0, ease((a - .14) / .4));
      if (r > 5) paint(lumpy(SC[0], SC[1], r, r * .85, 3), { wash: PAL.cream, fill: '#D9CFE0', fillOp: 80, ink: PAL.ink, sw: .9 });
    }
  }
  function tvFrame(t) {
    boilSeed('tv');
    const col = '#7A5A48', dk = '#4A3428', { x, y, w, h } = SCR;
    const piece = P => paint(P, { wash: col, fill: dk, fillOp: 60, tex: .5, ink: null });
    piece(rectPts(1070, 140, 720, y - 140)); piece(rectPts(1070, y + h, 720, 700 - y - h)); piece(rectPts(1070, y, x - 1070, h)); piece(rectPts(x + w, y, 1790 - x - w, h));
    paint(rrPts(1070, 140, 720, 560, 40), { ink: PAL.ink, sw: 1.6 });
    paint(rrPts(x, y, w, h, 24), { ink: PAL.ink, sw: 2 });
    for (const [ky, r] of [[260, 34], [370, 34]]) { paint(ellPts(1705, ky, r, r, 16), { wash: dk, ink: PAL.ink, sw: .9 }); inkLine([[1705, ky], [1705 + r * .8 * Math.cos(ky), ky + r * .8 * Math.sin(ky)]], 1, PAL.cream, 'inkfine', 0); }
    for (let i = 0; i < 5; i++) inkLine([[1670, 460 + i * 22], [1740, 460 + i * 22]], .8, dk, 'inkfine', 0);
    inkLine([[1430, 140], [1330, 30]], 1.4, PAL.ink, 'ink', 0); inkLine([[1430, 140], [1560, 40]], 1.4, PAL.ink, 'ink', 0);
    paint(ellPts(1430, 138, 40, 16, 12), { wash: dk, ink: PAL.ink, sw: .9 });
  }
  function shotF(t, lt, dur) {
    const leap = seg(lt, T_LEAP, T_LEAP + LEAP);
    // push in on the TV for the joke, ease back out for the leap
    const pz = ease(seg(lt, 1.3, 2.0)) * (1 - ease(seg(lt, T_LEAP - .1, T_LEAP + .4)));
    camBegin(lerp(960, 1100, pz) - 120 * ease(leap), lerp(520, 470, pz), lerp(1.02, 1.16, pz) - .06 * ease(leap));
    room(t);
    const koiOn = lt > T_POOF + .14;
    glow(...SC, 560, koiOn ? '#FFD96A' : '#7FE0D2', koiOn ? .45 + .4 * Math.exp(-(lt - T_POOF) * 3) : .35);
    tvScreen(t, lt); tvFrame(t);
    bench(560, 930, LN); suitcase(830, 932, 22, LN);
    // me: watching → surprised (she's a big manager!) → proud of her → rubs eyes at the koi → ? → the koi flies over me
    const m = emotions(lt, [[0, 'neutral', { lookX: .9, lookY: -.3 }], [.95, 'surprised', { lookX: .9, lookY: -.4 }], [1.5, 'hopeful', { lookX: .9, lookY: -.4 }],
                            [T_POOF + .2, 'surprised', { lookX: .9, lookY: -.4, emote: '!!' }], [T_POOF + .7, 'confused', { lookX: .9, lookY: -.3 }],
                            [T_LEAP + .05, 'surprised', { lookX: -.6, lookY: -1 }], [T_LEAP + .45, 'starstruck', { lookX: -1, lookY: -.8 }]], { take: .8 });
    let pose = { view: 'q' };
    const rub = seg(lt, T_POOF + .3, T_POOF + .68);
    if (rub > 0 && rub < 1) pose = { view: 'front', eyes: 'squeeze', aL: 1.35 + .15 * Math.sin(lt * 30), aR: 1.35 - .15 * Math.sin(lt * 30), squint: 0 };
    me(560, 868, 30, { ...m, ...pose }, LN);
    // the leap: out of the screen, over my head, out through the window
    if (lt > T_LEAP) {
      const k = easeOut(leap), p = arcPt(SC, [260, 330], 330, k), q = arcPt(SC, [260, 330], 330, Math.min(1, k + .03));
      for (let i = 1; i < 7; i++) { const pp = arcPt(SC, [260, 330], 330, Math.max(0, k - i * .04)); boilSeed('tr' + i); paint(starPts(pp[0] + jit(6), pp[1] + jit(6), 16 - i * 1.6, .3, 4), { wash: '#FFE27A', ink: null }); }
      const sp = seg(lt, T_LEAP, T_LEAP + .4);
      if (sp < 1) for (let i = 0; i < 7; i++) { boilSeed('dr' + i); const a = -Math.PI / 2 + (i - 3) * .45, d = 60 + 400 * sp; paint(ellPts(SC[0] + Math.cos(a) * d, SC[1] + Math.sin(a) * d + 300 * sp * sp, 9, 12, 8), { wash: PAL.sky, ink: PAL.ink, sw: .5 }); }
      glow(p[0], p[1], 220, '#FFD96A', .6);
      koi(p[0], p[1], lerp(150, 210, k), Math.atan2(q[1] - p[1], q[0] - p[0]), t * 1.6, { tie: true });
    }
    camEnd();
    if (lt < 1.0) smokeWipe(.5 + lt / 2.0);
  }

  // ---------- G · 19.4–31.1 · the platform at night: the koi becomes her star; I wish her well; I leave ----------
  //   19.4–21.0 the koi swims up and becomes a star (…闪亮的星星) · 21.3–22.5 tilt down to me
  //   21.54 我只希望…: she smiles, I'm wistful → I clasp my hands → my wish floats up → her star glows
  //   25.01 我才能放心走: the night train pulls in → I take my case, wave to her star → hop aboard → it pulls out → her star, iris
  const T_G = 19.4, S = [1300, 90];                         // her star, in world space
  const T_STAR = 21.0, T_ARR = 24.9, T_STOP = 26.0, T_JUMP = 27.3, T_LAND = 27.68, T_SHUT = 28.25, T_GO = 28.6;
  const XF_STOP = 2150, T_WISH0 = 23.55, T_WISH1 = 24.45;   // my wish: a little light that floats up to her star
  const xfG = tt => tt < T_STOP ? lerp(-300, XF_STOP, easeOut(seg(tt, T_ARR, T_STOP))) : XF_STOP + 420 * Math.pow(Math.max(0, tt - T_GO), 2);
  const bez = (k, P) => { const u = 1 - k; return [0, 1].map(d => u * u * u * P[0][d] + 3 * u * u * k * P[1][d] + 3 * u * k * k * P[2][d] + k * k * k * P[3][d]); };
  const KP = [[120, 520], [640, -520], [1760, 260], S];
  function shotG(t, lt, dur) {
    const cy = kf(t, [[T_G, -140], [21.3, -140], [22.5, 540], [28.9, 540], [30.0, 90]]);
    const cx = kf(t, [[T_G, 960], [21.3, 1060], [22.5, 1000], [28.9, 1000], [30.0, 1180]]);
    const z = kf(t, [[T_G, 1], [21.3, 1], [22.5, .95], [28.9, .95], [30.0, 1.05], [31.1, 1.12]]);
    camBegin(cx, cy, z);
    skyBg(LN, t); townBg(LN, t); trackBed(LN);
    // the koi rises, spirals up, and becomes a star
    if (t < T_STAR) {
      const k = ease(seg(t, T_G, T_STAR)), p = bez(k, KP), q = bez(Math.min(1, k + .02), KP);
      for (let i = 1; i < 8; i++) { const pp = bez(Math.max(0, k - i * .025), KP); boilSeed('kt' + i); paint(starPts(pp[0] + jit(5), pp[1] + jit(5), 18 - i * 1.8, .3, 4), { wash: '#FFE27A', ink: null }); }
      glow(p[0], p[1], 240, '#FFD96A', .7);
      koi(p[0], p[1], lerp(180, 70, k), Math.atan2(q[1] - p[1], q[0] - p[0]), t * 1.8, { tie: true });
    }
    // her star (painted after the steam, so the smoke never hides her)
    const drawStar = () => {
      const gotWish = t > T_WISH1 ? Math.exp(-(t - T_WISH1) * 3) : 0;
      const a = t - T_STAR, flare = gotWish + Math.exp(-a * 2.5) + (t > 26.9 && t < 27.4 ? .5 * Math.sin(seg(t, 26.9, 27.4) * Math.PI) : 0);
      glow(...S, 150 + 500 * Math.exp(-a * 3), '#FFF0B0', clamp(.4 + flare));
      for (let i = 0; i < 10; i++) {   // a ring of sparkles bursting out
        const q = seg(a, 0, .8); if (q <= 0 || q >= 1) continue;
        const ang = i / 10 * TAU, d = 80 + 300 * easeOut(q); boilSeed('sb' + i);
        paint(starPts(S[0] + Math.cos(ang) * d, S[1] + Math.sin(ang) * d, 22 * (1 - q), .3, 4), { wash: PAL.cream, ink: null });
      }
      const smile = lerp(.25, 1, ease(seg(t, 22.4, 22.75)));
      const wink = (t > 22.85 && t < 23.15) || (t > 26.95 && t < 27.25) || (t > 30.0 && t < 30.3) ? 1 : 0;
      starHer(...S, 72 * backOut(seg(a, 0, .4)) * (1 + .25 * flare), t, { k: .9, smile, wink });
        };
    // the train: arrives, takes me, and goes
    const xf = xfG(t);
    const inDoor = t > T_LAND && t < T_SHUT + .5 ? (dx, fy) =>
      me(dx, fy, 21, { ...feel('happy', t), ...turn(t, T_LAND, T_LAND + .2, .25, 0), aR: -.4, armR: carry(-.4, LN), aL: t > T_LAND + .25 ? 1.2 + .4 * Math.sin(t * 13) : .3 }, LN) : null;
    if (t > T_ARR - .2 && xf - 1700 < cx + W / z) {
      train(xf, LN, xf, { lit: true, door: ease(seg(t, T_STOP, T_STOP + .3)) * (1 - ease(seg(t, T_SHUT, T_SHUT + .3))), inDoor });
    }
    steam(t, te => [xfG(te) + TRAIN.chimney, RAIL - 430], LN, { each: .5, grow: .85, life: 1.7, wind: 60, on: te => te > T_ARR && te < 30.4 });
    if (t >= T_STAR) drawStar();
    platform(LN);
    lampPost(380, LN, 1);
    bench(1560, 930, LN);
    // me on the platform
    const X = 1000, gy = 930;
    if (t < T_LAND) {
      const hasCase = t > 26.45;
      if (!hasCase) suitcase(X + 190, gy + 2, 22, LN);
      const m = emotions(t, [[T_G, 'sad', { lookX: .5, lookY: -1, emote: null }], [22.85, 'hopeful', { lookX: .5, lookY: -1 }], [23.3, 'relieved', { emote: null }],
                             [24.6, 'happy', { lookX: .5, lookY: -1, emote: null }], [T_ARR + .15, 'surprised', { lookX: -1, lookY: -.2 }], [25.75, 'determined', { lookX: .3 }],
                             [26.5, 'happy', { lookX: .5, lookY: -1 }]], { take: .7 });
      let pose = { view: 'q' };
      if (t > 23.3 && t < T_ARR + .15) pose = { view: 'front', aL: .75 + .05 * Math.sin(t * 3), aR: .75 - .05 * Math.sin(t * 3), emote: null };   // hands together: a wish
      if (t > 26.05 && t < 26.45) pose = { view: 'q', sq: .2 * Math.sin(seg(t, 26.05, 26.45) * Math.PI), aR: -1.1 };   // bend for the case
      if (hasCase) pose = { view: 'q', aR: -.5, armR: carry(-.5, LN) };
      if (t > 26.55 && t < T_JUMP) pose.aL = 1.2 + .45 * Math.sin((t - 26.55) * 13);   // waving up at her star
      let x = X, y = gy, u = 28;
      if (t > T_JUMP - .12) {   // hop back into the doorway
        const k = ease(seg(t, T_JUMP, T_LAND)), d = XF_STOP + TRAIN.door;
        const p = arcPt([X, gy], [d, RAIL - 100], 140, k); x = p[0]; y = p[1]; u = lerp(28, 21, k);
        Object.assign(pose, jump(t, T_JUMP, T_LAND, 0));
      }
      me(x, y, u, { ...m, ...pose, sq: (m.sq || 0) + (pose.sq || 0), dy: (m.dy || 0) + (pose.dy || 0) }, LN);
    }
    // my wish floats up to her star; hearts burst when it arrives
    if (t > T_WISH0 && t < T_WISH1) {
      const k = ease(seg(t, T_WISH0, T_WISH1)), p = arcPt([X, gy - 8 * 28 - 30], S, -160, k);
      boilSeed('wish');
      glow(p[0], p[1], 120, '#FFB6C8', .9);
      paint(heartPts(p[0], p[1], 40 * (1 - .3 * k) * (1 + .1 * Math.sin(t * 12))), { wash: '#F58FA8', fill: PAL.cream, fillOp: 70, ink: PAL.ink, sw: .8 });
    }
    if (t > T_WISH1 && t < T_WISH1 + .8) for (let i = 0; i < 8; i++) {
      const q = seg(t, T_WISH1, T_WISH1 + .8), ang = i / 8 * TAU + .3, d = 90 + 200 * easeOut(q); boilSeed('wh' + i);
      paint(heartPts(S[0] + Math.cos(ang) * d, S[1] + Math.sin(ang) * d, 14 * (1 - q)), { wash: '#F58FA8', ink: null });
    }
    const sp = toScreen(...S);
    camEnd();
    if (t > 30.35) iris(sp[0], sp[1], t < 30.75 ? lerp(1500, 190, ease(seg(t, 30.35, 30.75))) : lerp(190, 0, easeIn(seg(t, 30.8, 31.08))), '#141630');
  }

  shots([[0, shotA], [3.02, shotB], [6.07, shotC], [9.08, shotD], [12.38, shotE], [15.39, shotF], [19.4, shotG]]);
})();
