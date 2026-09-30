// clip-audit.js: find text that is accidentally cut off by the frame or by a clipping container.
//
//   node clip-audit.js <url> [--step 0.1] [--min 0.5] [--from 0] [--to <duration>] [--tol 3] [--safe 0]
//
// The page must expose window.seek(t) and window.DURATION, and may expose window.__ready (a promise).
// For every sampled time the script measures each visible text run (glyph box of its text nodes, after
// transforms) against the frame (#wrap, or the viewport) and against every ancestor that clips
// (overflow hidden/clip, or an inset() clip-path). A cut that persists for at least --min seconds is
// reported: a word that rises through a mask for 0.3 s is animation, a word cut for 2 s is a defect.
// --safe N also reports text that is inside the frame but closer than N px to a frame edge (a safe-margin
// breach reads as a crop on a phone even when no glyph is cut).
// Intentional crops opt out with data-crop="intentional" on the element or an ancestor.
// Exit code 1 when anything is reported, 0 when clean, 2 when the page cannot be audited.
const { chromium } = require('playwright');

const args = process.argv.slice(2);
const url = args.find(a => !a.startsWith('--') && !/^[\d.]+$/.test(a));
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? +args[i + 1] : d; };
const STEP = opt('step', 0.1), MIN = opt('min', 0.5), TOL = opt('tol', 3), SAFE = opt('safe', 0);
if (!url) { console.error('usage: node clip-audit.js <url> [--step 0.1] [--min 0.5] [--from s] [--to s] [--tol px] [--safe px]'); process.exit(2); }

(async () => {
  const b = await chromium.launch({executablePath:process.env.CHROME_PATH||undefined});
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(url);
  await p.evaluate(() => window.__ready);
  const dur = await p.evaluate(() => window.DURATION);
  if (!(dur > 0) || !(await p.evaluate(() => typeof window.seek === 'function'))) {
    console.error('page does not expose window.seek and window.DURATION', errs.join('\n')); await b.close(); process.exit(2);
  }
  const from = opt('from', 0), to = Math.min(opt('to', dur), dur);
  const open = new Map(), found = [];
  for (let t = from; t <= to + 1e-9; t += STEP) {
    const cuts = await p.evaluate(({ t, tol, safe }) => {
      window.seek(t);
      const frameEl = document.getElementById('wrap');
      const F = frameEl ? frameEl.getBoundingClientRect() : { left: 0, top: 0, right: innerWidth, bottom: innerHeight };
      const out = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      const seen = new Set();
      for (let n = walker.nextNode(); n; n = walker.nextNode()) {
        const el = n.parentElement;
        if (!el || seen.has(el) || !n.textContent.trim() || el.closest('#transcript, #hud, script, style, title')) continue;
        seen.add(el);
        if (el.closest('[data-crop="intentional"]')) continue;
        // effective visibility
        let o = 1, vis = true;
        for (let a = el; a; a = a.parentElement) {
          const cs = getComputedStyle(a);
          if (cs.display === 'none' || cs.visibility === 'hidden') { vis = false; break; }
          o *= +cs.opacity;
        }
        if (!vis || o < 0.5) continue;
        const r = document.createRange(); r.selectNodeContents(el);
        const R = r.getBoundingClientRect();
        if (R.width < 2 || R.height < 2) continue;
        const clips = [{ name: 'frame', L: F.left, T: F.top, Rr: F.right, B: F.bottom }];
        for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
          if (a === frameEl) break;
          const cs = getComputedStyle(a);
          const ov = [cs.overflowX, cs.overflowY].some(v => v === 'hidden' || v === 'clip');
          const inset = /^inset\(/.test(cs.clipPath);
          if (ov || inset) { const q = a.getBoundingClientRect(); clips.push({ name: (a.id ? '#' + a.id : a.className ? '.' + String(a.className).split(' ')[0] : a.tagName.toLowerCase()), L: q.left, T: q.top, Rr: q.right, B: q.bottom, inset }); }
        }
        if (clips.some(c => R.right <= c.L || R.left >= c.Rr || R.bottom <= c.T || R.top >= c.B)) continue;   // hidden by some clip
        let cutFound = false;
        for (const c of clips) {
          if (c.inset) continue;   // inset() masks are usually reveals; report them only through the frame
          // fully outside this clip means hidden or waiting off-frame (a word under its mask before it rises,
          // a card that has already left), which is not a crop
          if (R.right <= c.L || R.left >= c.Rr || R.bottom <= c.T || R.top >= c.B) break;
          const cut = { left: c.L - R.left, right: R.right - c.Rr, top: c.T - R.top, bottom: R.bottom - c.B };
          const sides = Object.entries(cut).filter(([, v]) => v > tol).map(([k, v]) => `${k} ${Math.round(v)}px`);
          if (sides.length) { out.push({ text: el.textContent.trim().slice(0, 40), by: c.name, sides: sides.join(', ') }); cutFound = true; break; }
        }
        // safe margin only after every clip has been checked, so a margin warning never hides a real cut
        if (!cutFound && safe > 0) {
          const f = clips[0], m = { left: R.left - f.L, right: f.Rr - R.right, top: R.top - f.T, bottom: f.B - R.bottom };
          const near = Object.entries(m).filter(([, v]) => v < safe).map(([k, v]) => `${k} margin ${Math.round(v)}px`);
          if (near.length) out.push({ text: el.textContent.trim().slice(0, 40), by: 'safe margin', warn: true, sides: near.join(', ') });
        }
      }
      return out;
    }, { t, tol: TOL, safe: SAFE });
    const now = new Set();
    for (const c of cuts) {
      const key = c.text + '|' + c.by + '|' + c.sides.replace(/\d+px/g, '');
      now.add(key);
      if (!open.has(key)) open.set(key, { ...c, t0: t, t1: t }); else open.get(key).t1 = t;
    }
    for (const [key, v] of open) if (!now.has(key)) { if (v.t1 - v.t0 + STEP >= MIN) found.push(v); open.delete(key); }
  }
  for (const v of open.values()) if (v.t1 - v.t0 + STEP >= MIN) found.push(v);
  await b.close();
  if (errs.length) console.log('PAGE ERRORS:\n' + [...new Set(errs)].join('\n'));
  if (!found.length) { console.log(`PASS: no persistent clipping or margin warning from ${from}s to ${to}s (step ${STEP}s, min ${MIN}s)`); process.exit(0); }
  found.sort((a, b) => a.t0 - b.t0);
  for (const f of found) console.log(`${f.warn ? 'WARN' : 'CUT '} ${f.t0.toFixed(2)}-${f.t1.toFixed(2)}s  "${f.text}"  ${f.warn ? 'near' : 'cut by'} ${f.by}: ${f.sides}`);
  const cuts = found.filter(f => !f.warn).length;
  // the safe margin is measured on the font box (ascent to descent), so it is a warning for a human to confirm
  console.log(cuts ? `FAIL: ${cuts} persistent clipping finding(s), ${found.length - cuts} safe-margin warning(s)` : `PASS: no clipping, ${found.length} safe-margin warning(s) to confirm by eye`);
  process.exit(cuts ? 1 : 0);
})();
