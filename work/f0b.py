import cv2, numpy as np, json, sys
from lotpoly import segment, lot_contour
im, W, lab, st, cen = segment('src/r1/POILUS DORIENT_360 Coupe Etage R+1 (2k30)_00000.jpg')
L = {'1': [2], '2': [13, 23]}
TY = {'1': 'T4', '2': 'T4'}
eps = float(sys.argv[1]) if len(sys.argv) > 1 else 4
vis = im.copy(); out = {}
for l, ids in L.items():
    ap, c, mk = lot_contour(np.isin(lab, ids), eps=eps)
    out[l] = dict(typo=TY[l], points=ap.tolist())
    cv2.polylines(vis, [ap.reshape(-1, 1, 2)], True, (0, 0, 255) if l == '1' else (255, 0, 0), 1)
    for p in ap: cv2.circle(vis, tuple(int(v) for v in p), 3, (0, 200, 0), -1)
    print(l, len(ap))
cv2.imwrite('src/f0poly.png', vis[400:800, 780:1840])
json.dump(dict(level='R+1', image=dict(width=2560, height=1440), lots=out), open('polygones-R1.json', 'w'))
