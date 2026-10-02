/* vector_rig — articulated flat-vector characters with ONE continuous outline (no stitched parts).
 *
 * Why: characters assembled from separate shapes (a head image + a body image + arm rectangles) show seams, floating hands
 * and missing necks. Here every body part hangs on a skeleton (neck, shoulders, elbows, wrists, hips, knees), limbs are
 * tapered capsules that overlap at the joints, and each depth layer (back limbs / body+head / front limbs) is filled
 * WITHOUT strokes and then outlined ONCE by an SVG filter around its silhouette. Overlaps merge into one drawing; a front
 * arm crossing the body still gets its own contour, like a hand-drawn cartoon.
 *
 * Usage (plain browser JS; works inside HyperFrames compositions and GSAP timelines — everything is a pure function of the pose):
 *   const lz = VRig.make(svgElement, VRig.presets.chestnut({ shirt: '#E9B43A' }));
 *   lz.pose({ x: 960, y: 900, scale: 1, armR: [150, 40], hand R: 'wave', expr: 'happy' });
 *   gsap.to(state, { t: 1, onUpdate: () => lz.pose({ ...base, armR: [140 + 30 * Math.sin(state.t * 12), 40] }) });
 *
 * Pose fields (angles in degrees, 0 = pointing straight down, + = towards the character's front/outside):
 *   x, y (ground point between the feet), scale, facing (1 right / -1 left), turn (0 front … 1 three-quarter), lean, squash,
 *   head: tilt, headY (bob), armL/armR: [shoulder, elbow] (+ = away from the body, 90 = straight out, 170 = up), legL/legR: [hip, knee] (+ = apart), handL/handR: open|fist|wave|point|hold,
 *   expr: name in EXPR (or an object), blush 0..1, sweat 0..1, prop: { hand: 'R', draw(g, hand) }  (drawn in hand space)
 */
