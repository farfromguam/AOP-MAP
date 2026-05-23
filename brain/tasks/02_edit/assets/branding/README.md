# Sprint 02 Branding Asset Drop

Retrieved on 2026-05-23 for Sprint 02 Bucket F: AOP logo + Rock Warblers logo.

These are staged as raw/source assets. AOP logo reuse still needs AOP
confirmation. Rock Warblers logo reuse is cleared for this project by the
user-stated rights holder.

## Files

| File | Source | Size | SHA-256 | Publish status |
| --- | --- | ---: | --- | --- |
| `raw/aop-badge-official-site-2026-05-23.png` | `https://adventureoffroadpark.com/favicon.png` | 1000x1000 PNG, 140165 bytes | `bf7b842dbd6cc5428313f5b37aee5ca4ea2590675b21f2607eae3b0ecda53326` | Reference only until AOP confirms use |
| `raw/aop-wordmark-official-site-2026-05-23.png` | `https://adventureoffroadpark.com/assets/Adventure%20Off%20Road%20Park%20and%20Nature%20Center_1764622413285-C5NI7Kj4.png` | 854x231 PNG, 59191 bytes | `3c5e85ab41e8ff6bf082d5dc253920fd0ae0a56b4dcd99f5259f1c1d7ad16c72` | Reference only until AOP confirms use |
| `raw/rock-warblers-logo-facebook-event-2026-05-23.jpg` | Facebook event render for `https://www.facebook.com/events/adventure-offroad-park-nature-center/rock-warblers-trail-blazing-invitational/4541595172728436/` | 2048x1160 JPEG, 100679 bytes | `13848dba487d4a29a524feb54c8e00ed2f7194b24880e1d39f6b7bb736832a23` | Cleared for this AOP map project by Rock Warblers user grant |

## Source Notes

- AOP badge and wordmark came from the current `adventureoffroadpark.com` site
  bundle. The HTML references the badge as the favicon, and the React bundle
  references the wordmark as the nav logo.
- Exact-match web search for Rock Warblers found a public Facebook event:
  **Rock Warblers Trail Blazing Invitational**. The page metadata says it is a
  sports event in South Pittsburg by **Team Rock Warblers RC Rock Crawling** and
  Hilary Fryman on Friday, June 19, 2026.
- Facebook exposes `og:image` as
  `https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id=4541595172728436`.
  The direct `scontent` CDN URL resolved only through browser rendering and is
  session-bound, so the event URL and media id are the durable source handles.
- Permission update, 2026-05-23: user stated, "we have permission from the Rock
  Warblers. I am them." Treat the Rock Warblers logo as usable for this AOP map
  project. Keep attribution/provenance with the asset.

## Next Checks

- Ask AOP for explicit reuse permission and, ideally, vector or transparent logo
  originals.
- Ask Rock Warblers for a transparent PNG or SVG original if a cleaner source
  asset is needed.
- Decide whether logos belong in viewer chrome, on-map as draggable logo
  overlays, or both. On-map placement should use the shared find + move primitive
  from `../poi_editor_v2.md`.
