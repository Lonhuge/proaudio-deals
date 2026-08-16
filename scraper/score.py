#!/usr/bin/env python3
"""Score Kleinanzeigen listings against Thomann new prices.

Inputs : details.json (scraped ads), thomann.json (query -> product hits)
Output : scored.json
A match is only accepted when the Thomann product name genuinely corresponds
to the ad title, measured by token overlap on meaningful (non-brand-noise) words.
"""
import json, re, sys, pathlib

HERE = pathlib.Path(__file__).parent

STOP = set("""verkaufe verkauf neuwertig neu top zustand sehr gut guter gutem inkl inklusive mit und
ovp originalverpackung wie np vb selten kaum benutzt gebraucht wenig tausch preis euro der die das
ein eine fur von aus im in zu auf set bundle versand moglich abholung privat nichtraucher garantie
rechnung synthesizer synth pedal effektgerat modul module eurorack hp analog digital vintage rare
guitar gitarre bass black white silver schwarz weiss limited edition mk mkii mk2 v2 series serie
b-stock stock case""".split())

def toks(s):
    s = (s or "").lower()
    s = (s.replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "ss"))
    s = re.sub(r"[^a-z0-9\s\-+/.]", " ", s)
    out = []
    for t in s.split():
        t = t.strip("-./+")
        if t and t not in STOP:
            out.append(t)
    return out

def query_for(title):
    return " ".join(toks(title)[:4])

def parse_price(p):
    if not p:
        return None
    m = re.search(r"([\d.]+)(?:,(\d+))?\s*€", p)
    if not m:
        return None
    whole = m.group(1).replace(".", "")
    try:
        return int(whole)
    except ValueError:
        return None

ACC = re.compile(r"\b(case|bag|cover|decksaver|stand|strap|adaptor|adapter|power supply|psu|"
                 r"bracket|overlay|plugin|cloud|expander kit|softcase|flyht|thon|udg|rockboard|b-stock|b stock)\b", re.I)

# an ad whose subject is a case/cover/PSU, in either language
AD_ACC = re.compile(r"\b(case|gigcase|gigbag|hardshell|flightcase|transportcase|tasche|koffer|protector|cover|hulle|hülle|"
                    r"bag|decksaver|staubschutz|dustcover|netzteil|power supply|psu|rack ?ears|"
                    r"bracket|brackets|halterung|stand|manual|anleitung|handbuch|memory ?card|algorithm card|kopfhorer|kopfhörer|headphone|patchkabel|pedalboard|netzteil|expansion|ersatzteil|nur karton|leergehause|display|panel)\b", re.I)

# words that carry no identifying weight when deciding "same product"
FILLER = set("""audio pedal pedals effects designs instruments machines electronic electronics
sound synth synthesizer keyboard guitar bass module modul eurorack processor reverb delay
overdrive distortion fuzz boost compressor chorus tremolo phaser flanger looper""".split())

def ident(s):
    """Identifying tokens: everything meaningful minus generic category filler."""
    return {t for t in toks(s) if t not in FILLER}

def best_match(ad_title, hits):
    """Accept a hit only when the Thomann product name is fully contained in the ad title.

    Containment is the safeguard against near-miss pairings: a Meris Mercury 7 must not
    be priced against a Mercury X, nor a Nord Lead 2x against a Nord Lead A1. If the
    product carries an identifier the ad never mentions, it is a different product.
    """
    at = ident(ad_title)
    if not at:
        return None
    ad_is_acc = bool(AD_ACC.search(ad_title))
    best, best_len = None, -1
    for h in hits:
        name, price = h.get("name"), parse_price(h.get("price"))
        if not name or not price or ACC.search(name):
            continue
        # an ad selling a case must never be priced against the instrument itself
        if ad_is_acc and not AD_ACC.search(name):
            continue
        nt = ident(name)
        if len(nt) < 2 or not nt <= at:      # every product identifier must appear in the ad
            continue
        if len(nt) > best_len:               # prefer the most specific product that still fits
            best, best_len = (name, price), len(nt)
    return best

def main():
    details = json.load(open(HERE / "details.json"))
    thom = json.load(open(HERE / "thomann.json"))

    scored, unmatched = [], []
    for a in details:
        if a.get("err") or a.get("gone") or not a.get("price"):
            continue
        # seller filters
        ads = a.get("ads") or 1
        if ads <= 1 or not a.get("rating"):
            continue
        hits = thom.get(query_for(a["title"]))
        m = best_match(a["title"], hits) if hits else None
        if not m:
            unmatched.append(a["title"])
            continue
        name, ref = m
        pct = round(a["price"] / ref * 100)
        scored.append({
            "id": a["id"], "group": a["cat"], "item": a["title"][:70],
            "match": name, "ask": a["price"], "nw": ref, "pct": pct,
            "vb": a.get("vb", False), "seller": a.get("seller") or "—",
            "ads": ads, "loc": a.get("loc") or "", "href": a["href"],
            "flag2": ads == 2,
        })

    scored.sort(key=lambda r: r["pct"])
    json.dump(scored, open(HERE / "scored.json", "w"), ensure_ascii=False, indent=1)
    json.dump(sorted(set(unmatched)), open(HERE / "unmatched.json", "w"), ensure_ascii=False, indent=1)

    print(f"scored     : {len(scored)}")
    print(f"unmatched  : {len(set(unmatched))} distinct titles")
    for cut in (50, 60, 70, 80):
        print(f"  <={cut}% : {sum(1 for r in scored if r['pct'] <= cut)}")
    from collections import Counter
    print("by group   :", Counter(r["group"] for r in scored))
    print("flagged 2  :", sum(1 for r in scored if r["flag2"]))

if __name__ == "__main__":
    main()
