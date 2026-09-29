// Font gate: every @font-face the film declares must be 'loaded' after window.__ready, and the
// Arabic hero words must measure differently from the fallback face (proves Thmanyah painted them).
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
    const w = f => { c.font = f; return c.measureText('الموشن اترك تعليق Claude Code').width; };
    return { faces,
      serifVsFallback: [w('900 100px TSerif'), w('900 100px serif')],
      sansVsFallback: [w('700 100px TSans'), w('700 100px sans-serif')],
      monoVsFallback: [w('500 100px JBMono'), w('500 100px monospace')] };
  });
  await b.close();
  console.log(JSON.stringify(r, null, 1));
  const bad = r.readyError || r.faces.some(f => !f.endsWith('loaded')) ||
    [r.serifVsFallback, r.sansVsFallback, r.monoVsFallback].some(([a, z]) => Math.abs(a - z) < 1);
  console.log(bad ? 'FAIL' : 'PASS'); process.exit(bad ? 1 : 0);
})();
