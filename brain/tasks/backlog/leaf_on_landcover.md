# Leaf-on imagery for a crisper forest land-cover layer

Added: 2026-05-21
Status: DONE (2026-05-21) -- see Resolution below
Fit: V1 fit (quality improvement to a shipped V1 layer)

#aop #backlog #landcover #naip #imagery

-----

## The idea

Rebuild the forest land-cover layer (`website/data/aop_landcover.geojson`) from
leaf-on summer aerial imagery instead of the leaf-off NAIP 2021 ortho it ships
from today.

## Where it came from

The land-cover layer was built 2026-05-21 — see `tasks/01_mvp/landcover_layer.md`.
The only no-auth 4-band imagery available was NAIP 2021, acquired 2021-11-07:
partial leaf-off. Bare deciduous canopy lets brown litter show between
branches, so the classification had to be texture-based (canopy roughness),
and that caps forest-edge crispness at roughly a ~15 m softness floor. The
result is a clean, coherent stylized base — but the forest/clearing boundaries
are soft.

Leaf-on summer imagery (full canopy) would let NDVI — a crisp per-pixel signal
— drive the forest/non-forest split, giving sharp edges with no window blur and
a cleaner forest-vs-grass separation.

## What it would take

- Source leaf-on 4-band imagery for the AOP centre cell. Known option: NAIP
  2023, acquired 2023-06-09 (confirmed to cover the AOI — see
  `brain/output/aop_9_patch_data_acquisition_manifest.md`). It is *not* in the
  USGS `USGSNAIPImagery` ImageServer mosaic, and the TNM products API no longer
  serves NAIP downloads — so it needs an EarthExplorer login or the AWS
  `naip-source` requester-pays bucket. That auth friction is the real cost and
  the reason this is backlog, not done.
- Rerun `mvp/scripts/build_landcover.sh` against the new ortho. The classifier
  `classify_landcover.py` would shift from texture-led to NDVI-led; texture
  stays as the forest-vs-grass discriminator within the high-NDVI class.
  Tunables are already at the top of the script.
- Re-verify with `mvp/scripts/playwright_verify_landcover.py`.

## Fit with the northstar

The map promises trustworthy, source-traceable layers. A leaf-on rebuild is a
strict quality improvement to an existing V1 layer — same pipeline, same
provenance discipline, sharper output. Not urgent: the leaf-off layer is a
serviceable stylized base today. Pick this up when the EarthExplorer/AWS auth
friction is worth the crisper edges.

## Resolution (2026-05-21)

Done the same day. Leaf-on 2023 NAIP was adopted — the USDA `USDA_CONUS_PRIME`
ImageServer serves it with no EarthExplorer login, so the auth friction this
card worried about did not apply.

But the core premise here — that leaf-on NDVI would drive a crisp forest/open
edge — proved wrong. Leaf-on canopy is a smooth continuous blanket: neither
colour nor texture separates it from grass (the texture histogram is unimodal).
The leaf-off pipeline only worked because bare winter branches make extreme
texture. The crisp forest edge instead came from a **USGS 3DEP lidar
canopy-height model** — trees are tall, grass is not. Leaf-on NAIP is still
used, for the field colours.

Full detail: `tasks/01_mvp/landcover_layer.md` ("Update: lidar canopy-height
rebuild").
