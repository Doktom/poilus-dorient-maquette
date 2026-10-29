"""Geometrie 3D (metres) de tous les niveaux a partir des vues de dessus -> geo.json
Repere : origine = centre de l'enveloppe du R+1, x = grand cote, y = petit cote, z = altitude (coupe AA)."""
import json, numpy as np, cv2
from world import unproject3
MU = 11.43                                  # m par unite du modele (largeur R+1 = 13,00 m)
LEVELS = [('rdc', -0.237, 0.00), ('r1', 0.0, 2.80), ('rp2', 0.246, 5.60), ('rp3', 0.425, 8.40)]
POLYS = {'r1': '../polygones-R1.json', 'rp2': '../polygones-R2.json', 'rp3': '../polygones-R3.json'}
def load(l):
    f = cv2.imread(f'top_{l}.png', 0).astype(np.float32) / 255
    meta = json.load(open(f'top_{l}.png.json'))
    return f, meta
def px2model(pts, meta):
    return np.asarray(meta['lo']) + np.asarray(pts, float) * meta['step']
# repere a partir du R+1
f, meta = load('r1')
m = (f > 0.6).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
H, W = m.shape
inner = (st[1:, 0] > 0) & (st[1:, 1] > 0) & (st[1:, 0] + st[1:, 2] < W) & (st[1:, 1] + st[1:, 3] < H)
k = 1 + np.argmax(np.where(inner, st[1:, 4], 0))
cs, _ = cv2.findContours((lab == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
env = max(cs, key=cv2.contourArea)[:, 0, :]
envm = px2model(env, meta)
rect = cv2.minAreaRect(envm.astype(np.float32))
(cx, cy), (a, b), ang = rect
th = np.radians(ang if a >= b else ang + 90)
R = np.array([[np.cos(th), np.sin(th)], [-np.sin(th), np.cos(th)]])
C = np.array([cx, cy])
def model2world(xy):
    return ((np.asarray(xy) - C) @ R.T) * MU
# lots de l'image 0 -> monde
lots = {}
for l, h, _ in LEVELS:
    if l in POLYS:
        for n_, v in json.load(open(POLYS[l]))['lots'].items():
            lots[n_] = dict(level=l, typo=v['typo'], pts=model2world(unproject3(v['points'], 0, h)[:, :2]))
# orientation : lot 2 (rue) vers +y, lot 1 (jardin) vers -y
c1 = lots['1']['pts'].mean(0); c2 = lots['2']['pts'].mean(0)
flip = np.diag([1.0, 1.0])
if c2[1] < c1[1]: flip = np.diag([-1.0, -1.0])
def W2(xy): return model2world(xy) @ flip.T
for v in lots.values(): v['pts'] = (v['pts'] @ flip.T)
foot = W2(envm)
out = dict(levels=[], lots={})
for l, h, z in LEVELS:
    f, meta = load(l)
    m = (f > (0.42 if l == 'rdc' else 0.6)).astype(np.uint8)
    # garder ce qui est proche de l'enveloppe du R+1 (rayon 5 m)
    envpx = ((envm - np.asarray(meta['lo'])) / meta['step']).astype(np.int32)
    zone = np.zeros_like(m); cv2.fillPoly(zone, [envpx], 1)
    zone = cv2.dilate(zone, np.ones((int(5 / 0.02), int(5 / 0.02)), np.uint8))
    m = m & zone
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = st[:, 4] * 0.02 * 0.02 > 0.08; keep[0] = False
    m = keep[lab].astype(np.uint8)
    cs, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    walls = []
    for i, c in enumerate(cs):
        if hier[0][i][3] != -1: continue
        ap = cv2.approxPolyDP(c, 1.0, True)[:, 0, :]
        holes = []
        j = hier[0][i][2]
        while j != -1:
            hc = cs[j]
            if cv2.contourArea(hc) * 0.0004 > 0.01:
                holes.append(W2(px2model(cv2.approxPolyDP(hc, 1.0, True)[:, 0, :], meta)).round(3).tolist())
            j = hier[0][j][0]
        walls.append(dict(outer=W2(px2model(ap, meta)).round(3).tolist(), holes=holes))
    out['levels'].append(dict(id=l, z=z, walls=walls))
    print(l, len(walls), 'blocs de murs', sum(len(w['holes']) for w in walls), 'pieces')
out['lots'] = {n_: dict(level=v['level'], typo=v['typo'], pts=v['pts'].round(3).tolist()) for n_, v in lots.items()}
out['footprint_r1'] = foot.round(3).tolist()
json.dump(out, open('geo.json', 'w'))
x, y = foot[:, 0], foot[:, 1]
print('enveloppe R+1', round(x.max() - x.min(), 2), 'x', round(y.max() - y.min(), 2), 'm')
for n_, v in out['lots'].items():
    p = np.array(v['pts']); a = 0.5 * abs(np.dot(p[:, 0], np.roll(p[:, 1], 1)) - np.dot(p[:, 1], np.roll(p[:, 0], 1)))
    print('lot', n_, v['level'], 'surface polygone', round(a, 1), 'm2')
