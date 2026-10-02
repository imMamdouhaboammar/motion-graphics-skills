import { wordListsFromMediaMeta } from "./words.mjs";

// audio_meta.json word times are relative to each line's own file.
export function speechSpans(meta, { mergeGap = 0.6, offsets, sequential = false, gap = 0 } = {}) {
  const merge = Number(mergeGap);
  const lists = wordListsFromMediaMeta(meta);
  const voices = Array.isArray(meta?.voices) ? meta.voices : [];
  if (lists.length > 1 && !offsets && !sequential) {
    throw new Error(
      "audio_meta has multiple voice lines with file-relative times; pass --sequential or --offsets so spans land at composition time",
    );
  }
  const intervals = [];
  let cursor = 0;
  for (let i = 0; i < lists.length; i++) {
    const voice = voices[i];
    let offset = 0;
    if (offsets) {
      const id = voice?.id ?? String(i);
      if (!(id in offsets)) throw new Error(`--offsets is missing voice "${id}"`);
      offset = Number(offsets[id]);
      if (!Number.isFinite(offset)) throw new Error(`--offsets has an invalid time for voice "${id}"`);
    } else if (sequential) {
      offset = cursor;
      const lineDuration = Number(voice?.duration_s) || Math.max(...lists[i].map((w) => w.end), 0);
      cursor += lineDuration + (Number(gap) || 0);
    }
    for (const word of lists[i]) {
      if (word.end > word.start)
        intervals.push({ start: word.start + offset, end: word.end + offset });
    }
  }
  return mergeIntervals(intervals, Number.isFinite(merge) && merge >= 0 ? merge : 0.6);
}

export function duckKeyframes(
  spans,
  { duck = 0.25, attack = 0.15, release = 0.4, baseVolume = 1 } = {},
) {
  const base = finiteOr(baseVolume, 1);
  const ducked = round3(base * finiteOr(duck, 0.25));
  const keyframes = [];
  for (const span of spans) {
    keyframes.push({
      time: round3(Math.max(0, finiteOr(span.start, 0))),
      volume: ducked,
      duration: round3(finiteOr(attack, 0.15)),
    });
    keyframes.push({
      time: round3(Math.max(0, finiteOr(span.end, 0))),
      volume: round3(base),
      duration: round3(finiteOr(release, 0.4)),
    });
  }
  return keyframes.sort((a, b) => a.time - b.time);
}

/** Volume lane for `data-automation`: composition-time keyframes as clip-local ramps. */
export function duckLane(keyframes, { clipStart = 0, baseVolume = 1 } = {}) {
  const start = finiteOr(clipStart, 0);
  const envelope = [{ t: 0, v: finiteOr(baseVolume, 1) }];
  const valueAt = (time) => {
    for (let i = 1; i < envelope.length; i++) {
      const right = envelope[i], left = envelope[i - 1];
      if (time <= right.t)
        return left.v + (right.v - left.v) * (time - left.t) / (right.t - left.t);
    }
    return envelope.at(-1).v;
  };
  for (const kf of [...keyframes].sort((a, b) => a.time - b.time)) {
    const time = Math.max(0, finiteOr(kf.time, 0));
    const duration = Number(kf.duration);
    if (!Number.isFinite(duration) || duration <= 0)
      throw new Error("ducking attack and release durations must be positive finite seconds");
    const volume = finiteOr(kf.volume, envelope.at(-1).v);
    const current = valueAt(time);
    // A new ramp interrupts any preceding unfinished ramp.
    while (envelope.at(-1)?.t >= time) envelope.pop();
    envelope.push({ t: time, v: current });
    envelope.push({ t: time + duration, v: volume });
  }
  const points = [{ t: 0, v: round3(valueAt(start)) }];
  for (const point of envelope) {
    if (point.t > start) points.push({ t: round3(point.t - start), v: round3(point.v) });
  }
  return { version: 1, lanes: [{ target: "volume", points }] };
}

function mergeIntervals(intervals, mergeGap) {
  const sorted = intervals
    .map((range) => ({ start: round3(range.start), end: round3(range.end) }))
    .sort((a, b) => a.start - b.start || a.end - b.end);
  const merged = [];
  for (const range of sorted) {
    const prev = merged.at(-1);
    if (prev && (range.start <= prev.end || range.start - prev.end < mergeGap)) {
      prev.end = Math.max(prev.end, range.end);
    } else {
      merged.push({ ...range });
    }
  }
  return merged;
}

function finiteOr(value, fallback) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function round3(n) {
  return Math.round(Number(n) * 1000) / 1000;
}
