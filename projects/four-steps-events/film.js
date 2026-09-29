'use strict';
/* Four Steps, events film. Deterministic: every frame is a pure function of t.
   window.seek(t) draws time t. ?render disables realtime playback. ?opening=A|B|C picks the opening. */

// ---------------------------------------------------------------- core
const W = 1080, H = 1920, VO_DUR = 54.361;
const Q = new URLSearchParams(location.search);
const RENDER = Q.has('render');
const OPEN = (Q.get('opening') || 'A').toUpperCase();
const TAIL = +(Q.get('tail') || 0);
const DUR = VO_DUR + TAIL;
const C = { paper:'#F3EEE5', paper2:'#E6DED2', card:'#FBF7F0', ink:'#11110F', ink2:'#777168',
            blue:'#192EE8', navy:'#000032', volt:'#CAF222', light:'#FFFCF6' };

const clamp = (v, a = 0, b = 1) => v < a ? a : v > b ? b : v;
const lerp = (a, b, k) => a + (b - a) * k;
const E = {
  lin: x => x,
  oExpo: x => x >= 1 ? 1 : 1 - Math.pow(2, -10 * x),
  iExpo: x => x <= 0 ? 0 : Math.pow(2, 10 * x - 10),
  ioExpo: x => x <= 0 ? 0 : x >= 1 ? 1 : x < .5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2,
  oCub: x => 1 - Math.pow(1 - x, 3),
  iCub: x => x * x * x,
  ioCub: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
  oQuart: x => 1 - Math.pow(1 - x, 4),
  ioSine: x => -(Math.cos(Math.PI * x) - 1) / 2,
  oBack: x => { const c1 = 1.25, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
};
const P = (t, a, b, e = E.oExpo) => e(clamp((t - a) / (b - a)));
const two = t => Math.floor(t * 15 + 1e-6) / 15;            // hand-made elements run on twos
function rng(s) { return function () { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

const stage = document.getElementById('stage');
const fxRoot = document.getElementById('fx');
function el(tag, cls, par, css, html) {
  const e = document.createElement(tag); if (cls) e.className = cls; if (css) Object.assign(e.style, css);
  if (html != null) e.textContent = html; (par || stage).appendChild(e); return e;
}
function box(par, x, y, w, h, css, cls) {
  return el('div', 'a ' + (cls || ''), par, Object.assign({ left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px' }, css || {}));
}
function cut(par, name, x, y, w, css) {
  const e = el('img', 'cut', par, Object.assign({ left: x + 'px', top: y + 'px', width: w + 'px' }, css || {}));
  e.src = 'assets/cutouts/' + name + '.png'; return e;
}
function tf(e, o) {
  let s = '';
  if (o.p) s += `perspective(${o.p}px) `;
  s += `translate3d(${(o.x || 0).toFixed(2)}px,${(o.y || 0).toFixed(2)}px,${(o.z || 0).toFixed(2)}px)`;
  if (o.rx) s += ` rotateX(${o.rx.toFixed(3)}deg)`;
  if (o.ry) s += ` rotateY(${o.ry.toFixed(3)}deg)`;
  if (o.r) s += ` rotate(${o.r.toFixed(3)}deg)`;
  const sx = o.sx ?? o.s ?? 1, sy = o.sy ?? o.s ?? 1;
  if (sx !== 1 || sy !== 1) s += ` scale(${sx.toFixed(4)},${sy.toFixed(4)})`;
  e.style.transform = s;
  if (o.o != null) e.style.opacity = clamp(o.o).toFixed(3);
}
const show = (e, v) => { e.style.visibility = v ? 'visible' : 'hidden'; };
const op = (e, v) => { e.style.opacity = clamp(v).toFixed(3); };

// ---------------------------------------------------------------- svg helpers
const NS = 'http://www.w3.org/2000/svg';
function svg(par, x, y, w, h, vb) {
  const s = document.createElementNS(NS, 'svg');
  s.setAttribute('width', w); s.setAttribute('height', h); s.setAttribute('viewBox', vb || `0 0 ${w} ${h}`);
  Object.assign(s.style, { position: 'absolute', left: x + 'px', top: y + 'px' }); par.appendChild(s); return s;
}
function sv(par, tag, a) { const e = document.createElementNS(NS, tag); for (const k in a) e.setAttribute(k, a[k]); par.appendChild(e); return e; }
function crPath(p) {
  let d = `M${p[0][0].toFixed(1)},${p[0][1].toFixed(1)}`;
  for (let i = 0; i < p.length - 1; i++) {
    const p0 = p[i - 1] || p[i], p1 = p[i], p2 = p[i + 1], p3 = p[i + 2] || p2;
    d += `C${(p1[0] + (p2[0] - p0[0]) / 6).toFixed(1)},${(p1[1] + (p2[1] - p0[1]) / 6).toFixed(1)} ${(p2[0] - (p3[0] - p1[0]) / 6).toFixed(1)},${(p2[1] - (p3[1] - p1[1]) / 6).toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
  }
  return d;
}
function wob(pts, seed, amp = 3, seg = 44) {
  const r = rng(seed), out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const [x0, y0] = pts[i], [x1, y1] = pts[i + 1], n = Math.max(1, Math.round(Math.hypot(x1 - x0, y1 - y0) / seg));
    for (let j = 0; j < n; j++) { const k = j / n; out.push([x0 + (x1 - x0) * k + (j || i ? (r() - .5) * amp * 2 : 0), y0 + (y1 - y0) * k + (j || i ? (r() - .5) * amp * 2 : 0)]); }
  }
  out.push(pts[pts.length - 1]); return crPath(out);
}
const rrect = (x, y, w, h, seed, amp = 2.2) => wob([[x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y + .5]], seed, amp, 70);
function stroke(par, d, o) {
  return sv(par, 'path', Object.assign({ d, fill: 'none', stroke: C.ink, 'stroke-width': 4, 'stroke-linecap': 'round',
    'stroke-linejoin': 'round', pathLength: 1, 'stroke-dasharray': '1 1.01' }, o || {}));
}
const draw = (p, k) => { p.style.strokeDashoffset = (1 - clamp(k)).toFixed(4); };
function burst(par, cx, cy, r1, r2, n, color, seed) {
  const R = r1 * 1.3, s = svg(par, cx - R, cy - R, R * 2, R * 2, `${-R} ${-R} ${R * 2} ${R * 2}`), r = rng(seed), pts = [];
  for (let i = 0; i < n * 2; i++) { const a = i / (n * 2) * Math.PI * 2 + (r() - .5) * .2, rr = (i % 2 ? r2 : r1) * (.8 + r() * .32); pts.push(`${(Math.cos(a) * rr).toFixed(1)},${(Math.sin(a) * rr).toFixed(1)}`); }
  sv(s, 'polygon', { points: pts.join(' '), fill: color }); s.style.transformOrigin = '50% 50%'; return s;
}
// a printed, hand-cut burst: uneven spikes, nicked edges, and a second ink plate printed slightly off register
function printBurst(par, cx, cy, r, color, under, seed) {
  const R = r * 1.25, s = svg(par, cx - R, cy - R, R * 2, R * 2, `${-R} ${-R} ${R * 2} ${R * 2}`), rr = rng(seed);
  const shape = k => { const pts = [], n = 15; for (let i = 0; i < n * 2; i++) {
      const a = i / (n * 2) * Math.PI * 2 + (rr() - .5) * .16, big = i % 2 === 0;
      const rad = big ? r * (.78 + rr() * .3) : r * (.5 + rr() * .1);
      pts.push(`${(Math.cos(a) * rad * k).toFixed(1)},${(Math.sin(a) * rad * k).toFixed(1)}`);
      if (big && rr() > .5) pts.push(`${(Math.cos(a + .05) * rad * .93 * k).toFixed(1)},${(Math.sin(a + .05) * rad * .93 * k).toFixed(1)}`); }
    return pts.join(' '); };
  const pts = shape(1);
  if (under) { const u = sv(s, 'polygon', { points: pts, fill: under }); u.setAttribute('transform', 'translate(11 9)'); }
  sv(s, 'polygon', { points: pts, fill: color });
  s.style.transformOrigin = '50% 50%'; return s;
}
function torn(w, h, seed, amp = 7, edges = 'b') {           // clip-path polygon with a torn edge
  const r = rng(seed), pts = [], st = 22;
  pts.push('0px 0px');
  if (edges.includes('t')) { pts.length = 0; for (let x = 0; x <= w; x += st) pts.push(`${x}px ${(r() * amp).toFixed(1)}px`); } else pts.push(`${w}px 0px`);
  if (edges.includes('b')) { for (let x = w; x >= 0; x -= st) pts.push(`${x}px ${(h - r() * amp).toFixed(1)}px`); } else { pts.push(`${w}px ${h}px`, `0px ${h}px`); }
  return `polygon(${pts.join(',')})`;
}

// ---------------------------------------------------------------- type
function txt(par, str, o) {
  const b = el('div', 'txt ' + (o.cls || ''), par, {
    left: (o.x ?? 0) + 'px', top: (o.y ?? 0) + 'px', width: (o.w ?? W) + 'px', fontSize: o.size + 'px',
    fontFamily: o.serif ? 'TD' : 'TS', fontWeight: o.wt || 900, color: o.color || C.ink, textAlign: o.align || 'center',
    lineHeight: o.lh || 1.2, fontFeatureSettings: o.feat || 'normal', letterSpacing: '0' });
  if (o.origin) b.style.transformOrigin = o.origin;
  b.words = []; b.lines = [];
  str.split('\n').forEach(L => {
    const ld = el('div', 'ln', b); b.lines.push(ld); const wl = el('span', '', ld); ld.inner = wl; wl.style.display = 'inline-block';
    L.split(' ').forEach((w, i) => {
      if (i) wl.appendChild(document.createTextNode(' '));
      const s = el('span', 'w' + (w.includes('_') ? ' ltr' : ''), wl, null, w.replace(/_/g, ' ')); b.words.push(s);
    });
  });
  return b;
}
function smear(m, dir, col) {
  if (m < .8) return 'none';
  const out = []; for (let i = 1; i <= 4; i++) out.push(`${(dir * m * i / 4).toFixed(1)}px 0 0 ${col}${Math.round((.30 - i * .06) * 255).toString(16).padStart(2, '0')}`);
  return out.join(',');
}
// word arrives with a short horizontal motion blur; optional exit
function wIn(sp, t, t0, o = {}) {
  const d = o.d || .34, k = clamp((t - t0 + .04) / d);
  if (k <= 0 || (o.out != null && t > o.out + (o.od || .26))) { sp.style.opacity = 0; return; }
  const e = E.oExpo(k); let dx = (o.dx ?? -90) * (1 - e), dy = (o.dy || 0) * (1 - e), a = Math.min(1, k * 5), m = (1 - e) * (o.sm ?? 46);
  if (o.out != null && t > o.out) { const ko = clamp((t - o.out) / (o.od || .26)), eo = E.iCub(ko); dx += (o.odx ?? 110) * eo; dy += (o.ody || 0) * eo; a *= 1 - ko; m = Math.max(m, eo * 40); }
  sp.style.opacity = a.toFixed(3); sp.style.transform = `translate(${dx.toFixed(1)}px,${dy.toFixed(1)}px)`;
  sp.style.textShadow = smear(m, dx < 0 ? -1 : 1, o.col || C.ink);
}
function words(b, t, times, o = {}) { b.words.forEach((sp, i) => wIn(sp, t, times[Math.min(i, times.length - 1)] + (i >= times.length ? (i - times.length + 1) * .09 : 0), o)); }
// line rises through a mask
function rise(ln, t, t0, d = .5, out) {
  let k = E.oExpo(clamp((t - t0) / d)), y = (1 - k) * 160;
  if (out != null && t > out) y -= E.iCub(clamp((t - out) / .3)) * 110;
  ln.inner.style.transform = `translateY(${y.toFixed(2)}%)`;
}

// ---------------------------------------------------------------- shared drawings
function planDrawing(par, w, h, seed, o = {}) {   // printed floor plan
  const s = svg(par, 0, 0, w, h), r = rng(seed);
  const hall = stroke(s, rrect(30, 30, w - 60, h - 60, seed, 2), { 'stroke-width': 5 });
  const st = { x: w * .2, y: 70, w: w * .6, h: h * .14 };
  const stage = sv(s, 'path', { d: rrect(st.x, st.y, st.w, st.h, seed + 1, 1.5), fill: C.ink, 'fill-opacity': .88 });
  const seats = sv(s, 'g', {});
  const rows = o.rows || 11, cols = o.cols || 16, sx = w * .14, ex = w * .86, sy = st.y + st.h + 70, ey = h - 150;
  for (let i = 0; i < rows; i++) for (let j = 0; j < cols; j++) {
    if (j === Math.floor(cols / 2)) continue;
    sv(seats, 'rect', { x: (sx + (ex - sx) * j / (cols - 1) - 7).toFixed(1), y: (sy + (ey - sy) * i / (rows - 1) - 6).toFixed(1), width: 14, height: 11, rx: 3, fill: C.ink, 'fill-opacity': .72 });
  }
  const door = stroke(s, wob([[w * .1, h - 30], [w * .1, h - 100], [w * .22, h - 100]], seed + 3, 1), { 'stroke-width': 4, stroke: C.ink2 });
  return { s, hall, stage, seats, door, st };
}
function stageDrawing(par, w, h) {   // front elevation: deck, screen, truss, lamps
  const g = box(par, 0, 0, w, h);
  // printed like the plan: flat navy screen with a paper margin, one ink baseline for the deck
  const screen = box(g, w * .1, h * .22, w * .8, h * .5, { background: C.navy, boxShadow: `0 0 0 ${Math.max(4, w * .008).toFixed(0)}px ${C.card}, 3px 4px 0 ${Math.max(4, w * .008) + 1}px rgba(17,17,15,.12)` });
  const deck = box(g, -w * .02, h * .8, w * 1.04, Math.max(6, h * .022), { background: C.ink });
  const truss = cut(g, 'truss', -w * .04, 0, w * 1.08);
  const l1 = cut(g, 'spotlight', w * .05, h * .08, w * .2, { transform: 'rotate(18deg)' });
  const l2 = cut(g, 'spotlight', w * .75, h * .08, w * .2, { transform: 'scaleX(-1) rotate(18deg)' });
  return { g, screen, deck, truss, l1, l2 };
}
// the Four Steps lockup, split into mark shapes and wordmark
const MARK = ['M108.3,40.7h67.5V0h-28.3c-21.7,0-39.3,17.6-39.3,39.3v1.5Z', 'M40.8,100.5h135.1v-40.7h-94.3c-22.5,0-40.7,18.2-40.7,40.7Z',
  'M0,160.2h175.8v-40.7H40.7C18.2,119.5,0,137.7,0,160.2Z', 'M135.1,220h40.8v-40.8c-22.5,0-40.8,18.3-40.8,40.8Z'];
const WORDMARK_EL = [
  ['polygon', { points: '221.1 99.9 221.1 .1 291.4 .1 291.4 20.8 244.3 20.8 244.3 43.7 284.8 43.7 284.8 63.1 244.3 63.1 244.3 99.9 221.1 99.9' }],
  ['path', { d: 'M350.7,104.6c-9.9,0-19-2.3-27.3-7-8.3-4.7-14.9-11-19.7-19-4.9-8-7.3-16.8-7.3-26.3s2.4-18.3,7.3-26.3c4.9-8,11.4-14.3,19.7-19,8.3-4.7,17.4-7,27.3-7s18.8,2.3,27.1,7c8.3,4.7,14.9,11,19.8,19,4.9,8,7.3,16.7,7.3,26.3s-2.4,18.2-7.3,26.3c-4.9,8-11.5,14.4-19.8,19-8.3,4.7-17.4,7-27.1,7M350.7,83.4c5.7,0,10.9-1.3,15.6-4,4.7-2.6,8.5-6.3,11.3-11.1,2.8-4.7,4.1-10,4.1-15.9s-1.4-11.2-4.1-16c-2.8-4.7-6.5-8.4-11.3-11.1-4.7-2.7-10-4-15.6-4s-11,1.3-15.7,4c-4.7,2.7-8.5,6.4-11.2,11.1-2.7,4.7-4.1,10-4.1,16s1.4,11.2,4.1,15.9c2.8,4.7,6.5,8.4,11.3,11.1,4.7,2.7,10,4,15.6,4' }],
  ['path', { d: 'M458.3,102.1c-8.3,0-15.7-1.7-22.4-5-6.7-3.3-11.9-8.1-15.7-14.3-3.8-6.2-5.7-13.4-5.7-21.5V.1h23.2v59.6c0,4.1.8,7.8,2.4,11,1.6,3.2,4,5.8,7,7.6,3.1,1.8,6.8,2.8,11.2,2.8s7.9-.9,11-2.8c3.1-1.8,5.4-4.4,7.1-7.6,1.6-3.3,2.5-6.9,2.5-11V.1h23.3v61.2c0,7.8-1.8,14.8-5.4,21.1-3.6,6.2-8.8,11.1-15.4,14.5-6.7,3.5-14.3,5.2-23,5.2' }],
  ['path', { d: 'M518,99.9V.1h43.8c7,0,13.2,1.4,18.6,4.2,5.4,2.8,9.7,6.8,12.8,11.8,3.1,5.1,4.6,10.9,4.6,17.5s-.8,8.6-2.3,12.4c-1.5,3.8-3.7,7.2-6.6,10-2.8,2.9-6.2,5.1-10,6.7l21.3,37h-26.6l-17.5-33.4h-14.8v33.4h-23.3ZM560.8,47.1c2.5,0,4.9-.6,7-1.7,2.1-1.1,3.8-2.7,5-4.7,1.2-2,1.8-4.3,1.8-6.9s-.6-4.4-1.8-6.4c-1.2-2-2.9-3.6-5-4.7-2.1-1.2-4.4-1.8-6.9-1.8h-19.6v26.3h19.6Z' }],
  ['path', { d: 'M257.3,220c-9.6,0-17.6-1.6-23.9-4.8-6.3-3.2-10.9-7.3-13.7-12.4-2.9-5.1-4.3-10.5-4.3-16.2h23.3c0,.4,0,.8,0,1.2,0,.4,0,.8.1,1.2.4,2.3,1.4,4.4,2.9,6.1,1.6,1.7,3.7,3,6.3,4,2.6,1,5.7,1.4,9.2,1.4s7.8-.4,10.5-1.2c2.7-.8,4.6-2.1,5.9-3.8,1.2-1.7,1.9-3.8,1.9-6.3s-.7-4.1-2.2-5.6c-1.5-1.5-3.7-2.8-6.5-3.9-2.9-1.1-6.6-2.1-11.3-3.2-7.1-1.7-13.3-3.7-18.6-5.9-5.3-2.2-9.7-5.5-13.4-9.7-3.7-4.2-5.5-9.6-5.5-16.1s1.4-11.1,4.3-15.5c2.9-4.4,7.2-7.8,12.9-10.3,5.7-2.4,12.8-3.7,21.3-3.7s15.8,1.3,21.6,3.9c5.8,2.6,10.2,6.2,13.1,10.9,2.9,4.7,4.4,10.2,4.4,16.7h-23.3c0-2-.5-3.9-1.6-5.5-1.1-1.7-2.8-3-5.2-4.1-2.4-1-5.5-1.5-9.4-1.5s-7,.4-9.2,1.3c-2.2.9-3.7,2-4.5,3.3-.8,1.3-1.2,2.9-1.2,4.7s.8,3.9,2.3,5.4c1.5,1.5,3.9,2.8,7.1,3.9,3.2,1.1,7.5,2.1,12.9,3.1,7.2,1.4,13.4,3.4,18.6,5.9,5.2,2.5,9.3,6,12.4,10.2,3,4.3,4.5,9.5,4.5,15.7s-1.7,12.1-5.2,16.7c-3.5,4.6-8.3,8.1-14.6,10.5-6.3,2.4-13.5,3.6-21.9,3.6' }],
  ['polygon', { points: '330.8 220 330.8 140.9 302.8 140.9 302.8 120.2 381.7 120.2 381.7 140.9 353.9 140.9 353.9 220 330.8 220' }],
  ['polygon', { points: '391.6 220 391.6 120.2 462 120.2 462 140.8 414.9 140.8 414.9 159.7 455.3 159.7 455.3 179 414.9 179 414.9 199.3 462.7 199.3 462.7 220 391.6 220' }],
  ['path', { d: 'M474.2,220v-99.8h43.2c6.9,0,13.1,1.5,18.5,4.4,5.5,3,9.7,7.1,12.8,12.4,3.1,5.3,4.6,11.2,4.6,17.8s-1.5,13.3-4.5,18.6c-3,5.4-7.3,9.5-12.7,12.5-5.4,3-11.6,4.4-18.4,4.4h-20.2v29.6h-23.3ZM516.4,169.7c2.5,0,4.8-.7,6.9-2,2.1-1.3,3.7-3.1,5-5.4,1.2-2.3,1.8-4.8,1.8-7.6s-.6-4.5-1.8-6.7c-1.2-2.2-2.9-3.9-5-5.2-2.1-1.3-4.4-2-6.8-2h-19v28.8h19Z' }],
  ['path', { d: 'M598.4,220c-9.6,0-17.6-1.6-23.9-4.8-6.3-3.2-10.9-7.3-13.7-12.4-2.9-5.1-4.3-10.5-4.3-16.2h23.3c0,.4,0,.8,0,1.2,0,.4,0,.8.1,1.2.4,2.3,1.4,4.4,2.9,6.1,1.6,1.7,3.7,3,6.3,4,2.6,1,5.7,1.4,9.2,1.4s7.8-.4,10.5-1.2c2.7-.8,4.6-2.1,5.9-3.8,1.2-1.7,1.9-3.8,1.9-6.3s-.7-4.1-2.2-5.6c-1.5-1.5-3.7-2.8-6.5-3.9-2.9-1.1-6.6-2.1-11.3-3.2-7.1-1.7-13.3-3.7-18.6-5.9-5.3-2.2-9.7-5.5-13.4-9.7-3.7-4.2-5.5-9.6-5.5-16.1s1.4-11.1,4.3-15.5c2.9-4.4,7.2-7.8,12.9-10.3,5.7-2.4,12.8-3.7,21.3-3.7s15.8,1.3,21.6,3.9c5.8,2.6,10.2,6.2,13.1,10.9,2.9,4.7,4.4,10.2,4.4,16.7h-23.3c0-2-.5-3.9-1.6-5.5-1.1-1.7-2.8-3-5.2-4.1-2.4-1-5.5-1.5-9.4-1.5s-7,.4-9.2,1.3c-2.2.9-3.7,2-4.5,3.3-.8,1.3-1.2,2.9-1.2,4.7s.8,3.9,2.3,5.4c1.5,1.5,3.9,2.8,7.1,3.9,3.2,1.1,7.5,2.1,12.9,3.1,7.2,1.4,13.4,3.4,18.6,5.9,5.2,2.5,9.3,6,12.4,10.2,3,4.3,4.5,9.5,4.5,15.7s-1.7,12.1-5.2,16.7c-3.5,4.6-8.3,8.1-14.6,10.5-6.3,2.4-13.5,3.6-21.9,3.6' }]
];
function lockup(par, x, y, scale, color) {
  const s = svg(par, x, y, 640.1 * scale, 220 * scale, '0 0 640.1 220');
  const m = MARK.map(d => { const p = sv(s, 'path', { d, fill: color }); p.style.transformBox = 'fill-box'; p.style.transformOrigin = '50% 50%'; return p; });
  const wg = sv(s, 'g', { fill: color }); WORDMARK_EL.forEach(([tag, a]) => sv(wg, tag, a));
  return { s, m, wg };
}

// ---------------------------------------------------------------- scene registry
const scenes = [];
let B3SEAT = [540, 1000];
function scene(a, b, build, css) { const root = el('div', 'scene', stage, css); const f = build(root); scenes.push({ a, b, root, f }); return root; }

// ================================================================ B1  OPENINGS  (0 to 5.6)
const TRUSS_Y = 700;
function openingA(R) {
  // typography-led editorial collage
  const beam = box(R, 0, 0, W, H, { background: C.light, clipPath: 'polygon(0 0,0 0,0 0)' });
  const truss = cut(R, 'truss', -110, TRUSS_Y, 1300);          // sits behind the type, its rail on the gap between the lines
  const t1 = txt(R, 'آخر', { x: -60, y: 70, w: 1128, size: 450, align: 'right', lh: 1, serif: true, cls: 'lift' });
  const t2 = txt(R, 'فعالية', { x: -70, y: 480, w: 1100, size: 310, align: 'left', lh: 1, cls: 'lift' });
  const t3 = txt(R, 'كبيرة', { x: -40, y: 900, w: 1140, size: 370, align: 'right', lh: 1, cls: 'lift' });
  const big = [t1, t2, t3];
  const spot = el('div', 'a', R, { left: '-40px', top: '1330px', width: '480px', height: '470px', transformOrigin: '50% 30%' });
  cut(spot, 'spotlight', 0, 0, 480);
  const burstB = printBurst(R, 540, 1230, 360, C.ink, C.blue, 21);
  const ticket = box(R, 230, 1080, 620, 300, { background: C.card, clipPath: torn(620, 300, 5, 8, 'b'), transformOrigin: '50% 50%' }, 'card e3');
  txt(ticket, 'منبهر', { x: 120, y: 42, w: 500, size: 160, serif: true, wt: 900 });
  box(ticket, 118, 20, 0, 250, { borderLeft: '4px dashed ' + C.ink2, opacity: .55 });
  box(ticket, 0, 0, 20, 300, { background: C.blue });
  el('div', 'lbl a', ticket, { left: '30px', top: '40px', fontSize: '28px', writingMode: 'vertical-rl' }, 'تذكرة دخول');
  const sub = txt(R, 'حضرتها وطلعت منها', { x: 0, y: 960, w: W, size: 112, serif: true, wt: 700, cls: 'lift' });
  const q1 = txt(R, 'تذكر وش اللي', { x: 0, y: 610, w: W, size: 104, serif: true, wt: 500, color: C.ink, cls: 'lift' });
  const q2 = txt(R, 'علق في بالك؟', { x: 0, y: 770, w: W, size: 176, serif: true, wt: 900, cls: 'lift' });
  return t => {
    // big words: land on the VO, then compress up to make room
    const up = P(t, 1.18, 1.62, E.ioCub), out = P(t, 3.36, 3.7, E.iCub);
    words(t1, t, [-.2], { dx: -140 }); words(t2, t, [.36], { dx: 150 }); words(t3, t, [.8], { dx: -150 });
    big.forEach((b, i) => { b.style.transformOrigin = '50% 0'; tf(b, { y: lerp(0, [-10, -170, -330][i], up) - out * 900, s: lerp(1, .6, up), o: 1 - out }); });
    // light beam from the lamp, behind the type
    const sw = -34 + 30 * P(t, -.3, .6, E.oCub) + 3 * Math.sin(t * 1.4);
    tf(spot, { r: sw, y: out * 700 });
    const lx = 120, ly = 1470 + out * 700, a = (-60 + sw) * Math.PI / 180, hw = .115;
    const f = 2600, pa = [lx + Math.cos(a - hw) * f, ly + Math.sin(a - hw) * f], pb = [lx + Math.cos(a + hw) * f, ly + Math.sin(a + hw) * f];
    beam.style.clipPath = `polygon(${lx}px ${ly}px,${pa[0].toFixed(0)}px ${pa[1].toFixed(0)}px,${pb[0].toFixed(0)}px ${pb[1].toFixed(0)}px)`;
    op(beam, P(t, -.2, .2) * (1 - out));
    tf(truss, { x: lerp(1200, 0, P(t, .3, .62)) + out * -1300, y: -up * 300, o: 1 - P(t, 2.5, 2.8) });
    // منبهر: the ticket is slapped down on a printed burst
    const kk = P(two(t), 2.8, 3.02, E.oBack);
    tf(burstB, { s: kk * (1 - out), r: 6 * kk }); op(burstB, t > 2.8 ? 1 : 0);
    tf(ticket, { s: lerp(.3, 1, kk) * (1 - out * .4), r: lerp(-22, -5, kk), y: -out * 900, o: t > 2.8 ? 1 - out : 0 });
    words(sub, t, [1.24, 1.9, 2.42], { out: 2.74, od: .2 });
    const qo = P(t, 5.26, 5.44, E.iCub); tf(q1, { y: -qo * 520, o: 1 - qo }); tf(q2, { y: -qo * 520, o: 1 - qo });
    words(q1, t, [3.46, 4.02, 4.26]); words(q2, t, [4.42, 4.7, 4.84]);
  };
}
function openingB(R) {
  // object-led: a printed plan stands up into a stage
  const hd = txt(R, 'آخر فعالية كبيرة', { x: 0, y: 150, w: W, size: 150, cls: 'lift' });
  const hold = el('div', 'a', R, { left: '60px', top: '560px', width: '960px', height: '1100px', perspective: '1600px' });
  const card = box(hold, 0, 0, 960, 1100, { background: C.card, transformOrigin: '50% 100%', transformStyle: 'preserve-3d' }, 'card');
  const pl = planDrawing(card, 960, 1100, 11);
  const elev = box(card, 190, -330, 580, 480, { transformOrigin: '50% 100%' });
  const sd = stageDrawing(elev, 580, 480);
  const cones = [0, 1].map(i => box(R, 0, 0, W, H, { background: C.blue, opacity: 0 }));
  const sub = txt(R, 'حضرتها وطلعت منها', { x: 0, y: 380, w: W, size: 92, serif: true, wt: 700 });
  const bb = burst(R, 540, 1460, 260, 150, 10, C.ink, 4);
  const bw = txt(R, 'منبهر', { x: 0, y: 1390, w: W, size: 120, color: C.card });
  const q1 = txt(R, 'تذكر وش اللي\nعلق في بالك؟', { x: 0, y: 520, w: W, size: 130, serif: true, wt: 700, cls: 'lift' });
  return t => {
    const out = P(t, 3.36, 3.7, E.iCub);
    words(hd, t, [-.1, .36, .82], { out: 3.36 });
    const tilt = lerp(58, 20, P(t, -.3, 1.3, E.ioCub));
    tf(card, { rx: tilt, y: out * 1200 });
    const up = P(t, .82, 1.5, E.oCub);
    tf(elev, { rx: lerp(-90, -tilt, up), o: up > 0 ? 1 : 0 });
    tf(sd.truss, { y: lerp(-500, 0, P(t, 1.24, 1.6, E.oBack)) });
    [sd.l1, sd.l2].forEach((l, i) => op(l, P(t, 1.9 + i * .15, 2.1 + i * .15)));
    cones.forEach((c, i) => {
      const cx = i ? 800 : 280, cy = 760 + out * 1200, a = (i ? 110 : 70) * Math.PI / 180, hw = .2, f = 1500;
      c.style.clipPath = `polygon(${cx}px ${cy}px,${cx + Math.cos(a - hw) * f}px ${cy + Math.sin(a - hw) * f}px,${cx + Math.cos(a + hw) * f}px ${cy + Math.sin(a + hw) * f}px)`;
      op(c, (t > 2.84 ? .9 : 0) * (1 - out));
    });
    words(sub, t, [1.24, 1.9, 2.42], { out: 3.36 });
    const kk = P(two(t), 2.8, 3.0, E.oBack); tf(bb, { s: kk * (1 - out) }); words(bw, t, [2.84], { out: 3.36 });
    words(q1, t, [3.46, 4.02, 4.26, 4.42, 4.7, 4.84]);
  };
}
function openingC(R) {
  // depth-led: the camera pushes through layered paper planes
  const rig = el('div', 'a', R, { left: 0, top: 0, width: W + 'px', height: H + 'px', perspective: '1200px', perspectiveOrigin: '50% 48%' });
  const world = el('div', 'a', rig, { left: 0, top: 0, width: W + 'px', height: H + 'px', transformStyle: 'preserve-3d' });
  const far = el('div', 'a', world, { left: '-240px', top: '200px', width: '1560px', height: '1300px' });
  const sd = stageDrawing(far, 1560, 1300);
  const mid = el('div', 'a', world, { left: '-400px', top: '900px', width: '1880px', height: '900px' });
  const ms = svg(mid, 0, 0, 1880, 900);
  for (let rI = 0; rI < 4; rI++) for (let j = 0; j < 22; j++) sv(ms, 'rect', { x: 40 + j * 84 + (rI % 2) * 42, y: 120 + rI * 150, width: 66, height: 110, rx: 18, fill: C.ink, 'fill-opacity': .92 - rI * .08 });
  const cam = cut(mid, 'camera', 1320, -330, 560);
  const near = el('div', 'a', world, { left: '0', top: '0', width: W + 'px', height: H + 'px' });
  const badge = el('div', 'a', near, { left: '-40px', top: '-380px', width: '330px', height: '870px', transformOrigin: '50% 0' }); cut(badge, 'badge', 0, 0, 330);
  const cable = cut(near, 'cable', 640, 1450, 560);
  const hd = txt(R, 'آخر فعالية\nكبيرة', { x: 0, y: 170, w: W, size: 190, cls: 'lift', lh: 1.05 });
  const sub = txt(R, 'حضرتها وطلعت منها منبهر', { x: 0, y: 1540, w: W, size: 84, serif: true, wt: 700, color: C.card });
  const dark = box(R, 0, 0, W, H, { background: C.navy, opacity: 0 });
  R.insertBefore(dark, rig);
  const q1 = txt(R, 'تذكر وش اللي\nعلق في بالك؟', { x: 0, y: 520, w: W, size: 130, serif: true, wt: 700, cls: 'lift' });
  return t => {
    const push = P(t, -.4, 3.4, E.ioSine), out = P(t, 3.36, 3.8, E.iCub);
    tf(far, { z: lerp(-1600, -1100, push) + out * 900 });
    tf(mid, { z: lerp(-700, -150, push) + out * 1400, o: 1 - out });
    tf(near, { z: lerp(-100, 380, push) + out * 800, o: 1 - out });
    const bt = t + .5; tf(badge, { r: 10 * Math.exp(-.8 * bt) * Math.cos(3.2 * bt) });
    op(far, 1 - out);
    words(hd, t, [-.1, .36, .82], { out: 3.36 });
    words(sub, t, [1.24, 1.9, 2.42, 2.84], { out: 3.36 });
    op(dark, P(t, 1.1, 1.5) * (1 - out));
    words(q1, t, [3.46, 4.02, 4.26, 4.42, 4.7, 4.84]);
  };
}
const OPENINGS = { A: openingA, B: openingB, C: openingC };
scene(-1, 5.62, R => (OPENINGS[OPEN] || openingA)(R));

// ================================================================ B2  المسرح؟ الإضاءة؟ ساعة  (5.05 to 9.75)
scene(4.8, 9.75, R => {
  const holder = el('div', 'a', R, { left: '50px', top: '740px', width: '980px', height: '1100px', perspective: '1800px' });
  const card = box(holder, 0, 0, 980, 1100, { background: C.card, transformStyle: 'preserve-3d' }, 'card e2');
  const pl = planDrawing(card, 980, 1100, 31, { rows: 11, cols: 17 });
  const lb1 = el('div', 'lbl a', card, { left: '60px', top: '1010px', fontSize: '30px' }, 'مدخل');
  el('div', 'lbl a', card, { right: '60px', top: '1010px', fontSize: '28px' }, 'مخطط القاعة  ·  ١:٢٠٠');
  const pathS = svg(card, 0, 0, 980, 1100);
  const route = stroke(pathS, wob([[120, 1030], [130, 930], [300, 880], [470, 880], [490, 380]], 5, 4), { stroke: C.blue, 'stroke-width': 10 });
  const elev = box(card, 196, -330, 588, 560, { transformOrigin: '50% 100%' });
  const sd = stageDrawing(elev, 588, 560);
  const title = txt(R, 'المسرح؟', { x: 0, y: 110, w: W, size: 190, serif: true, wt: 700, cls: 'lift' });
  const navy = box(R, 0, 0, W, H, { background: C.navy, opacity: 0 });
  // stopwatch (behind the cone) and the swinging lamp
  const swW = 860, swX = 110, swY = 620, swC = [swX + swW * .504, swY + swW * (968 / 705) * .63];
  const sw = cut(R, 'stopwatch', swX, swY, swW, null); sw.className = 'cut flat';
  const lamp = el('div', 'a', R, { left: '560px', top: '-160px', width: '560px', height: '540px', transformOrigin: '50% 12%' });
  cut(lamp, 'spotlight', 0, 0, 560);
  const strike = box(R, 0, 0, 70, 70, { borderRadius: '50%', background: C.volt, opacity: 0 });
  const cone = box(R, 0, 0, W, H, { background: C.light });
  const coneWord = txt(cone, 'الإضاءة؟', { x: -40, y: 1040, w: W, size: 148, serif: true, wt: 900, color: C.ink });
  const t2a = txt(R, 'ولا', { x: 0, y: 118, w: W, size: 84, serif: true, wt: 500, cls: 'lift' });
  const t2 = txt(R, 'التنظيم', { x: 0, y: 190, w: W, size: 210, serif: true, wt: 900, cls: 'lift' });
  const t3 = txt(R, 'اللي كان ماشي كأنه ساعة؟', { x: 0, y: 470, w: W, size: 52, wt: 500, color: C.ink2 });
  const blocks = [0, 1, 2, 3, 4, 5].map(i => box(R, 0, 0, 1, 1, { background: C.blue, borderRadius: '3px' }));
  const lampPivot = [560 + 280, -160 + 540 * .12], lens = [560 + 560 * .33, -160 + 540 * .66];
  return t => {
    // the plan peeks in under the question on «بالك», then rises into frame
    const peek = P(t, 4.84, 5.2, E.oExpo), inK = P(t, 5.26, 5.62, E.oExpo);
    tf(card, { y: lerp(lerp(1400, 960, peek), 0, inK), r: lerp(-4, 0, inK) });
    draw(route, P(two(t), 5.3, 5.9, E.oCub));
    const fold = P(t, 5.62, 6.02, E.oCub);
    tf(elev, { rx: lerp(-90, 0, fold), o: fold > 0 ? 1 : 0 });
    tf(sd.truss, { y: lerp(-300, 0, P(t, 5.7, 5.98, E.oBack)) });
    words(title, t, [5.5], { out: 6.0, od: .2 });
    // lights down at الإضاءة
    const dn = P(two(t), 6.0, 6.1, E.lin), upP = t >= 7.2 ? 1 : 0;
    op(navy, dn * (1 - upP));
    tf(holder, { o: 1 - dn, s: lerp(1, .9, dn) });
    // lamp swing
    const sT = t - 6.0, ang = t < 6 ? -60 : lerp(-60, 8, E.oCub(clamp(sT / .42))) + (sT > .42 ? 4 * Math.exp(-3 * (sT - .42)) * Math.sin(6 * (sT - .42)) : 0);
    const toC = P(t, 7.08, 7.55, E.ioCub);
    tf(lamp, { r: ang, x: lerp(0, swC[0] - lampPivot[0], toC), y: lerp(0, swC[1] - lampPivot[1] - 100, toC), s: lerp(1, .15, toC), o: (t > 6 ? 1 : 0) * (1 - P(t, 7.3, 7.55)) });
    const ra = ang * Math.PI / 180, vx = lens[0] - lampPivot[0], vy = lens[1] - lampPivot[1];
    let lx = lampPivot[0] + vx * Math.cos(ra) - vy * Math.sin(ra), ly = lampPivot[1] + vx * Math.sin(ra) + vy * Math.cos(ra);
    lx = lerp(lx, swC[0], toC); ly = lerp(ly, swC[1], toC);
    tf(strike, { x: lx - 35, y: ly - 35, o: (t > 6.12 && t < 6.26) ? 1 : 0 });
    // cone: a flat sheet of light that becomes the stopwatch hand
    const tick = t > 8.9 ? Math.floor((t - 8.9) * 15) * 6 : 0;
    let dir = Math.atan2(1150 - ly, 540 - lx) * 180 / Math.PI + (ang - 8) * .9 + lerp(0, 200, P(t, 7.08, 8.6, E.ioSine)) + tick;
    const hw = lerp(16.5, .9, toC) * Math.PI / 180, len = lerp(2600, swW * .33, toC), d = dir * Math.PI / 180;
    const back = lerp(0, 40, toC);
    cone.style.clipPath = `polygon(${(lx - Math.cos(d) * back).toFixed(1)}px ${(ly - Math.sin(d) * back).toFixed(1)}px,${(lx + Math.cos(d - hw) * len).toFixed(1)}px ${(ly + Math.sin(d - hw) * len).toFixed(1)}px,${(lx + Math.cos(d + hw) * len).toFixed(1)}px ${(ly + Math.sin(d + hw) * len).toFixed(1)}px)`;
    cone.style.background = toC > .5 ? C.blue : C.light;
    op(cone, t < 6.12 ? 0 : 1 - P(t, 9.35, 9.6));
    op(coneWord, 1 - toC * 2);
    tf(sw, { s: lerp(.2, 1, P(t, 7.08, 7.5, E.oExpo)), o: t > 7.08 ? 1 - P(t, 9.35, 9.6) : 0 });
    sw.style.transformOrigin = `${swW * .504}px ${swW * (968 / 705) * .63}px`;
    words(t2a, t, [7.02], { out: 9.2 }); words(t2, t, [7.08], { out: 9.2 }); words(t3, t, [7.74, 7.94, 8.08, 8.5, 8.9], { out: 9.2, dx: -40, sm: 20 });
    // minute marks peel off the dial and become the ruled lines of the first planning sheet
    blocks.forEach((b, i) => {
      const t0 = 8.95 + i * .06, k = P(two(t), t0, t0 + .4, E.ioCub), a = (-90 + (i + 1) * 30) * Math.PI / 180;
      const sx = swC[0] + Math.cos(a) * swW * .3, sy = swC[1] + Math.sin(a) * swW * .3;
      const gx = lerp(sx, 250, k), gy = lerp(sy, 1060 + i * 64, k), gw = lerp(14, 660 - (i % 3) * 90, k);
      Object.assign(b.style, { left: gx.toFixed(1) + 'px', top: gy.toFixed(1) + 'px', width: gw.toFixed(1) + 'px', height: lerp(26, 10, k).toFixed(1) + 'px' });
      op(b, t > t0 ? 1 : 0);
    });
  };
});

// ================================================================ B3  backstage layers  (9.4 to 16.2)
scene(9.4, 16.2, R => {
  const rig = el('div', 'a', R, { left: 0, top: 0, width: W + 'px', height: H + 'px', perspective: '2000px', perspectiveOrigin: '50% 40%' });
  const cam = el('div', 'a', rig, { left: 0, top: 0, width: W + 'px', height: H + 'px', transformStyle: 'preserve-3d' });
  const CW = 760, CH = 960, CX = 200, CY = 600;
  const L = [0, 1, 2, 3].map(i => { const c = box(cam, CX, CY, CW, CH, { background: C.card, transformOrigin: '50% 50%' }, 'card e2'); return c; });
  // L0 the event as guests see it
  const sd = stageDrawing(box(L[0], 50, 40, CW - 100, 520), CW - 100, 520);
  const aud = svg(L[0], 0, 560, CW, 360);
  for (let r = 0; r < 5; r++) for (let j = 0; j < 13 - (r % 2); j++) sv(aud, 'rect', { x: 40 + j * 54 + (r % 2) * 27, y: 30 + r * 62, width: 40, height: 48, rx: 12, fill: C.ink, 'fill-opacity': .9 - r * .1 });
  // L1 lighting plot
  const lp = svg(L[1], 0, 0, CW, CH);
  stroke(lp, rrect(40, 40, CW - 80, CH - 80, 3), { stroke: C.ink2, 'stroke-width': 2 });
  for (let i = 0; i < 7; i++) { const x = 90 + i * 97; sv(lp, 'circle', { cx: x, cy: 160, r: 24, fill: 'none', stroke: C.ink, 'stroke-width': 4 });
    sv(lp, 'path', { d: `M${x},184 L${x - 70 + i * 10},700 L${x + 70 + i * 10},700 Z`, fill: 'none', stroke: C.ink2, 'stroke-width': 2, 'stroke-dasharray': '8 8' }); }
  sv(lp, 'rect', { x: 120, y: 700, width: CW - 240, height: 60, fill: C.ink, 'fill-opacity': .85 });
  // L2 cue sheet
  const cues = [['١٨:٣٠', 'فتح الأبواب'], ['١٩:٠٠', 'دخول الضيوف'], ['١٩:٢٠', 'كلمة الافتتاح'], ['١٩:٤٠', 'العرض المرئي'], ['٢٠:٠٥', 'التكريم'], ['٢٠:٣٠', 'التغطية المباشرة']];
  el('div', 'a', L[2], { left: '0', top: '50px', width: CW + 'px', textAlign: 'center', font: '900 54px TS' }, 'جدول التشغيل');
  const rowsE = cues.map((c, i) => {
    const r = box(L[2], 50, 170 + i * 122, CW - 100, 110, { borderBottom: '3px solid ' + C.ink2 });
    el('div', 'a', r, { right: '10px', top: '26px', font: '700 50px TS', direction: 'ltr' }, c[0]);
    el('div', 'a', r, { right: '220px', top: '26px', font: '500 46px TS' }, c[1]);
    const ts = svg(r, 20, 20, 70, 70); const tk = stroke(ts, 'M10,38 L28,56 L62,12', { stroke: C.blue, 'stroke-width': 9 });
    r.tk = tk; return r;
  });
  const scrib = svg(rowsE[3], 0, 0, CW - 100, 110);
  const cross = stroke(scrib, wob([[CW - 330, 40], [CW - 120, 76], [CW - 320, 66], [CW - 110, 38]], 9, 3, 30), { stroke: C.blue, 'stroke-width': 13 });
  const fix = el('div', 'a', rowsE[3], { right: '14px', top: '-92px', font: '900 92px TD', color: C.blue, direction: 'ltr', transform: 'rotate(-6deg)' }, '١٩:٣٥');
  const ring = svg(rowsE[3], CW - 330, -110, 260, 150); const ringP = stroke(ring, wob([[40, 90], [60, 20], [200, 12], [240, 70], [180, 132], [50, 120], [30, 70]], 19, 4, 40), { stroke: C.blue, 'stroke-width': 6 });
  // L3 guest flow plan
  const fp = planDrawing(L[3], CW, CH, 41, { rows: 9, cols: 13 });
  const flow = stroke(fp.s, wob([[90, CH - 60], [100, CH - 200], [260, CH - 240], [380, 330]], 8, 4), { stroke: C.blue, 'stroke-width': 9 });
  const labels = ['الحدث', 'مخطط الإضاءة', 'جدول التشغيل', 'مسار الضيوف'].map((s, i) => el('div', 'lbl a', L[i], { left: '0', top: '-58px', fontSize: '34px', color: C.ink }, s));
  const radio = cut(R, 'radio', -30, 1250, 300);
  // ليالي / تخطيط: the word sits behind the stack, the top sheets overlap its foot
  const t1a = txt(R, 'ليالي', { x: 0, y: 30, w: W, size: 104, serif: true, wt: 500 });
  const t1 = txt(R, 'تخطيط', { x: 0, y: 95, w: W, size: 250, serif: true, wt: 900 });
  R.insertBefore(t1, rig); R.insertBefore(t1a, rig);
  const t2 = txt(R, 'أصغر غلطة', { x: 0, y: 190, w: W, size: 132, cls: 'lift' });
  // seat map of thousands, drawn past the frame edges; the camera pulls back out of the one blue seat
  const seatW = el('div', 'a', R, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
  const seatC = el('canvas', 'a', seatW, { left: '-120px', top: 0 }); seatC.width = W + 240; seatC.height = H + 200;
  const g = seatC.getContext('2d'); let blueSeat = null;
  { const r = rng(77), cx = 540 + 120, cy = 330; g.fillStyle = C.ink; let n = 0;
    for (let rad = 190; rad < 2100; rad += 20) { const step = 18 / rad;
      for (let a = Math.PI * .02; a < Math.PI * .98; a += step) { const x = cx + Math.cos(a) * rad * 1.08, y = cy + Math.sin(a) * rad;
        if (y < 560 || y > H + 180 || x < 0 || x > W + 240) continue; const ad = Math.abs(a - Math.PI / 2); if (Math.abs(ad - .33) < .025 || ad < .012) continue;
        g.globalAlpha = .62 + r() * .3; g.beginPath(); g.arc(x, y, 4.6, 0, 7); g.fill(); n++; } }
    g.globalAlpha = 1; blueSeat = [540 + Math.cos(Math.PI * .5 + .09) * 590 * 1.08, cy + Math.sin(Math.PI * .5 + .09) * 590]; window.__seats = n; B3SEAT = blueSeat; }
  seatW.style.transformOrigin = `${blueSeat[0].toFixed(1)}px ${blueSeat[1].toFixed(1)}px`;
  const blueDot = box(seatW, blueSeat[0] - 9, blueSeat[1] - 9, 18, 18, { background: C.blue, borderRadius: '50%' });
  const t3a = txt(R, 'قدام', { x: 0, y: 70, w: W, size: 80, serif: true, wt: 500 });
  const t3 = txt(R, 'آلاف الضيوف', { x: 0, y: 140, w: W, size: 150, cls: 'lift' });
  // تنحسب: a rubber stamp, printed at an angle
  const stamp = box(R, 250, 1250, 580, 230, { border: `10px solid ${C.ink}`, background: C.card, transformOrigin: '50% 50%' }, 'card e2');
  txt(stamp, 'تنحسب', { x: 0, y: 12, w: 560, size: 150, color: C.ink });
  return t => {
    // the sheet prints down over the ruled lines that came off the stopwatch
    const rev = P(t, 9.42, 9.82, E.ioCub);
    const sep = i => P(t, 10.2 + (3 - i) * .09, 10.95 + (3 - i) * .09, E.ioCub);
    const zoom = P(t, 12.85, 13.5, E.ioCub), pull = P(t, 14.25, 14.7, E.iCub);
    L.forEach((c, i) => {
      const k = sep(i), drift = P(t, 10.9, 12.85, E.ioSine);
      let o = { x: -i * 95 * k, y: -i * 150 * k, z: -i * (6 + 420 * k), ry: -34 * k - 6 * drift, rx: 9 * k };
      if (i === 2) { o = { x: lerp(o.x, -60, zoom), y: lerp(o.y, -120, zoom), z: lerp(o.z, 500, zoom), ry: lerp(o.ry, 0, zoom), rx: lerp(o.rx, 0, zoom) }; }
      else if (i < 2) { o.z += 1900 * zoom; o.x -= 500 * zoom; }       // the sheets in front fly past the lens
      else o.z -= 800 * zoom;
      o.s = i === 2 ? lerp(1, .02, pull) : 1;
      o.o = i === 2 ? 1 - P(t, 14.6, 14.7) : i < 2 ? 1 - P(t, 12.95, 13.2) : 1 - zoom;
      tf(c, o);
      c.style.clipPath = rev < 1 ? `inset(0 0 ${(100 - rev * 100).toFixed(1)}% 0)` : 'none';
      op(labels[i], P(t, 10.6 + i * .08, 10.9 + i * .08) * (1 - P(t, 12.7, 12.9)));
    });
    L[2].style.transformOrigin = '62% 58%';
    draw(flow, P(two(t), 10.9, 11.6));
    rowsE.forEach((r, i) => { draw(r.tk, P(two(t), 11.9 + i * .14, 12.1 + i * .14)); r.style.opacity = i === 3 ? 1 : lerp(1, .35, P(t, 13.4, 13.7)); });
    tf(radio, { x: lerp(-420, 0, P(t, 11.76, 12.15)), r: lerp(-30, -10, P(t, 11.76, 12.3)), o: 1 - P(t, 12.8, 13.0) });
    draw(cross, P(two(t), 13.55, 13.85));
    fix.style.clipPath = `inset(0 0 0 ${(100 - 100 * P(two(t), 13.85, 14.1, E.lin)).toFixed(1)}%)`;
    draw(ringP, P(two(t), 14.0, 14.25));
    words(t1a, t, [10.68], { out: 12.8, dx: -60, sm: 24 }); words(t1, t, [11.3], { out: 12.8 });
    words(t2, t, [13.08, 13.62], { out: 14.02, od: .2 });
    // pull back out of the one blue seat into thousands
    const rad = P(two(t), 14.3, 14.62, E.oCub) * 260;
    seatW.style.clipPath = t < 14.62 ? `circle(${rad.toFixed(0)}px at ${blueSeat[0].toFixed(0)}px ${blueSeat[1].toFixed(0)}px)` : 'none';
    tf(seatW, { s: lerp(3.4, 1.1, P(t, 14.3, 15.5, E.oCub)), o: t > 14.3 ? 1 : 0 });
    words(t3a, t, [14.28], { dx: -50, sm: 20 }); words(t3, t, [14.32, 14.78]);
    const kk = P(two(t), 15.24, 15.4, E.iCub);
    tf(stamp, { s: lerp(1.6, 1, kk), r: -7, o: t > 15.24 ? clamp(kk * 3) : 0 });
  };
});

// ================================================================ B4  في Four Steps  (15.72 to 19.1)
let b4root;
b4root = scene(15.72, 19.1, R => {
  R.style.background = C.blue;
  const ms = svg(R, -170, 1240, 175.8 * 4.4, 220 * 4.4, '0 0 175.8 220');
  const mk = MARK.map(d => sv(ms, 'path', { d, fill: C.paper }));
  const fi = txt(R, 'في', { x: 820, y: 250, w: 170, size: 120, serif: true, wt: 700, color: C.paper, align: 'right' });
  const lk = lockup(R, 150, 262, 1.0, C.paper); lk.m.forEach(p => p.style.display = 'none');
  lk.s.setAttribute('viewBox', '210 0 430.1 220'); lk.s.setAttribute('width', 430.1 * 1.4); lk.s.setAttribute('height', 220 * 1.4);
  const t1 = txt(R, 'هذا شغلنا', { x: 0, y: 700, w: 990, size: 170, color: C.paper, align: 'right' });
  const t2 = txt(R, 'كل يوم', { x: 0, y: 930, w: 990, size: 120, serif: true, wt: 700, color: C.paper, align: 'right' });
  // the correction stroke: a marker band that runs across the frame, then floods it (on twos)
  const wr = rng(404), N = 24, wa = [...Array(N + 1)].map(() => (wr() - .5) * 14), wb = [...Array(N + 1)].map(() => (wr() - .5) * 14);
  return t => {
    const tt = two(t), a = P(tt, 15.7, 15.86, E.oCub), b = P(tt, 15.84, 16.12, E.ioCub);
    if (t < 16.12) {
      const [dx, dy] = B3SEAT, x0 = lerp(dx - 10, -40, a), x1 = lerp(dx + 10, W + 40, a), cy = lerp(dy, H / 2, b), hh = lerp(11, H / 2 + 60, b);
      const top = [], bot = [];
      for (let i = 0; i <= N; i++) { const x = lerp(x0, x1, i / N); top.push(`${x.toFixed(0)}px ${(cy - hh + wa[i]).toFixed(0)}px`); bot.unshift(`${x.toFixed(0)}px ${(cy + hh + wb[i]).toFixed(0)}px`); }
      R.style.clipPath = `polygon(${top.concat(bot).join(',')})`;
    } else R.style.clipPath = 'none';
    mk.forEach((p, i) => { const k = P(t, 15.98 + i * .1, 16.4 + i * .1); p.style.transform = `translateX(${(-(1 - k) * 180).toFixed(1)}px)`; op(p, k > 0 ? 1 : 0); });
    tf(ms, { y: lerp(60, -50, P(t, 15.98, 18.6, E.ioSine)) });
    words(fi, t, [15.94]);
    lk.s.style.clipPath = `inset(0 ${(100 - 100 * P(t, 16.34, 16.8, E.oCub)).toFixed(1)}% 0 0)`;
    tf(lk.s, { x: lerp(24, -10, P(t, 16.34, 18.6, E.ioSine)) });
    words(t1, t, [16.96, 17.52], { col: C.paper }); words(t2, t, [18.02, 18.2], { col: C.paper, dx: -60, sm: 24 });
    // the whole field folds into the first poster of the corridor
    const ex = P(t, 18.55, 19.05, E.ioCub);
    tf(R, { p: 1400, x: lerp(0, -470, ex), y: lerp(0, 120, ex), ry: lerp(0, 62, ex), s: lerp(1, .36, ex) });
    R.style.transformOrigin = '50% 55%';
  };
});

// ================================================================ B5  proof  (18.7 to 30.1)
scene(18.7, 30.1, R => {
  // a) corridor of event posters
  const rig = el('div', 'a', R, { left: 0, top: 0, width: W + 'px', height: H + 'px', perspective: '1000px', perspectiveOrigin: '50% 58%' });
  const world = el('div', 'a', rig, { left: 0, top: 0, width: W + 'px', height: H + 'px', transformStyle: 'preserve-3d' });
  // five posters, big and close: the kind of event is the only thing printed on them
  const kinds = ['مؤتمر', 'معرض', 'ندوة', 'ملتقى', 'حفل'];
  const posters = kinds.map((k, i) => {
    const side = i % 2 ? 1 : -1, blue = i === 0;
    const p = box(world, 190, 640, 700, 920, { background: blue ? C.blue : C.card, transformOrigin: '50% 50%' }, 'card e2');
    el('div', 'a', p, { left: '0', top: '190px', width: '700px', textAlign: 'center', font: `900 210px TS`, color: blue ? C.paper : C.ink }, k);
    box(p, 70, 600, 560, 12, { background: blue ? C.paper : C.blue });
    p.side = side; p.zi = 250 - i * 560; return p;
  });
  const h1 = txt(R, 'أدرنا فعاليات', { x: 0, y: 190, w: W, size: 84, serif: true, wt: 700, cls: 'lift' });
  const h2 = txt(R, 'لأكبر الجهات', { x: 0, y: 300, w: W, size: 150, cls: 'lift' });
  const h3 = txt(R, 'في المملكة', { x: 0, y: 500, w: W, size: 60, wt: 500, color: C.ink2 });
  // c) ندوة الحج الكبرى sits under the first poster and is revealed when that poster turns away like a page
  const P2 = box(R, 100, 550, 880, 720, { background: C.card, transformOrigin: '50% 50%' }, 'card e2');
  // b) مؤتمر ومعرض الحج: the official logo, emblem revealed through a rising mask, then line by line
  const P1 = box(R, 90, 480, 900, 860, { background: C.card, transformOrigin: '0% 50%' }, 'card e2');
  const hs = svg(P1, 50, 145, 800, 569, '240 310 520 370');
  const defs = sv(hs, 'defs', {}); sv(defs, 'path', { id: 'hceP', d: EVLOGO.hce.d });
  const clipR = (id, x, y, w, h) => { const c = sv(defs, 'clipPath', { id }); return sv(c, 'rect', { x, y, width: w, height: h }); };
  const emR = clipR('hceEm', 540, 310, 220, 370);
  const emG = sv(hs, 'g', { 'clip-path': 'url(#hceEm)' }); sv(emG, 'use', { href: '#hceP', fill: EVLOGO.hce.fill });
  const emEdge = sv(hs, 'rect', { x: 540, y: 660, width: 220, height: 3.2, fill: C.blue });
  const bands = [[330, 90], [420, 85], [505, 170]].map(([y, h], i) => {
    clipR('hceW' + i, 240, y, 290, h); clipR('hceC' + i, 240, y, 290, h);
    const win = sv(hs, 'g', { 'clip-path': `url(#hceW${i})` }), mv = sv(win, 'g', {}), inner = sv(mv, 'g', { 'clip-path': `url(#hceC${i})` });
    sv(inner, 'use', { href: '#hceP', fill: EVLOGO.hce.fill }); return { mv, h };
  });
  const tape = cut(P1, 'tape', 350, -120, 210, { transform: 'rotate(8deg)' });
  // the rosette assembles around the Kaaba at large scale, then settles into the lockup
  const zw = el('div', 'a', P2, { left: '40px', top: '222px', width: '800px', height: '276px' });
  const gs = svg(zw, 0, 0, 800, 276, '215 395 580 200');
  const ghs = EVLOGO.ghs.map(p => { const e = sv(gs, p.t, p.t === 'polygon' ? { points: p.g, fill: p.c } : { d: p.g, fill: p.c });
    e.style.transformBox = 'fill-box'; e.style.transformOrigin = '50% 50%'; e.p0 = p.g.match(/-?\d*\.?\d+/g).map(Number); return e; });
  const RC = [699.25, 500];
  const kaaba = ghs.slice(0, 2), ros = ghs.slice(2, 18), arab = ghs.slice(18).filter(e => e.p0[1] < 500), lat = ghs.slice(18).filter(e => e.p0[1] >= 500);
  const zc = [(RC[0] - 215) / 580 * 800, (RC[1] - 395) / 200 * 276];
  zw.style.transformOrigin = `${zc[0]}px ${zc[1]}px`;
  // d) the pass and its protocol
  // d) the guest pass: the hero prop of this beat
  const badge = el('div', 'a', R, { left: '335px', top: '-90px', width: '410px', height: '1080px', transformOrigin: '50% 0' });
  cut(badge, 'badge', 0, 0, 410, null).className = 'cut hi';
  const bc = box(badge, 26, 548, 358, 470, {});
  box(bc, 0, 0, 358, 70, { background: C.blue });
  el('div', 'a', bc, { left: '0', top: '8px', width: '358px', textAlign: 'center', font: '500 36px TS', color: C.card }, 'دعوة خاصة');
  el('div', 'a', bc, { left: '0', top: '118px', width: '358px', textAlign: 'center', font: '900 120px TD' }, 'ضيف');
  el('div', 'a', bc, { left: '0', top: '320px', width: '358px', textAlign: 'center', font: '500 30px TS', color: C.ink2 }, 'رقم الدعوة ٠٤٧');
  // three protocol slips, one after another; each later becomes a row of the run of show
  const PW = 262, PH = 150, RW = 520, RH = 112;
  const protoSpec = [['المقعد', 'الصف الأول', 18, 640, -4], ['البوابة', 'بوابة ٣', 800, 780, 4], ['المراسم', 'فريق الاستقبال', 18, 940, 3]];
  const runSpec = [['٠٩:٠٠', 'الاستقبال'], ['٠٩:٢٠', 'كبار الضيوف'], ['٠٩:٣٠', 'الافتتاح']];
  const proto = protoSpec.map((p, i) => {
    const c = box(R, p[2], p[3], PW, PH, { background: C.card, transformOrigin: '50% 50%', overflow: 'hidden' }, 'card');
    const pa = box(c, 0, 0, RW, PH), pb = box(c, 0, 0, RW, RH);
    el('div', 'lbl a', pa, { right: `${RW - PW + 26}px`, top: '18px', fontSize: '30px' }, p[0]);
    el('div', 'a', pa, { right: `${RW - PW + 24}px`, top: '64px', font: '900 40px TS' }, p[1]);
    el('div', 'a', pb, { right: '22px', top: '26px', font: '900 50px TS', direction: 'ltr' }, runSpec[i][0]);
    el('div', 'a', pb, { right: '196px', top: '28px', font: '500 44px TS' }, runSpec[i][1]);
    const s = svg(pb, 20, 24, 64, 64); c.tk = stroke(s, 'M8,34 L26,52 L58,10', { stroke: C.blue, 'stroke-width': 9 });
    const edge = box(c, 0, 0, 12, 400, { background: C.blue });
    c.pa = pa; c.pb = pb; c.p = p; R.insertBefore(c, badge); return c;
  });
  const g1 = txt(R, 'لمناسبات رسمية', { x: 0, y: 1300, w: W, size: 130, cls: 'lift' });
  const g2 = txt(R, 'كل ضيف', { x: 0, y: 1260, w: W, size: 140, cls: 'lift' });
  const g3 = txt(R, 'له بروتوكول', { x: 0, y: 1460, w: W, size: 100, serif: true, wt: 700, cls: 'lift' });
  // e) every minute counts: the phrase leads, the stopwatch is proof
  const swW = 420, swX0 = 600, swY0 = 760, sw = cut(R, 'stopwatch', swX0, swY0, swW, null); sw.className = 'cut flat';
  const swC = [swX0 + swW * .504, swY0 + swW * (968 / 705) * .63];
  const hand = box(R, swC[0] - 4, swC[1] - swW * .3, 8, swW * .3, { background: C.blue, transformOrigin: '50% 100%', borderRadius: '4px' });
  const pin = box(R, swC[0] - 11, swC[1] - 11, 22, 22, { background: C.ink, borderRadius: '50%' });
  const m1 = txt(R, 'كل دقيقة', { x: 0, y: 170, w: W, size: 230, serif: true, wt: 900, cls: 'lift' });
  const m2 = txt(R, 'لها حساب', { x: 0, y: 480, w: W, size: 96, wt: 700, cls: 'lift' });
  const dot = box(R, 530, 1050, 20, 20, { background: C.blue, borderRadius: '50%' });
  return t => {
    // corridor
    const fwd = P(t, 18.7, 21.95, E.ioSine), cOut = P(t, 21.5, 21.9, E.iCub);
    posters.forEach((p, i) => {
      const z = p.zi + fwd * 2000;
      const past = E.iCub(clamp((z - 60) / 380));   // the nearest poster slides past the lens instead of fading
      tf(p, { x: p.side * (190 + past * 1100), y: 60, z, ry: -p.side * 10, r: p.side * (3 + past * 8), o: (1 - cOut) * clamp((z + 1500) / 400) * (past < 1 ? 1 : 0) });
    });
    op(world, t < 21.95 ? 1 : 0);
    words(h1, t, [18.76, 19.28], { out: 21.45 }); words(h2, t, [19.92, 20.52], { out: 21.45 }); words(h3, t, [20.94, 21.06], { out: 21.45, dx: -50, sm: 20 });
    // hero posters: the conference poster turns away like a page and the symposium is under it
    const a1 = P(t, 21.5, 21.98, E.oExpo), turn = P(t, 22.96, 23.42, E.ioCub), drop = P(t, 24.55, 24.95, E.iCub);
    tf(P1, { p: 1600, z: lerp(-3000, 0, a1), r: lerp(-6, -1.5, a1), ry: -104 * turn, x: -40 * turn, o: a1 > 0 && turn < .98 ? 1 : 0 });
    const eK = P(t, 21.62, 22.2, E.ioCub);
    emR.setAttribute('y', (668 - 346 * eK).toFixed(1)); emR.setAttribute('height', (346 * eK + 12).toFixed(1));
    emEdge.setAttribute('y', (666 - 346 * eK).toFixed(1)); emEdge.style.opacity = eK > 0 && eK < 1 ? 1 : 0;
    [21.86, 22.26, 22.66].forEach((t0, i) => { const k = P(t, t0 - .04, t0 + .4, E.oExpo); bands[i].mv.setAttribute('transform', `translate(0 ${((1 - k) * bands[i].h * 1.05).toFixed(2)})`); });
    tf(tape, { y: lerp(-200, 0, P(t, 21.9, 22.15, E.oBack)), r: 8 });
    tf(P2, { r: lerp(-1.5, 1.5, turn), y: drop * 1700, x: drop * 200, o: t > 22.9 ? 1 : 0 });
    tf(zw, { s: lerp(2.7, 1, P(t, 23.7, 24.15, E.ioCub)) });
    const kk = P(two(t), 23.1, 23.3, E.oBack);
    kaaba.forEach(e => { e.style.opacity = t > 23.1 ? 1 : 0; e.style.transform = `translateY(${(-(1 - kk) * 30).toFixed(1)}px)`; });
    ros.forEach((e, i) => { const k = P(two(t), 23.18 + (i % 8) * .045 + (i >= 10 ? .03 : 0), 23.5 + (i % 8) * .045, E.oCub), dx = e.p0[0] - RC[0], dy = e.p0[1] - RC[1];
      e.style.transform = `translate(${(dx * 1.4 * (1 - k)).toFixed(1)}px,${(dy * 1.4 * (1 - k)).toFixed(1)}px) rotate(${((1 - k) * 120).toFixed(1)}deg)`; e.style.opacity = k > 0 ? 1 : 0; });
    const arK = P(t, 23.78, 24.15, E.oCub), laK = P(t, 24.0, 24.4, E.oCub);
    arab.forEach(e => e.style.opacity = e.p0[0] > 600 - 390 * arK ? 1 : 0);   // Arabic reveals right to left
    lat.forEach(e => e.style.opacity = e.p0[0] < 215 + 390 * laK ? 1 : 0);    // English left to right
    // pass
    const bt = t - 24.68, sway = bt > 0 ? 11 * Math.exp(-2.2 * bt) * Math.cos(7 * bt) : 0, bOut = P(t, 27.6, 27.95, E.iCub);
    tf(badge, { y: lerp(-1150, 0, P(t, 24.68, 25.1, E.oCub)), r: sway * (1 - P(t, 25.9, 26.3)), x: -bOut * 1150, s: 1.2, o: t > 24.6 ? 1 : 0 });
    // slips slide out from behind the pass, one per beat; then they line up as the run of show
    const mo = P(t, 27.62, 28.1, E.ioCub);
    proto.forEach((c, i) => {
      const t0 = [26.0, 26.62, 27.24][i], k = P(t, t0, t0 + .36, E.oExpo), [, , px, py, pr] = c.p;
      const fromX = i === 1 ? -330 : 330;
      const rx = 40, ry = 800 + i * 136, mk = P(t, 27.62 + i * .08, 28.1 + i * .08, E.ioCub);
      Object.assign(c.style, { left: lerp(px, rx, mk).toFixed(1) + 'px', top: lerp(py, ry, mk).toFixed(1) + 'px',
        width: lerp(PW, RW, mk).toFixed(1) + 'px', height: lerp(PH, RH, mk).toFixed(1) + 'px' });
      tf(c, { x: fromX * (1 - k), r: lerp(pr, 0, mk), o: k > 0 ? 1 - P(t, 29.55, 29.8) : 0 });
      op(c.pa, 1 - P(t, 27.7 + i * .08, 27.85 + i * .08)); op(c.pb, P(t, 27.95 + i * .08, 28.1 + i * .08));
      draw(c.tk, P(two(t), 28.3 + i * .32, 28.5 + i * .32));
    });
    words(g1, t, [24.68, 25.4], { out: 25.68, od: .2 });
    words(g2, t, [25.94, 26.32], { out: 27.55 }); words(g3, t, [27.0, 27.34], { out: 27.55 });
    // minutes
    const sIn = P(t, 27.84, 28.25, E.oExpo), end = P(t, 29.55, 30.0, E.ioCub);
    const swx = lerp(560, 0, sIn);
    tf(sw, { x: swx, s: lerp(1, 0, end), o: sIn > 0 ? 1 : 0 }); sw.style.transformOrigin = `${swW * .504}px ${swW * (968 / 705) * .63}px`;
    const hr = (t - 27.84) * 200 + (t > 28.9 ? Math.floor((t - 28.9) * 15) * 6 : 0);
    tf(hand, { x: swx, r: hr, s: 1 - end, o: sIn > 0 ? 1 - end : 0 }); tf(pin, { x: swx, o: sIn > 0 ? 1 - end : 0 });
    hand.style.transformOrigin = `50% 100%`;
    words(m1, t, [27.84, 28.38], { out: 29.55 }); words(m2, t, [28.92, 29.32], { out: 29.6 });
    // the stopwatch collapses into the pen dot of the next scene
    tf(dot, { x: lerp(swC[0] - 540, 0, end), y: lerp(swC[1] - 1060, 0, end), o: t > 29.55 ? 1 : 0 });
  };
});

// ================================================================ B6  one path through the workflow  (29.9 to 38.9)
scene(29.9, 38.9, R => {
  const world = el('div', 'a', R, { left: 0, top: 0, width: W + 'px', height: '7400px', transformOrigin: '0 0' });
  // stations
  // the idea: one big word laid over a torn note; the pen dot waits under it
  const note = box(world, 180, 640, 720, 330, { background: C.card, clipPath: torn(720, 330, 3, 10, 'b'), transformOrigin: '50% 60%' }, 'card');
  const lb0 = txt(world, 'نبدأ معك من', { x: 0, y: 440, w: W, size: 104, serif: true, wt: 700 });
  const nt = txt(world, 'الفكرة', { x: 0, y: 580, w: W, size: 290, serif: true, wt: 900, cls: 'lift' });
  // planning: the path becomes the centre aisle of the plan
  const plan = box(world, 90, 1700, 900, 880, { background: C.card, transformOrigin: '50% 50%' }, 'card e2');
  const pl = planDrawing(plan, 900, 880, 51, { rows: 8, cols: 13 });
  const lb1 = txt(world, 'نخطط', { x: 0, y: 1390, w: 1020, size: 230, align: 'right', cls: 'lift' });
  // venue and tech: truss, screen, one baseline
  const stg = box(world, 0, 3250, W, 700);
  const sd = stageDrawing(box(stg, 60, 0, 960, 640), 960, 640);
  const lb2 = txt(world, 'نجهز المكان\nوالتقنية', { x: 0, y: 2780, w: 940, size: 120, align: 'right', lh: 1.12, cls: 'lift' });
  const frames = [0, 1, 2].map(i => {
    const f = box(sd.screen, 0, 0, 768, 320, { overflow: 'hidden', background: [C.card, C.ink, C.paper2][i] });
    if (i === 0) el('div', 'a', f, { left: 0, top: '30px', width: '768px', textAlign: 'center', font: '900 200px TD', color: C.ink }, 'أهلًا');
    if (i === 1) { const s = svg(f, 0, 0, 768, 320); for (let j = 0; j < 9; j++) sv(s, 'rect', { x: 60 + j * 74, y: 260 - j * 24, width: 50, height: 30 + j * 24, fill: C.card }); }
    if (i === 2) cut(f, 'mic', 300, 20, 170, { transform: 'rotate(-20deg)' });
    return f;
  });
  const lb3 = txt(world, 'ننتج المحتوى\nالمرئي', { x: 0, y: 3930, w: 940, size: 120, align: 'right', lh: 1.12, cls: 'lift' });
  // coverage: the viewfinder closes onto the frame it films and that frame is the live post
  const camE = cut(world, 'camera', -170, 4600, 540, { transform: 'scaleX(-1)' });
  const post = box(world, 620, 4430, 400, 700, { background: C.card, transformOrigin: '50% 50%', overflow: 'hidden' }, 'card e2');
  const pimg = box(post, 22, 86, 356, 380, { background: C.navy, overflow: 'hidden' });
  stageDrawing(box(pimg, 16, 56, 324, 290), 324, 290);
  box(post, 22, 22, 46, 46, { background: C.ink, borderRadius: '50%' });
  const live = el('div', 'a', post, { left: '22px', top: '100px', padding: '4px 18px', background: C.blue, color: C.card, font: '700 32px TS' }, 'مباشر');
  el('div', 'a', post, { right: '24px', top: '494px', font: '700 40px TS', color: C.ink }, 'الحدث الآن');
  el('div', 'a', post, { right: '24px', top: '556px', font: '500 30px TS', color: C.ink2 }, 'تغطية مباشرة من القاعة');
  const vf = svg(world, 0, 0, W, 7400); const vfr = sv(vf, 'path', { d: 'M0,0', fill: 'none', stroke: C.ink, 'stroke-width': 8, 'stroke-linecap': 'round' });
  const brackets = (x0, y0, x1, y1, c) => `M${x0},${y0 + c}V${y0}H${x0 + c}M${x1 - c},${y0}H${x1}V${y0 + c}M${x1},${y1 - c}V${y1}H${x1 - c}M${x0 + c},${y1}H${x0}V${y1 - c}`;
  const lb4 = txt(world, 'نغطي الحدث\nإعلاميًا', { x: 0, y: 5150, w: 580, size: 110, align: 'right', lh: 1.12, cls: 'lift' });
  // the exit: a lit doorway in a paper wall, a door leaf swung open, a printed exit card
  const wall = box(world, 60, 5600, 960, 520, { background: C.paper2 }, 'card');
  box(world, 20, 6116, 1040, 8, { background: C.ink });
  const doorway = box(world, 410, 5700, 260, 420, { background: C.light, boxShadow: `inset 0 0 0 7px ${C.ink}, inset 14px 10px 0 7px rgba(17,17,15,.08)` });
  const spill = box(world, 300, 6120, 480, 170, { background: C.light, clipPath: 'polygon(110px 0,370px 0,480px 170px,0 170px)', opacity: .95 });
  const leaf = box(world, 670, 5660, 110, 500, { background: C.card, boxShadow: `inset 5px 0 0 ${C.ink}, inset -3px 0 0 ${C.ink2}` });
  const sign = box(world, 800, 5680, 200, 104, { background: C.card, transformOrigin: '50% 0' }, 'card');
  el('div', 'a', sign, { right: '26px', top: '8px', font: '900 58px TS', color: C.ink }, 'مخرج');
  { const s = svg(sign, 22, 30, 60, 44); sv(s, 'path', { d: 'M56,22H8M26,4L8,22L26,40', fill: 'none', stroke: C.blue, 'stroke-width': 8, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }); }
  const lb5a = txt(world, 'لين يطلع', { x: 0, y: 6300, w: W, size: 64, wt: 500, color: C.ink2 });
  const lb5b = txt(world, 'آخر ضيف', { x: 0, y: 6370, w: W, size: 250, serif: true, wt: 900, cls: 'lift' });
  const guest = box(world, 0, 0, 34, 34, { background: C.ink, borderRadius: '50%' });
  [[plan, 350, -50, 6], [post, 150, -40, -8]].forEach(([p, x, y, r]) => box(p, x, y, 200, 70, { background: '#2a2826', opacity: .92, transform: `rotate(${r}deg)`, clipPath: torn(200, 70, x + y, 5, 'tb') }));
  // the path: every segment starts at one object and lands on the next
  const PS = svg(world, 0, 0, W, 7400);
  const pts = [[540, 1060], [540, 1400], [540, 1700], [540, 2200], [540, 2590], [540, 2640], [562, 2662], [978, 2662], [1000, 2684], [1000, 3300], [1000, 3780], [1000, 4298], [978, 4320], [842, 4320], [820, 4342], [820, 4430], [820, 4800], [820, 5130], [820, 5458], [798, 5480], [562, 5480], [540, 5502], [540, 5760], [540, 6100]];
  const pd = pts.map((p, i) => (i ? 'L' : 'M') + p[0] + ',' + p[1]).join('');
  const path = sv(PS, 'path', { d: pd, fill: 'none', stroke: C.blue, 'stroke-width': 12, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
  const plen = path.getTotalLength();
  path.setAttribute('stroke-dasharray', `${plen} ${plen}`);
  const pen = box(world, 0, 0, 30, 30, { background: C.blue, borderRadius: '50%' });
  // head position keyframes (fraction of path) keyed to the VO
  const lenAt = y => { let lo = 0, hi = plen; for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; path.getPointAtLength(m).y < y ? lo = m : hi = m; } return lo / plen; };
  const K = [[30.0, 0], [30.9, lenAt(1500)], [31.26, lenAt(1700)], [32.0, lenAt(2640)], [32.9, lenAt(3300)], [33.8, lenAt(3780)], [34.94, lenAt(4430)], [36.08, lenAt(5130)], [36.7, lenAt(5500)], [37.3, lenAt(5760)]];
  const headS = t => { if (t <= K[0][0]) return 0; for (let i = 0; i < K.length - 1; i++) if (t < K[i + 1][0]) return lerp(K[i][1], K[i + 1][1], E.ioSine((t - K[i][0]) / (K[i + 1][0] - K[i][0]))); return K[K.length - 1][1]; };
  const endS = lenAt(5760);
  const CAM = [[0, 0], [31.26, 1190], [32.04, 2570], [33.8, 2770], [34.94, 4250], [36.7, 5380]];
  return t => {
    const s = headS(t), hp = path.getPointAtLength(s * plen);
    path.style.strokeDashoffset = (plen * (1 - s)).toFixed(1);
    tf(pen, { x: hp.x - 15, y: hp.y - 15, o: t < 37.3 ? 1 : 0 });
    const exitY = P(t, 38.2, 38.5, E.iCub) * 1900;
    let camY = CAM[0][1]; for (let i = 1; i < CAM.length; i++) camY = lerp(camY, CAM[i][1], P(t, CAM[i][0] - .3, CAM[i][0] + .12, E.ioCub));
    tf(world, { x: 0, y: -(camY + exitY) });
    // stations (each label leaves before the camera would crop it at the top)
    const nk = P(two(t), 30.3, 30.54, E.oBack); tf(note, { s: lerp(.4, 1, nk), r: lerp(-10, -2, nk), o: t > 30.3 ? 1 : 0 });
    words(lb0, t, [30.0, 30.42, 30.66], { out: 31.0, dx: -50, sm: 20 });
    const ik = P(t, 30.74, 31.1, E.oExpo); tf(nt, { s: lerp(1.25, 1, ik), o: t > 30.72 ? clamp(ik * 2) : 0 }); nt.style.transformOrigin = '50% 60%';
    const pk = P(t, 30.95, 31.35, E.oExpo); tf(plan, { s: lerp(.85, 1, pk), r: lerp(3, .6, pk), o: pk > 0 ? 1 : 0 });
    words(lb1, t, [31.26], { out: 31.95 });
    const tr = P(t, 32.04, 32.4, E.oBack); tf(sd.truss, { y: lerp(-700, 0, tr), o: t > 32.02 ? 1 : 0 });
    tf(sd.screen, { sy: P(t, 32.3, 32.6, E.oExpo), o: t > 32.3 ? 1 : 0 }); sd.screen.style.transformOrigin = '50% 100%';
    [sd.l1, sd.l2].forEach((l, i) => op(l, P(t, 32.5 + i * .12, 32.62 + i * .12)));
    words(lb2, t, [32.04, 32.66, 33.08], { out: 33.45 });
    frames.forEach((f, i) => { const k = P(t, 33.8 + i * .32, 34.05 + i * .32, E.oExpo); tf(f, { x: lerp(-800, 0, k), o: k > 0 ? 1 : 0 }); });
    words(lb3, t, [33.8, 34.0, 34.2], { out: 34.66 });
    // viewfinder brackets frame the whole screen, then close in until they are the edges of the post
    const vk = P(two(t), 34.8, 35.0, E.oCub), vc = P(t, 35.0, 35.4, E.ioCub);
    const vx0 = lerp(560, 620, vc), vy0 = lerp(4340, 4430, vc), vx1 = lerp(1070, 1020, vc), vy1 = lerp(5220, 5130, vc);
    vfr.setAttribute('d', brackets(vx0, vy0, vx1, vy1, lerp(90, 40, vc) * vk)); op(vf, vk > 0 ? 1 - P(t, 35.5, 35.7) : 0);
    post.style.clipPath = `inset(${(50 - 50 * vc).toFixed(1)}% ${(50 - 50 * vc).toFixed(1)}% ${(50 - 50 * vc).toFixed(1)}% ${(50 - 50 * vc).toFixed(1)}%)`;
    op(post, vc > 0 ? 1 : 0);
    tf(camE, { x: lerp(-360, 0, P(t, 34.5, 34.95, E.oExpo)) });
    tf(live, { o: t > 35.5 ? (Math.floor((t - 35.5) * 3) % 2 ? .75 : 1) : 0 });
    words(lb4, t, [34.94, 35.72, 36.08], { out: 36.45 });
    const sk = P(two(t), 36.66, 36.86, E.oBack); tf(sign, { r: lerp(-14, -3, sk), o: t > 36.66 ? 1 : 0 });
    words(lb5a, t, [36.7, 37.2], { dx: -50, sm: 20 }); words(lb5b, t, [37.64, 38.02]);
    // the last guest walks the end of the path into the light; the door swings shut behind them
    const gk = P(t, 37.3, 38.0, E.ioSine), gp = path.getPointAtLength(lerp(endS, 1, gk) * plen);
    tf(guest, { x: gp.x - 17, y: gp.y - 17 - Math.abs(Math.sin(t * 18)) * 6, s: lerp(1, .6, gk), o: t > 37.28 && gk < .96 ? 1 : 0 });
    const shut = P(t, 38.02, 38.22, E.iCub);
    Object.assign(leaf.style, { left: lerp(670, 410, shut).toFixed(1) + 'px', width: lerp(110, 260, shut).toFixed(1) + 'px', top: lerp(5660, 5700, shut).toFixed(1) + 'px', height: lerp(500, 420, shut).toFixed(1) + 'px',
      clipPath: `polygon(0 ${lerp(8, 0, shut).toFixed(2)}%,100% 0,100% 100%,0 ${lerp(92, 100, shut).toFixed(2)}%)` });
    op(spill, 1 - shut);
  };
});

// ================================================================ B7  lights out, the event keeps working  (38.2 to 44.8)
scene(38.2, 44.8, R => {
  const navy = box(R, 0, 0, W, H, { background: C.navy, opacity: 0 });
  const lev = cut(R, 'lever', 320, 520, 440, null); lev.className = 'cut hi';
  lev.style.transformOrigin = '50% 50%';
  const l1 = txt(R, 'وبعد ما', { x: 0, y: 220, w: W, size: 110, serif: true, wt: 700, cls: 'lift' });
  const l2 = txt(R, 'تنطفي الأضواء', { x: 0, y: 1500, w: W, size: 150, serif: true, wt: 900, color: C.paper });
  // pieces of the event that remain: five kinds, one shape each, no blue in the dark
  function tile(kind, w, h) {
    const c = box(R, 0, 0, w, h, { background: C.card, transformOrigin: '50% 50%', overflow: 'hidden' }, 'card');
    if (kind === 0) { // video frame, landscape, play mark
      c.style.background = C.ink; const f = box(c, 0, 0, w, h, { background: C.navy }); stageDrawing(box(f, w * .12, h * .06, w * .76, h * .8), w * .76, h * .8);
      const s = svg(c, w / 2 - 34, h / 2 - 38, 68, 76); sv(s, 'path', { d: 'M4,4 L64,38 L4,72Z', fill: C.card });
      box(c, 0, h - 10, w, 10, { background: C.ink2 }); box(c, 0, h - 10, w * .38, 10, { background: C.card }); }
    if (kind === 1) { // photo, square with a print border
      const f = box(c, 16, 16, w - 32, w - 32, { background: C.paper2, overflow: 'hidden' }); cut(f, 'mic', (w - 32) * .22, 10, (w - 32) * .5, { transform: 'rotate(-25deg)' }); }
    if (kind === 2) { // quote, a strip of paper with a big serif quote mark
      c.style.background = C.paper; el('div', 'a', c, { right: '22px', top: `${-h * .16}px`, font: `900 ${Math.round(h * .8)}px TD`, color: C.ink }, '«');
      for (let j = 0; j < 2; j++) box(c, 30, h * .55 + j * 26, w - 60 - j * 80, 12, { background: C.ink2, opacity: .6 }); }
    if (kind === 3) { // recap sheet, portrait, title and bars
      el('div', 'a', c, { right: '22px', top: '16px', font: `900 ${Math.round(w * .12)}px TS` }, 'ملخص الحدث');
      for (let j = 0; j < 4; j++) box(c, 22, h * .34 + j * h * .14, (w - 44) * [1, .8, .9, .55][j], h * .06, { background: C.ink, opacity: j ? .25 : .8 }); }
    if (kind === 4) { // social post, portrait with an avatar and a photo
      box(c, 16, 16, 34, 34, { background: C.ink, borderRadius: '50%' }); box(c, 60, 26, w * .4, 12, { background: C.ink2, opacity: .6 });
      const f = box(c, 16, 64, w - 32, h * .58, { background: C.paper2, overflow: 'hidden' }); cut(f, 'camera', -10, 10, w - 20, { transform: 'scaleX(-1)' }); }
    return c;
  }
  // one clearly first (the video), then the others
  const heroSpec = [[0, 600, 340, 240, 700, -3], [2, 380, 200, 610, 1090, -5], [1, 290, 350, 80, 1080, 5], [3, 300, 400, 640, 1320, 4], [4, 300, 440, 150, 1400, -4]];
  const heroes = heroSpec.map(([k, w, h, x, y, r]) => { const c = tile(k, w, h); c.hx = x; c.hy = y; c.hr = r; c.style.left = x + 'px'; c.style.top = y + 'px'; return c; });
  const bubbles = [[180, 560], [820, 880], [560, 1480]].map(([x, y], i) => {
    const b = svg(R, x - 90, y - 60, 180, 130); sv(b, 'path', { d: 'M20,10 H160 Q170,10 170,20 V80 Q170,90 160,90 H70 L40,122 L46,90 H20 Q10,90 10,80 V20 Q10,10 20,10Z', fill: C.paper });
    [0, 1, 2].forEach(j => sv(b, 'circle', { cx: 60 + j * 30, cy: 50, r: 8, fill: C.ink })); b.style.transformOrigin = '30% 100%'; return b;
  });
  const talk = txt(R, 'الناس تتكلم عنه', { x: 0, y: 250, w: W, size: 130, color: C.paper });
  // many
  // more of them, fewer on screen: depth (scale and dimming) implies the rest
  const many = []; const rr = rng(99);
  const TS_ = [[300, 170], [220, 220], [240, 130], [200, 260], [200, 290]];
  for (let ring = 1; ring <= 3; ring++) { const n = 3 + ring * 3; for (let j = 0; j < n; j++) {
    const a = j / n * Math.PI * 2 + ring * .6 + rr() * .25, rad = 330 + ring * 230, k = Math.floor(rr() * 5);
    const [tw, th] = TS_[k]; const c = tile(k, tw, th); R.insertBefore(c, heroes[0]);
    c.tx = 540 + Math.cos(a) * rad * .92 - tw / 2; c.ty = 1000 + Math.sin(a) * rad * 1.3 - th / 2; c.t0 = 42.4 + ring * .3 + rr() * .2; c.rr = (rr() - .5) * 14; c.sc = 1 - ring * .17; c.dim = ring * .16;
    c.hw = tw; c.hh = th; many.push(c); } }
  const m1 = txt(R, 'ومحتوى تستفيد منه', { x: 0, y: 220, w: W, size: 92, serif: true, wt: 700, color: C.paper });
  const shade = box(R, 0, 0, W, H, { background: C.navy, opacity: 0 });
  const months = txt(R, 'شهور', { x: 0, y: 690, w: W, size: 400, serif: true, wt: 900, color: C.paper });
  return t => {
    const inL = P(t, 38.5, 38.92, E.oExpo);
    const flip = P(two(t), 39.0, 39.2, E.lin);
    tf(lev, { y: lerp(1500, 0, inL), sy: lerp(1, -1, flip), o: 1 - P(t, 39.8, 40.15) });
    // lights off with a short flicker, on twos
    const f = two(t); const dk = f < 39.2 ? 0 : (f < 39.27 ? 1 : f < 39.34 ? 0 : 1);
    op(navy, dk);
    words(l1, t, [38.4, 38.96], { out: 39.2, od: .12 });
    words(l2, t, [39.06, 39.4], { out: 39.85, col: C.paper });
    const gather = P(t, 42.3, 42.75, E.ioCub), fold = P(t, 44.35, 44.7, E.iCub);
    const clear = P(t, 43.85, 44.12, E.ioCub);           // everything moves off the centre before «شهور»
    const push = (x, y, k) => { const dx = x - 540, dy = y - 1000, d = Math.hypot(dx, dy) || 1; return [dx / d * 520 * k, dy / d * 700 * k]; };
    heroes.forEach((c, i) => {
      const t0 = i ? 40.55 + (i - 1) * .3 : 39.9, k = P(two(t), t0, t0 + .22, E.oBack);
      const hx = c.hx + c.offsetWidth / 2, hy = c.hy + c.offsetHeight / 2, gx = lerp(0, 540 - hx, gather * .45), gy = lerp(0, 1000 - hy, gather * .45), [px, py] = push(hx + gx, hy + gy, clear);
      tf(c, { s: lerp(.4, 1, k) * lerp(1, .6, gather), r: c.hr * k, x: gx + px, y: gy + py, o: k > 0 ? 1 - fold : 0 });
    });
    bubbles.forEach((b, i) => { const k = P(two(t), 41.26 + i * .2, 41.46 + i * .2, E.oBack); tf(b, { s: k * (1 - gather), o: k > 0 ? 1 : 0 }); });
    words(talk, t, [41.06, 41.26, 41.56, 41.96], { out: 42.1, od: .2, col: C.paper });
    many.forEach(c => {
      const k = P(t, c.t0, c.t0 + .45, E.oExpo), cx = c.tx + c.hw / 2, cy = c.ty + c.hh / 2, [px, py] = push(cx, cy, clear * .6);
      c.style.left = lerp(540 - c.hw / 2, c.tx, k).toFixed(1) + 'px'; c.style.top = lerp(1000 - c.hh / 2, c.ty, k).toFixed(1) + 'px';
      tf(c, { x: px + (540 - cx) * fold, y: py + (1000 - cy) * fold, s: c.sc * lerp(.3, 1, k) * lerp(1, 0, fold), r: c.rr * k, o: k > 0 ? 1 : 0 });
      c.style.filter = `brightness(${(1 - c.dim).toFixed(2)})`;
    });
    words(m1, t, [42.36, 43.12, 43.78], { out: 44.0, col: C.paper });
    op(shade, P(t, 43.9, 44.15) * .72 * (1 - fold));
    tf(months, { s: lerp(1.3, 1, P(t, 44.08, 44.32, E.oExpo)), o: t > 44.08 ? 1 - fold : 0 });
  };
});

// ================================================================ B8  CTA  (44.4 to 48.2)
scene(44.4, 48.2, R => {
  R.style.background = C.paper;
  const q = txt(R, 'عندك فعالية جاية؟', { x: 0, y: 800, w: W, size: 150, serif: true, wt: 700, cls: 'lift' });
  const l1 = txt(R, 'خلّها تنذكر', { x: 0, y: 760, w: W, size: 110, serif: true, wt: 700, cls: 'mask lift' });
  const l2 = txt(R, 'باسمك', { x: 0, y: 880, w: W, size: 330, serif: true, wt: 900, cls: 'mask lift' });
  const us = svg(R, 0, 0, W, H);
  const ul = stroke(us, wob([[200, 1262], [540, 1250], [880, 1258]], 17, 5, 60), { stroke: C.blue, 'stroke-width': 22 });
  return t => {
    const rv = P(t, 44.4, 44.72, E.ioCub) * 1250;
    R.style.clipPath = t < 44.73 ? `circle(${rv.toFixed(0)}px at 540px 1000px)` : 'none';
    const out = P(t, 47.45, 47.85, E.iCub);
    // the whole question builds at once, centred, then steps up to make room
    words(q, t, [44.6, 44.72, 44.84], { out: 47.3, dx: -60, sm: 26 });
    tf(q, { y: -lerp(0, 330, P(t, 45.62, 45.98, E.ioCub)) });
    rise(l1.lines[0], t, 45.86, .5); rise(l2.lines[0], t, 46.9, .55);
    tf(l1, { y: -out * 200, o: 1 - out }); tf(l2, { y: -out * 200, o: 1 - out });
    draw(ul, P(two(t), 47.02, 47.4, E.oCub));
    op(us, t < 47.55 ? 1 : 0);
  };
});

// ================================================================ B9  Four Steps  (47.5 to end)
scene(47.5, 999, R => {
  R.style.background = C.paper;
  const LS = 1.3, LX = (W - 640.1 * LS) / 2, LY = 290;
  const lk = lockup(R, LX, LY, LS, C.blue);
  // underline pieces (screen coords) to their mark positions
  const markBox = [[108.3, 0, 67.5, 40.7], [40.8, 59.8, 135.1, 40.7], [0, 119.5, 175.8, 40.7], [135.1, 179.2, 40.8, 40.8]];
  const slotA = txt(R, 'نمشي معك', { x: 0, y: 740, w: W, size: 110, serif: true, wt: 700, cls: 'lift' });
  const slotB = txt(R, 'خطوة بخطوة', { x: 0, y: 890, w: W, size: 176, serif: true, wt: 900, cls: 'lift' });
  const slotC = txt(R, 'لين يصير الحدث', { x: 0, y: 820, w: W, size: 130, serif: true, wt: 700, cls: 'lift' });
  // four steps built from the mark's own geometry: flat right end, round left end, climbing right to left
  const steps = [0, 1, 2, 3].map(i => box(R, 700 - i * 150, 1520 - i * 70, 190, 44, { background: C.blue, borderRadius: '22px 0 0 22px', transformOrigin: '100% 50%' }));
  // two props come back as callbacks: the lamp (it lights the last words) and the camera
  const spot = el('div', 'a', R, { left: '-150px', top: '1300px', width: '460px', height: '440px', transformOrigin: '40% 40%' }); cut(spot, 'spotlight', 0, 0, 460);
  const camP = cut(R, 'camera', 740, 1520, 400);   // lens faces into the frame, toward the three words
  const cone = box(R, 0, 0, W, H, { background: C.light });
  const w1 = txt(R, 'تشوفه', { x: 0, y: 660, w: W, size: 240, serif: true, wt: 900 });
  const w1c = txt(cone, 'تشوفه', { x: 0, y: 660, w: W, size: 240, serif: true, wt: 900 });
  // تعيشه: a torn label slapped across the frame
  const lab = box(R, 220, 1000, 640, 210, { background: C.ink, clipPath: torn(640, 210, 88, 9, 'tb'), transformOrigin: '50% 50%' });
  txt(lab, 'تعيشه', { x: 0, y: 8, w: 640, size: 150, color: C.card });
  const w3 = txt(R, 'وتتذكره', { x: 0, y: 1250, w: W, size: 200, serif: true, wt: 900, color: C.blue });
  return t => {
    // underline breaks into four steps and becomes the mark
    lk.m.forEach((p, i) => {
      const k = P(t, 47.52 + i * .07, 48.05 + i * .07, E.ioCub), [bx, by, bw, bh] = markBox[i];
      const tx = LX + (bx + bw / 2) * LS, ty = LY + (by + bh / 2) * LS, sx = 200 + (i + .5) * 170, sy = 1255;
      p.style.transform = `translate(${((sx - tx) / LS * (1 - k)).toFixed(2)}px,${((sy - ty) / LS * (1 - k)).toFixed(2)}px) scale(${lerp(170 / (bw * LS), 1, k).toFixed(3)},${lerp(22 / (bh * LS), 1, k).toFixed(3)})`;
      p.setAttribute('fill', k < .5 ? C.blue : C.blue);
    });
    lk.wg.style.clipPath = `inset(0 ${(100 - 100 * P(t, 47.9, 48.35, E.oCub)).toFixed(1)}% 0 0)`;
    // after the reveal the lockup steps back to a small anchor at the top; at the very end it returns, alone, to the centre
    const small = P(t, 48.5, 48.95, E.ioCub), fin = P(t, 53.8, 54.16, E.ioCub);
    lk.s.style.transformOrigin = '50% 0';
    tf(lk.s, { y: lerp(lerp(0, -130, small), 960 - 143 * .9 - LY, fin), s: lerp(lerp(1, .62, small), .9, fin) });
    words(slotA, t, [48.28, 48.96], { out: 50.05, od: .18, dx: -60, sm: 24 }); words(slotB, t, [49.26, 49.68], { out: 50.05, od: .18, dx: 90 });
    // one step per beat of «خطوة بخطوة»
    steps.forEach((s, i) => { const t0 = [49.26, 49.46, 49.68, 49.88][i], k = P(two(t), t0, t0 + .16, E.oExpo);
      tf(s, { sx: k, o: k > 0 ? 1 - P(t, 50.02, 50.2) : 0 }); });
    words(slotC, t, [50.22, 50.5, 50.76], { out: 51.4, od: .2 });
    // props: two callbacks only
    const pr = i => P(t, 50.22 + i * .14, 50.7 + i * .14, E.oExpo), gone = P(t, 53.55, 53.8, E.iCub);
    tf(spot, { x: lerp(-400, 0, pr(0)) - gone * 500, r: lerp(40, 22, pr(0)) });
    tf(camP, { x: lerp(500, 0, pr(1)) + gone * 500 });
    // تشوفه: revealed by the lamp's light (the VO's «شيء الناس» stays in the ear)
    const lx = 170, ly = 1420, sweep = P(t, 51.9, 52.35, E.oCub), hw = lerp(.02, .26, sweep), a = lerp(-1.05, -.82, sweep), f = 1700;
    cone.style.clipPath = `polygon(${lx}px ${ly}px,${(lx + Math.cos(a - hw) * f).toFixed(0)}px ${(ly + Math.sin(a - hw) * f).toFixed(0)}px,${(lx + Math.cos(a + hw) * f).toFixed(0)}px ${(ly + Math.sin(a + hw) * f).toFixed(0)}px)`;
    op(cone, t > 51.88 ? 1 - P(t, 52.45, 52.8) : 0);
    // the three words clear upward through the top, leaving the lockup alone
    const cl = i => P(t, 53.62 + i * .04, 53.84 + i * .04, E.iCub);
    tf(w1, { y: cl(0) * 70, o: P(t, 52.4, 52.7) * (1 - cl(0)) });
    // تعيشه: the label is slapped down, on twos
    const k2 = P(two(t), 52.52, 52.66, E.iCub);
    tf(lab, { s: lerp(1.35, 1, k2), r: -3, y: cl(1) * 70, o: t > 52.52 ? clamp(k2 * 3) * (1 - cl(1)) : 0 });
    // وتتذكره: stamped in blue
    const k3 = P(two(t), 53.3, 53.44, E.iCub);
    tf(w3, { s: lerp(1.6, 1, k3), r: -2, y: cl(2) * 70, o: t > 53.3 ? clamp(k3 * 3) * (1 - cl(2)) : 0 });
  };
});

// ---------------------------------------------------------------- texture
function buildFx() {
  const tone = el('div', '', fxRoot); tone.id = 'tone';
  // printed paper: fine even tooth and a few fibres, no stains, no ageing
  const fib = el('canvas', 'a', fxRoot, { left: 0, top: 0, mixBlendMode: 'multiply', opacity: .5 }); fib.width = W; fib.height = H;
  { const g = fib.getContext('2d'), r = rng(7); g.fillStyle = '#fff'; g.fillRect(0, 0, W, H);
    const id = g.getImageData(0, 0, W, H), d = id.data; for (let i = 0; i < d.length; i += 4) { const n = 255 - r() * 11; d[i] = n; d[i + 1] = n; d[i + 2] = n - 1; } g.putImageData(id, 0, 0);
    g.lineWidth = 1; for (let i = 0; i < 500; i++) { const x = r() * W, y = r() * H, a = r() * 6.28, l = 6 + r() * 24; g.strokeStyle = `rgba(120,108,90,${.05 + r() * .08})`;
      g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a) * l * .5 + (r() - .5) * 6, y + Math.sin(a) * l * .5 + (r() - .5) * 6, x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke(); } }
  el('div', '', fxRoot).id = 'vig';
  const grains = [0, 1, 2, 3].map(i => { const c = el('canvas', 'grain', fxRoot); c.width = 540; c.height = 960; const g = c.getContext('2d'), r = rng(100 + i), id = g.createImageData(540, 960);
    for (let j = 0; j < id.data.length; j += 4) { const v = r() * 255; id.data[j] = id.data[j + 1] = id.data[j + 2] = v; id.data[j + 3] = 255; } g.putImageData(id, 0, 0); return c; });
  return t => { const k = Math.floor(t * 15 + 1e-6) % 4; grains.forEach((c, i) => c.style.display = i === k ? 'block' : 'none'); };
}

// ---------------------------------------------------------------- clock
let fxF = null;
function renderAt(t) {
  for (const s of scenes) { const on = t >= s.a && t < s.b; s.root.style.display = on ? 'block' : 'none'; if (on) s.f(t); }
  fxF(t);
}
// the composition stops at the end of the VO; a ?tail hold repeats that exact frame (grain included)
window.seek = t => { renderAt(Math.max(0, Math.min(VO_DUR - 1e-4, t))); return true; };
window.DURATION = DUR;

function fit() {
  const s = RENDER ? 1 : Math.min(innerWidth / W, innerHeight / H);
  document.getElementById('wrap').style.transform = `translate(${-W / 2 * s}px,${-H / 2 * s}px) scale(${s})`;
}
window.__ready = (async () => {
  fxF = buildFx();
  await Promise.all(['300', '400', '500', '700', '900'].flatMap(w => [document.fonts.load(`${w} 40px TS`, 'ابجد Four'), document.fonts.load(`${w} 40px TD`, 'ابجد')]));
  await document.fonts.ready;
  await Promise.all([...document.images].map(i => i.decode().catch(() => {})));
  fit(); addEventListener('resize', fit);
  window.seek(+(Q.get('t') || 0));
  if (!RENDER && !Q.has('t')) {
    const vo = document.getElementById('vo'), hud = document.getElementById('hud'); let t0 = performance.now(), playing = false;
    hud.textContent = 'click to play with sound';
    addEventListener('click', () => { vo.currentTime = 0; vo.play(); playing = true; });
    const loop = () => { const t = playing ? vo.currentTime : ((performance.now() - t0) / 1000) % DUR; window.seek(t); hud.textContent = t.toFixed(2) + 's'; requestAnimationFrame(loop); };
    requestAnimationFrame(loop);
  }
  return true;
})();
