#!/usr/bin/env python3
"""Classify a NAIP 4-band ortho into the AOP land-cover map.

Reads a 4-band (R, G, B, NIR) NAIP GeoTIFF and writes a single-band class
raster plus a colorized PNG preview. The output is a full coverage: every
valid pixel gets exactly one of five land-cover classes.

  1 forest_deciduous   bare-canopy hardwood -- the bulk of the woods
  2 forest_evergreen   conifer / needleleaf -- the darker, denser tree shade
  3 open_grass         vigorous open vegetation (pasture, mown grass)
  4 open_meadow        dry / dormant open vegetation
  5 open_bare          bare ground -- soil, dirt, gravel

Two stages.

1. Forest vs open. Forest is a neighbourhood-scale land cover, not a pixel
   property. The NAIP here is early-November (partial leaf-off): bare
   deciduous canopy lets brown litter show between branches, so a single
   0.6 m pixel flips noisily between "rough" and "bare". So canopy roughness
   is measured as a *field* -- local NIR std-dev, then a low-pass pass over
   that std-dev -- giving a smooth forest score that is uniformly high inside
   woods and uniformly low over fields. Otsu thresholds it per image; the
   mask is then cleaned morphologically (closing fills canopy-gap holes,
   opening drops stray specks).

2. Sub-classes by vegetation vigour. NDVI = (NIR - R) / (NIR + R). NDVI is
   useless for forest-vs-open in leaf-off (bare hardwood canopy NDVI collapses
   toward bare ground), but it is exactly the right signal *within* each zone:
     - Inside the forest mask, conifers keep their needles and stay
       photosynthetically active in November, so evergreen reads as high NDVI
       against the low-NDVI bare hardwood canopy.
     - Inside the open mask, NDVI ranks ground by greenness: lush pasture
       high, dormant grass mid, bare soil low.
   NDVI is low-passed into a smooth field and split with Otsu so each
   sub-class is a coherent region, not pixel speckle; a light morphological
   pass tidies the sub-class edges.

Honest limit: the open-ground split is a *relative* greenness ranking within
this one leaf-off image, not absolute crop identification. Leaf-on summer
imagery would make it -- and the forest edges -- far crisper; see
tasks/backlog/leaf_on_landcover.md.

Pure numpy + GDAL bindings; box filters use summed-area tables (no scipy).

Classes: 0 nodata, 1 forest_deciduous, 2 forest_evergreen, 3 open_grass,
4 open_meadow, 5 open_bare.
"""
import sys
import numpy as np
from osgeo import gdal

gdal.UseExceptions()

NODATA = 0
FOREST_DECIDUOUS, FOREST_EVERGREEN = 1, 2
OPEN_GRASS, OPEN_MEADOW, OPEN_BARE = 3, 4, 5

CLASS_NAMES = {
    FOREST_DECIDUOUS: "forest_deciduous",
    FOREST_EVERGREEN: "forest_evergreen",
    OPEN_GRASS: "open_grass",
    OPEN_MEADOW: "open_meadow",
    OPEN_BARE: "open_bare",
}

# Muted Earth preview palette -- matches the viewer's fill colours so the PNG
# preview reads the same as the shipped map.
CLASS_RGB = {
    NODATA: (255, 255, 255),
    FOREST_DECIDUOUS: (185, 194, 163),  # #b9c2a3 muted sage
    FOREST_EVERGREEN: (127, 140, 102),  # #7f8c66 darker conifer green
    OPEN_GRASS: (207, 212, 176),        # #cfd4b0 pale sage
    OPEN_MEADOW: (220, 207, 163),       # #dccfa3 warm khaki
    OPEN_BARE: (205, 186, 143),         # #cdba8f ochre tan
}

