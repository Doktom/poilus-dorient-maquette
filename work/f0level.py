"""Contours des lots sur l'image 0 d'un niveau a partir des pieces detectees (segment_rooms).
usage: python f0level.py <dossier_images> <niveau> <sortie.json> lot:typo:id,id ...   ex: 3:T4:15 4:T4:285,295"""
import cv2, numpy as np, json, sys, glob
from lotpoly import segment_rooms, lot_contour
src, level, out = sys.argv[1:4]
f0 = sorted(glob.glob(src + '/*.jpg'))[0]
im, W, lab, st, cen = segment_rooms(f0)
lots = {}; vis = im.copy()
for spec in sys.argv[4:]:
    l, ty, ids = spec.split(':')
    ap, c, mk = lot_contour(np.isin(lab, [int(i) for i in ids.split(',')]), eps=4)
    lots[l] = dict(typo=ty, points=ap.tolist())
    cv2.polylines(vis, [ap.reshape(-1, 1, 2)], True, (0, 0, 255), 2)
    print(l, len(ap), 'sommets')
json.dump(dict(level=level, image=dict(width=2560, height=1440), lots=lots), open(out, 'w'))
cv2.imwrite(out.replace('.json', '.png'), vis[250:950, 600:2000])
