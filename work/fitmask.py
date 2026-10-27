"""Ajuste le modele de camera en orbite (orbit.py) directement sur le dessus des murs (blanc pur) des 30 images.
Points du plan = contours des lots + contour exterieur du batiment, traces sur l'image 0.
usage: python fitmask.py <dossier_images> <polygones.json> <sortie_frames.json> [rapport.json]"""
import sys, os, glob, json
import numpy as np, cv2
from scipy.optimize import least_squares
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orbit
from lotpoly import segment
from wall import wallmask

FR, POLY, OUT = sys.argv[1:4]
ROOF = int(os.environ.get('ROOF', '0'))
files = sorted(glob.glob(os.path.join(FR, '*.jpg')))
N = len(files)
poly = json.load(open(POLY, encoding='utf8'))['lots']

def edges_dt(path):
    im, W = wallmask(path)
    W = (W > 0).astype(np.uint8)
    if ROOF:   # comble : le toit (zinc gris fonce) limite aussi les pieces
        g = im.astype(int); W = (W | ((g.max(2) < ROOF) & (g.max(2) - g.min(2) < 40))).astype(np.uint8)
    e = cv2.morphologyEx(W, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    return cv2.distanceTransform((1 - e).astype(np.uint8), cv2.DIST_L2, 5), W

def sample(pts, step=6):
    pts = np.asarray(pts, float); out = []
    for a, b in zip(pts, np.roll(pts, -1, 0)):
        n = max(1, int(np.linalg.norm(b - a) / step))
        t = np.linspace(0, 1, n, endpoint=False)[:, None]
        out.append(a + t * (b - a))
    return np.vstack(out)

DT, WM = zip(*[edges_dt(f) for f in files])
P0 = np.vstack([sample(v['points']) for v in poly.values()])   # points du plan : contours des lots (image 0)
print('points', len(P0))

def interp(D, xy):
    h, w = D.shape
    bad = ~np.isfinite(xy).all(1) | (xy[:, 0] < 0) | (xy[:, 1] < 0) | (xy[:, 0] > w - 2) | (xy[:, 1] > h - 2)
    xy = np.where(np.isfinite(xy), xy, 0)
    x = np.clip(xy[:, 0], 0, w - 2); y = np.clip(xy[:, 1], 0, h - 2)
    x0 = x.astype(int); y0 = y.astype(int); fx = x - x0; fy = y - y0
    return (D[y0, x0] * (1 - fx) * (1 - fy) + D[y0, x0 + 1] * fx * (1 - fy) + D[y0 + 1, x0] * (1 - fx) * fy + D[y0 + 1, x0 + 1] * fx * fy) + bad * 1000.0

def residuals(p, frames, delta):
    q = np.append(p[:4], delta)
    X = orbit.unproject(P0, 0, q)
    r = []
    for f in frames:
        r.append(interp(DT[f], orbit.project(X, f, q)))
    return np.concatenate(r)

frames = [f for f in range(1, N)]
best = None
for delta in (2 * np.pi / N, -2 * np.pi / N):
    for phi in np.linspace(0.35, 1.25, 19):
      for fl in (1500, 1900, 2400, 3000, 3800, 4800, 6000, 7500, 9500):
        for oy in (520, 720, 920):
            p = np.array([np.log(fl), phi, 1280, oy])
            c = np.mean(np.minimum(residuals(p, [1, 2, 3, 27, 28, 29], delta), 40))
            if best is None or c < best[0]:
                best = (c, p, delta)
print('init', best[0], np.exp(best[1][0]), best[1][1], best[2])
p, delta = best[1], best[2]
for sub, fs in ((40, [1, 2, 3, 4, 26, 27, 28, 29]), (20, frames), (6, frames)):
    r = least_squares(lambda p: np.minimum(residuals(p, fs, delta), sub), p, x_scale=[0.05, 0.02, 20, 20], loss='soft_l1', f_scale=3, diff_step=1e-4, bounds=([np.log(600), 0.15, 0, 0], [np.log(30000), 1.45, 2560, 1440]))
    p = r.x
    rr = residuals(p, frames, delta)
    print(f'clip {sub}: median {np.median(rr):.2f}px  p90 {np.percentile(rr, 90):.2f}  f={np.exp(p[0]):.0f} phi={np.degrees(p[1]):.1f} o=({p[2]:.0f},{p[3]:.0f})')
# pas libre
r = least_squares(lambda pp: np.minimum(residuals(pp[:4], frames, pp[4]), 6), np.append(p, delta), loss='soft_l1', f_scale=3, diff_step=1e-4)
p, delta = r.x[:4], r.x[4]
rr = residuals(p, frames, delta)
per = [float(np.median(residuals(p, [f], delta))) for f in range(N)]
print(f'pas libre {np.degrees(delta):.3f} deg: median {np.median(rr):.2f}px p90 {np.percentile(rr, 90):.2f}')
print('mediane par image', np.round(per, 1).tolist())
q = np.append(p, delta)
out = {}
for f in range(N):
    out[str(f)] = {l: orbit.project(orbit.unproject(np.array(v['points'], float), 0, q), f, q).round(1).tolist() for l, v in poly.items()}
json.dump(out, open(OUT, 'w'))
json.dump(dict(q=q.tolist(), per_frame_median=per), open(OUT.replace('.json', '_model.json'), 'w'))
print('->', OUT)
