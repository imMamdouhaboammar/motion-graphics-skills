// Turn an animated HTML file into an MP4.
// The HTML must define window.seek(seconds) and draw the exact frame for any moment.
//
//   node render.mjs <input.html> <new-output-folder> [--seconds 12] [--width 1080] [--height 1350] [--gif]
//
// Output goes into a NEW (or empty) folder, so nothing you already have is overwritten:
//   video.mp4, check-start.png, check-middle.png, check-end.png, render-log.json (and video.gif with --gif)
//
// --width and --height set the browser window the page is drawn in. They do not redesign
// the animation: ask Claude to build it at the size you export (1080 x 1350 feed, 1080 x 1920 Story/Reel).
import fs from 'node:fs';
import path from 'node:path';
import { spawn, execFileSync } from 'node:child_process';
import { once } from 'node:events';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const FPS = 30;
const SEEK_TIMEOUT_MS = 15000, LOAD_TIMEOUT_MS = 30000;

class Stop extends Error {} // a problem we can explain to the reader in plain words

// ---- 1. Read and check the arguments (nothing is opened or written yet) ----
function readArgs(argv) {
  const valueFlags = new Set(['--seconds', '--width', '--height']);
  const flags = {}, positional = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (valueFlags.has(a)) { flags[a] = argv[++i]; }
    else if (a === '--gif') { flags.gif = true; }
    else if (a.startsWith('--')) { throw new Stop(`Unknown option: ${a}`); }
    else positional.push(a);
  }
  if (positional.length !== 2) {
    throw new Stop('Usage: node render.mjs <input.html> <new-output-folder> [--seconds 12] [--width 1080] [--height 1350] [--gif]\n' +
      'Example: node render.mjs examples/launch-video/index.html launch-video');
  }
  const num = (flag, def) => (flags[flag] === undefined ? def : Number(flags[flag]));
  const seconds = num('--seconds', 12), width = num('--width', 1080), height = num('--height', 1350);
  if (!Number.isFinite(seconds) || seconds < 1 || seconds > 60) throw new Stop('--seconds must be a number from 1 to 60.');
  for (const [name, v] of [['--width', width], ['--height', height]]) {
    if (!Number.isInteger(v) || v < 320 || v > 3840 || v % 2) throw new Stop(`${name} must be a whole, even number from 320 to 3840.`);
  }
  const input = path.resolve(positional[0]), outDir = path.resolve(positional[1]);
  if (!fs.existsSync(input) || !fs.statSync(input).isFile()) throw new Stop(`Cannot find the input file: ${input}`);
  if (!/\.html?$/i.test(input)) throw new Stop('The input must be an .html file.');
  if (path.dirname(input) === outDir) throw new Stop('Choose an output folder that is different from the folder your HTML file is in.');
  if (fs.existsSync(outDir)) {
    if (!fs.statSync(outDir).isDirectory()) throw new Stop(`The output path exists and is not a folder: ${outDir}`);
    if (fs.readdirSync(outDir).length) throw new Stop(`The output folder is not empty: ${outDir}\nChoose a new folder name so nothing is overwritten.`);
  }
  return { input, outDir, seconds, width, height, gif: !!flags.gif };
}

// ---- 2. Check the tools before doing any work ----
function checkTools() {
  const major = Number(process.versions.node.split('.')[0]);
  if (major < 18) throw new Stop(`Node ${process.versions.node} is too old. Install the LTS version from https://nodejs.org/en/download`);
  try { execFileSync('ffmpeg', ['-version'], { stdio: 'ignore' }); }
  catch { throw new Stop('ffmpeg was not found. Install it, close and reopen your terminal, then check with: ffmpeg -version'); }
  try { return createRequire(import.meta.url)('puppeteer'); }
  catch { throw new Stop('Puppeteer is not installed in this folder. Run: npm install'); }
}