# Window radii are pixel counts tuned at REF_PX_M. main() rescales every
# radius to the ortho's actual pixel size so the *metric* window is held
# constant -- the park build feeds a 0.6 m ortho, the 9-patch build a coarser
# ~1.5 m one. At REF_PX_M the scale is 1.0 and the radii are unchanged.
REF_PX_M = 0.60             # reference pixel size the radii below were tuned at
TEXTURE_RADIUS = 6          # local NIR std-dev window (~7.5 m at 0.6 m px)
FOREST_SMOOTH_RADIUS = 5    # low-pass over the std-dev field -> coherent score
CLOSE_RADIUS = 16           # fill canopy-gap holes up to ~20 m across
OPEN_RADIUS = 7             # drop forest specks smaller than ~9 m
FOREST_NDVI_RADIUS = 30     # within-forest NDVI low-pass -> conifer stands
OPEN_NDVI_RADIUS = 7        # within-open NDVI low-pass -> field vigour
FOREST_CLEAN_RADIUS = 16    # consolidate evergreen stipple into real stands
OPEN_CLEAN_RADIUS = 4       # light tidy of open-ground sub-class specks
EVERGREEN_PERCENTILE = 80   # evergreen = the high-NDVI tail of the forest
PREVIEW_STRIDE = 4          # downsample factor for the PNG preview


def summed_area(a):
    """2-D cumulative-sum table padded with a zero row/column."""
    sat = np.zeros((a.shape[0] + 1, a.shape[1] + 1), dtype=np.float64)
    sat[1:, 1:] = np.cumsum(np.cumsum(a, axis=0, dtype=np.float64), axis=1)
    return sat


def box_sum(a, r):
    """Sum over a (2r+1) square window, edge-clamped. Returns (sum, count)."""
    sat = summed_area(a)
    h, w = a.shape
    ys, xs = np.arange(h), np.arange(w)
    y0, y1 = np.clip(ys - r, 0, h), np.clip(ys + r + 1, 0, h)
    x0, x1 = np.clip(xs - r, 0, w), np.clip(xs + r + 1, 0, w)
    s = (sat[y1[:, None], x1[None, :]] - sat[y0[:, None], x1[None, :]]
         - sat[y1[:, None], x0[None, :]] + sat[y0[:, None], x0[None, :]])
    cnt = (y1 - y0)[:, None] * (x1 - x0)[None, :]
    return s, cnt


def box_mean(a, r):
    s, cnt = box_sum(a, r)
    return s / cnt


def masked_box_mean(a, mask, r):
    """Box mean of `a` over only the `mask` pixels in each window.

    Used to low-pass a field *within* one land-cover zone without bleeding
    values across the zone boundary. NaN where a window holds no mask pixel.
    """
    num = box_sum(a * mask, r)[0]
    den = box_sum(mask, r)[0]
    out = np.full(a.shape, np.nan, dtype=np.float64)
    nz = den > 0
    out[nz] = num[nz] / den[nz]
    return out


def dilate(mask, r):
    """Binary dilation by a (2r+1) square."""
    return box_sum(mask.astype(np.float64), r)[0] > 0.5


def erode(mask, r):
    """Binary erosion by a (2r+1) square."""
    return box_sum((~mask).astype(np.float64), r)[0] < 0.5


def closing(mask, r):
    """Fill holes / gaps smaller than the structuring element."""
    return erode(dilate(mask, r), r)


def opening(mask, r):
    """Drop specks smaller than the structuring element."""
    return dilate(erode(mask, r), r)


def tidy(mask, r):
    """Close then open a sub-class mask so it reads as coherent regions."""
    return opening(closing(mask, r), r)


def otsu(values):
    """Otsu's bimodal threshold on a 1-D float array."""
    v = values[np.isfinite(values)]
    if v.size == 0:
        return 0.0
    hist, edges = np.histogram(v, bins=256)
    hist = hist.astype(np.float64)
    total = hist.sum()
    if total == 0:
        return float(np.median(v))
    p = hist / total
    mids = (edges[:-1] + edges[1:]) / 2.0
    omega = np.cumsum(p)
    mu = np.cumsum(p * mids)
    mu_t = mu[-1]
    denom = omega * (1.0 - omega)
    denom[denom == 0] = 1e-12
    sigma_b = (mu_t * omega - mu) ** 2 / denom
    return float(mids[int(np.nanargmax(sigma_b))])


