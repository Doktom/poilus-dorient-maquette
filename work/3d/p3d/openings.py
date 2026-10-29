"""Murs nettoyes + ouvertures (fenetres/baies/portes) par niveau, dans un raster monde aligne (2 cm) -> geo3d.json"""
import json, numpy as np, cv2
g = json.load(open('geo.json'))
RES = 0.02; X0, Y0, NX, NY = -12.0, -12.0, 1200, 1200
def topx(p): return ((np.asarray(p) - [X0, Y0]) / RES).round().astype(np.int32)
def tow(p): return (np.asarray(p, float) * RES + [X0, Y0]).round(3)
foot = np.zeros((NY, NX), np.uint8); cv2.fillPoly(foot, [topx(g['footprint_r1'])], 1)
footd = cv2.dilate(foot, np.ones((7, 7), np.uint8))
def polys(mask, eps=1.0, min_area=0.02):
    cs, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    for i, c in enumerate(cs):
        if hier[0][i][3] != -1 or cv2.contourArea(c) * RES * RES < min_area: continue
        holes, j = [], hier[0][i][2]
        while j != -1:
            if cv2.contourArea(cs[j]) * RES * RES > 0.01:
                holes.append(tow(cv2.approxPolyDP(cs[j], eps, True)[:, 0, :]).tolist())
            j = hier[0][j][0]
        out.append(dict(outer=tow(cv2.approxPolyDP(c, eps, True)[:, 0, :]).tolist(), holes=holes))
    return out
res = dict(levels=[], lots=g['lots'], footprint=g['footprint_r1'])
for L in g['levels']:
    m = np.zeros((NY, NX), np.uint8)
    for w in L['walls']:
        cv2.fillPoly(m, [topx(w['outer'])] + [topx(h) for h in w['holes']], 1)
    m &= footd
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    ops = np.zeros_like(m)
    for k in ((1, 25), (25, 1)):                       # murs orientes (>= 50 cm), puis comblement des trous <= 1,9 m dans l'axe
        orient = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones(k, np.uint8))
        kk = (1, 95) if k == (1, 25) else (95, 1)
        ops |= cv2.morphologyEx(orient, cv2.MORPH_CLOSE, np.ones(kk, np.uint8)) & (1 - m)
    # perimetre du batiment : bande de 60 cm autour de l'enveloppe -> fenetres ; sinon portes interieures
    edge = foot - cv2.erode(foot, np.ones((31, 31), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(ops)
    wins, doors = [], []
    for i in range(1, n):
        if st[i, 4] < 20: continue
        comp = (lab == i).astype(np.uint8)
        length = max(st[i, 2], st[i, 3]) * RES
        p = polys(comp, 0.8, 0.005)
        if not p: continue
        ext = (comp & edge).sum() > 0.5 * comp.sum()
        (wins if ext else doors).append(dict(poly=p[0]['outer'], w=round(length, 2)))
    res['levels'].append(dict(id=L['id'], z=L['z'], walls=polys(m, 1.8), windows=wins, doors=doors))
    print(L['id'], 'murs', len(polys(m)), 'fenetres', len(wins), [w['w'] for w in wins], 'portes', len(doors))
json.dump(res, open('geo3d.json', 'w'))
# apercu
tiles = []
for L in res['levels']:
    t = np.full((NY, NX, 3), 255, np.uint8)
    for w in L['walls']: cv2.fillPoly(t, [topx(w['outer'])] + [topx(h) for h in w['holes']], (70, 70, 70))
    for w in L['windows']: cv2.fillPoly(t, [topx(w['poly'])], (255, 140, 0))
    for w in L['doors']: cv2.fillPoly(t, [topx(w['poly'])], (0, 180, 0))
    for n_, v in res['lots'].items():
        if v['level'] == L['id']: cv2.polylines(t, [topx(v['pts'])], True, (0, 0, 255), 2)
    tiles.append(cv2.resize(t[100:1100, 100:1100], (500, 500)))
cv2.imwrite('geo3d_prev.png', np.vstack([np.hstack(tiles[:2]), np.hstack(tiles[2:])]))
