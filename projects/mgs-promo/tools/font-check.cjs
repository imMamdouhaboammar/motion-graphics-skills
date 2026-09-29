// Font gate: every @font-face the film declares must be 'loaded' after window.__ready, and the
// Arabic hero words must measure differently from the fallback face (proves Thmanyah painted them).
// Arabic and Latin are measured apart: in a mixed string a Latin-only subset of an Arabic face would
// still change the width through its Latin glyphs and hide the Arabic falling back.
// Each face is compared with its generic family and with an undeclared family: canvas paints a missing
// glyph in the browser default face, which need not match the generic family.
// usage: NODE_PATH=<global node_modules> node tools/font-check.cjs <url>
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto(process.argv[2], { waitUntil: 'domcontentloaded' });
  const r = await p.evaluate(async () => {
    // bounded: a readiness promise that never settles (for example one that adopted a paused GSAP
    // timeline) must fail this gate with a message instead of hanging it
    const TIMEOUT_MS = 20000;
    try {
      await Promise.race([window.__ready, new Promise((_, rej) => setTimeout(() => rej(new Error(`window.__ready did not settle within ${TIMEOUT_MS} ms`)), TIMEOUT_MS))]);
    } catch (e) { return { readyError: String(e) }; }
    const faces = []; document.fonts.forEach(f => faces.push(`${f.family} ${f.weight} ${f.status}`));
    const c = document.createElement('canvas').getContext('2d');
    const w = (f, t) => { c.font = f; return c.measureText(t).width; };
    const AR = 'الموشن اترك تعليق', LAT = 'Claude Code';
    return { faces,
      serifArabicVsFallback: [w('900 100px TSerif', AR), w('900 100px serif', AR), w('900 100px NoSuchFace', AR)],
      sansArabicVsFallback: [w('700 100px TSans', AR), w('700 100px sans-serif', AR), w('700 100px NoSuchFace', AR)],
      monoLatinVsFallback: [w('500 100px JBMono', LAT), w('500 100px monospace', LAT), w('500 100px NoSuchFace', LAT)] };
  });
  await b.close();
  console.log(JSON.stringify(r, null, 1));
  const bad = r.readyError || r.faces.some(f => !f.endsWith('loaded')) ||
    [r.serifArabicVsFallback, r.sansArabicVsFallback, r.monoLatinVsFallback].some(([a, ...fb]) => fb.some(z => Math.abs(a - z) < 1));
  console.log(bad ? 'FAIL' : 'PASS');
  process.exit(bad ? 1 : 0);
})();
