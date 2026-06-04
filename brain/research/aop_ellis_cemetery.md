# AOP Ellis Cemetery — the hole in the park plot

TL;DR:
- The AOP working-envelope polygon has a literal interior ring — a hole — in parcel `110 008.00`.
- That hole is the Ellis Cemetery: Marion County parcel `110 008.04`, owner of record `BRYSON & ELLIS CEMETERY`, class `05 RELIGIOUS`, ~0.12 acre.
- It is an inholding: a family burying ground excepted out of the deed when the surrounding Ellis land became Adventure Off Road Park.
- Confirmed two ways — the cemetery parcel geometry is bit-identical to the hole ring, and a point query at the hole centroid returns exactly that parcel.

#aop #research #cemetery #parcels #inholding #ellis-cove

-----

## The finding

`website/data/publish.geojson` ships the AOP boundary as `AOP working parcel
envelope - included parcel candidates`, a MultiPolygon. Its first polygon has
two rings: an outer ring and one interior ring — a hole — at bbox
`-85.744114, 35.089462, -85.743621, 35.089580` (a 5-point ring, i.e. a
4-corner rectangle, ~45 m x 13 m).

That hole is the Ellis Cemetery.

This was raised when a USGenWeb cemetery transcription for "Ellis Cemetery,
Marion County, TN" was reviewed (see the full record below). Its driving
directions place it off Ellis Cove Road, just past the Battle Creek bridge —
inside the AOP land. The question was whether that cemetery is the hole in the
plot. It is.

## How it was confirmed (2026-05-21)

1. **Point query.** A point-in-polygon query against the Tennessee Comptroller
   Marion County parcel layer (`TN_County_Parcel_Map` FeatureServer layer 35)
   at the hole centroid `-85.7438675, 35.089521` returns exactly one parcel:
   - `Assessment_Data_58_ID`: `110 008.04`
   - `Assessment_Data_58_PARCELID`: `058 110    00804 000 2023`
   - `Assessment_Data_58_OWNER`: `BRYSON & ELLIS CEMETERY`
   - `Assessment_Data_58_CLASS`: `05 RELIGIOUS`
   - `Assessment_Data_58_ADDRESS`: `ELLIS COVE RD`
   - `Assessment_Data_58_DEEDAC`: `0`
2. **Geometry match.** Fetching parcel `110 008.04` with geometry returns a
   5-point polygon whose bbox is identical to the hole ring above. Computed
   area ~472 m2 = ~0.117 acre.
3. **Parcel lineage.** `110 008.04` is a `.04` sub-parcel of `110 008` — the
   parent being `110 008.00`, the AOP working-envelope parcel on `ELLIS COVE RD
   1040`. The cemetery is the carve-out; the park is the remainder.

This is a definitive match, not a hypothesis. The cemetery is an inholding:
the family burying ground was excepted out of the deed when the surrounding
Ellis land was sold. Tennessee keeps family cemeteries (and statutory access
to them) with the family even when the land around them changes hands.

Note on acreage: the two-parcel AOP envelope deed acres (`483.46` + `90`) are
recorded *excluding* the cemetery — the hole is correctly-missing land, not a
gap in the data. It does not by itself explain the unreconciled 600+ acre
official AOP claim.

## Cemeteries in the 9-patch

A query for cemetery-owned parcels (`OWNER LIKE '%CEMETERY%'`) across the
9-patch bbox returns four. Only Ellis is an AOP inholding; the other three are
nearby context. The family names echo the area's springs and creeks (Gilliam
Spring, Bible Spring, Tate Cove Creek in the hydrography layer).

| Parcel | Owner of record | Display name | Address | ~Acres | AOP inholding |
| --- | --- | --- | --- | ---: | --- |
| `110 008.04` | `BRYSON & ELLIS CEMETERY` | Ellis Cemetery | Ellis Cove Rd | 0.12 | yes |
| `093 029.00` | `CEMETERY GILLIAM` | Gilliam Cemetery | Goff-Payne Rd | 2.91 | no |
| `093 003.00` | `CEMETERY BIBLE` | Bible Cemetery | Battle Creek Rd | 0.74 | no |
| `093 001.02` | `CEMETERY TATE` | Tate Cemetery | Tate Cove Rd | 0.70 | no |

## Burial roster (Ellis Cemetery)

Transcribed in the USGenWeb record below: 12 markers, 9 named (all Ellis) and
3 unnamed infants. Latest burial Ross H. Ellis, 1981 — the plot was active
into the 1980s.

