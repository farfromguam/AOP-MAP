# AOP Trail Number → Name Index

Last touched: 2026-05-29

The AOP paper/QR map labels trails by **number only** (confirmed against the
SFWDA 2015 raster `import/community_trails/sfwda_aop_trail_map_2015-03-11.png`:
numbers 1–60+, color-coded green=Easy / blue=Moderate / black-triangle=Difficult,
no name legend on the sheet). This file collects the number→name mapping found
off-park.

## Key finding

**No complete public 1–120 AOP number→name index exists freely online.** The
park's full index lives in (a) the onX Offroad app data — subscription-gated,
and (b) the park's own digital map (Replit-hosted JS SPA behind the QR code).
Community paper-map photos are posted on the Hardline Crawlers forum thread but
that site returns 403 to scripted clients (manual browser visit needed):
`https://www.hardlinecrawlers.com/threads/aop-adventure-offroad-park-paper-map.49037/`

## Official site has NO names (rendered the SPA, 2026-05-29)

The official `adventureoffroadpark.com` is a Vite SPA; the live trail page is
**`/trails`** (the old `/pages/map` route now 404s in the router). Rendered it
in headless Chromium and watched the network: the "trail map" is just **two
static raster assets + a Google Maps embed** (location pin only, no trail
geometry). No data API for trails — the only `/api/*` calls are events/auth.
Trail names are NOT in the site bundle or any data file.

Current official map assets (timestamps ≈ Nov 2025 — newer than the SFWDA 2015
raster), saved to `import/community_trails/`:
- `aop_official_trail_map_2025-11.webp` / `.png` — the current map. **Same scheme
  as 2015: numbers only**, legend = Easy(green ●) / Moderate(blue ■) /
  Difficult(black ▲) + Picnic / Camping / Bathrooms. Named features visible on
  the sheet: "Lesson Zone", Jeep Entrance, Buggy Entrance (no per-trail names).
- `aop_official_map_rules_2025-11.pdf` — 4-page "Map + Rules"; page 1 = the same
  map, pages 2–4 = rules prose (CID-encoded, not a name legend).

Scraper: `/tmp/aop_map_scrape.py` (one-off, not committed).

Conclusion: **the number→name mapping is not published by the park at all.** The
paper/QR map and the official site are both numbers-only by design. onX is the
only public namer.

## Wayback Machine sweep (2026-05-29) — names were never the park's system

Pulled the full CDX capture history for `adventureoffroadpark.com` (the park has
cycled through ≥4 platforms: BigCommerce blog ~2014–15 → Adobe Muse `/map.html`
~2020 → Shopify `/pages/map` ~2022 → current Vite SPA `/trails`). Every map
across every era is **numbers-only**:

- 2015 SFWDA raster — numbers only (already held).
- **2015 BigCommerce blog post `/blog/aop-trail-96/`** (archived 200): titled
  "AOP Trail 96," body = *"Trail 96 is a Blue, or moderate difficulty trail… a
  short loop… rock and ledge obstacles… passable by modified Jeeps and Trucks."*
  Referred to purely by **number** — no name. This is the park's own voice.
- 2020 `/map.html` and 2022 `/pages/map` — both just embed a map image, no name
  list in the page.
- 2025 `/trails` — numbers-only image (held).

**Conclusion: the park identifies trails by NUMBER, not name — and always has.**
There is no "lost" name index because an official name set never existed. The
onX names (Launch Pad, Major Tom, …) are **onX-contributor-applied labels**, not
AOP's nomenclature, and onX only named ~8 of the ~120. So the realistic ceiling
on a number→name index is: onX's handful + whatever names ride along on the
event/bounty obstacles (Bounty Hill, Riot Hill, Lesson Zone, Freeze Zone). The
remaining ~110 trails have numbers and difficulty colors only, by design.

## Best public source: onX Offroad

onX publishes per-trail guide pages at
`onxmaps.com/offroad/trails/us/tennessee/<number>-<slug>`. Only a handful of AOP
trails have published pages. **Caution:** Tennessee numbered slugs are a MIX of
AOP *and* Windrock Park (Windrock also numbers its trails). Park membership was
verified per trail by the page text, NOT inferred from the number.

### Confirmed AOP trails (onX page explicitly says "AOP")

| # | Name | Difficulty (onX) | Notes |
|---|------|------------------|-------|
| 1 | Launch Pad | Easy (TR2), 1.2 mi | Dirt climb to "Area 51"; splits to 18 & 50 at end; meets 3, 22 |
| 2 | Convergence | Easy | Peels off Trail 1 toward the buggy side |
| 3 | Major Tom | Easy / casual | Easy to underestimate |
| 5 | Lifeform | Easy | Uphill connector; small rock, roots; comes out to Trail 3 |
| 6 | Descension | Moderate (TR6) | Mild downhill, ends rutted/eroded |
| 7 | Ascension | Moderate (TR5) | — |
| 9 | Little Dipper | Easy (TR2) | Full self-loop; connects to harder trails |
| 11 | Ground Control | Easy (TR3), 0.3 mi | "Child's roller coaster," scattered rock |

