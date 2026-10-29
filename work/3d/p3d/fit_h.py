"""Hauteur du plan de coupe d'un niveau dans le repere du R+1 (camera fixe), ajustee sur le dessus des murs.
usage: python p3d/fit_h.py <dossier_images>"""
import sys, glob, numpy as np, cv2
from world import *
from lotpoly import segment
import json
files = sorted(glob.glob(sys.argv[1] + '/*.jpg'))
polyfile = sys.argv[2] if len(sys.argv) > 2 else None
DT = [edges_dt(f) for f in files]
if polyfile:
    pts = np.vstack([sample(v['points']) for v in json.load(open(polyfile))['lots'].values()])
else:
  W0 = segment(files[0])[1]
  cs, _ = cv2.findContours(W0, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
  pts = np.vstack([sample(cv2.approxPolyDP(c, 2, True)[:, 0, :]) for c in cs if cv2.contourArea(c) > 2000 or len(c) > 300])
good = [f for f in range(1, 30) if DT[f][1] > 20000]
print('points', len(pts), 'images utiles', good)
def cost(h, fs=good, cap=8):
    X = unproject3(pts, 0, h)
    return np.concatenate([np.minimum(interp(DT[f][0], project3(X, f)), cap) for f in fs])
hs = np.linspace(-4, 4, 161)
c = [np.mean(cost(h, cap=30)) for h in hs]; h0 = hs[int(np.argmin(c))]
hs2 = np.linspace(h0 - 0.06, h0 + 0.06, 121); c2 = [np.mean(cost(h)) for h in hs2]; h1 = hs2[int(np.argmin(c2))]
r = cost(h1)
print(f'h = {h1:.4f}  mediane {np.median(r):.2f}px  p90 {np.percentile(r, 90):.2f}px  (grossier {h0:.3f})')
