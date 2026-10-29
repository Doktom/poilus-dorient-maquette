"""Murs d'un plan d'etage (PDF architecte vectoriel) -> masques raster en cm.
Calques : contours murs porteurs (0.57 noir, 1.7 gris 0.3), cloisons (0.85 noir)."""
import sys, os, json
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layer import items
S = 3.0                      # px par point PDF
M_PER_PT = 13.00 / 491.7     # calage sur la cote 13,00 du plan d'etage
def raster(pdf, crop=(150, 40, 1010, 744)):
    x0, y0, x1, y1 = crop
    W, H = int((x1 - x0) * S), int((y1 - y0) * S)
    lay = {}
    for name, specs in (('porteur', [(0.57, (0.0, 0.0, 0.0)), (1.7, (0.3, 0.3, 0.3))]), ('cloison', [(0.85, (0.0, 0.0, 0.0))])):
        im = np.zeros((H, W), np.uint8)
        for w, c in specs:
            for a, b, c2, d in items(pdf, w, c):
                p = (int(round((a - x0) * S)), int(round((b - y0) * S))); q = (int(round((c2 - x0) * S)), int(round((d - y0) * S)))
                cv2.line(im, p, q, 255, 1)
        lay[name] = im
    return lay
def fill_thin(lines, maxhalf_px):
    free = (lines == 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(free, connectivity=4)
    dt = cv2.distanceTransform(free, cv2.DIST_L2, 3)
    mx = np.zeros(n); np.maximum.at(mx, lab.ravel(), dt.ravel())
    thin = (mx < maxhalf_px); thin[0] = False
    big = st[:, 4] > 0.3 * lines.size; thin &= ~big
    return ((lines > 0) | thin[lab]).astype(np.uint8)
def clean(lay):
    px = M_PER_PT / S
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    clo = cv2.morphologyEx(lay['cloison'], cv2.MORPH_CLOSE, k)
    allw = cv2.bitwise_or(lay['porteur'], clo)
    wm = fill_thin(allw, 0.26 / px)
    wm = cv2.morphologyEx(wm, cv2.MORPH_OPEN, np.ones((4, 4), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(wm)
    keep = st[:, 4] * px * px > 0.12; keep[0] = False
    return keep[lab].astype(np.uint8)
if __name__ == '__main__':
    pdf, out = sys.argv[1], sys.argv[2]
    lay = raster(pdf)
    wm = clean(lay)
    vis = np.full(wm.shape + (3,), 255, np.uint8); vis[wm > 0] = (60, 60, 60); vis[lay['cloison'] > 0] = (0, 0, 220)
    cv2.imwrite(out, vis)
    np.save(out + '.npy', wm)
    print(wm.shape, 'm/px', M_PER_PT / S)
