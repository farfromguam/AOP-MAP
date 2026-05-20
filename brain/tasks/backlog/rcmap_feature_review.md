# rcmap.io Feature Review

rcmap.io is the place-catalog peer for AOP. RC drivers already use it to find spots like the one AOP is. This card pulls every visible feature from the site and decides what the AOP map should match, ignore, or beat.

This is not a "vendor with cool ideas" review. This is "what is our map up against in the RC crawling world today." Same tag set as the Scribblemaps card -- V1 / V2 / Internal / Out.

-----

## Source

- https://www.rcmap.io/ -- the catalog homepage.
- https://www.rcmap.io/places/the-kk-rc-trail -- an example place page.
- `./scribblemaps_feature_review.md` -- the prior backlog card. Same tag system.
- `../../northstar/map_northstar.md` -- the V1/V2 line we measure against.
- `../01_mvp/aop_south_pittsburg_map_build_card.md` -- the current build card.

Captured 2026-05-20.


## Per-place data

### Three-axis ratings: Fun / Access / Challenge
**Fit:** V1 fit. This is the established RC scale-trucking vocabulary. Use it on trail features and place pages instead of inventing a difficulty scheme. Confirm the axis definitions before printing them on the legend; "Access" in particular needs to mean the same thing on the AOP map as it does on rcmap.io or the rating is noise.

### Description, notes, additional instructions
**Fit:** V1 fit. Trail/place rows already need a notes field. The split between "notes" and "additional instructions" on rcmap.io is worth copying -- the second one is where rules, gate codes, etiquette, and seasonal info live.

### KMZ file attachment per place
**Fit:** V1 fit. RC drivers exchange KMZ already. The publish path should accept KMZ both as ingest into `raw` and as a downloadable attachment from the public trail/place page. Make sure the file carries provenance and a permission scope; we are not republishing third-party KMZs without consent.

### User pics
**Fit:** V2 fit. Photo submission is the contribution surface, not a publish surface. Treat user pics as observations attached to a place/trail, reviewed before they appear on the public map. Don't ship public photo upload before the validation loop is real.

### Submitter attribution
**Fit:** Internal fit. The source register already handles this on the staff side. No need to expose "added by Driver X" on the public viewer until accounts exist.

### Events section on the place page
**Fit:** V1 fit. The rcmap.io place page has a dedicated Events area. AOP hosts events (G6-style rallies, Pro-Line-style adventures, comp-class crawls), so the public AOP page should surface upcoming and past events the same way. See `./rc_event_mapping_backlog.md` for the underlying event-data shape.

### Category tag (Crawling / RC Track / RC Shop / Jet Boating / Other)
**Fit:** V1 fit, narrow. AOP itself is a multi-category place (trails + parking/staging + shop/store if any). The print legend and the website filter should let a visitor say "show me crawling, hide the staging icons." Don't import rcmap.io's whole taxonomy; pick the categories AOP actually has.

### Address + Google Maps link
**Fit:** V1 fit. Trivial to add to the public map's "About AOP" panel. The handoff is to send people to AOP from the map, not to replace driving directions.


## Place actions

### Add to Favorites
**Fit:** V2 fit. Requires accounts. Park.

### Check-in to indicate attendance
**Fit:** V2 fit. Cute social signal; not load-bearing for a trustworthy map. Park until the loop earns it.

### Rate the place
**Fit:** V1 fit, with a constraint. Park-level rating (Fun/Access/Challenge) is fine to show on the public AOP page from internal sources. Public submission of ratings is V2.

### Submit photos
**Fit:** V2 fit. Same answer as User pics above.

### Report issues / suggest edits
**Fit:** V2 fit. This is the rcmap.io flavor of an observation queue. The right shape for AOP is identical -- a "tell us this is wrong" path that lands in the same review queue as board marks. Build it when the loop is proven.


## Catalog-level features

### Search across places
**Fit:** Out for AOP map. We are not building a multi-park catalog. AOP is the place.

### Geolocation snap-to-map
**Fit:** V1 fit (small). On the public viewer, "find me" is cheap and helpful for visitors physically at AOP. Skip on the print map for obvious reasons.

### Leaderboard
**Fit:** Out for V1. Gamification belongs in the activity-tracker peer (Scaletra), not in a park map.

### Giveaways
**Fit:** Out. Marketing surface, not map surface.

### Facebook group cross-link (2000+ members)
**Fit:** Out for the map. Worth a single link on the About panel if AOP wants it; not a feature.


## Platform

### iOS app
**Fit:** V2 fit. The static MapLibre viewer on a phone browser covers V1. A native app is a V2+ question and not on the table yet.


## Things this review intentionally does not turn into work

- A multi-park catalog. AOP is one place; we are not building rcmap.io.
- Public photo upload before the loop is proven.
- Leaderboards or trophies on the AOP map. If those exist anywhere in the AOP world, they live in Scaletra.
- A custom mobile app before the static viewer is shipped.


## What to do with this card

- Land the **V1 fit** items as small additions on the active build card during normal work: Fun/Access/Challenge axes, KMZ attachment + ingest, notes-vs-instructions split, geolocation, address panel.
- Keep the **V2 fit** items in mind when sketching the validation-loop intake UI later: ratings, photos, check-ins, edit-suggestions all share one queue.
- Leave the **Out** items in place. The point is to remember we said no.
