"""Repere 3D commun : camera en orbite du R+1 (polys_r1_b_model.json), plans de coupe a hauteur h (unites du modele)."""
import os, sys, json, glob
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import orbit
from wall import wallmask
Q = np.array(json.load(open(os.path.join(ROOT, 'polys_r1_b_model.json')))['q'])

def project3(X, f, q=Q):
    P, r, u, w, F, ox, oy = orbit.camera(q, f)
    Xw = np.asarray(X, float) - P
    z = Xw @ w
    return np.c_[ox + F * (Xw @ r) / z, oy - F * (Xw @ u) / z]

def unproject3(px, f, h, q=Q):
    P, r, u, w, F, ox, oy = orbit.camera(q, f)
    px = np.asarray(px, float)
    d = ((px[:, 0] - ox) / F)[:, None] * r + (-(px[:, 1] - oy) / F)[:, None] * u + w
    s = (h - P[2]) / d[:, 2]
    return P + s[:, None] * d

def edges_dt(path):
    im, W = wallmask(path)
    W = (W > 0).astype(np.uint8)
    e = cv2.morphologyEx(W, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    return cv2.distanceTransform((1 - e).astype(np.uint8), cv2.DIST_L2, 5), int(W.sum())

def interp(D, xy):
    h, w = D.shape
    bad = ~np.isfinite(xy).all(1) | (xy[:, 0] < 0) | (xy[:, 1] < 0) | (xy[:, 0] > w - 2) | (xy[:, 1] > h - 2)
    xy = np.where(np.isfinite(xy), xy, 0)
    x = np.clip(xy[:, 0], 0, w - 2); y = np.clip(xy[:, 1], 0, h - 2)
    x0 = x.astype(int); y0 = y.astype(int); fx = x - x0; fy = y - y0
    return (D[y0, x0] * (1 - fx) * (1 - fy) + D[y0, x0 + 1] * fx * (1 - fy) + D[y0 + 1, x0] * (1 - fx) * fy + D[y0 + 1, x0 + 1] * fx * fy) + bad * 1000.0

def sample(pts, step=6):
    pts = np.asarray(pts, float); out = []
    for a, b in zip(pts, np.roll(pts, -1, 0)):
        n = max(1, int(np.linalg.norm(b - a) / step))
        t = np.linspace(0, 1, n, endpoint=False)[:, None]
        out.append(a + t * (b - a))
    return np.vstack(out)
