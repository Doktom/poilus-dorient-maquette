import cv2, numpy as np, sys
from lotpoly import segment_rooms as segment
from wall import wallmask
path, out = sys.argv[1], sys.argv[2]
im, m = wallmask(path)
cv2.imwrite(out.replace('.png', '_mask.png'), m[250:950, 600:2000])
im, W, lab, st, cen = segment(path)
vis = im.copy(); rng = np.random.default_rng(1); rooms = []
for i in range(1, lab.max() + 1):
    if st[i, 4] < 300: continue
    c = rng.integers(60, 255, 3).tolist()
    vis[lab == i] = (0.5 * vis[lab == i] + 0.5 * np.array(c)).astype(np.uint8)
    cv2.putText(vis, str(i), (int(cen[i][0]) - 10, int(cen[i][1]) + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
    rooms.append((i, int(st[i, 4])))
cv2.imwrite(out, vis[250:950, 600:2000]); print(rooms)
