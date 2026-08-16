#!/usr/bin/env python3
"""Score Kleinanzeigen listings against the Reverb used market.

Thomann covers what it stocks; this covers the rest — boutique pedals, Eurorack,
discontinued synths. The benchmark is therefore a *used asking price*, not a new
price, and rows scored here are labelled accordingly.
"""
import json, re, statistics, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from score import toks, ident, query_for, FILLER, AD_ACC

HERE = pathlib.Path(__file__).parent

# rows that are not the product: accessories, clones, kits, spares
REJECT = re.compile(
    r"\b(cover|backpack|case|bag|gigbag|sleeve|decksaver|dust ?cover|stand|bracket|"
    r"clone|nano|micro ?rings|nrings|diy|kit\b|pcb|panel only|faceplate|"
    r"manual|sticker|patch ?cable|cable|power supply|psu|adapter|adaptor|"
    r"eprom|firmware|rom\b|battery|replacement|spare|repair|for parts|"
    r"expansion card|memory card|cartridge|overlay|t-?shirt|poster|b-?stock)\b", re.I)

def clean_rows(hits):
    out = []
    for h in hits or []:
        if not isinstance(h, dict):
            continue
        name = h.get("m") or h.get("t") or ""
        text = f"{h.get('m','')} {h.get('t','')}"
        price = h.get("p")
        if not name or not price or REJECT.search(text):
            continue
        out.append((name, text, int(price)))
    return out

def reference(ad_title, hits):
    """Median asking price across Reverb rows that genuinely name this product."""
    at = ident(ad_title)
    if not at:
        return None
    prices, names = [], []
    for name, text, price in clean_rows(hits):
        nt = ident(name)
        if len(nt) < 2 or not nt <= at:      # same containment rule as the Thomann pass
            continue
        prices.append(price)
        names.append(name)
    if len(prices) < 2:                       # one data point is not a market
        return None
    return int(statistics.median(prices)), names[0], len(prices)

def main():
    ads  = json.load(open(HERE / "search_priced.json"))
    thom = json.load(open(HERE / "thomann.json"))
    rev  = json.load(open(HERE / "reverb.json"))
    pool = {**rev.get("iframe", {}), **rev.get("api", {})}

    # only score what Thomann could not
    from score import best_match
    done = {a["id"] for a in ads
            if thom.get(query_for(a["title"])) and best_match(a["title"], thom[query_for(a["title"])])}

    def key(t):
        return " ".join([x for x in toks(t) if x not in FILLER][:3])

    rows = []
    for a in ads:
        if a["id"] in done:
            continue
        if AD_ACC.search(a["title"]):   # the ad is a case/cover, not the instrument
            continue
        hits = pool.get(key(a["title"])) or pool.get(query_for(a["title"]))
        r = reference(a["title"], hits)
        if not r:
            continue
        ref, matched, n = r
        rows.append({**a, "match": matched, "ref": ref, "n": n,
                     "pct": round(a["price"] / ref * 100)})
    rows.sort(key=lambda r: r["pct"])
    json.dump(rows, open(HERE / "reverb_scored.json", "w"), ensure_ascii=False, indent=1)

    print(f"newly scored: {len(rows)}")
    for c in (50, 60, 70):
        print(f"  <={c}%: {sum(1 for r in rows if r['pct'] <= c)}")
    print()
    for r in [x for x in rows if x["pct"] <= 65]:
        print(f"{r['pct']:>4}%  {r['price']:>5}€/{r['ref']:>5}€ (n={r['n']:>2})  {r['cat']:<7} "
              f"{r['title'][:44]:<44} -> {r['match'][:30]}")

if __name__ == "__main__":
    main()