def pct(a, q):
    return float(np.percentile(a[np.isfinite(a)], q))


def share(mask, base):
    """Percentage of `base` pixels that are also in `mask`."""
    b = int(base.sum())
    return 100.0 * int((mask & base).sum()) / b if b else 0.0


def write_preview(cls, path):
    sub = cls[::PREVIEW_STRIDE, ::PREVIEW_STRIDE]
    h, w = sub.shape
    rgb = np.zeros((3, h, w), dtype=np.uint8)
    for value, (r, g, b) in CLASS_RGB.items():
        mask = sub == value
        rgb[0][mask], rgb[1][mask], rgb[2][mask] = r, g, b
    mem = gdal.GetDriverByName("MEM").Create("", w, h, 3, gdal.GDT_Byte)
    for i in range(3):
        mem.GetRasterBand(i + 1).WriteArray(rgb[i])
    gdal.GetDriverByName("PNG").CreateCopy(path, mem)


def main():
    in_tif, out_tif, preview_png = sys.argv[1], sys.argv[2], sys.argv[3]
    ds = gdal.Open(in_tif)
    geo, proj = ds.GetGeoTransform(), ds.GetProjection()
    bands = [ds.GetRasterBand(i + 1).ReadAsArray().astype(np.float32)
             for i in range(4)]
    red, green, blue, nir = bands
    h, w = red.shape
    print(f"==> NAIP ortho {w} x {h} px, 4 bands")

    # Hold the metric window constant across ortho resolutions: the projection
    # is metric (EPSG:26916), so geo[1] is the pixel size in metres.
    px_m = abs(geo[1]) or REF_PX_M
    scale = REF_PX_M / px_m
    tex_r = max(1, round(TEXTURE_RADIUS * scale))
    smooth_r = max(1, round(FOREST_SMOOTH_RADIUS * scale))
    close_r = max(1, round(CLOSE_RADIUS * scale))
    open_r = max(1, round(OPEN_RADIUS * scale))
    forest_ndvi_r = max(1, round(FOREST_NDVI_RADIUS * scale))
    open_ndvi_r = max(1, round(OPEN_NDVI_RADIUS * scale))
    forest_clean_r = max(1, round(FOREST_CLEAN_RADIUS * scale))
    open_clean_r = max(1, round(OPEN_CLEAN_RADIUS * scale))
    print(f"==> pixel size {px_m:.2f} m, radius scale {scale:.2f} "
          f"(texture {tex_r}, smooth {smooth_r}, close {close_r}, "
          f"open {open_r}, forest-ndvi {forest_ndvi_r}, "
          f"open-ndvi {open_ndvi_r}, forest-clean {forest_clean_r}, "
          f"open-clean {open_clean_r})")

    nodata = (red == 0) & (green == 0) & (blue == 0) & (nir == 0)
    valid = ~nodata

    # --- Stage 1: forest vs open ------------------------------------------
    # canopy roughness as a smooth field: local NIR std-dev, then a low-pass
    # pass so within-canopy speckle resolves to a coherent forest score
    mean_nir = box_mean(nir, tex_r)
    mean_sq = box_mean(nir * nir, tex_r)
    texture = np.sqrt(np.maximum(mean_sq - mean_nir * mean_nir, 0.0))
    forest_score = box_mean(texture, smooth_r)

    forest_thr = otsu(forest_score[valid])
    print(f"==> forest score: p10={pct(forest_score[valid],10):.1f} "
          f"p50={pct(forest_score[valid],50):.1f} "
          f"p90={pct(forest_score[valid],90):.1f} "
          f"-> Otsu forest threshold {forest_thr:.2f}")

    forest = valid & (forest_score > forest_thr)
    raw_pct = 100.0 * forest.sum() / valid.sum()

    # morphological cleanup: close canopy-gap holes, then drop forest specks
    forest = closing(forest, close_r)
    forest = opening(forest, open_r)
    forest &= valid
    open_ = valid & ~forest
    print(f"==> forest cover: {raw_pct:.1f}% raw -> "
          f"{100.0 * forest.sum() / valid.sum():.1f}% "
          f"after close({close_r})/open({open_r})")

    # --- Stage 2: sub-classes by vegetation vigour ------------------------
    # NDVI = (NIR - R)/(NIR + R), low-passed *within* each zone (masked box
    # mean) so the forest/open edge does not bleed across the split.
    denom = nir + red
    denom[denom == 0] = 1e-6
    ndvi = (nir - red) / denom
    forest_f = forest.astype(np.float64)
    open_f = open_.astype(np.float64)

    # forest: evergreen is the high-NDVI tail. Conifers keep their needles in
    # November and stay green where bare hardwood canopy does not. Leaf-off
    # hardwood NDVI is pixel-noisy, so NDVI is low-passed hard over a stand-
    # scale window; evergreen is then the top EVERGREEN_PERCENTILE% -- a
    # coherent minority accent, not a 50/50 Otsu coin flip that confetti-
    # speckles the woods.
    ndvi_forest = masked_box_mean(ndvi, forest_f, forest_ndvi_r)
    ever_thr = (float(np.percentile(ndvi_forest[forest], EVERGREEN_PERCENTILE))
                if forest.any() else 1.0)
    evergreen = tidy(forest & (ndvi_forest > ever_thr), forest_clean_r) & forest
    deciduous = forest & ~evergreen
    print(f"==> forest split: NDVI p{EVERGREEN_PERCENTILE} {ever_thr:.3f} -> "
          f"evergreen {share(evergreen, forest):.1f}% / "
          f"deciduous {share(deciduous, forest):.1f}% of forest")

    # open: NDVI ranks open ground by greenness. Two Otsu cuts -> bare (low),
    # meadow (mid), grass (high). Open ground is far less pixel-noisy than
    # leaf-off canopy, so a field-scale smooth is enough.
    ndvi_open = masked_box_mean(ndvi, open_f, open_ndvi_r)
    bare_thr = otsu(ndvi_open[open_])
    bare = tidy(open_ & (ndvi_open <= bare_thr), open_clean_r) & open_
    vegetated = open_ & ~bare
    grass_thr = otsu(ndvi_open[vegetated])
    grass = tidy(vegetated & (ndvi_open > grass_thr), open_clean_r) & vegetated
    meadow = vegetated & ~grass
    print(f"==> open split: bare Otsu {bare_thr:.3f}, grass Otsu "
          f"{grass_thr:.3f} -> grass {share(grass, open_):.1f}% / "
          f"meadow {share(meadow, open_):.1f}% / "
          f"bare {share(bare, open_):.1f}% of open")

    cls = np.zeros((h, w), dtype=np.uint8)
    cls[deciduous] = FOREST_DECIDUOUS
    cls[evergreen] = FOREST_EVERGREEN
    cls[grass] = OPEN_GRASS
    cls[meadow] = OPEN_MEADOW
    cls[bare] = OPEN_BARE

    out = gdal.GetDriverByName("GTiff").Create(
        out_tif, w, h, 1, gdal.GDT_Byte, options=["COMPRESS=LZW"])
    out.SetGeoTransform(geo)
    out.SetProjection(proj)
    band = out.GetRasterBand(1)
    band.WriteArray(cls)
    band.SetNoDataValue(0)
    out.FlushCache()

    write_preview(cls, preview_png)
    print(f"==> wrote {out_tif} and preview {preview_png}")


if __name__ == "__main__":
    main()