// Resolve with the value, or reject after ms. The timer is always cleared.
function withTimeout(promise, ms, message) {
  let timer;
  const limit = new Promise((_, reject) => { timer = setTimeout(() => reject(new Stop(message)), ms); });
  return Promise.race([promise, limit]).finally(() => clearTimeout(timer));
}

// PNG width and height live in bytes 16-23 of the file header.
const pngSize = buf => [buf.readUInt32BE(16), buf.readUInt32BE(20)];

async function render(opts, puppeteer, state) {
  const { input, outDir, seconds, width, height } = opts;
  fs.mkdirSync(outDir, { recursive: true });
  state.mp4 = path.join(outDir, 'video.mp4');
  const N = Math.round(seconds * FPS);

  // ---- 3. Open the HTML in a hidden browser, offline ----
  // Our own Ctrl+C handler cleans up, so Puppeteer's must not exit first.
  state.browser = await puppeteer.launch({ headless: true, handleSIGINT: false, handleSIGTERM: false, handleSIGHUP: false });
  const page = await state.browser.newPage();
  const pageErrors = [], blocked = [];
  page.on('pageerror', e => pageErrors.push(String(e.message || e)));
  await page.setRequestInterception(true);
  page.on('request', r => {
    const u = r.url();
    if (u.startsWith('file:') || u.startsWith('data:') || u.startsWith('blob:')) r.continue();
    else { blocked.push(u); r.abort(); } // the file must be self-contained
  });
  await page.setViewport({ width, height, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(input).href + '?render', { waitUntil: 'load', timeout: LOAD_TIMEOUT_MS });

  // ---- 4. Check the page can be controlled by time ----
  await page.waitForFunction(() => typeof window.seek === 'function', { timeout: SEEK_TIMEOUT_MS })
    .catch(() => { throw new Stop('The HTML has no window.seek(seconds) function. Ask Claude to add one that draws any moment from the time alone.'); });
  if (await page.evaluate(() => '__ready' in window)) {
    await page.waitForFunction(() => window.__ready === true, { timeout: SEEK_TIMEOUT_MS })
      .catch(() => { throw new Stop('The page set window.__ready but never made it true.'); });
  }
  await page.evaluate(() => document.fonts && document.fonts.ready);

  // A design bigger than the frame would be cut off. (A design smaller than the frame can't be
  // detected here, which is why the README says to build at the size you export.)
  const [sw, sh] = await page.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.scrollHeight]);
  if (sw > width || sh > height) throw new Stop(`The page is ${sw} x ${sh}, bigger than the ${width} x ${height} frame, so part of it would be cut off. Export at the size it was designed for, or ask Claude to redesign it.`);

  const grab = async t => {
    await withTimeout(
      page.evaluate(t => new Promise(res => { window.seek(t); requestAnimationFrame(() => requestAnimationFrame(res)); }), t),
      SEEK_TIMEOUT_MS, `window.seek(${t}) took longer than ${SEEK_TIMEOUT_MS / 1000}s`);
    return Buffer.from(await page.screenshot({ type: 'png' })); // Puppeteer 23 returns a Uint8Array
  };

  const first = await grab(0);
  const [w, h] = pngSize(first);
  if (w !== width || h !== height) throw new Stop(`Frames came out ${w} x ${h}, expected ${width} x ${height}.`);
  const middle = await grab(seconds / 2);
  const end = await grab(seconds);
  if (first.equals(middle)) console.warn('WARNING: the start and middle frames are identical. Check that window.seek really moves the animation.');
  const loopMatches = first.equals(end);
  fs.writeFileSync(path.join(outDir, 'check-start.png'), first);
  fs.writeFileSync(path.join(outDir, 'check-middle.png'), middle);
  fs.writeFileSync(path.join(outDir, 'check-end.png'), end);

  // ---- 5. Capture every frame and pipe it into ffmpeg ----
  const ff = state.ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', 'pipe:0',
    '-vf', 'scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p',
    '-c:v', 'libx264', '-crf', '16', '-threads', '2', '-pix_fmt', 'yuv420p', '-color_range', 'tv', '-colorspace', 'bt709',
    '-an', '-frames:v', String(N), '-movflags', '+faststart', state.mp4], { stdio: ['pipe', 'inherit', 'inherit'] });
  // One promise for "ffmpeg is gone", whether it closed or failed to start.
  const ffGone = new Promise(resolve => {
    ff.once('close', code => resolve({ code }));
    ff.once('error', err => resolve({ error: err }));
  });
  ff.stdin.on('error', () => {}); // a broken pipe is reported through ffGone below
  const stoppedEarly = r => new Stop(r.error ? `ffmpeg could not start: ${r.error.message}` : `ffmpeg stopped early with exit code ${r.code}.`);

  const t0 = Date.now();
  for (let i = 0; i < N; i++) {
    const png = await grab(i / FPS);
    if (ff.exitCode !== null || ff.killed) throw stoppedEarly(await ffGone);
    if (!ff.stdin.write(png)) {
      // Wait for room in the pipe, but not forever: stop if ffmpeg exits instead.
      const r = await Promise.race([once(ff.stdin, 'drain').then(() => null), ffGone]);
      if (r) throw stoppedEarly(r);
    }
    if (i % FPS === 0) process.stdout.write(`\rFrame ${i + 1} of ${N}`);
  }
  ff.stdin.end();
  const done = await withTimeout(ffGone, 120000, 'ffmpeg did not finish within 2 minutes of the last frame.');
  if (done.error || done.code !== 0) throw stoppedEarly(done);
  state.ff = null;
  await state.browser.close(); state.browser = null;

  if (opts.gif) {
    execFileSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-i', state.mp4, '-threads', '2',
      '-vf', 'fps=15,scale=540:-2:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse',
      '-loop', '0', path.join(outDir, 'video.gif')]);
  }
  state.finished = true;

  const log = {
    input, output: state.mp4, width, height, fps: FPS, seconds, frames: N,
    renderSeconds: Math.round((Date.now() - t0) / 100) / 10,
    firstFrameMatchesLast: loopMatches, pageErrors, blockedRequests: blocked,
    mp4Bytes: fs.statSync(state.mp4).size, gif: !!opts.gif,
  };
  fs.writeFileSync(path.join(outDir, 'render-log.json'), JSON.stringify(log, null, 2));
  console.log(`\n\nDone: ${state.mp4}`);
  console.log(`${N} frames, ${width} x ${height}, ${seconds}s at ${FPS} fps.`);
  console.log(loopMatches ? `Loop check: the frames at 0s and ${seconds}s match, so it loops cleanly.`
    : `Loop check: the frames at 0s and ${seconds}s differ. That's expected on a short test. If ${seconds}s is the full length, the loop will jump.`);
  if (pageErrors.length) console.log(`Note: the page reported ${pageErrors.length} error(s). See render-log.json.`);
  if (blocked.length) console.log(`Note: ${blocked.length} internet request(s) were blocked. See render-log.json.`);
  console.log('Open check-start.png, check-middle.png and check-end.png to see the frames.');
}

// Close everything we opened and remove a half-written video. Safe to call twice.
async function cleanup(state) {
  if (state.ff && state.ff.exitCode === null) state.ff.kill('SIGKILL');
  if (state.browser) { const b = state.browser; state.browser = null; await b.close().catch(() => {}); }
  if (!state.finished && state.mp4 && fs.existsSync(state.mp4)) fs.rmSync(state.mp4, { force: true });
}

const state = { browser: null, ff: null, mp4: null, finished: false };
for (const [sig, code] of [['SIGINT', 130], ['SIGTERM', 143]]) process.once(sig, () => { cleanup(state).finally(() => process.exit(code)); });
try {
  const opts = readArgs(process.argv.slice(2));
  const puppeteer = checkTools();
  await render(opts, puppeteer, state);
} catch (e) {
  console.error('\nSTOPPED: ' + (e instanceof Stop ? e.message : (e && e.stack) || String(e)) + '\n');
  process.exitCode = 1;
} finally {
  await cleanup(state);
}