Referenced as AOP trail numbers in the above descriptions but **no published
named page found**: 18, 22, 50.

Theme: David Bowie / Space Oddity — Launch Pad, Major Tom, Ground Control,
Ascension/Descension, Little Dipper, Lifeform, Area 51.

### NOT AOP — Windrock Park (numbered slugs that collide, verified)

4 Lane (7.5 mi, Road 116/WMA), 8 Humpback, 33 Bead Buster, 52 Cold Gap Shortcut,
53 Cold Gap Waterfall, 59 Grassy Gap, 60 Bridge Branch, 64 Patricks Pond,
66 Caryville Flats, 70 Disney Hollow, 73 Harness Creek, 74 Middle Ridge,
83 American Knob Bypass, 87 Poplar Creek, 88 Bearwallow Branch,
89 Little Braden Flat, 93 Oak Elbow.

### Unconfirmed

16 Mud Suck Creek — "Jeep Badge of Honor Trail," TR8, 5.5 mi; onX page names no
park. Length suggests Windrock, not AOP's ~500 acres. Earlier web-search blurbs
attributed it to AOP — treat as unverified.

## Trail descriptions harvested (2026-05-29)

Full prose saved to `import/community_trails/aop_trail_descriptions.json` (raw
zone; onX text is onX-copyright, #96 is AOP-copyright-via-Wayback — do NOT
publish without source rows + license clearance). onX serves each description in
its `og:description` meta tag, so curl + grep pulls it without JS rendering.

- **8 AOP trails (onX prose):** 1 Launchpad, 2 Convergence, 3 Major Tom,
  5 Lifeform, 6 Descension, 7 Ascension, 9 Little Dipper, 11 Ground Control.
- **1 park-authored (Wayback):** Trail 96 — "Blue / moderate… short loop…
  rock and ledge obstacles… passable by modified Jeeps and Trucks." The ONLY
  per-trail writeup the park ever published; refers to it by number only.
- The 2014 `/blog/new-aop-trail-map` post is just a map-release announcement (no
  trail prose). Blog index across all Wayback snapshots confirms `aop-trail-96`
  was the sole per-trail post; everything else is race/event content.

That is the ceiling of freely-harvestable descriptions: **9 trails of ~120.**
The other ~110 have only a number + difficulty color on the map. To go further
needs the onX app (subscription, licensed) or the park directly.

## Curation authorization + curated catalog (2026-05-29)

The park team confirmed these names **match what is observed in the park**, and
this data is being assembled **for park use** (curate/refine freely, not taken
verbatim). That clears the `source_register` publish gate for assembly:
- Name provenance upgraded from "onX label" to **observed** (the onX text only
  corroborates names the park already uses). Per `ai_rules/verify_by_observation`.
- Curated catalog: **`website/data/aop_trail_catalog.json`** (schema
  `aop-trail-catalog-v1`) — the 9 trails with full data + named landmarks,
  structured as the authoring seed. Standalone for now (no per-trail geometry to
  match yet); wires into the POI/viewer once centerlines are digitized.
- Caveat kept per-row: the onX-derived description *text* is onX-copyright and
  must be **rewritten in the park's voice before any public publish** (the names
  and facts are fine; the prose is the licensed part).

## Status of follow-ups (was "Next steps")

- [DEAD END] Hardline Crawlers paper-map thread — 403 to scrapers; per user, not
  worth a manual visit.
- [DONE] Rendered the official SPA — numbers-only, no name data (see above).
- [DONE] Wayback sweep — numbers-only across all eras; 9 descriptions harvested.
- [OPEN] onX app (subscription) export, if license allows — only path to the
  full ~120 named set.
- [OPEN] Ask the park directly for a names list + republish permission (gates
  promotion out of `raw` — `northstar/source_register.md`).

## How the index was pulled

onX trail index pages are JS-rendered (WebFetch returns only chrome). The static
path is the sitemap: `onxmaps.com/offroad/sitemap_index.xml` →
`offroad-trails-sitemap*.xml` + `beginner-offroad-trails-sitemap*.xml`. Curl +
grep for `/trails/us/tennessee/<n>-<slug>` yielded 26 numbered TN trails; each
verified for park membership by fetching its page. Descriptions come from each
page's `og:description` meta tag (full prose, no JS render needed).
