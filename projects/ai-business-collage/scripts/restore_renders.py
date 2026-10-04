#!/usr/bin/env python3
"""Restore byte-identical renders from repository parts; Python standard library only."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
for item in json.loads((root/'renders/render_parts_manifest.json').read_text()):
    target=root/item['path']
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256']:
        print('Already restored:',item['path']); continue
    temp=target.with_suffix(target.suffix+'.restoring')
    digest=hashlib.sha256(); size=0
    try:
        with temp.open('wb') as out:
            for part in item['parts']:
                data=(root/part['path']).read_bytes()
                if len(data)!=part['bytes'] or hashlib.sha256(data).hexdigest()!=part['sha256']:
                    raise ValueError('Part failed integrity check: '+part['path'])
                out.write(data); digest.update(data); size+=len(data)
        if size!=item['bytes'] or digest.hexdigest()!=item['sha256']:
            raise ValueError('Render failed integrity check: '+item['path'])
        temp.replace(target); print('Restored:',item['path'])
    except Exception:
        temp.unlink(missing_ok=True); raise
