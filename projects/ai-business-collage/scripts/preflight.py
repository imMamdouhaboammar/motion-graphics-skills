#!/usr/bin/env python3
"""Read-only production gate. Never starts image generation or rendering."""
import argparse, csv, hashlib, importlib.util, json, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def check():
    config = json.loads((ROOT / 'src/project.json').read_text())
    checks = []
    def record(name, passed, detail):
        checks.append(dict(name=name, passed=passed, detail=detail))
    for name in ('voiceover', 'reference'):
        file = ROOT / config['inputs'][name]['path']
        digest = hashlib.sha256(file.read_bytes()).hexdigest() if file.exists() else None
        record(name + '_immutable', digest == config['inputs'][name]['sha256'], str(file.relative_to(ROOT)))
    record('ffprobe', bool(shutil.which('ffprobe')), 'Required for media verification')
    record('ffmpeg', bool(shutil.which('ffmpeg')), 'Required for media analysis and delivery verification')
    for path in config['font']['files']:
        record('font:' + path, (ROOT / path).is_file(), 'Real Thmanyah font required; fallback forbidden')
    record('image_provider_decision', config['image_generation']['substitution_approved'],
           'Native tool cannot expose/select the requested GPT Images 2.5 model; explicit decision required')
    rows = list(csv.DictReader((ROOT / 'assets/asset_manifest.csv').open(encoding='utf-8-sig')))
    for row in rows:
        file = ROOT / row['output_path']
        passed = row['state'] == 'COMPOSITE_REVIEWED' and file.is_file() and (row['alpha_verified'] == 'true' or row['asset_id'] in ('A02','A08','A32'))
        record('asset:' + row['asset_id'], passed, row['state'])
    alignment = json.loads((ROOT / 'analysis/voice_alignment.json').read_text())
    record('phrase_alignment', alignment['status'] == 'ASR_TIMED_APPROVED_COPY', alignment['status'])
    runtime = shutil.which('hyperframes')
    local_runtime = ROOT / 'node_modules/.bin/hyperframes'
    record('hyperframes_runtime', bool(runtime) or local_runtime.exists(), 'CLI must be installed and validated before capture')
    record('hardware_workload', config['runtime']['hardware_workload_verified'] or config['runtime']['cpu_fallback_approved'], 'QSV candidate failed actual decode probe')
    record('composition', (ROOT / 'index.html').is_file(), 'Native HyperFrames composition exists')
    return dict(status='READY' if all(x['passed'] for x in checks) else 'BLOCKED', checks=checks)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = check()
    report = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + '\n')
    print(report)
    raise SystemExit(0 if result['status'] == 'READY' else 2)
