#!/usr/bin/env node
'use strict';

function browserArgs(osName) {
  if (osName === 'Darwin') {
    return ['--enable-gpu', '--ignore-gpu-blocklist', '--use-angle=metal'];
  }
  if (osName === 'Windows') {
    return ['--enable-gpu', '--ignore-gpu-blocklist', '--use-angle=d3d11'];
  }
  return ['--enable-gpu', '--ignore-gpu-blocklist', '--use-gl=angle'];
}

function classifyRenderer(renderer) {
  const value = String(renderer || '').trim();
  const lower = value.toLowerCase();
  const softwareMarkers = [
    'swiftshader',
    'llvmpipe',
    'software rasterizer',
    'softpipe',
    'lavapipe',
    'mesa offscreen',
    'microsoft basic render driver',
    'basic render driver',
  ];
  const hardwareMarkers = [
    'apple',
    'nvidia',
    'intel',
    'amd',
    'radeon',
  ];

  const software = softwareMarkers.some((marker) => lower.includes(marker));
  const hardware = (
    Boolean(value)
    && !software
    && hardwareMarkers.some((marker) => lower.includes(marker))
  );

  return {
    hardware,
    renderer: value || null,
    classification: hardware ? 'hardware' : 'software-or-unknown',
  };
}

function platformName() {
  if (process.platform === 'darwin') return 'Darwin';
  if (process.platform === 'win32') return 'Windows';
  return 'Linux';
}

function usage() {
  console.log(`Usage:
  node browser_gpu_probe.cjs [--allow-software]

Launches Chromium through the active project's Playwright installation,
reads the actual WebGL renderer, and exits nonzero when rendering is
software-only unless --allow-software is explicit.
`);
}

async function run() {
  const args = process.argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    usage();
    return 0;
  }
  const allowSoftware = args.includes('--allow-software');

  let chromium;
  try {
    ({ chromium } = require('playwright'));
  } catch (error) {
    console.error(JSON.stringify({
      decision: 'blocked',
      reason: 'playwright-unavailable',
      detail: String(error && error.message ? error.message : error),
    }, null, 2));
    return 2;
  }

  const osName = platformName();
  const launchArgs = browserArgs(osName);
  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      args: launchArgs,
    });
    const page = await browser.newPage();
    const observed = await page.evaluate(() => {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
      if (!gl) {
        return {
          vendor: null,
          renderer: null,
          webgl: false,
        };
      }
      const ext = gl.getExtension('WEBGL_debug_renderer_info');
      const vendor = ext
        ? gl.getParameter(ext.UNMASKED_VENDOR_WEBGL)
        : gl.getParameter(gl.VENDOR);
      const renderer = ext
        ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)
        : gl.getParameter(gl.RENDERER);
      return {
        vendor: String(vendor || ''),
        renderer: String(renderer || ''),
        webgl: true,
      };
    });

    const classification = classifyRenderer(observed.renderer);
    const result = {
      decision: classification.hardware ? 'gpu' : (allowSoftware ? 'software-explicit' : 'blocked'),
      reason: classification.hardware
        ? 'hardware-webgl-renderer-observed'
        : (allowSoftware ? 'software-renderer-explicitly-allowed' : 'software-renderer-observed'),
      os: osName,
      launch_args: launchArgs,
      webgl: observed.webgl,
      vendor: observed.vendor || null,
      renderer: classification.renderer,
      hardware: classification.hardware,
    };
    console.log(JSON.stringify(result, null, 2));

    if (classification.hardware || allowSoftware) return 0;
    return 3;
  } catch (error) {
    console.error(JSON.stringify({
      decision: 'blocked',
      reason: 'browser-gpu-probe-failed',
      detail: String(error && error.message ? error.message : error),
      launch_args: launchArgs,
    }, null, 2));
    return 2;
  } finally {
    if (browser) {
      await browser.close().catch(() => {});
    }
  }
}

module.exports = {
  browserArgs,
  classifyRenderer,
};

if (require.main === module) {
  run().then(
    (code) => {
      process.exitCode = code;
    },
    (error) => {
      console.error(String(error && error.stack ? error.stack : error));
      process.exitCode = 2;
    },
  );
}
