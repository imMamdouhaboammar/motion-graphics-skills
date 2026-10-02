#!/usr/bin/env python3
"""fetch_assets.py — find and download license-safe assets, and record every one in assets/ASSETS.md.

    python fetch_assets.py search --kind image|audio --q "paper texture" [--n 8] [--cc0]
    python fetch_assets.py get --project projects/<id> --url <file url> --name a1.jpg \
        --source openverse --page <landing page> --license "CC BY 2.0" --attribution "author"

Sources (only ones whose licences allow reuse in a published, modified video):
    openverse  images + audio (CC0 / CC BY / CC BY-SA, commercial + modification allowed). No key needed.
    pixabay    images, illustrations, vectors (Pixabay Content License).  Needs env PIXABAY_KEY.
    freesound  sound effects (CC0 / CC BY). Needs env FREESOUND_KEY. (Openverse already indexes much of Freesound.)
Never fetch commercial music or copyrighted characters/logos: music comes from the user or from these libraries.
"""
import argparse, json, os, sys, urllib.parse, urllib.request

UA = {"User-Agent": "reelmimic/0.1 (asset search)"}


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)


def openverse(kind, q, n, cc0):
    lic = "&license=cc0" if cc0 else "&license_type=commercial,modification"
    ep = "images" if kind == "image" else "audio"
    d = get_json(f"https://api.openverse.org/v1/{ep}/?q={urllib.parse.quote(q)}{lic}&page_size={n}")
    out = []
    for r in d.get("results", []):
        lic_name = ("CC0" if r["license"] == "cc0" else f"CC {r['license'].upper()} {r.get('license_version') or ''}".strip())
        out.append({"source": "openverse/" + r.get("source", ""), "title": r.get("title"), "url": r["url"],
                    "page": r.get("foreign_landing_url"), "thumb": r.get("thumbnail"), "license": lic_name,
                    "license_url": r.get("license_url"), "attribution": r.get("attribution") or r.get("creator"),
                    "duration_ms": r.get("duration")})
    return out


def pixabay(q, n):
    key = os.environ.get("PIXABAY_KEY")
    if not key: return []
    d = get_json(f"https://pixabay.com/api/?key={key}&q={urllib.parse.quote(q)}&per_page={max(3, n)}&safesearch=true")
    return [{"source": "pixabay", "title": h.get("tags"), "url": h["largeImageURL"], "page": h["pageURL"], "thumb": h["previewURL"],
             "license": "Pixabay Content License", "license_url": "https://pixabay.com/service/license-summary/",
             "attribution": h.get("user")} for h in d.get("hits", [])[:n]]


def freesound(q, n):
    key = os.environ.get("FREESOUND_KEY")
    if not key: return []
    d = get_json(f"https://freesound.org/apiv2/search/text/?query={urllib.parse.quote(q)}&filter=license:(\"Creative Commons 0\" OR \"Attribution\")"
                 f"&fields=name,url,license,username,previews,duration&page_size={n}&token={key}")
    return [{"source": "freesound", "title": r["name"], "url": r["previews"]["preview-hq-mp3"], "page": r["url"], "thumb": None,
             "license": "CC0" if "zero" in r["license"] else "CC BY", "license_url": r["license"], "attribution": r["username"],
             "duration_ms": int(r["duration"] * 1000)} for r in d.get("results", [])]


def search(a):
    res = openverse(a.kind, a.q, a.n, a.cc0)
    res += pixabay(a.q, a.n) if a.kind == "image" else freesound(a.q, a.n)
    print(json.dumps(res[: a.n * 2], ensure_ascii=False, indent=1))


def get(a):
    adir = os.path.join(a.project, "assets"); os.makedirs(adir, exist_ok=True)
    dst = os.path.join(adir, a.name)
    with urllib.request.urlopen(urllib.request.Request(a.url, headers=UA), timeout=60) as r, open(dst, "wb") as f:
        f.write(r.read())
    ledger = os.path.join(adir, "ASSETS.md")
    new = not os.path.exists(ledger)
    with open(ledger, "a", encoding="utf-8") as f:
        if new: f.write("| 檔名 | 來源 | 原始頁面 | 授權 | 署名 |\n|---|---|---|---|---|\n")
        f.write(f"| {a.name} | {a.source} | {a.page or a.url} | {a.license} | {a.attribution or ''} |\n")
    print(json.dumps({"file": os.path.relpath(dst, a.project).replace("\\", "/"), "bytes": os.path.getsize(dst)}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("--kind", choices=["image", "audio"], required=True); s.add_argument("--q", required=True)
    s.add_argument("--n", type=int, default=8); s.add_argument("--cc0", action="store_true")
    g = sub.add_parser("get")
    for k in ["project", "url", "name", "source", "license"]: g.add_argument("--" + k, required=True)
    g.add_argument("--page"); g.add_argument("--attribution")
    a = ap.parse_args()
    try:
        search(a) if a.cmd == "search" else get(a)
    except Exception as e:
        sys.exit(f"{a.cmd} failed: {e}")