(function (root) {
  const NS = 'http://www.w3.org/2000/svg';
  const el = (tag, attrs = {}, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const rad = (d) => (d * Math.PI) / 180;
  const f = (n) => (Math.round(n * 10) / 10).toString();

  // A tapered capsule: the convex hull of two circles (r1 at a, r2 at b) — one smooth limb segment.
  function capsule(ax, ay, r1, bx, by, r2) {
    const dx = bx - ax, dy = by - ay, d = Math.hypot(dx, dy) || 0.001, a = Math.atan2(dy, dx);
    const s = Math.max(-1, Math.min(1, (r1 - r2) / d)), t = Math.acos(s);
    const p = (cx, cy, r, ang) => [cx + r * Math.cos(ang), cy + r * Math.sin(ang)];
    const [x1, y1] = p(ax, ay, r1, a + t), [x2, y2] = p(bx, by, r2, a + t), [x3, y3] = p(bx, by, r2, a - t), [x4, y4] = p(ax, ay, r1, a - t);
    return `M${f(x1)},${f(y1)} L${f(x2)},${f(y2)} A${f(r2)},${f(r2)} 0 0 0 ${f(x3)},${f(y3)} L${f(x4)},${f(y4)} A${f(r1)},${f(r1)} 0 1 0 ${f(x1)},${f(y1)} Z`;
  }
  const circle = (x, y, r) => `M${f(x - r)},${f(y)} a${f(r)},${f(r)} 0 1,0 ${f(2 * r)},0 a${f(r)},${f(r)} 0 1,0 ${f(-2 * r)},0 Z`;
  const ellipse = (x, y, rx, ry) => `M${f(x - rx)},${f(y)} a${f(rx)},${f(ry)} 0 1,0 ${f(2 * rx)},0 a${f(rx)},${f(ry)} 0 1,0 ${f(-2 * rx)},0 Z`;

  // one outline filter per line weight/colour, shared by all rigs on the page
  function outlineFilter(svg, w, ink) {
    const id = `vrig-ol-${String(w).replace('.', 'p')}-${ink.replace('#', '')}`;   // ids can't contain '.'
    if (svg.querySelector('#' + id)) return id;
    let defs = svg.querySelector('defs') || el('defs', {}, svg);
    const fl = el('filter', { id, x: '-30%', y: '-30%', width: '160%', height: '160%', 'color-interpolation-filters': 'sRGB' }, defs);
    el('feMorphology', { in: 'SourceAlpha', operator: 'dilate', radius: w, result: 'grow' }, fl);
    el('feFlood', { 'flood-color': ink, result: 'ink' }, fl);
    el('feComposite', { in: 'ink', in2: 'grow', operator: 'in', result: 'line' }, fl);
    const m = el('feMerge', {}, fl); el('feMergeNode', { in: 'line' }, m); el('feMergeNode', { in: 'SourceGraphic' }, m);
    return id;
  }

  // ---------- expressions: drawn as strokes/fills over the face (face space: head centre 0,0, head radius 1) ----------
  const EXPR = {
    neutral: { eyes: 'dot', mouth: 'line' },
    happy: { eyes: 'arc', mouth: 'smile', blush: 0.6 },
    grin: { eyes: 'arc', mouth: 'grin', blush: 0.5 },
    smug: { eyes: 'half', mouth: 'smirk', brows: 'up' },
    shock: { eyes: 'wide', mouth: 'o', brows: 'up', sweat: 1 },
    scream: { eyes: 'wide', mouth: 'scream', brows: 'up' },
    cry: { eyes: 'closed', mouth: 'wail', tears: 1, brows: 'sad' },
    sad: { eyes: 'dot', mouth: 'frown', brows: 'sad' },
    angry: { eyes: 'dot', mouth: 'teeth', brows: 'angry' },
    deadpan: { eyes: 'flat', mouth: 'line' },
    love: { eyes: 'heart', mouth: 'smile', blush: 1 },
    evil: { eyes: 'half', mouth: 'grin', brows: 'angry' },
  };

  function drawFace(g, spec, e, turn, s) {
    const ink = spec.ink, lw = spec.featureWidth * s;
    const shift = turn * 0.28, sx = 1 - turn * 0.18;   // three-quarter: features slide toward the facing side
    const X = (x) => (x * sx + shift) * spec.headR * s, Y = (y) => y * spec.headR * s;
    const stroke = (d, w = lw) => el('path', { d, fill: 'none', stroke: ink, 'stroke-width': w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, g);
    const fill = (d, c) => el('path', { d, fill: c }, g);
    const ey = spec.eyeY, ex = spec.eyeX;
    for (const side of [-1, 1]) {
      const cx = X(side * ex), cy = Y(ey), r = 0.085 * spec.headR * s;
      switch (e.eyes) {
        case 'dot': fill(circle(cx, cy, r), ink); break;
        case 'wide': fill(ellipse(cx, cy, r * 2.1, r * 2.4), '#FFFFFF'); stroke(ellipse(cx, cy, r * 2.1, r * 2.4), lw * 0.8); fill(circle(cx, cy + r * 0.3, r * 0.9), ink); break;
        case 'arc': stroke(`M${f(cx - r * 1.6)},${f(cy + r * 0.6)} Q${f(cx)},${f(cy - r * 1.6)} ${f(cx + r * 1.6)},${f(cy + r * 0.6)}`); break;
        case 'closed': stroke(`M${f(cx - r * 1.6)},${f(cy - r * 0.2)} Q${f(cx)},${f(cy + r * 1.4)} ${f(cx + r * 1.6)},${f(cy - r * 0.2)}`); break;
        case 'half': fill(`M${f(cx - r * 1.5)},${f(cy)} L${f(cx + r * 1.5)},${f(cy)} A${f(r * 1.5)},${f(r * 1.2)} 0 0 1 ${f(cx - r * 1.5)},${f(cy)} Z`, ink); break;
        case 'flat': stroke(`M${f(cx - r * 1.5)},${f(cy)} L${f(cx + r * 1.5)},${f(cy)}`); break;
        case 'heart': { const h = r * 1.8; fill(`M${f(cx)},${f(cy + h * 0.9)} C${f(cx - h * 1.6)},${f(cy - h * 0.2)} ${f(cx - h * 0.6)},${f(cy - h * 1.2)} ${f(cx)},${f(cy - h * 0.35)} C${f(cx + h * 0.6)},${f(cy - h * 1.2)} ${f(cx + h * 1.6)},${f(cy - h * 0.2)} ${f(cx)},${f(cy + h * 0.9)} Z`, '#E2476E'); break; }
      }
      if (e.brows) {
        const by = cy - r * 2.6, w = r * 1.8, tilt = { up: -0.35, sad: side * 0.5, angry: -side * 0.55 }[e.brows] || 0;
        stroke(`M${f(cx - w)},${f(by + tilt * w * side)} L${f(cx + w)},${f(by - tilt * w * side)}`, lw * 0.9);
      }
      if (e.tears) fill(`M${f(cx - r)},${f(cy + r * 1.2)} L${f(cx + r)},${f(cy + r * 1.2)} L${f(cx + r * 1.4)},${f(cy + r * 9)} L${f(cx - r * 1.4)},${f(cy + r * 9)} Z`, '#8FD3F5');
    }
    const mx = X(0), my = Y(spec.mouthY), m = 0.1 * spec.headR * s;
    switch (e.mouth) {
      case 'line': stroke(`M${f(mx - m)},${f(my)} L${f(mx + m)},${f(my)}`); break;
      case 'smile': stroke(`M${f(mx - m * 1.4)},${f(my - m * 0.3)} Q${f(mx)},${f(my + m * 1.2)} ${f(mx + m * 1.4)},${f(my - m * 0.3)}`); break;
      case 'frown': stroke(`M${f(mx - m * 1.2)},${f(my + m * 0.5)} Q${f(mx)},${f(my - m * 0.8)} ${f(mx + m * 1.2)},${f(my + m * 0.5)}`); break;
      case 'smirk': stroke(`M${f(mx - m)},${f(my + m * 0.2)} Q${f(mx + m * 0.4)},${f(my + m * 0.4)} ${f(mx + m * 1.4)},${f(my - m * 0.6)}`); break;
      case 'grin': { const d = `M${f(mx - m * 1.8)},${f(my - m * 0.4)} Q${f(mx)},${f(my + m * 2.2)} ${f(mx + m * 1.8)},${f(my - m * 0.4)} Z`; fill(d, '#6B1F2A'); stroke(d, lw * 0.8); fill(`M${f(mx - m * 1.5)},${f(my - m * 0.3)} L${f(mx + m * 1.5)},${f(my - m * 0.3)} L${f(mx + m * 1.2)},${f(my + m * 0.3)} L${f(mx - m * 1.2)},${f(my + m * 0.3)} Z`, '#FFFFFF'); break; }
      case 'o': { const d = ellipse(mx, my + m * 0.3, m * 0.7, m * 0.9); fill(d, '#6B1F2A'); stroke(d, lw * 0.8); break; }
      case 'scream': { const d = ellipse(mx, my + m * 1.2, m * 1.6, m * 2.4); fill(d, '#6B1F2A'); stroke(d, lw * 0.8); fill(ellipse(mx, my + m * 2.6, m * 1.0, m * 0.6), '#E2476E'); break; }
      case 'wail': { const d = `M${f(mx - m * 1.8)},${f(my)} Q${f(mx)},${f(my - m * 1.2)} ${f(mx + m * 1.8)},${f(my)} Q${f(mx)},${f(my + m * 2.4)} ${f(mx - m * 1.8)},${f(my)} Z`; fill(d, '#6B1F2A'); stroke(d, lw * 0.8); break; }
      case 'teeth': { const d = `M${f(mx - m * 1.5)},${f(my - m * 0.5)} L${f(mx + m * 1.5)},${f(my - m * 0.5)} L${f(mx + m * 1.2)},${f(my + m * 0.7)} L${f(mx - m * 1.2)},${f(my + m * 0.7)} Z`; fill(d, '#FFFFFF'); stroke(d, lw * 0.8); break; }
    }
    const bl = e.blush ?? 0;
    if (bl > 0) for (const side of [-1, 1]) el('path', { d: ellipse(X(side * (ex + 0.18)), Y(ey + 0.3), 0.14 * spec.headR * s, 0.07 * spec.headR * s), fill: '#F29A96', opacity: 0.55 * bl }, g);
    if (e.sweat) { const x = X(0.72), y = Y(-0.35), r = 0.09 * spec.headR * s; const d = `M${f(x)},${f(y - r * 2.2)} Q${f(x + r * 1.2)},${f(y)} ${f(x)},${f(y + r)} Q${f(x - r * 1.2)},${f(y)} ${f(x)},${f(y - r * 2.2)} Z`; fill(d, '#9ED6F7'); stroke(d, lw * 0.6); }
  }

  // hands and feet (drawn inside the limb layer, so they share its single outline)
  function handPath(kind, x, y, ang, r) {
    const c = Math.cos(ang), s = Math.sin(ang), P = (u, v) => [x + u * c - v * s, y + u * s + v * c];
    const poly = (pts) => 'M' + pts.map(([u, v]) => P(u, v).map(f).join(',')).join(' L') + ' Z';
    switch (kind) {
      case 'fist': return circle(...P(r * 0.3, 0), r * 1.05);
      case 'point': return circle(...P(r * 0.2, 0), r * 0.95) + ' ' + capsule(...P(r * 0.5, 0), r * 0.32, ...P(r * 2.3, 0), r * 0.26);
      case 'wave': case 'open': default: {
        let d = ellipse(...P(r * 0.5, 0), r * 1.0, r * 1.0);
        const fingers = kind === 'wave' ? [-0.8, -0.3, 0.2, 0.7] : [-0.6, -0.2, 0.2, 0.6];
        for (const k of fingers) d += ' ' + capsule(...P(r * 0.9, k * r), r * 0.26, ...P(r * 1.9, k * r * 1.5), r * 0.22);
        d += ' ' + capsule(...P(r * 0.3, -r * 0.9), r * 0.28, ...P(r * 0.9, -r * 1.7), r * 0.22);   // thumb
        return d;
      }
    }
  }

  const VRig_capsule = capsule;
  function make(svg, spec) {
    spec = Object.assign({}, DEFAULT, spec);
    const g = el('g', {}, svg), layers = {};
    for (const k of ['shadow', 'back', 'body', 'face', 'front', 'fx']) layers[k] = el('g', {}, g);
    // soft gradients instead of shading patches: skin lit from upper-left, hair lighter on top
    const uid = Math.random().toString(36).slice(2, 8), defs = svg.querySelector('defs') || el('defs', {}, svg);
    const sg = el('radialGradient', { id: `vrig-skin-${uid}`, cx: '0.42', cy: '0.38', r: '0.7' }, defs);
    el('stop', { offset: '0', 'stop-color': mix(spec.skin, '#FFFFFF', 0.25) }, sg); el('stop', { offset: '0.7', 'stop-color': spec.skin }, sg); el('stop', { offset: '1', 'stop-color': mix(spec.skin, '#C98A6A', 0.28) }, sg);
    const hgd = el('linearGradient', { id: `vrig-hair-${uid}`, x1: '0', y1: '0', x2: '0', y2: '1' }, defs);
    el('stop', { offset: '0', 'stop-color': mix(spec.hairColor, '#FFFFFF', 0.12) }, hgd); el('stop', { offset: '1', 'stop-color': mix(spec.hairColor, '#000000', 0.12) }, hgd);
    const skinFill = `url(#vrig-skin-${uid})`, hairFill = `url(#vrig-hair-${uid})`;
    const clear = (n) => { while (n.firstChild) n.removeChild(n.firstChild); };
    const api = {
      spec, g,
      pose(P = {}) {
        for (const k in layers) clear(layers[k]);
        const s = (P.scale ?? 1) * spec.scale, facing = P.facing ?? 1, turn = P.turn ?? 0, sq = P.squash ?? 0;
        const ol = outlineFilter(svg, Math.max(2, Math.round(spec.lineWidth * s * 2) / 2), spec.ink);   // line weight follows the size
        for (const k of ['back', 'body', 'front']) layers[k].setAttribute('filter', `url(#${ol})`);
        const x0 = P.x ?? 0, y0 = P.y ?? 0;
        g.setAttribute('transform', `translate(${f(x0)},${f(y0)}) scale(${facing * (1 + sq * 0.5)},${1 - sq}) rotate(${f(P.lean ?? 0)})`);
        const e = typeof P.expr === 'object' ? P.expr : Object.assign({}, EXPR[P.expr || 'neutral'] || EXPR.neutral);
        if (P.blush != null) e.blush = P.blush; if (P.sweat != null) e.sweat = P.sweat;
        // skeleton (character space, y up is negative)
        const legLen = spec.legLen * s, hipY = -legLen, torsoH = spec.torsoH * s, shY = hipY - torsoH, neckTop = shY - spec.neckLen * s;
        const headR = spec.headR * s, headY = neckTop - headR * 0.9 + (P.headY ?? 0) * s;
        const hipW = spec.hipW * s, shW = spec.shoulderW * s;
        // shadow
        el('path', { d: ellipse(0, 4 * s, spec.shoulderW * 1.6 * s, 10 * s), fill: '#000', opacity: 0.18 }, layers.shadow);
        // legs: [hip, knee] angles; feet stay at the ends
        const limb = (layer, ox, oy, a1, a2, l1, l2, r0, r1, r2, flip) => {
          const A1 = rad(a1) * flip, A2 = rad(a1 + a2) * flip;
          const kx = ox + Math.sin(A1) * l1, ky = oy + Math.cos(A1) * l1, ex = kx + Math.sin(A2) * l2, ey = ky + Math.cos(A2) * l2;
          return { kx, ky, ex, ey, ang: Math.atan2(ey - ky, ex - kx), d: capsule(ox, oy, r0, kx, ky, r1) + ' ' + capsule(kx, ky, r1, ex, ey, r2) };
        };
        const legs = { L: P.legL || [0, 0], R: P.legR || [0, 0] }, arms = { L: P.armL || [8, 10], R: P.armR || [8, 10] };
        // which limbs are in front: with a three-quarter turn the far side goes behind the body
        const farSide = turn > 0.2 ? 'L' : null;
        for (const side of ['L', 'R']) {
          const sg = side === 'L' ? -1 : 1, layer = side === farSide ? layers.back : layers.body;
          const L = limb(layer, sg * hipW * 0.5, hipY, legs[side][0] * sg, -legs[side][1] * sg, legLen * 0.52, legLen * 0.5, spec.legR * s, spec.legR * 0.9 * s, spec.legR * 0.8 * s, 1);
          el('path', { d: L.d, fill: spec.pants }, layer);
          const fx = L.ex + sg * spec.footLen * 0.25 * s, fy = L.ey - spec.footH * 0.3 * s;
          el('path', { d: ellipse(fx + (facing > 0 ? 1 : 1) * spec.footLen * 0.2 * s * (turn > 0.2 ? 1 : sg * 0.4), fy, spec.footLen * 0.55 * s, spec.footH * 0.55 * s), fill: spec.shoe }, layer);
        }
        // torso + neck + head in ONE layer → one outline around the whole silhouette (no seams at neck/shoulders)
        const tb = layers.body, tw = shW * 0.5, hw = hipW * 0.62;
        const hemY = hipY + spec.legR * 1.1 * s, hemW = hw * 1.12;
        const torso = `M${f(-hemW)},${f(hemY)} Q${f(0)},${f(hemY + 8 * s)} ${f(hemW)},${f(hemY)} C${f(tw * 1.12)},${f(hipY - torsoH * 0.35)} ${f(tw * 1.08)},${f(shY + 18 * s)} ${f(tw * 0.78)},${f(shY + 2 * s)} Q${f(0)},${f(shY - 14 * s)} ${f(-tw * 0.78)},${f(shY + 2 * s)} C${f(-tw * 1.08)},${f(shY + 18 * s)} ${f(-tw * 1.12)},${f(hipY - torsoH * 0.35)} ${f(-hemW)},${f(hemY)} Z`;
        el('path', { d: capsule(0, shY + 4 * s, spec.neckR * s, 0, neckTop + headR * 0.2, spec.neckR * s), fill: spec.skin }, tb);
        el('path', { d: torso, fill: spec.shirt }, tb);
        if (spec.hood) el('path', { d: ellipse(0, shY + 4 * s, tw * 0.95, 13 * s), fill: mix(spec.shirt, '#000000', 0.12) }, tb);
        const tilt = P.head ?? 0;
        const hg = el('g', { transform: `rotate(${f(tilt)} 0 ${f(neckTop)})` }, tb);
        if (spec.ears !== false) for (const side of [-1, 1]) if (!(turn > 0.5 && side < 0)) el('path', { d: ellipse(side * headR * (0.97 - turn * 0.1) + turn * headR * 0.1, headY + headR * 0.12, headR * 0.13, headR * 0.19), fill: spec.skin }, hg);
        const headD = spec.headShape === 'long' ? ellipse(0, headY, headR * 0.86, headR * 1.12) : ellipse(0, headY, headR, headR * 0.96);
        el('path', { d: headD, fill: skinFill }, hg);
        if (spec.hair) el('path', { d: spec.hair(headR, headY, turn), fill: hairFill }, hg);
        // face features + interior lines (hairline, clothing) — thin strokes, no filter
        const fg = el('g', { transform: `rotate(${f(tilt)} 0 ${f(neckTop)}) translate(0 ${f(headY)})` }, layers.face);
        drawFace(fg, spec, e, turn, s);
        if (spec.glasses) for (const side of [-1, 1]) el('path', { d: circle((side * spec.eyeX * (1 - turn * 0.18) + turn * 0.28) * headR, spec.eyeY * headR, 0.2 * headR), fill: 'rgba(255,255,255,0.25)', stroke: spec.ink, 'stroke-width': spec.featureWidth * s * 0.9 }, fg);
        if (spec.hairDetail) el('path', { d: spec.hairDetail(headR, 0, turn), fill: 'none', stroke: spec.ink, 'stroke-width': spec.featureWidth * s * 0.7, 'stroke-linecap': 'round', opacity: 0.8 }, fg);
        if (spec.hairShine !== false && spec.hair) el('path', { d: `M${f(-headR * 0.62)},${f(-headR * 0.55)} Q${f(-headR * 0.3)},${f(-headR * 0.92)} ${f(headR * 0.25)},${f(-headR * 0.88)}`, fill: 'none', stroke: mix(spec.hairColor, '#FFFFFF', 0.35), 'stroke-width': headR * 0.07, 'stroke-linecap': 'round', opacity: 0.8 }, fg);
        if (spec.nose !== false && !['scream', 'wail'].includes(e.mouth)) el('path', { d: `M${f(turn * 0.3 * headR)},${f(headR * 0.24)} q${f(headR * 0.05)},${f(headR * 0.06)} 0,${f(headR * 0.1)}`, fill: 'none', stroke: mix(spec.skin, '#8A4A2A', 0.6), 'stroke-width': spec.featureWidth * s * 0.6, 'stroke-linecap': 'round' }, fg);
        const dg = el('g', {}, layers.face);   // clothing details (below the front arms)
        if (spec.hood) {
          const py = hipY - torsoH * 0.28, pw = tw * 0.55;
          el('path', { d: `M${f(-pw)},${f(py)} L${f(pw)},${f(py)} L${f(pw * 1.15)},${f(py + torsoH * 0.3)} L${f(-pw * 1.15)},${f(py + torsoH * 0.3)} Z`, fill: 'none', stroke: mix(spec.shirt, '#000000', 0.35), 'stroke-width': spec.featureWidth * s * 0.55, 'stroke-linejoin': 'round' }, dg);
          for (const side of [-1, 1]) el('path', { d: `M${f(side * tw * 0.18)},${f(shY + 10 * s)} q${f(side * 3 * s)},${f(torsoH * 0.22)} ${f(side * 1 * s)},${f(torsoH * 0.34)}`, fill: 'none', stroke: '#FFF6E0', 'stroke-width': spec.featureWidth * s * 0.55, 'stroke-linecap': 'round' }, dg);
        }
        // arms: shoulder → elbow → wrist, hand at the end; near arm in the front layer (its own contour over the body)
        const hands = {};
        for (const side of ['L', 'R']) {
          const sg = side === 'L' ? -1 : 1, layer = side === farSide ? layers.back : layers.front;
          const ox = sg * (tw - spec.armR * 0.6 * s), oy = shY + spec.armR * s;
          const A = limb(layer, ox, oy, arms[side][0] * sg, arms[side][1] * sg, spec.armLen * 0.5 * s, spec.armLen * 0.48 * s, spec.armR * s, spec.armR * 0.85 * s, spec.armR * 0.72 * s, 1);
          el('path', { d: A.d, fill: spec.sleeve || spec.shirt }, layer);
          if (spec.cuffs !== false) { const cx = A.ex - Math.cos(A.ang) * spec.armR * 0.9 * s, cy = A.ey - Math.sin(A.ang) * spec.armR * 0.9 * s;
            el('path', { d: VRig_capsule(cx - Math.cos(A.ang) * 5 * s, cy - Math.sin(A.ang) * 5 * s, spec.armR * 0.8 * s, cx + Math.cos(A.ang) * 5 * s, cy + Math.sin(A.ang) * 5 * s, spec.armR * 0.78 * s), fill: mix(spec.sleeve || spec.shirt, '#000000', 0.15) }, layer); }
          const hk = side === 'L' ? P.handL : P.handR;
          el('path', { d: handPath(hk || 'fist', A.ex, A.ey, A.ang, spec.handR * s), fill: spec.skin }, layer);
          hands[side] = { x: A.ex, y: A.ey, ang: A.ang, layer };
        }
        if (P.prop) { const h = hands[P.prop.hand || 'R']; const pg = el('g', { transform: `translate(${f(h.x)},${f(h.y)}) rotate(${f((h.ang * 180) / Math.PI)})` }, layers.front); P.prop.draw(pg, h, s); }
        api.hands = hands; api.headTop = headY - headR; api.headY = headY;
        return api;
      },
    };
    return api;
  }

  function mix(a, b, k) { const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16), c = (i) => Math.round(((pa >> i) & 255) * (1 - k) + ((pb >> i) & 255) * k); return '#' + ((1 << 24) + (c(16) << 16) + (c(8) << 8) + c(0)).toString(16).slice(1); }

  const DEFAULT = {
    scale: 1, ink: '#2B2233', lineWidth: 4, featureWidth: 5,
    headR: 118, headShape: 'round', eyeX: 0.34, eyeY: 0.05, mouthY: 0.46,
    neckLen: 26, neckR: 18, torsoH: 120, shoulderW: 150, hipW: 118, legLen: 108, legR: 22, footLen: 58, footH: 30,
    armLen: 150, armR: 18, handR: 15,
    skin: '#FBE3CF', shirt: '#E9B43A', pants: '#4A5A78', shoe: '#3A2E3A', hairColor: '#5A3522',
  };

  // hair generators (head space: centre (0, headY), radius r). Presets are original designs; add your own.
  const presets = {
    // bowl cut with a chestnut-shaped tip and a wavy fringe (original)
    chestnut: (o = {}) => Object.assign({
      hair: (r, cy, turn) => { const t = turn * r * 0.06; return `M${f(-r * 1.03 + t)},${f(cy + r * 0.05)} C${f(-r * 1.05 + t)},${f(cy - r * 0.9)} ${f(-r * 0.3 + t)},${f(cy - r * 1.12)} ${f(t)},${f(cy - r * 1.02)} C${f(r * 0.1 + t)},${f(cy - r * 1.35)} ${f(r * 0.25 + t)},${f(cy - r * 1.3)} ${f(r * 0.18 + t)},${f(cy - r * 1.02)} C${f(r * 0.7 + t)},${f(cy - r * 1.0)} ${f(r * 1.08 + t)},${f(cy - r * 0.6)} ${f(r * 1.03 + t)},${f(cy + r * 0.05)} Q${f(r * 0.8 + t)},${f(cy - r * 0.25)} ${f(r * 0.5 + t)},${f(cy - r * 0.18)} Q${f(r * 0.25 + t)},${f(cy - r * 0.36)} ${f(0 + t)},${f(cy - r * 0.2)} Q${f(-r * 0.25 + t)},${f(cy - r * 0.36)} ${f(-r * 0.5 + t)},${f(cy - r * 0.18)} Q${f(-r * 0.8 + t)},${f(cy - r * 0.25)} ${f(-r * 1.03 + t)},${f(cy + r * 0.05)} Z`; },
      hairDetail: (r, cy, turn) => `M${f(-r * 0.2)},${f(-r * 1.0)} Q${f(0)},${f(-r * 1.08)} ${f(r * 0.12)},${f(-r * 0.98)}`,
      hairColor: '#5A3522', shirt: '#E9B43A', hood: true,
    }, o),
    // crew cut with a small green sprout on top, long face, round glasses (original)
    sprout: (o = {}) => Object.assign({
      headShape: 'long', glasses: true, eyeY: 0.08,
      hair: (r, cy) => `M${f(-r * 0.82)},${f(cy - r * 0.45)} Q${f(-r * 0.8)},${f(cy - r * 1.12)} ${f(0)},${f(cy - r * 1.14)} Q${f(r * 0.8)},${f(cy - r * 1.12)} ${f(r * 0.82)},${f(cy - r * 0.45)} Q${f(r * 0.5)},${f(cy - r * 0.72)} ${f(0)},${f(cy - r * 0.72)} Q${f(-r * 0.5)},${f(cy - r * 0.72)} ${f(-r * 0.82)},${f(cy - r * 0.45)} Z ` +
        `M${f(-r * 0.06)},${f(cy - r * 1.12)} Q${f(-r * 0.3)},${f(cy - r * 1.5)} ${f(-r * 0.05)},${f(cy - r * 1.55)} Q${f(r * 0.1)},${f(cy - r * 1.4)} ${f(r * 0.06)},${f(cy - r * 1.12)} Z`,
      hairColor: '#6E4A9A', shirt: '#F4F1EA', pants: '#3A3A48', skin: '#F6D3B8',
    }, o),
  };

  root.VRig = { make, presets, EXPR, capsule, DEFAULT };
})(typeof window !== 'undefined' ? window : globalThis);
