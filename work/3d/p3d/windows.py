"""Fenetres/baies des facades : trous des murs exterieurs du plan AVP recale (avp_fit.json), dans la bande d'enveloppe du rendu."""
import json, numpy as np, cv2
from walls import M_PER_PT, S
PX = M_PER_PT / S
g = json.load(open('geo3d.json')); fit = json.load(open('avp_fit.json'))
RES = 0.02; X0 = -12.0; N = 1200
def topx(p): return ((np.asarray(p) - X0) / RES).round().astype(np.int32)
foot = np.zeros((N, N), np.uint8); cv2.fillPoly(foot, [topx(g['footprint'])], 1)
band = foot - cv2.erode(foot, np.ones((25, 25), np.uint8))           # 50 cm a l'interieur de l'enveloppe
NPY = {'rdc': 'w_rdc.png.npy', 'r1': 'w_e1.png.npy', 'rp2': 'w_e2.png.npy', 'rp3': 'w_e3.png.npy'}
prev = []
for L in g['levels']:
    f = fit[L['id']]; a = np.load(NPY[L['id']]).astype(np.uint8)
    ys, xs = np.nonzero(a)
    q = (np.c_[xs, ys] * PX - f['mean']) @ np.array(f['R']).T + f['t']
    am = np.zeros((N, N), np.uint8); ij = ((q - X0) / RES).astype(int); ok = (ij >= 0).all(1) & (ij < N).all(1)
    am[ij[ok, 1], ij[ok, 0]] = 1
    am = cv2.morphologyEx(am, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    # trous du mur exterieur AVP : bande de facade sans mur AVP, comblee dans l'axe du mur
    wallband = cv2.dilate(am & band, np.ones((3, 3), np.uint8))
    gaps = np.zeros_like(am)
    for k in ((1, 25), (25, 1)):
        o = cv2.morphologyEx(wallband, cv2.MORPH_OPEN, np.ones(k, np.uint8))
        kk = (1, 160) if k == (1, 25) else (160, 1)
        gaps |= cv2.morphologyEx(o, cv2.MORPH_CLOSE, np.ones(kk, np.uint8)) & (1 - wallband) & band
    n, lab, st, _ = cv2.connectedComponentsWithStats(gaps)
    wins = []
    for i in range(1, n):
        x, y, w, h, area = st[i]
        length = max(w, h) * RES; depth = min(w, h) * RES
        if length < 0.45 or length > 3.2 or depth < 0.1: continue
        x0, y0 = X0 + x * RES, X0 + y * RES
        # rectangle colle sur la facade (bord exterieur de l'enveloppe)
        wins.append(dict(x0=round(x0, 3), y0=round(y0, 3), x1=round(x0 + w * RES, 3), y1=round(y0 + h * RES, 3), w=round(length, 2)))
    L['windows'] = wins
    print(L['id'], len(wins), sorted(w['w'] for w in wins))
    t = np.full((N, N, 3), 255, np.uint8)
    for w in L['walls']: cv2.fillPoly(t, [topx(w['outer'])] + [topx(h) for h in w['holes']], (190, 190, 190))
    t[am > 0] = (60, 60, 60)
    for w in wins: cv2.rectangle(t, tuple(topx([w['x0'], w['y0']])), tuple(topx([w['x1'], w['y1']])), (255, 120, 0), -1)
    prev.append(cv2.resize(t[100:1100, 100:1100], (500, 500)))
json.dump(g, open('geo3d.json', 'w'))
cv2.imwrite('win_prev.png', np.vstack([np.hstack(prev[:2]), np.hstack(prev[2:])]))
