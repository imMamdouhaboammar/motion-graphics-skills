import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const read = (path) => fs.readFileSync(new URL(path, import.meta.url), 'utf8');
function calls(path, block = 0, extra = {}) {
  const code = [...read(path).matchAll(/```js\n([\s\S]*?)```/g)][block][1];
  const recorded = [];
  const tl = Object.fromEntries(['set', 'to', 'fromTo'].map(method => [method,
    (...args) => { recorded.push({ method, target: args[0], vars: args[method === 'fromTo' ? 2 : 1], time: args.at(-1) }); return tl; }
  ]));
  vm.runInNewContext(code, { tl, T: 1, old: '#old', oldScene: '#old', newScene: '#new', BURN_DURATION: 2, ...extra });
  return recorded;
}

test('burn keeps the whole incoming scene hidden until its reveal', () => {
  const c = calls('../transitions/css-destruction.md', 1);
  assert.ok(c.some(x => x.target === '#scene2' && x.method === 'set' && x.vars.opacity === 0 && x.time <= 1));
  assert.ok(c.some(x => x.target === '#scene2' && x.method === 'to' && x.vars.opacity === 1 && x.time === 2.8));
});

test('cover scene swap happens while a wipe is fully stationary across the frame', () => {
  const c = calls('../transitions/css-cover.md');
  const cover = c.find(x => x.target === '#wipe-a' && x.method === 'to' && x.vars.x === 0);
  const exit = c.find(x => x.target === '#wipe-a' && x.method === 'to' && x.vars.x === 1920);
  for (const swap of c.filter(x => x.method === 'set' && ['#old', '#new'].includes(x.target))) {
    assert.ok(swap.time >= cover.time + cover.vars.duration && swap.time <= exit.time);
  }
});

test('RGB glitch overlays use the catalog opacity', () => {
  const c = calls('../transitions/css-distortion.md');
  for (const x of c.filter(x => /^#glitch-/.test(x.target))) assert.equal(x.vars.opacity, 0.35);
});

test('every light leak fades out after its drift', () => {
  const c = calls('../transitions/css-light.md');
  for (const id of ['#leak-1', '#leak-2', '#leak-warm']) {
    const last = c.filter(x => x.target === id).at(-1);
    assert.equal(last.vars.opacity, 0);
    if (id === '#leak-2') assert.ok(last.time >= 1.7);
  }
});

test('card flip example uses valid JavaScript identifiers', () => {
  assert.equal(calls('../transitions/css-3d.md').length, 4);
});

test('waterfall arrivals stay within two frames of previous settling', () => {
  const c = calls('../rules/waterfall-entry.md').filter(x => x.method === 'to');
  for (let i = 1; i < c.length; i++) {
    assert.ok(Math.abs(c[i].time - c[i - 1].time - c[i - 1].vars.duration) <= 2 / 60 + 1e-8);
  }
});

test('binary decrypt returns to original color and shadow when seeking backwards', () => {
  const html = read('../../music-to-video/references/motion-primitives/binary-decrypt/scene.html');
  const code = html.match(/<script>([\s\S]*?)<\/script>/)[1];
  const tweens = [];
  const spans = Array.from({length: 7}, () => ({style: {}, getAttribute: () => 'D'}));
  vm.runInNewContext(code, {window: {}, document: {querySelectorAll: () => spans}, gsap: {timeline: () => ({to: (state, vars) => tweens.push({state, vars})})}});
  const {state, vars} = tweens[0];
  state.p = 1; vars.onUpdate();
  assert.equal(spans[0].style.color, 'var(--hg-fg)');
  state.p = 0.2; vars.onUpdate();
  assert.equal(spans[0].style.color, 'var(--hg-cyan)');
  assert.equal(spans[0].style.textShadow, '0 0 30px rgba(42, 255, 240, 0.5)');
});
