"""High-zoom per-marker crops from the cv2 detector, for careful number reading.

Crops each of the 124 detected markers from the 2500px raster, ordered
top->bottom/left->right within each difficulty, and tiles them into paginated
contact sheets labelled by marker index. Read the sheets, transcribe
index->number, then write trail_number_reads.json keyed by the SAME centroids.
"""
import json
import cv2
import numpy as np
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = str(REPO / "brain/import/community_trails/sfwda_aop_trail_map_2015-03-11.png")
MK = str(REPO / "brain/output/paper_trace/markers.json")

img = cv2.imread(SRC)
markers = json.load(open(MK))["markers"]
for i, m in enumerate(markers):
    m["i"] = i

COLS, ROWS = 5, 4
PAD = 10
CELL_H = 150     # drawn crop height (px)
LABEL = 24

def crop(m):
    x, y, w, h = m["bbox"]
    x0, y0 = max(0, x - PAD), max(0, y - PAD)
    x1, y1 = min(img.shape[1], x + w + PAD), min(img.shape[0], y + h + PAD)
    c = img[y0:y1, x0:x1]
    scale = CELL_H / c.shape[0]
    return cv2.resize(c, (max(1, int(c.shape[1] * scale)), CELL_H), interpolation=cv2.INTER_NEAREST)

for diff in ("easy", "moderate", "difficult"):
    grp = sorted([m for m in markers if m["difficulty"] == diff],
                 key=lambda m: (round(m["centroid_px"][1] / 80), m["centroid_px"][0]))
    per = COLS * ROWS
    for pg in range((len(grp) + per - 1) // per):
        sl = grp[pg * per:(pg + 1) * per]
        cw = CELL_H + 30
        sheet = np.full((ROWS * (CELL_H + LABEL), COLS * cw, 3), 255, np.uint8)
        for k, m in enumerate(sl):
            r, cc = divmod(k, COLS)
            cim = crop(m)
            gy, gx = r * (CELL_H + LABEL) + LABEL, cc * cw
            sheet[gy:gy + CELL_H, gx:gx + cim.shape[1]] = cim
            cv2.putText(sheet, f"#{m['i']}", (gx + 2, gy - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 2)
        out = f"/tmp/mk_{diff}_{pg}.png"
        cv2.imwrite(out, sheet)  # /tmp sheets: read them, transcribe idx->number into /tmp/rebuild_reads.py
        print("wrote", out, len(sl), "markers")
