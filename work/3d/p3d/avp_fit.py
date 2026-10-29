"""Recalage plan AVP (raster murs, walls.py) -> repere monde (geo3d.json) : 8 orientations x translation x echelle."""
import json, numpy as np, cv2, sys
from walls import M_PER_PT, S
PX = M_PER_PT / S
g = json.load(open('geo3d.json'))
RES = 0.04; X0 = -12; N = 600
def world_mask(lid):
    L = [l for l in g['levels'] if l['id'] == lid][0]
    m = np.zeros((N, N), np.uint8)
    for w in L['walls']:
        cv2.fillPoly(m, [((np.array(w['outer']) - X0) / RES).astype(np.int32)] + [((np.array(h) - X0) / RES).astype(np.int32) for h in w['holes']], 1)
    return m
def fit(avp_npy, lid):
    a = np.load(avp_npy).astype(np.uint8)
    wm = cv2.GaussianBlur(world_mask(lid).astype(np.float32), (0, 0), 2)
    ys, xs = np.nonzero(a)
    pts = np.c_[xs, ys].astype(float) * PX          # metres, repere plan (x droite, y bas)
    pts -= pts.mean(0)
    best = None
    for rot in range(4):
        for mir in (1, -1):
            c, s_ = np.cos(rot * np.pi / 2), np.sin(rot * np.pi / 2)
            Rm = np.array([[c, -s_], [s_, c]]) @ np.diag([mir, 1])
            for sc in np.linspace(0.94, 1.06, 13):
                q = pts @ Rm.T * sc
                img = np.zeros((N, N), np.float32)
                ij = ((q - X0) / RES).astype(int); ok = (ij >= 0).all(1) & (ij < N).all(1)
                np.add.at(img, (ij[ok, 1], ij[ok, 0]), 1)
                img = cv2.GaussianBlur(img, (0, 0), 2)
                r = cv2.matchTemplate(wm, img[100:500, 100:500], cv2.TM_CCORR_NORMED)
                _, v, _, loc = cv2.minMaxLoc(r)
                if best is None or v > best[0]:
                    best = (v, rot, mir, sc, ((loc[0] - 100) * RES, (loc[1] - 100) * RES))
    v, rot, mir, sc, t = best
    c, s_ = np.cos(rot * np.pi / 2), np.sin(rot * np.pi / 2)
    Rm = np.array([[c, -s_], [s_, c]]) @ np.diag([mir, 1])
    mean = np.c_[xs, ys].astype(float).mean(0) * PX
    return dict(score=round(v, 3), rot=rot, mir=mir, scale=round(sc, 3), t=[round(t[0], 3), round(t[1], 3)], mean=mean.tolist(), R=(Rm * sc).tolist())
if __name__ == '__main__':
    out = {}
    for npy, lid in (('w_e1.png.npy', 'r1'), ('w_e2.png.npy', 'rp2'), ('w_rdc.png.npy', 'rdc'), ('w_e3.png.npy', 'rp3')):
        out[lid] = fit(npy, lid); print(lid, out[lid])
    json.dump(out, open('avp_fit.json', 'w'))
