import cv2, numpy as np, sys
from wall import wallmask
path, out, thr = sys.argv[1], sys.argv[2], int(sys.argv[3])
im, m = wallmask(path)
g = im.astype(int); v = g.max(2); sat = g.max(2) - g.min(2)
roof = (v < thr) & (sat < 40)
bar = ((m > 0) | roof).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(1 - bar, connectivity=4)
H, W = bar.shape
vis = im.copy(); rng = np.random.default_rng(3); rooms = []
for i in range(1, n):
    x, y, w, h, a = st[i]
    if a < 300 or x == 0 or y == 0 or x + w >= W or y + h >= H or a > 400000: continue
    c = rng.integers(60, 255, 3).tolist()
    vis[lab == i] = (0.45 * vis[lab == i] + 0.55 * np.array(c)).astype(np.uint8)
    cv2.putText(vis, str(i), (int(cen[i][0]) - 10, int(cen[i][1]) + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    rooms.append((i, int(a)))
cv2.imwrite(out, vis[200:800, 760:2060]); np.save(out + '.npy', lab); print(rooms)
