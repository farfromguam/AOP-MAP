# Source Register

TL;DR:
- Every imported, traced, drawn, or submitted feature needs source provenance.
- Permission and confidence travel with the feature all the way to print and web export.
- `raw`, `core`, and `publish` are separate zones because inspection material is not automatically publishable material.

#aop #sources #provenance #publishing

-----

The risky part is not drawing trails. The risky part is knowing which trails are true, which are useful guesses, and which are not ours to publish.

## Required source fields

Each source should carry:

- `name`
- `source_type`
- `url_or_contact`
- `retrieved_on`
- `license_or_permission`
- `publish_status`
- `confidence_default`
- `notes`

Each feature-source link should carry:

- `feature_id`
- `source_id`
- `claim`
- `confidence`
- `last_checked`
- `review_status`
- `notes`

A single scalar `source` field is not enough. One trail can be supported by an official map, a RiderPlanet point, imagery, hillshade, and a field GPX. The map needs to preserve that stack, not collapse it.

## Data zones

`raw` is for imported and inspection material: parcels, GPX, image traces, app checks, source captures.

`core` is the edited working map.

`publish` is only what is explicitly safe for print and web.

Movement from `raw` to `core` is review. Movement from `core` to `publish` is permission plus confidence.

## Publish rule

If a feature has unknown permission, it does not publish.

If a feature has low confidence, it can publish only when visibly labeled as candidate or unverified.

If a feature is field-use critical, uncertainty must stay visible. A clean-looking wrong line is worse than an honest candidate line.
