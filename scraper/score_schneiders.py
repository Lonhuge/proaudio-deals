#!/usr/bin/env python3
"""Score Eurorack listings against SchneidersLaden new prices.

SchneidersLaden is the Berlin modular retailer, so it stocks the boutique
Eurorack that Thomann and Reverb both miss. Product identity comes from the
URL slug rather than the display name — the shop shows "Maths 2 (Silver)"
but the slug says make-noise-maths-2-silver, which carries the manufacturer.
Discontinued modules fall back to archived SchneidersLaden pages (Wayback).
"""
import json, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from score import toks, ident, FILLER, AD_ACC

HERE = pathlib.Path(__file__).parent
REJECT = re.compile(r"\b(blank panel|panel|blindplatte|cable|kabel|netzteil|power|psu|bus board|"
                    r"rack ?ears|case|koffer|bag|screws|schrauben|sticker|manual|expander only|"
                    r"clone|pixie|nano|micro)\b", re.I)

def key3(t):
    return " ".join([x for x in toks(t) if x not in FILLER][:3])

def best(ad_title, hits):
    """Most specific SchneidersLaden product fully named by the ad."""
    at = ident(ad_title)
    if not at:
        return None
    pick = None
    for h in hits or []:
        if not isinstance(h, dict):
            continue
        name, price = h.get("m"), h.get("p")
        if not name or not price or REJECT.search(name) or REJECT.search(h.get("t", "")):
            continue
        nt = ident(name)
        if len(nt) < 2 or not nt <= at:
            continue
        if pick is None or len(nt) > pick[2]:
            pick = (h.get("t") or name, price, len(nt))
    return pick[:2] if pick else None

def main():
    ads = [a for a in json.load(open(HERE / "ads_v2.json")) if a["cat"] == "modular"]
    sl  = json.load(open(HERE / "schneiders.json"))
    try:
        wb = json.load(open(HERE / "wayback_prices.json"))
    except Exception:
        wb = {}

    rows = []
    for a in ads:
        if AD_ACC.search(a["title"]):
            continue
        k = key3(a["title"])
        m = best(a["title"], sl.get(k))
        src = "new"
        if not m and k in wb:                     # discontinued: archived shop price
            m, src = (wb[k]["slug"].replace("-", " "), wb[k]["price"]), "archived"
        if not m:
            continue
        name, ref = m
        rows.append({**a, "match": name, "ref": ref, "reftype": src,
                     "pct": round(a["price"] / ref * 100)})
    rows.sort(key=lambda r: r["pct"])
    json.dump(rows, open(HERE / "modular_scored.json", "w"), ensure_ascii=False)
    print(f"modular priced: {len(rows)} of {len(ads)}")
    for c in (50, 60, 70):
        print(f"  <={c}%: {sum(1 for r in rows if r['pct'] <= c)}")
    for r in [x for x in rows if 15 <= x["pct"] <= 62][:22]:
        print(f"{r['pct']:>4}%  {r['price']:>5}€/{r['ref']:>5}€ [{r['reftype'][:4]}]  "
              f"{r['title'][:44]:<44} -> {r['match'][:34]}")

if __name__ == "__main__":
    main()
