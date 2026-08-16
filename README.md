# Pro-audio deal scan — Kleinanzeigen

Finds used pro-audio gear on [Kleinanzeigen](https://www.kleinanzeigen.de) selling well below its
reference price, filtered by how trustworthy the seller looks.

**Report:** open `index.html` in a browser, or view the published version linked in the project notes.

Scan date: **16 August 2026**. Prices in EUR incl. German VAT.

---

## Selection rules

| Rule | Applied |
|---|---|
| Asking price ≤ 60% of reference | primary cutoff, adjustable in the report via slider |
| Seller has exactly 1 ad | excluded |
| Seller has exactly 2 ads | included, flagged |
| Seller has no satisfaction rating | excluded |

Kleinanzeigen omits the "N Anzeigen online" counter when a seller has exactly one listing, so ad
counts were confirmed against each seller's own profile page rather than inferred from the ad.

## Two reference benchmarks

Gear still in production is measured against its **current new price**, looked up per model at
Thomann, with Geizhals covering boutique brands Thomann does not stock (Manley, Tube-Tech LCA 2B,
Chandler, Crane Song).

Discontinued and vintage gear has no new price, so it is measured against **comparable units
currently listed on Reverb in euros**, condition-matched where the listing allowed it. This is an
*asking-price* reference, not a completed sale — eBay blocks automated access to its sold-listings
archive and Reverb's sold-price guide is gated behind a per-model form. Real transaction prices run
below asking, so those percentages are the optimistic end.

Every row in the report says which benchmark it used.

## Coverage

| | |
|---|---|
| Ads scraped (all searches paged to exhaustion) | **7,833** |
| Priced against a reference | **902** |
| Past the seller filter | **246** |
| Qualifying at ≤60% | **102** |

Guitar pedals 95 · Modular 49 · Synths 41 · Outboard 37 · Vintage 24.

## Three reference sources

| Source | Covers | Benchmark |
|---|---|---|
| **Thomann** | mainstream stock | current **new** price |
| **Reverb** (JSON API, `X-Display-Currency: EUR`) | discontinued & boutique | **used** market median |
| **SchneidersLaden** | Eurorack | current **new** price |

SchneidersLaden is the Berlin modular shop, and it prices the Eurorack that the other two miss
entirely — Reverb returns clones for Mutable Instruments, Thomann does not stock Make Noise, Erica
or Xaoc at all. Product identity comes from the **URL slug**, not the display name: the shop shows
"Maths 2 (Silver)" while the slug reads `make-noise-maths-2-silver` and carries the manufacturer.

Two locale traps live here. SchneidersLaden's English pages write €390.00 with a period as the
*decimal* separator, so stripping periods (correct for German 1.234,00) multiplies every price by
100. Reverb writes €9,999 with a comma as the *thousands* separator. Both parsers now detect the
format instead of assuming one.

`scraper/wb2.py` recovers prices for discontinued modules from **archived SchneidersLaden product
pages** via the Wayback Machine. It resolves exact snapshot timestamps from the CDX index —
`/web/<year>/<url>` silently returns a placeholder page when no snapshot is near, which yields no
price and looks like a miss. archive.org rate-limits hard: requests are serial with a 4 s delay and
three retries, and even then it intermittently refuses connections.

## Matching

`scraper/score.py` pairs an ad with a Thomann product only when **every identifying token in the
product name also appears in the ad title**. Looser token-overlap scoring produced confident
nonsense — a Meris Mercury 7 priced against the newer Mercury X (36% "discount"), a Nord Lead 2x
against a Nord Lead A1 (50%), a Prophet 600 against a Prophet 6. Two rules do most of the work:

- single-character tokens are significant — the whole difference between Mercury **7** and
  Mercury **X** lives there, and dropping them as noise is what created the false bargains;
- B-Stock and open-box listings never serve as the "new" reference.

Run it with `python3 scraper/score.py`.

## Known limits

- Only gear with a findable reference price is scored. Vintage items with no usable comparable
  (Aurora Audio GT4-2, Drawmer LX20, dbx 376, Lexicon MPX500, Schoeps CMC) were left out rather
  than guessed at.
- A rating badge reflects completed transactions of any kind. It is not a guarantee on a
  four-figure channel strip.
- Ads sell and prices move. Everything here was confirmed live at scan time and nothing more.
- One seller had the same Tube-Tech LCA 2B posted three times; it is listed once.

## Files

- `index.html` — the report, self-contained, no build step, works offline
- `data/listings.json` — the scored listings behind it

## Build

`index.html` is generated — edit `report.src.html`, then:

```bash
python3 build.py report.src.html
```

The wrapper adds the doctype, `<meta charset="utf-8">` (required — the report is full of
German umlauts and euro signs) and the viewport tag.
