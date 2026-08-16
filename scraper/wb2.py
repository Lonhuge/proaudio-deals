#!/usr/bin/env python3
"""Recover new prices for discontinued Eurorack from archived SchneidersLaden pages.

Uses exact CDX snapshot timestamps — the /web/<year>/ shortcut returns a
placeholder when no snapshot is close, which silently yields no price.
Serial with a delay: archive.org returns 429 under concurrency.
"""
import json, re, time, urllib.request

snaps   = json.load(open("snapshots.json"))          # slug -> [timestamp, original_url]
targets = dict(json.load(open("wayback_targets.json")))  # key -> slug
by_slug = {sg: k for k, sg in targets.items()}
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

PRICE = [r'itemprop="price"[^>]*content="([\d.,]+)"',
         r'data-price="([\d.,]+)"',
         r'class="price[^"]*"[^>]*>\s*([\d.,]+)\s*&euro;',
         r'([\d.]+,\d{2})\s*&euro;', r'&euro;\s*([\d.,]+)', r'€\s?([\d.,]+)']

def to_eur(v):
    v = v.replace(".", "") if re.search(r",\d{2}$", v) else v.replace(",", "")
    try:
        p = round(float(v.replace(",", ".")))
    except ValueError:
        return None
    return p if 10 <= p <= 20000 else None

out, miss = {}, 0
for slug, (ts, orig) in snaps.items():
    url = f"https://web.archive.org/web/{ts}/{orig}"
    price = None
    for attempt in range(3):                       # archive.org refuses connections under load
        try:
            html = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45)\
                                 .read().decode("utf-8", "ignore")
            for pat in PRICE:
                m = re.search(pat, html)
                if m and (price := to_eur(m.group(1))):
                    break
            break
        except Exception:
            time.sleep(6 * (attempt + 1))
    if price:
        out[by_slug[slug]] = {"slug": slug, "price": price, "snapshot": ts[:8]}
    else:
        miss += 1
    time.sleep(4.0)

json.dump(out, open("wayback_prices.json", "w"), ensure_ascii=False, indent=1)
print(f"recovered {len(out)} prices, {miss} without one")
for k, v in list(out.items())[:16]:
    print(f"  {k:<32} €{v['price']:<6} {v['slug']}  [{v['snapshot']}]")
