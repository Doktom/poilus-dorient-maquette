"""Vue de dessus (orthographique) du dessus des murs d'un niveau : vote sur les images ou le blanc pur est detecte.
usage: python topview.py <dossier_images> <h> <sortie.png> [res_m=0.01] [m_par_unite=11.6]"""
import sys, glob, numpy as np, cv2, json
from world import *
src, h, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
res = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01
MU = float(sys.argv[5]) if len(sys.argv) > 5 else 11.6
files = sorted(glob.glob(src + '/*.jpg'))
# emprise : image 0 entiere ramenee sur le plan
c0 = unproject3(np.array([[500, 150], [2100, 150], [2100, 1100], [500, 1100]], float), 0, h)
lo = c0[:, :2].min(0) - 0.05; hi = c0[:, :2].max(0) + 0.05
step = res / MU
xs = np.arange(lo[0], hi[0], step); ys = np.arange(lo[1], hi[1], step)
GX, GY = np.meshgrid(xs, ys)
P = np.c_[GX.ravel(), GY.ravel(), np.full(GX.size, h)]
votes = np.zeros(GX.shape, np.float32); seen = np.zeros(GX.shape, np.float32)
for f, path in enumerate(files):
    im, W = wallmask(path)
    if (W > 0).sum() < 20000: continue
    uv = project3(P, f).astype(np.float32)
    mx = uv[:, 0].reshape(GX.shape); my = uv[:, 1].reshape(GX.shape)
    v = cv2.remap(W, mx, my, cv2.INTER_LINEAR, borderValue=0).astype(np.float32) / 255
    inside = (mx > 0) & (my > 0) & (mx < W.shape[1] - 1) & (my < W.shape[0] - 1)
    votes += v * inside; seen += inside
frac = votes / np.maximum(seen, 1)
cv2.imwrite(out, (frac * 255).astype(np.uint8))
json.dump(dict(lo=lo.tolist(), step=step, shape=list(GX.shape), h=h, MU=MU, res=res), open(out + '.json', 'w'))
print(out, GX.shape, 'images', int(seen.max()))
