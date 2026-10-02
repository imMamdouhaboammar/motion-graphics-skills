// demo.js: "The red apple", a 10-second example that exercises the engine. One idea, not a template: don't reuse its
// story, meadow or shot structure in your own video.
//   Shot A (0–4.6 s): establishing. The camera drifts down from the sun to a meadow. Lulu and Kuri walk in and stop
//                     under an apple tree. Kuri spots the apple, can't reach it, droops. Lulu thinks … idea!
//   Page turn (4.6–5.6 s).
//   Shot B (4.6–10 s): closer, framed as a picture-book page. Lulu crouches (anticipation), jumps and plucks the apple
//                     (action), lands with a squash and a hair bounce (follow-through), turns and gives it to Kuri,
//                     who falls in love with it. The page fades back to paper.
(() => {
  captions([
    [0.5, 2.5, '露露和小栗出門散步。', { pos: 'top' }],
    [2.9, 4.4, '樹上有一顆紅蘋果⋯⋯', { pos: 'top' }],
    [5.95, 7.3, '跳高一點⋯⋯摘到了！'],
    [7.8, 9.4, '這顆送給你！'],
  ]);

  // ---------- shot A: the meadow ----------
  const GA = 880;
  function meadow(t, lt, dur) {
    camBegin(kf(lt, [[0, 820], [2.6, 960], [dur + 1, 1010]]), kf(lt, [[0, 300], [2.4, 555], [dur + 1, 640]], ease), kf(lt, [[0, 1.12], [2.4, 1.0], [dur + 1, 1.32]]));
    sky(PAL.sky, PAL.cream, { y1: GA - 100 });
    sun(1580, 150, 70, t, { face: true });
    cloud(460 + lt * 12, 170, .9, { key: 'c1' }); cloud(1120 + lt * 8, 90, .6, { key: 'c2' });
    hill(350, GA + 140, 760, 300, mixCol(PAL.sage, PAL.skyLt, .35));
    house(360, GA - 150, .55);
    hill(1500, GA + 170, 900, 330, mixCol(PAL.leaf, PAL.skyLt, .25), { ang: .15 });
    ground(GA, PAL.sage);
    tufts(-300, 2200, () => GA + 6, 26, PAL.sageDk, t, 'tA');
    for (let i = 0; i < 7; i++) flower(-200 + i * 330 + hash(i) * 90, GA + 40 + hash(i + 4) * 90, 1.1, [PAL.rose, PAL.lilac, PAL.butter][i % 3], t);
    tree(1420, GA, 1.25);
    boilSeed('appleA'); apple(1330, 610 + Math.sin(t * 1.4) * 3, 26);
    crayonLine([[1330, 584], [1340, 560]], .5, PAL.cocoa);

    // Kuri trots in behind Lulu, stops, looks up at the apple, and droops
    const kw = stroll(lt, .15, 2.7, -420, 800, 26, 2.2);
    const km = emotions(lt, [[0, 'happy'], [2.95, 'curious', { lookX: .8, lookY: -1 }], [3.65, 'sad', { lookX: .6, lookY: -.4 }]]);
    const kpose = lt < 2.7 ? pose(km, walkCycle(kw.walk || 0, true), { view: 'side' }) : pose(km, { view: 'q' });
    kuri(kw.x, GA + 10, 26, { ...kpose, seed: 2 });
    // Lulu leads, stops under the tree, thinks, gets an idea
    const lw = stroll(lt, 0, 2.5, -150, 1060, 30, 3);
    const lm = emotions(lt, [[0, 'happy'], [3.05, 'thinking'], [3.9, 'idea']]);
    const lpose = lt < 2.5 ? pose(lm, walkCycle(lw.walk || 0, true), { view: 'side' }) : pose(lm, { view: lt < 2.62 ? 'q' : 'front' });
    lulu(lw.x, GA + 4, 30, { ...lpose, seed: 1 });
    camEnd();
    if (lt < .6) flash(1 - easeOut(lt / .6), PAL.paper);   // open from the blank page
  }

  // ---------- shot B: the jump ----------
  const GB = 900, P = [943, 357];   // P: where the apple hangs = Lulu's raised hand at the top of her jump
  const tJ0 = 1.5, tJ1 = 2.2, tGrab = 1.83, tTurn = 2.85, tGive = 3.45, tGot = 3.8;
  function jumpShot(t, lt, dur) {
    const land = lt > tJ1 ? shakeXY(t, 5 * Math.exp(-(lt - tJ1) * 9)) : [0, 0];
    camBegin(kf(lt, [[0, 930], [dur, 880]]) + land[0], kf(lt, [[0, 560], [tJ0, 540], [tJ1 + .4, 575]]) + land[1], kf(lt, [[0, 1], [dur, 1.07]]));
    sky(PAL.skyLt, PAL.cream, { y1: GB - 60, strokes: 6 });
    hill(1100, GB + 200, 1300, 360, mixCol(PAL.leaf, PAL.skyLt, .3));
    ground(GB, PAL.sage);
    tufts(-300, 2200, () => GB + 6, 22, PAL.sageDk, t, 'tB');
    for (let i = 0; i < 5; i++) flower(-100 + i * 480 + hash(i + 9) * 100, GB + 70 + hash(i + 2) * 60, 1.5, [PAL.lilac, PAL.rose, PAL.butter][i % 3], t);
    tree(1480, GB, 1.8);
    // the branch reaching out over Lulu, with the apple's stem
    boilSeed('branch');
    colorIn(ribbon([[1420, 430], [1200, 330], [1040, 300], [925, 305]], 34, 12), { col: PAL.bark, ang: .2, gap: 8 });
    for (let i = 0; i < 4; i++) leafProp(1300 - i * 115, 330 - 25 * (i % 2) - i * 8, 30, -.5 + i * .4);
    const grabbed = lt >= tGrab;
    if (!grabbed) { boilSeed('stem'); crayonLine([[P[0] + 2, 306], [P[0], P[1] - 28]], .5, PAL.cocoa); boilSeed('appleB'); apple(P[0], P[1] + 8 + Math.sin(t * 1.4) * 2, 40); }
    else { boilSeed('stem'); crayonLine([[P[0] + 2, 306], [P[0] - 4 + 8 * spring(lt, tGrab, 5, 20), 328]], .5, PAL.cocoa); }   // the snapped stem twangs

    // Kuri: worried → surprised by the jump → excited → the apple arrives → love, with a little hop
    const km = emotions(lt, [[0, 'sad', { lookX: .6, lookY: -.5 }], [tJ0 - .05, 'surprised', { lookY: -.8 }], [tJ1 + .15, 'excited'], [tGive, 'curious', { lookX: .6 }], [tGot + .05, 'love']]);
    const khop = jump(lt, tGot + .35, tGot + .7, 1.6);
    const giftFlight = lt > tGive && lt < tGot;
    const K = kuri(520, GB + 8, 34, { ...pose(km, khop, { view: 'q' }), seed: 3, aR: lt > tGive - .2 ? kf(lt, [[tGive - .2, -1.1], [tGive + .1, .1], [tGot + .3, -.35]]) : km.aR, bR: lt > tGive ? 1.2 : .3,
      holdR: lt >= tGot ? (u) => apple(0, -u * .75, u * 1.15) : null, propFront: false });

    // Lulu: determined look up → crouch → jump with her arm up → grab → land → turn to Kuri → give
    const lm = emotions(lt, [[0, 'determined', { lookX: .4, lookY: -1 }], [tGrab, 'excited'], [tJ1 + .5, 'happy'], [tGot + .15, 'proud']], { take: .6 });
    const hop = jump(lt, tJ0, tJ1, 4.6);
    const k = seg(lt, tJ0, tJ1), inAir = lt > tJ0 && lt < tJ1;
    const hair = inAir ? 1.3 * (2 * k - 1) : lt >= tJ1 ? -1.2 * spring(lt, tJ1, 5, 16) : 0;
    const reach = kf(lt, [[tJ0 - .3, -1.2], [tJ0 - .05, -.2], [tJ0 + .12, 1.15], [tJ1 + .1, 1.15], [tJ1 + .5, .6], [tTurn, -1]], ease);
    let lp = pose(lm, hop, { hair, aR: reach, bR: lt < tJ1 + .3 ? .35 : .8, aL: inAir ? .3 : lm.aL, view: 'front' });
    if (lt < tJ0) lp.lookY = -1;
    if (lt >= tTurn) lp = pose(lp, { view: 'q', flip: true, aR: kf(lt, [[tTurn, -1], [tGive, -.15], [tGot, -.3], [tGot + .5, -1.2]]), bR: kf(lt, [[tTurn, .8], [tGive, .25], [tGot + .5, .3]]) });
    if (lt >= tTurn && lt < tTurn + .12) lp.sq = (lp.sq || 0) + .08;   // a little squash on the turn drawing
    const holding = grabbed && lt < tGive + .05;
    const L = lulu(860, GB + 4, 40, { ...lp, seed: 5, hairCol: undefined, holdR: holding ? (u) => apple(0, -u * .6, u * 1.0) : null, propFront: false });
    // the hand-over: the apple arcs from Lulu's hand to Kuri's paws
    if (lt >= tGive + .05 && lt < tGot && L.handR && K.handR) {
      const q = ease(seg(lt, tGive + .05, tGot)); boilSeed('gift');
      const p = arcPt([L.handR[0], L.handR[1] - 24], [K.handR[0], K.handR[1] - 26], 70, q); apple(p[0], p[1], 40);
    }
    camEnd();
    bookPage(ease(seg(lt, 1.0, 1.7)));
    vignette(.3 + .4 * seg(lt, dur - 1.2, dur));
    if (lt > dur - .55) flash(easeIn(seg(lt, dur - .55, dur - .05)), PAL.paper);   // the page fades back to blank paper
  }

  shots([[0, meadow], [4.6, jumpShot, { turn: 1.0 }]]);
})();
