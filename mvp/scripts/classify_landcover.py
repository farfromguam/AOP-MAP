#!/usr/bin/env python3
"""Classify a NAIP 4-band ortho into the AOP land-cover map.

Reads a 4-band (R, G, B, NIR) NAIP GeoTIFF and writes a single-band class
raster plus a colorized PNG preview. The output is a full coverage: every
valid pixel gets exactly one of five land-cover classes.

  1 forest_deciduous   bright leaf-on hardwood canopy -- the bulk of the woods
  2 forest_evergreen   conifer / needleleaf -- the darker, denser tree shade
  3 open_grass         the greenest open-ground colour cluster
  4 open_meadow        the mid open-ground colour cluster
  5 open_bare          the brownest open-ground colour cluster

This pipeline expects LEAF-ON summer imagery (USDA NAIP 2023, acquired June,
full canopy). Leaf-on is what makes the *sub-class* work meaningful: the
fields hold real, separable colours and conifer stands read distinctly
against leaf-on hardwood. See tasks/01_mvp/landcover_layer.md.

The method mirrors the manual Illustrator workflow it replaces -- separate the
trees off the fields, then posterise the remaining ground into a few field
colours -- but runs it automatically and reproducibly.

Two stages.

1. Forest vs open -- canopy texture. Tree canopy is rough (sunlit crowns next
   to deep inter-crown shadow), open ground is smooth; this holds in any
   season and does not depend on canopy brightness, which is unreliable
   (leaf-on crowns in full sun are bright, not dark). Roughness is the local
   NIR standard deviation, low-passed into a coherent forest score, then
   Otsu-thresholded and tidied with a morphological closing/opening. Because
   texture is a neighbourhood property, the forest edge carries an inherent
   softness of about one window width -- imagery alone cannot place a canopy
   edge per-pixel; a lidar canopy-height model is the crisp alternative.

2. Sub-classes.
     - Forest split: evergreen is the darkest tail of the canopy (conifers
       read darker than leaf-on hardwood), measured as a stand-scale smoothed
       darkness field and cut at a percentile so it stays a coherent accent.
     - Open split: k-means colour quantisation. Every open-ground pixel's RGB
       colour is clustered into N_OPEN_CLUSTERS groups; a majority filter
       consolidates the per-pixel labels into contiguous solid fields. The
       clusters are ranked by greenness onto open_grass / open_meadow /
       open_bare. This is the "fields are one of a few grass colours" step.

Honest limit: the open-ground split is a relative colour ranking within one
image, not absolute crop identification, and k-means is unsupervised so the
cluster boundaries follow whatever colour spread the scene happens to have.

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
REF_PX_M = 0.60               # reference pixel size the radii below were tuned at
TEXTURE_RADIUS = 16           # local NIR std-dev window -- spans several crowns
FOREST_SMOOTH_RADIUS = 8      # low-pass the roughness into a coherent forest score
CLOSE_RADIUS = 8              # fill canopy-gap holes
OPEN_RADIUS = 5               # drop forest/field specks
FOREST_DARK_RADIUS = 30       # stand-scale smooth of canopy darkness -> conifer
FOREST_CLEAN_RADIUS = 16      # consolidate evergreen stipple into real stands
EVERGREEN_PERCENTILE = 78     # evergreen = the darkest tail of the canopy
OPEN_PRESMOOTH_RADIUS = 2     # light colour denoise before k-means
OPEN_MAJORITY_RADIUS = 10     # field-scale majority vote -> contiguous solids
N_OPEN_CLUSTERS = 3           # open-ground colour clusters (maps to the 3 open
                              # classes; >3 needs new classes + viewer entries)
KMEANS_SAMPLE = 60000         # pixels sampled to fit the k-means centroids
KMEANS_ITERS = 25             # Lloyd's iterations
KMEANS_SEED = 0               # deterministic init so the build is reproducible
PREVIEW_STRIDE = 4            # downsample factor for the PNG preview


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


def kmeans(features, k, iters, seed):
    """Lloyd's k-means on an (N, D) float array. Returns (labels, centroids).

    Deterministic: a fixed seed picks the initial centroids so a rebuild is
    byte-reproducible.
    """
    n = features.shape[0]
    rng = np.random.default_rng(seed)
    cent = features[rng.choice(n, size=k, replace=False)].copy()
    labels = np.full(n, -1, dtype=np.int32)
    for _ in range(iters):
        new = assign(features, cent)
        if np.array_equal(new, labels):
            break
        labels = new
        for j in range(k):
            m = labels == j
            if m.any():
                cent[j] = features[m].mean(axis=0)
    return labels, cent


def assign(features, cent):
    """Nearest-centroid label for each row of `features` (memory-light loop)."""
    best = np.zeros(features.shape[0], dtype=np.int32)
    best_d = None
    for j in range(cent.shape[0]):
        d = ((features - cent[j]) ** 2).sum(axis=1)
        if best_d is None:
            best_d = d
        else:
            m = d < best_d
            best[m] = j
            best_d[m] = d[m]
    return best


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
    print(f"==> NAIP ortho {w} x {h} px, 4 bands (leaf-on workflow)")

    # Hold the metric window constant across ortho resolutions: the projection
    # is metric (EPSG:26916), so geo[1] is the pixel size in metres.
    px_m = abs(geo[1]) or REF_PX_M
    scale = REF_PX_M / px_m
    tex_r = max(1, round(TEXTURE_RADIUS * scale))
    smooth_r = max(1, round(FOREST_SMOOTH_RADIUS * scale))
    close_r = max(1, round(CLOSE_RADIUS * scale))
    open_r = max(1, round(OPEN_RADIUS * scale))
    dark_r = max(1, round(FOREST_DARK_RADIUS * scale))
    forest_clean_r = max(1, round(FOREST_CLEAN_RADIUS * scale))
    presmooth_r = max(1, round(OPEN_PRESMOOTH_RADIUS * scale))
    majority_r = max(1, round(OPEN_MAJORITY_RADIUS * scale))
    print(f"==> pixel size {px_m:.2f} m, radius scale {scale:.2f} "
          f"(texture {tex_r}, smooth {smooth_r}, close {close_r}, "
          f"open {open_r}, dark {dark_r}, forest-clean {forest_clean_r}, "
          f"presmooth {presmooth_r}, majority {majority_r})")

    nodata = (red == 0) & (green == 0) & (blue == 0) & (nir == 0)
    valid = ~nodata

    # --- Stage 1: forest vs open -- canopy texture ------------------------
    # Tree canopy is rough (sunlit crowns beside deep inter-crown shadow),
    # open ground is smooth. Roughness = local NIR std-dev; that is patchy
    # within a single crown, so it is low-passed into a coherent forest score
    # that reads uniformly high over woods and uniformly low over fields.
    # Otsu thresholds it; a morphological close/open tidies holes and specks.
    # Texture is a neighbourhood signal, so the forest edge carries an
    # inherent softness of roughly one window width -- the cost of detecting
    # canopy from imagery alone (a lidar height model would be crisp).
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
    forest = closing(forest, close_r)
    forest = opening(forest, open_r)
    forest &= valid
    open_ = valid & ~forest
    print(f"==> forest cover: {raw_pct:.1f}% raw -> "
          f"{100.0 * forest.sum() / valid.sum():.1f}% "
          f"after close({close_r})/open({open_r})")

    # NDVI -- used only to rank the open colour clusters by greenness below.
    denom = nir + red
    denom[denom == 0] = 1e-6
    ndvi = (nir - red) / denom

    # --- Stage 2a: forest split -- evergreen is the darkest canopy --------
    # Conifers read darker than leaf-on hardwood. Darkness is smoothed over a
    # stand-scale window so the split is coherent stands, not pixel stipple;
    # evergreen is then the darkest EVERGREEN_PERCENTILE tail.
    brightness = (red + green + blue) / 3.0
    forest_f = forest.astype(np.float64)
    darkness = 255.0 - brightness
    dark_forest = masked_box_mean(darkness, forest_f, dark_r)
    ever_thr = (float(np.percentile(dark_forest[forest], EVERGREEN_PERCENTILE))
                if forest.any() else 1e9)
    evergreen = tidy(forest & (dark_forest > ever_thr), forest_clean_r) & forest
    deciduous = forest & ~evergreen
    print(f"==> forest split: darkness p{EVERGREEN_PERCENTILE} {ever_thr:.1f} "
          f"-> evergreen {share(evergreen, forest):.1f}% / "
          f"deciduous {share(deciduous, forest):.1f}% of forest")

    # --- Stage 2b: open split -- k-means colour quantisation --------------
    # Posterise the open ground into N_OPEN_CLUSTERS colours, the automated
    # form of "pull the fields out as a few grass colours". A light masked
    # colour denoise runs first; the per-pixel labels are then majority-voted
    # over a field-scale window so each field reads as a contiguous solid.
    open_f = open_.astype(np.float64)
    rs = masked_box_mean(red, open_f, presmooth_r)
    gs = masked_box_mean(green, open_f, presmooth_r)
    bs = masked_box_mean(blue, open_f, presmooth_r)
    feat = np.stack([rs[open_], gs[open_], bs[open_]], axis=1) / 255.0

    n_open = feat.shape[0]
    if n_open >= N_OPEN_CLUSTERS:
        sample = feat
        if n_open > KMEANS_SAMPLE:
            rng = np.random.default_rng(KMEANS_SEED)
            sample = feat[rng.choice(n_open, KMEANS_SAMPLE, replace=False)]
        _, cent = kmeans(sample, N_OPEN_CLUSTERS, KMEANS_ITERS, KMEANS_SEED)
        labels = assign(feat, cent)

        # majority-vote the per-pixel labels into contiguous fields
        lab_img = np.full((h, w), -1, dtype=np.int32)
        lab_img[open_] = labels
        counts = np.stack(
            [box_sum((lab_img == j).astype(np.float64), majority_r)[0]
             for j in range(N_OPEN_CLUSTERS)], axis=0)
        maj = np.argmax(counts, axis=0)

        # rank clusters by greenness (mean NDVI of their majority pixels):
        # greenest -> open_grass, brownest -> open_bare
        greenness = []
        for j in range(N_OPEN_CLUSTERS):
            m = open_ & (maj == j)
            greenness.append(float(np.mean(ndvi[m])) if m.any() else -1.0)
        order = list(np.argsort(greenness))   # ascending: bare ... grass
        open_classes = [OPEN_BARE, OPEN_MEADOW, OPEN_GRASS]
        cluster_class = {order[i]: open_classes[i] for i in range(N_OPEN_CLUSTERS)}
        print(f"==> open split: {N_OPEN_CLUSTERS}-colour k-means, cluster "
              f"NDVI {[round(g, 3) for g in greenness]}")
    else:
        maj = np.zeros((h, w), dtype=np.int32)
        cluster_class = {0: OPEN_MEADOW}

    cls = np.zeros((h, w), dtype=np.uint8)
    cls[deciduous] = FOREST_DECIDUOUS
    cls[evergreen] = FOREST_EVERGREEN
    for j, klass in cluster_class.items():
        cls[open_ & (maj == j)] = klass

    for value in (OPEN_GRASS, OPEN_MEADOW, OPEN_BARE):
        print(f"    {CLASS_NAMES[value]}: "
              f"{share(cls == value, open_):.1f}% of open")

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
