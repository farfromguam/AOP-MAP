# Scaletra Feature Review

Scaletra is the activity-tracking peer for AOP. It is the app an RC driver runs *while at* AOP. Where rcmap.io is the place catalog, Scaletra is the run recorder -- a Strava-for-scale-trucking.

That puts Scaletra in a different relationship to the AOP map than Scribblemaps or rcmap.io. We are not trying to be Scaletra. We are asking: which of its outputs should we ingest, which of its patterns should our public map mirror, and which are driver-side concerns we don't touch.

-----

## Source

- https://www.scaletra.com/ -- the marketing surface.
- https://support.scaletra.com/ -- the support index, where the real feature list lives.
- https://support.scaletra.com/activities-challenges-and-trophies/44N1tQRH1L1pgHJfmzYgjf/photo-waypoints/45FW8Zm4UodCR2SYu8tm7A -- photo waypoints help article.
- `./scribblemaps_feature_review.md` and `./rcmap_feature_review.md` -- prior backlog cards.

Captured 2026-05-20.


## Activity recording

### GPS track recording during a run
**Fit:** V2 fit (as ingest, not as our own recorder). The AOP map should not try to be a recording app. It should be the place where a finished Scaletra activity (or other GPX) lands as an observation. Open backlog research: does Scaletra publish activities anywhere we can read them, or is the ingest path "driver exports GPX and uploads"?

### Auto-pause, gray-line prevention, battery optimization, lock-screen notifications
**Fit:** Out. These are driver-side recording quality concerns. Not our problem; not our surface.

### Edit / crop activity after recording
**Fit:** V2 fit. If we ingest activities as observations, the driver should be able to trim a run before submitting -- but we lift that on top of whatever they already did in Scaletra, not duplicate it. Keep this as a note for the V2 intake design.

### Offline mode
**Fit:** V2 candidate, same as the Scribblemaps note. Means offline PMTiles for the public viewer so a phone keeps the AOP map alive without signal. Real work, real value, park until V1 is shipped.


## Photo waypoints

### Photos anchored as waypoints on the activity GPS track
**Fit:** V2 fit, high signal. This is the natural shape for capturing field reports: a run with a few photos at the points worth noting. It maps cleanly onto board-photo transcription, hazard reports, and "what changed" submissions. When the V2 intake gets designed, this is the model -- not a separate "submit a photo" form.


## Vehicles / garage

### Virtual garage with vehicle profiles, sort/filter, deletion
**Fit:** Out for the AOP map. Vehicles belong to the driver, not to the park. If a future AOP intake form wants "which truck did you run?" as an optional tag, fine -- but we don't build a garage.


## Challenges, trophies, rewards

### Challenge participation, withdrawal, digital trophies, coupons
**Fit:** Out for V1, V2 candidate (narrow). If AOP runs an event series, a "completed AOP loop" trophy issued by Scaletra is something the user could ask Scaletra for, not something we build. The AOP map's job is to be trustworthy, not to be a game.


## Social

### Fistbumps, comments, follow drivers, fistbump photos
**Fit:** Out. Driver-to-driver social belongs in Scaletra. Not the map's surface.

### Block, hide, report, unfollow
**Fit:** Out, same reason.

### Share to social media
**Fit:** V1 fit (small). Trail/place pages on the public viewer should have proper Open Graph and Twitter card metadata so a shared link previews nicely. Cheap and useful.


## Privacy / visibility

### "Hide My Map", visibility scopes (public / friends / private)
**Fit:** V1 fit, conceptually. This is the same model AOP already uses on the `permission` field (`public`, `internal`, etc.). Worth naming the alignment explicitly so when an AOP staff member sees "public / friends / private" in Scaletra, the mental model already matches our `permission` vocabulary. No code change -- a docs/voice item.


## Account / auth

### OTP auth, password reset, account deletion, email change
**Fit:** V2 fit. Standard account plumbing for when V2 intake is built. Don't reinvent this.


## Automated checks

### Overspeeding detection
**Fit:** Out. Driver-side concern, not park-map data. Interesting only as evidence that Scaletra is doing automated validation on activity data -- which is a hint for our own observation review when we get there.

### Data aggregation
**Fit:** Research note, not work. If Scaletra is aggregating activity data at AOP, that's something AOP themselves might want to know about. Park as an open question.


## Cross-product question worth keeping open

If Scaletra activities at AOP exist in the wild already, then the AOP map has two paths into ingest before V2 even ships:

1. Drivers export GPX from Scaletra and hand it to AOP staff for review.
2. Scaletra exposes activity data we can read (public profiles, public activities, an API).

Neither path requires us to build a recorder. Both feed the same observation queue. This is worth a small research card under `research/` -- "what can we get out of Scaletra, and under what terms" -- before we design V2 intake.


## What to do with this card

- Treat Scaletra as **upstream data**, not as a competitor surface. Our map sits downstream of activities recorded there, the same way it sits downstream of board marks and field GPX.
- The single most relevant pattern to mirror is **photo waypoints on a track**. When V2 intake is designed, start from that shape.
- Open a small research card on Scaletra ingest options before we commit to a V2 intake design.
- Everything tagged **Out** stays out. The map is not a fitness app, not a social network, and not a game.