- Ross H. Ellis — 1890-1981
- Nathaniel Ellis — 1850-1920
- Martha Ellis — 1853-1935
- John Paul Ellis — Feb 27, 1933 - July 17, 1941
- David C. Ellis — 1886-1950
- Mary Ellen Ellis — 1881-1951
- Charles H. Ellis — Mar 11, 1884 - Sept 14, 1965
- Charles Ellis — 1933-1935
- Esther Ellis — 1893-1935
- Baby (unnamed infant) x3

## Sources

- **Parcel data:** Tennessee Comptroller of the Treasury — Marion County
  parcels, `TN_County_Parcel_Map` FeatureServer layer 35 (`Marion_Parcels`).
  Public record. Same service as the AOP boundary import.
- **Burial roster:** USGenWeb Archives, Marion County, TN cemeteries —
  transcription contributed by Leslie Paul Ellis. USGenWeb terms (below) allow
  free non-commercial use as long as the contributor notice travels with the
  data; they forbid reproduction for profit. **Publish decision (2026-06-03,
  owner): PUBLISHABLE — keep the roster in the served cemetery layer.** AOP is a
  non-commercial hobby-event map (`northstar/whats_this_for.md`), so the use falls
  inside USGenWeb's free-non-commercial grant; the contributor notice travels with
  the data (`burial_source` + `burial_terms` are baked onto every Ellis feature in
  `website/data/aop_cemeteries.geojson`), satisfying their hard requirement. The
  prior "community research, not publishable until settled" caveat is now resolved
  in favor of publishing. If AOP ever monetizes (paid handouts, sponsored print),
  re-open this against `northstar/source_register.md` before that export.

### USGenWeb record, retained verbatim

```
MARION COUNTY, TN - CEMETERIES - Ellis Cemetery
====================================================================
     USGENWEB NOTICE: In keeping with our policy of providing
         free information on the Internet, data may be used by
         non-commercial entities, as long as this message
         remains on all copied material. These electronic
         pages may NOT be reproduced in any format for profit
         or for presentation by other persons or organizations.

         Persons or organizations desiring to use this material
         for purposes other than stated above must obtain the
         written consent of the file contributor.

         The submitter has given permission to the USGenWeb Archives
         to store the file permanently for free access.

         This file was contributed for use in the USGenWeb
         Archives by: Leslie Paul Ellis  <stelmo4122@msn.com>
====================================================================

State: Tennessee
County: Marion
City: So. Pittsburg (Battle Creek Community)
Name of Cemetery: Ellis Cemetery

On I-24 between Chattanooga, TN and Nashville, TN, exit at Kimball,
Tennessee. Go to Kimball Crossing (shops, restaurants, motels). Turn left
onto Battle Creek Road (old Highway 41). Proceed about one and one-half
miles until you reach Ellis Road, a half-left turn. Go a short distance
and turn right at the first opportunity. Proceed until you come to Ellis
Cove Road (the sign may be out). It is the second road to the left. It is
paved. Continue on this road and cross the bridge across Battle Creek.
Proceed until you see what looks look like a wide path. It is driveable.
It leads to the cemetery.

Burials: Ross H. Ellis 1890-1981; Nathaniel Ellis 1850-1920; Martha Ellis
1853-1935; John Paul Ellis Feb 27, 1933-July 17, 1941; David C. Ellis
1886-1950; Mary Ellen Ellis 1881-1951; Charles H. Ellis Mar 11, 1884-Sept
14, 1965; Charles Ellis 1933-1935; Esther Ellis 1893-1935; three infants
recorded only as "Baby".
```

## Open questions

- The county owner of record is `BRYSON & ELLIS CEMETERY`. The USGenWeb
  transcription is Ellis-only. There may be a Bryson section, or two adjoining
  family plots — the viewer carries both names (`name` = Ellis Cemetery,
  `aka` = Bryson & Ellis Cemetery) until this is resolved.
- Whether the cemetery's statutory access route crosses AOP land, and what
  that means for park traffic near the Battle Creek bridge, is an AOP
  operational question, not a mapping one — flag for AOP.
- ~~Burial-roster publishability needs a `source_register` decision before the
  roster ships beyond the inspection viewer.~~ **RESOLVED 2026-06-03 (owner):
  publishable — keep shipping; non-commercial hobby use, contributor notice
  travels in-data. See the Sources section above. Re-open only if AOP monetizes.**

## Where this is wired

The cemeteries are a viewer layer — see `tasks/01_mvp/cemeteries_layer.md` and
the "Cemeteries Layer" section of `research/viewer.md`.
