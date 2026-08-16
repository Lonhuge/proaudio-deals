#!/usr/bin/env python3
"""Recover discontinued-module prices from archived SchneidersLaden pages.

Saves after every hit so a mid-run block costs nothing, and skips work already
recovered. Exact CDX snapshot timestamps only — /web/<year>/ returns a
placeholder when no snapshot is near, which reads as a false miss.
"""
import json, re, time, urllib.request, pathlib

HERE = pathlib.Path(__file__).parent
snaps   = json.load(open(HERE / "snapshots.json"))
targets = dict(json.load(open(HERE / "wayback_targets.json")))
by_slug = {sg: k for k, sg in targets.items()}
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
OUT = HERE / "wayback_prices.json"

out = json.load(open(OUT)) if OUT.exists() and OUT.stat().st_size > 2 else {}
PRICE = [r'itemprop="price"[^>]*content="([\d.,]+)"', r'data-price="([\d.,]+)"',
         r'([\d.]+,\d{2})\s*&euro;', r'&euro;\s*([\d.,]+)']

def to_eur(v):
    v = v.replace(".", "") if re.search(r",\d{2}$", v) else v.replace(",", "")
    try:
        p = round(float(v.replace(",", ".")))
    except ValueError:
        return None
    return p if 10 <= p <= 20000 else None

todo = [(sg, v) for sg, v in snaps.items() if by_slug.get(sg) not in out]
print(f"{len(todo)} to fetch, {len(out)} already recovered", flush=True)

blocked = 0
for i, (slug, (ts, orig)) in enumerate(todo, 1):
    price = None
    try:
        html = urllib.request.urlopen(
            urllib.request.Request(f"https://web.archive.org/web/{ts}/{orig}", headers=UA),
            timeout=35).read().decode("utf-8", "ignore")
        for pat in PRICE:
            m = re.search(pat, html)
            if m and (price := to_eur(m.group(1))):
                break
        blocked = 0
    except Exception:
        blocked += 1
    if price:
        out[by_slug[slug]] = {"slug": slug, "price": price, "snapshot": ts[:8]}
        json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)   # save as we go
    if i % 10 == 0:
        print(f"  {i}/{len(todo)} — {len(out)} recovered", flush=True)
    time.sleep(6 if blocked else 1.5)      # ease off only when actually refused
print(f"done: {len(out)} prices recovered", flush=True)
