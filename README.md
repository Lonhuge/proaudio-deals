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

| Category | Ads priced | Matched to a reference | Qualifying |
|---|---|---|---|
| Compressors, EQs, preamps, effects, mics | 696 scraped | 114 | 15 |
| Vintage / discontinued outboard | 62 matched | 56 | 5 |
| Guitar pedals | 463 | 64 | 6 |
| Synthesizers | 383 | 32 | 1 |
| Modular / Eurorack | 363 | 15 | 2 |

The nine qualifiers in the three newer categories are a **floor, not a complete answer**. Only 111
of 1,209 priced listings could be matched to a reference price, because Thomann does not stock much
of this world: Chase Bliss, Noise Engineering and Mutable Instruments return unrelated products, and
Mutable is discontinued outright. The unmatched remainder is kept in `data/search_priced.json`
rather than dropped — wiring in a source that covers boutique pedals and Eurorack (Reverb's EU
listings, ModularGrid) would score it without rescraping.

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
