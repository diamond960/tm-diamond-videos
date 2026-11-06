"""Cut presenter poses out of a white-background pose sheet.

Usage: python3 engine/presenter_extract.py sheet.png out_dir name1,name2,name3,name4
Writes out_dir/<name>.png (RGBA, trimmed, white fringe removed), ordered left to right.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi


def extract(sheet_path, out_dir, names):
    rgb = np.asarray(Image.open(sheet_path).convert("RGB")).astype(np.float32)
    mn = rgb.min(axis=2)
    sat = rgb.max(axis=2) - mn
    whiteish = (mn > 228) & (sat < 22)
    lab, n = ndi.label(whiteish)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    fg = ~bg
    fg = ndi.binary_opening(fg, iterations=1)
    # soft edge: in a 3px band around the figure, alpha follows how far the colour is from white
    band = ndi.binary_dilation(fg, iterations=3) & ~ndi.binary_erosion(fg, iterations=2)
    soft = np.clip((255.0 - mn) / 70.0, 0, 1)
    alpha = fg.astype(np.float32)
    alpha[band] = np.maximum(soft[band], ndi.binary_erosion(fg, iterations=2)[band])
    alpha = ndi.gaussian_filter(alpha, 0.6) * (ndi.binary_dilation(fg, iterations=3))
    a = np.clip(alpha, 0, 1)[..., None]
    col = np.where(a > 0.02, (rgb - (1 - a) * 255.0) / np.maximum(a, 0.02), rgb)
    col = np.clip(col, 0, 255)
    rgba = np.concatenate([col, a * 255.0], axis=2).astype(np.uint8)
    # figures = big connected blobs; small bits join the nearest blob
    blobs, m = ndi.label(ndi.binary_dilation(fg, iterations=6))
    sizes = ndi.sum(np.ones_like(blobs), blobs, range(1, m + 1))
    big = [i + 1 for i, s in enumerate(sizes) if s > fg.size * 0.01]
    cents = {b: ndi.center_of_mass(blobs == b) for b in big}
    big.sort(key=lambda b: cents[b][1])
    owner = np.zeros_like(blobs)
    for b in big:
        owner[blobs == b] = b
    for i in range(1, m + 1):
        if i in big:
            continue
        cy, cx = ndi.center_of_mass(blobs == i)
        nb = min(big, key=lambda b: (cents[b][0] - cy) ** 2 + (cents[b][1] - cx) ** 2)
        owner[blobs == i] = nb
    os.makedirs(out_dir, exist_ok=True)
    out = []
    for name, b in zip(names, big):
        m_ = owner == b
        ys, xs = np.where(m_ & (a[..., 0] > 0.02))
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        crop = rgba[y0:y1, x0:x1].copy()
        crop[..., 3] = (crop[..., 3] * m_[y0:y1, x0:x1]).astype(np.uint8)
        p = os.path.join(out_dir, name + ".png")
        Image.fromarray(crop).save(p, optimize=True)
        out.append((p, crop.shape[1], crop.shape[0]))
    return out


if __name__ == "__main__":
    for row in extract(sys.argv[1], sys.argv[2], sys.argv[3].split(",")):
        print(*row)
