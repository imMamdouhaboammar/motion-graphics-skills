// sheets.js: model sheets as standalone loops (reference, not part of a video — the one place labels are fine).
//   studio.html?loop=cast   (or render: node render.mjs --loop=cast --sheet=1 --cols=1 --w=1920 --out=docs/cast.jpg)
//   ?loop=looks             brushes and fills
(() => {
  const label = (txt, x, y, size = 24) => letter(txt, x, y, size, PAL.inkSoft, { alpha: .9 });

  // Views and moods of both characters.
  LOOPS.cast = t => {
    vignette(0);
    const views = ['front', 'q', 'side', 'back'];
    views.forEach((v, i) => { const x = 150 + i * 250; lulu(x, 400, 26, { ...feel('neutral', t, { seed: i }), view: v }); label(v, x, 440); });
    views.forEach((v, i) => { const x = 1180 + i * 200; kuri(x, 400, 26, { ...feel('happy', t, { seed: i }), view: v }); label(v, x, 440); });
    const moods = Object.keys(EMO);
    moods.forEach((m, i) => {
      const x = 70 + (i % 18) * 105, y = 770;
      lulu(x, y - 0, 17, { ...feel(m, t, { seed: i }), emote: null });
      kuri(x, y + 230, 17, { ...feel(m, t, { seed: i + 3 }), emote: null });
      label(m, x, y + 30, 17);
    });
  };
  LOOPS.cast.len = 4;

  // Brushes and fills.
  LOOPS.looks = t => {
    vignette(0);
    const lines = [['crayon', crayonLine], ['cpen', pencilLine], ['pastel', pastelLine], ['graphite', sketchLine]];
    lines.forEach(([n, f], i) => { boilSeed('ln' + i); f([[80, 120 + i * 90], [400, 90 + i * 90], [700, 140 + i * 90]], 1.2, [PAL.coral, PAL.ink, PAL.lilac, PAL.inkSoft][i]); label(n, 800, 115 + i * 90); });
    const fills = [['scribble', 'scribble', PAL.butter], ['hatch', 'hatch', PAL.sky], ['cross', 'cross', PAL.rose], ['smudge', 'smudge', PAL.lilac], ['flat', 'flat', PAL.sage]];
    fills.forEach(([n, f, c], i) => { boilSeed('f' + i); colorIn(ellPts(170 + i * 360, 620, 150, 130, 30, 3), { col: c, fill: f }); label(n, 170 + i * 360, 800); });
    boilSeed('props'); apple(1100, 250, 60); starProp(1300, 250, 60); heartProp(1480, 250, 55); leafProp(1680, 250, 60, .4); balloon(1300, 480, 55, 150);
    emote('!', 1100, 480, 50); emote('heart', 1500, 480, 50); emote('zzz', 1680, 480, 50, 1, t);
    sun(300, 950, 60, t); cloud(800, 960, .8); flower(1200, 1040, 1.3, PAL.rose, t); flower(1300, 1040, 1.1, PAL.lilac, t);
  };
  LOOPS.looks.len = 4;
})();
