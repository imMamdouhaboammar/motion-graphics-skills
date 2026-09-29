#!/usr/bin/env node
'use strict';

function usage() {
  console.log(`Usage:
  node browser-readiness-probe.cjs <url> [--timeout 3000]

Reports DOM, fonts, images, and window.__ready state as plain JSON.
Exit 0 when observed readiness is healthy, 1 when the page loaded but is
blocked, and 2 for usage/dependency/navigation failures.
`);
}

const args = process.argv.slice(2);
if (args.includes('--help') || args.includes('-h')) {
  usage();
  process.exit(0);
}

const url = args.find((arg, index) => !arg.startsWith('--') && args[index - 1] !== '--timeout');
const timeoutIndex = args.indexOf('--timeout');
const timeoutMs = timeoutIndex >= 0 ? Number(args[timeoutIndex + 1]) : 3000;

if (!url || !Number.isFinite(timeoutMs) || timeoutMs <= 0) {
  usage();
  process.exit(2);
}

let chromium;
try {
  ({ chromium } = require('playwright'));
} catch (error) {
  console.error(JSON.stringify({
    ok: false,
    classification: 'dependency-error',
    error: 'Playwright is not available in the active project',
    detail: String(error && error.message ? error.message : error),
  }, null, 2));
  process.exit(2);
}

function plainError(error) {
  return String(error && error.message ? error.message : error);
}

(async () => {
  let browser;
  try {
    browser = await chromium.launch();
    const page = await browser.newPage();
    const pageErrors = [];
    page.on('pageerror', (error) => pageErrors.push(plainError(error)));

    await page.goto(url, {
      waitUntil: 'domcontentloaded',
      timeout: timeoutMs,
    });

    const observed = await page.evaluate(async (limit) => {
      const race = async (promise) => {
        return Promise.race([
          Promise.resolve(promise).then(
            () => ({ state: 'resolved' }),
            (error) => ({ state: 'rejected', error: String(error && error.message ? error.message : error) }),
          ),
          new Promise((resolve) => setTimeout(() => resolve({ state: 'pending' }), limit)),
        ]);
      };

      const fonts = document.fonts && document.fonts.ready
        ? await race(document.fonts.ready)
        : { state: 'unsupported' };

      const images = [...document.images].map((image) => ({
        src: image.currentSrc || image.src || '',
        complete: image.complete,
        naturalWidth: image.naturalWidth,
        naturalHeight: image.naturalHeight,
      }));

      const ready = window.__ready;
      const readyExists = typeof ready !== 'undefined';
      const readyThenable = Boolean(ready && typeof ready.then === 'function');
      const readyLooksLikeGsap = Boolean(
        ready
        && typeof ready.paused === 'function'
        && typeof ready.play === 'function'
        && typeof ready.totalDuration === 'function'
      );

      let readyState = { state: readyExists ? 'plain' : 'missing' };
      if (readyThenable) {
        readyState = await race(ready);
      }

      const timelineRegistry = window.__timelines && typeof window.__timelines === 'object'
        ? Object.keys(window.__timelines)
        : [];

      return {
        dom: {
          readyState: document.readyState,
          url: location.href,
        },
        fonts,
        images: {
          total: images.length,
          complete: images.filter((image) => image.complete).length,
          failed: images.filter((image) => image.complete && image.naturalWidth === 0).length,
          pending: images.filter((image) => !image.complete).length,
        },
        ready: {
          exists: readyExists,
          thenable: readyThenable,
          looksLikeGsapTimeline: readyLooksLikeGsap,
          ...readyState,
        },
        timelineRegistry,
      };
    }, timeoutMs);

    const findings = [];
    if (observed.fonts.state === 'pending') findings.push('fonts-pending');
    if (observed.fonts.state === 'rejected') findings.push('fonts-rejected');
    if (observed.images.pending > 0) findings.push('images-pending');
    if (observed.images.failed > 0) findings.push('images-failed');
    if (observed.ready.exists && observed.ready.state === 'pending') {
      findings.push(
        observed.ready.looksLikeGsapTimeline
          ? 'readiness-thenable-deadlock-risk'
          : 'readiness-pending'
      );
    }
    if (observed.ready.exists && observed.ready.state === 'rejected') {
      findings.push('readiness-rejected');
    }

    const result = {
      ok: findings.length === 0,
      classification: findings.length ? 'readiness-blocked' : 'ready',
      findings,
      observed,
      pageErrors: [...new Set(pageErrors)],
    };

    console.log(JSON.stringify(result, null, 2));
    process.exitCode = result.ok ? 0 : 1;
  } catch (error) {
    console.error(JSON.stringify({
      ok: false,
      classification: 'probe-error',
      error: plainError(error),
    }, null, 2));
    process.exitCode = 2;
  } finally {
    if (browser) {
      await browser.close().catch(() => {});
    }
  }
})();
