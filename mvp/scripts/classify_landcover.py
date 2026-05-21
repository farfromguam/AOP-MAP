#!/usr/bin/env python3
"""Classify a NAIP 4-band ortho into the AOP forest mask for the park map.

Reads a 4-band (R, G, B, NIR) NAIP GeoTIFF, decides which ground is forest,
and writes a single-band class raster (1 forest, 2 open, 0 nodata) plus a
small colorized PNG preview.

Forest is a neighbourhood-scale land cover, not a pixel property. The NAIP
here is early-November (partial leaf-off): bare deciduous canopy lets brown
litter show between branches, so a single 0.6 m pixel flips noisily between
"rough" and "bare". So canopy roughness is measured as a *field* -- local NIR
std-dev, then a low-pass pass over that std-dev -- giving a smooth forest
score that is uniformly high inside woods and uniformly low over fields.

Otsu picks the forest threshold per-image. The thresholded mask is then
cleaned morphologically: a closing fills canopy-gap holes punched through the
woods (without eroding real clearings or softening their edges), and an
opening drops stray forest specks stranded in open fields.

Only forest is vectorized downstream; open ground is left as the viewer's
paper background, and water is carried by the separate USGS NHD layer.

Pure numpy + GDAL bindings; box filters use summed-area tables (no scipy).

Classes: 0 nodata, 1 forest, 2 open.
"""
import sys
import numpy as np
from osgeo import gdal

gdal.UseExceptions()

FOREST, OPEN = 1, 2
CLASS_NAMES = {FOREST: "forest", OPEN: "open"}
CLASS_RGB = {0: (255, 255, 255), FOREST: (70, 110, 70), OPEN: (208, 193, 152)}

TEXTURE_RADIUS = 6        # local NIR std-dev window (~7.5 m at 0.6 m px)
FOREST_SMOOTH_RADIUS = 5  # low-pass over the std-dev field -> coherent score
CLOSE_RADIUS = 16         # fill canopy-gap holes up to ~20 m across
OPEN_RADIUS = 7           # drop forest specks smaller than ~9 m
PREVIEW_STRIDE = 4        # downsample factor for the PNG preview


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

    nodata = (red == 0) & (green == 0) & (blue == 0) & (nir == 0)
    valid = ~nodata

    # canopy roughness as a smooth field: local NIR std-dev, then a low-pass
    # pass so within-canopy speckle resolves to a coherent forest score
    mean_nir = box_mean(nir, TEXTURE_RADIUS)
    mean_sq = box_mean(nir * nir, TEXTURE_RADIUS)
    texture = np.sqrt(np.maximum(mean_sq - mean_nir * mean_nir, 0.0))
    forest_score = box_mean(texture, FOREST_SMOOTH_RADIUS)

    forest_thr = otsu(forest_score[valid])
    print(f"==> forest score: p10={pct(forest_score[valid],10):.1f} "
          f"p50={pct(forest_score[valid],50):.1f} "
          f"p90={pct(forest_score[valid],90):.1f} "
          f"-> Otsu forest threshold {forest_thr:.2f}")

    forest = valid & (forest_score > forest_thr)
    raw_pct = 100.0 * forest.sum() / valid.sum()

    # morphological cleanup: close canopy-gap holes, then drop forest specks
    forest = closing(forest, CLOSE_RADIUS)
    forest = opening(forest, OPEN_RADIUS)
    forest &= valid
    clean_pct = 100.0 * forest.sum() / valid.sum()
    print(f"==> forest cover: {raw_pct:.1f}% raw -> {clean_pct:.1f}% "
          f"after close({CLOSE_RADIUS})/open({OPEN_RADIUS})")

    cls = np.zeros((h, w), dtype=np.uint8)
    cls[valid & ~forest] = OPEN
    cls[forest] = FOREST

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
