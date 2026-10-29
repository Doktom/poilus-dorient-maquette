"""geo3d.json -> scene3d.json : fenetres posees sur la face exterieure, types/hauteurs, emprise rectangulaire, annexes."""
import json, numpy as np, cv2
from regularize import regularize
g = json.load(open('geo3d.json'))
RES = 0.02; X0 = -12.0; N = 1200
def topx(p): return ((np.asarray(p) - X0) / RES).round().astype(np.int32)
foot = np.zeros((N, N), np.uint8); cv2.fillPoly(foot, [topx(g['footprint'])], 1)
F = np.array(g['footprint']); xmin, ymin = F.min(0); xmax, ymax = F.max(0)
def outer(cx, cy, side):
    # avance vers l'exterieur depuis le centre de l'ouverture jusqu'a sortir de l'emprise
    d = {'xmin': (-1, 0), 'xmax': (1, 0), 'ymin': (0, -1), 'ymax': (0, 1)}[side]
    x, y = cx, cy
    for _ in range(200):
        i, j = topx([x + d[0] * RES, y + d[1] * RES])
        if not (0 <= i < N and 0 <= j < N) or not foot[j, i]: break
        x += d[0] * RES; y += d[1] * RES
    return x if d[0] else y
fp = cv2.approxPolyDP(topx(g['footprint']).reshape(-1, 1, 2), 1.5, True)[:, 0, :] * RES + X0
def lot_from_walls(level_id, pts):
    """Lot = espace libre (hors murs) autour du tracé 360 (dilaté de 15 cm), cloisons internes comblées, contour redressé."""
    L = [l for l in g['levels'] if l['id'] == level_id][0]
    wm = np.zeros((N, N), np.uint8)
    for w in L['walls']:
        cv2.fillPoly(wm, [topx(w['outer'])] + [topx(h) for h in w['holes']], 1)
    tr = np.zeros((N, N), np.uint8); cv2.fillPoly(tr, [topx(pts)], 1)
    zone = cv2.dilate(tr, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    m = (zone & (1 - wm) & foot).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21)))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    ap = cv2.approxPolyDP(c, 1.5, True)[:, 0, :] * RES + X0
    return regularize(ap)
out = dict(footprint=regularize(fp), bbox=[round(xmin, 3), round(ymin, 3), round(xmax, 3), round(ymax, 3)], lots={n: dict(v, pts=lot_from_walls(v['level'], v['pts'])) for n, v in g['lots'].items()}, levels=[])
H = {'rdc': 0.0, 'r1': 2.80, 'rp2': 5.60, 'rp3': 8.40}
for L in g['levels']:
    wins = []
    cand = [] if L['id'] == 'rdc' else list(L['windows'])
    # baies vitrees vues dans la coupe du rendu (vitrage coupe) : ajoutees si >= 1 m et non deja couvertes
    for w in [w for w in L.get('windows_render', [])]: pass
    for w in cand:
        cx, cy = (w['x0'] + w['x1']) / 2, (w['y0'] + w['y1']) / 2
        dists = {'xmin': cx - xmin, 'xmax': xmax - cx, 'ymin': cy - ymin, 'ymax': ymax - cy}
        side = min(dists, key=dists.get)
        horiz = side in ('ymin', 'ymax')
        a0, a1 = (w['x0'], w['x1']) if horiz else (w['y0'], w['y1'])
        pos = outer(cx, cy, side)
        if L['id'] == 'rdc':
            z0, z1, kind = 0.0, 2.46, 'garage' if w['w'] > 1.8 else 'porte'
        elif w['w'] >= 1.2:
            z0, z1, kind = 0.0, 2.15, 'baie'
        else:
            z0, z1, kind = 0.95, 2.15, 'fenetre'
        wins.append(dict(side=side, a0=round(a0, 3), a1=round(a1, 3), pos=round(pos, 3), z0=z0, z1=z1, kind=kind))
    if L['id'] == 'rdc':   # facade sud-est (rue) : porte de garage sous les balcons, entree vitree du hall
        wins += [dict(side='ymax', a0=-2.45, a1=1.0, pos=round(ymax, 3), z0=0.0, z1=2.46, kind='garage'),
                 dict(side='ymax', a0=6.4, a1=8.6, pos=round(ymax, 3), z0=0.0, z1=2.5, kind='porte')]
    walls = [dict(outer=regularize(w['outer']), holes=[regularize(h) for h in w['holes']]) for w in L['walls']]
    out['levels'].append(dict(id=L['id'], z=H[L['id']], walls=walls, windows=wins))
    print(L['id'], [(w['side'], w['kind'], round(w['a1'] - w['a0'], 2)) for w in wins])
from shapely.geometry import Polygon
inner = Polygon(out['footprint']).buffer(-0.22, join_style='mitre')
out['ring'] = dict(outer=out['footprint'], hole=np.round(np.array(inner.exterior.coords)[:-1], 3).tolist())
json.dump(out, open('scene3d.json', 'w'))
import regularize as RG
print('bbox', out['bbox'], 'replis', len(RG.FALLBACK), RG.FALLBACK[:20])
