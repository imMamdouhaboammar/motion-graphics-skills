#!/usr/bin/env python3
"""Where did the time go? Reads projects/<id>/job.json (+ logs/events.jsonl) and prints the production timeline:
wall-clock per stage, every agent turn (who / phase / minutes), the critical path, and what agents spent time on.

  python timeline.py projects/<id> [--json out.json]
"""
import argparse, collections, datetime as D, json, os, re, sys

def ts(x): return D.datetime.fromisoformat(x.replace('Z', ''))
def mins(a, b): return (b - a).total_seconds() / 60

ap = argparse.ArgumentParser(); ap.add_argument('proj'); ap.add_argument('--json'); a = ap.parse_args()
j = json.load(open(os.path.join(a.proj, 'job.json'), encoding='utf-8'))
ev = j.get('log', [])
full = os.path.join(a.proj, 'logs', 'events.jsonl')
if os.path.exists(full):
    ev = [json.loads(l) for l in open(full, encoding='utf-8') if l.strip()] or ev

# agent turns
open_t, turns = {}, []
for e in ev:
    if e.get('type') != 'turn': continue
    k = (e.get('who'), e.get('phase'))
    if e['state'] == 'start': open_t[k] = e['ts']
    elif k in open_t:
        s = open_t.pop(k); turns.append({'who': e.get('who'), 'phase': e.get('phase'), 'start': s, 'end': e['ts'], 'min': round(mins(ts(s), ts(e['ts'])), 1), 'ok': e.get('ok')})
for k, s in open_t.items(): turns.append({'who': k[0], 'phase': k[1], 'start': s, 'end': None, 'min': None, 'ok': None})
turns.sort(key=lambda t: t['start'])

t0 = ts(j.get('createdAt') or ev[0]['ts']); tA = ts(j['approvedAt']) if j.get('approvedAt') else None
last = ts(ev[-1]['ts']) if ev else t0
print(f"project {j['id']}  stage={j['stage']}")
print(f"  created → approved : {mins(t0, tA):.0f} min (includes waiting for the user)" if tA else '  not approved yet')
if tA: print(f"  approved → last event: {mins(tA, last):.0f} min")

# phases after approval
by_phase = collections.defaultdict(lambda: [None, None])
for t in turns:
    if tA and ts(t['start']) < tA: continue
    ph = {'setup': 'setup', 'cast_qa': 'cast', 'cast_fix': 'cast', 'build_chunk': 'shots', 'shot_qa': 'shots', 'fix_chunk': 'shots',
          'assemble': 'assemble', 'critique': 'final', 'revise': 'final'}.get(t['phase'], t['phase'])
    s, e = ts(t['start']), ts(t['end']) if t['end'] else last
    b = by_phase[ph]; b[0] = s if b[0] is None or s < b[0] else b[0]; b[1] = e if b[1] is None or e > b[1] else b[1]
print('\nwall-clock per production phase (min):')
for ph in ['setup', 'cast', 'shots', 'assemble', 'final']:
    if ph in by_phase: s, e = by_phase[ph]; print(f"  {ph:9s} {mins(s, e):6.0f}   ({s:%H:%M}–{e:%H:%M} UTC)")

print('\nagent turns:')
for t in turns: print(f"  {t['start'][11:16]}  {t['who'] or '-':14s} {t['phase']:12s} {t['min'] if t['min'] is not None else 'running':>7}  {'' if t['ok'] in (True, None) else 'FAIL'}")

# per chunk: build + review rounds
chunks = collections.defaultdict(list)
shot2chunk = {}
try:
    prod = json.load(open(os.path.join(a.proj, 'build', 'production.json'), encoding='utf-8'))
    for c in prod.get('chunks') or []:
        for s in c.get('shots') or []: shot2chunk[s] = c['id']
except (OSError, ValueError): pass
for t in turns:
    m = re.search(r'-(C\d+)$', t['who'] or '')
    c = m.group(1) if m else shot2chunk.get((re.search(r'^shot-qa-(\S+)$', t['who'] or '') or [None, None])[1])
    if c and t['min']: chunks[c].append((t['phase'], t['min']))
if chunks:
    print('\nper segment (build / review / fix minutes, rounds):')
    for c in sorted(chunks, key=lambda x: int(x[1:])):
        L = chunks[c]; f = lambda p: sum(m for ph, m in L if ph == p)
        rounds = (j.get('pipeline') or {}).get('chunks', {}).get(c, {}).get('round')
        print(f"  {c}: build {f('build_chunk'):.0f}, review {f('shot_qa'):.0f} ({sum(1 for ph, _ in L if ph == 'shot_qa')} shot reviews), fix {f('fix_chunk'):.0f} ({sum(1 for ph, _ in L if ph == 'fix_chunk')} fix turns), rounds {rounds or '?'}  → {sum(m for _, m in L):.0f} min")

# what agents spend time on (gap to their next event)
cat = collections.Counter(); byw = collections.defaultdict(list)
for e in ev:
    if e.get('who'): byw[e['who']].append(e)
for w, es in byw.items():
    for x, y in zip(es, es[1:]):
        g = (ts(y['ts']) - ts(x['ts'])).total_seconds()
        if g > 1800 or x.get('type') == 'turn': continue
        d = str(x.get('detail') or '')
        if x.get('type') == 'tool' and x.get('name') in ('Bash', 'shell', 'PowerShell'):
            k = 'wait/sleep' if re.match(r'\s*sleep \d', d) else 'screenshots' if re.search(r'snapshot|preview|hf_frames|render\.mjs|puppeteer|shot_page', d) else 'hyperframes render' if 'render' in d else 'edit/other cmd'
        elif x.get('type') == 'tool': k = 'look at images' if re.search(r'\.(png|jpe?g)$', d, re.I) else f"{x.get('name')}"
        else: k = 'thinking/writing'
        cat[k] += g
tot = sum(cat.values()) or 1
print('\nagent time by activity (all agents summed):')
for k, v in cat.most_common(): print(f"  {k:18s} {v / 60:6.0f} min  {100 * v / tot:4.0f}%")
if a.json: json.dump({'turns': turns, 'activity_min': {k: round(v / 60, 1) for k, v in cat.items()}}, open(a.json, 'w'), indent=1)
