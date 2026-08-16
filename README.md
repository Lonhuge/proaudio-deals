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

| Category | Status |
|---|---|
| Compressors, EQs, preamps, effects, mics | complete — 696 ads scraped, 20 qualifying listings |
| Vintage / discontinued outboard | complete — 62 matched, 5 qualifying |
| Guitar pedals | **incomplete** — see below |
| Synthesizers | **incomplete** — see below |
| Modular / Eurorack | **incomplete** — see below |

The three newer categories were scraped (940 ads found, 802 candidates after filtering) but the
run was cut short: requesting ad detail pages at six concurrent connections triggered a temporary
IP-range block from Kleinanzeigen, and the partial results were then lost. The category filters
are present in the report but carry no data yet. Rerunning at one connection with a delay between
requests is the fix.

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
