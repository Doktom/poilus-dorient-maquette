"""Redressement des polygones issus du raster : arêtes quasi parallèles aux axes du bâtiment mises à l'équerre,
petits ressauts supprimés, sommets recalculés par intersection des droites support.
Le repère monde est déjà aligné sur le bâtiment (x = grand côté, y = petit côté)."""
import numpy as np

FALLBACK = []
SNAP_DEG = 12.0      # tolérance angulaire pour mettre une arête à l'équerre
MIN_EDGE = 0.04      # arêtes plus courtes supprimées (m)
MERGE = 0.035        # deux arêtes parallèles consécutives à moins de 3,5 cm fusionnent
OBL_MAX = 0.30       # arête oblique plus courte = chanfrein du raster, supprimée


def _area(p):
    return 0.5 * (np.dot(p[:, 0], np.roll(p[:, 1], -1)) - np.dot(p[:, 1], np.roll(p[:, 0], -1)))


def _oblique(d):
    ang = np.degrees(np.arctan2(d[:, 1], d[:, 0])) % 90
    return np.minimum(ang, 90 - ang) >= SNAP_DEG


def _drop_short(p):
    changed = True
    while changed and len(p) > 4:
        changed = False
        d = np.roll(p, -1, 0) - p
        e = np.linalg.norm(d, axis=1)
        # chanfreins (arêtes obliques courtes) et micro-arêtes
        score = np.where(_oblique(d) & (e < OBL_MAX), e - 1.0, e)
        i = int(np.argmin(score))
        if score[i] < MIN_EDGE:
            j = (i + 1) % len(p)
            p[i] = (p[i] + p[j]) / 2
            p = np.delete(p, j, 0)
            changed = True
    return p


def regularize(pts):
    p = np.asarray(pts, float)
    if len(p) < 4:
        return p.round(3).tolist()
    a0 = abs(_area(p))
    p = _drop_short(p.copy())
    n = len(p)
    # droites support : (kind, valeur) avec kind 'h' (y = c), 'v' (x = c) ou 'o' (oblique : point + direction)
    lines = []
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        d = b - a
        L = np.hypot(*d)
        ang = np.degrees(np.arctan2(d[1], d[0])) % 180
        if min(ang, 180 - ang) < SNAP_DEG:
            lines.append(['h', (a[1] + b[1]) / 2, L, a, b])
        elif abs(ang - 90) < SNAP_DEG:
            lines.append(['v', (a[0] + b[0]) / 2, L, a, b])
        else:
            lines.append(['o', (a, d / L), L, a, b])
    # fusion des droites parallèles consécutives proches (moyenne pondérée par la longueur)
    merged = True
    while merged and len(lines) > 4:
        merged = False
        for i in range(len(lines)):
            j = (i + 1) % len(lines)
            A, B = lines[i], lines[j]
            if A[0] == B[0] and A[0] != 'o' and abs(A[1] - B[1]) < MERGE:
                A[1] = (A[1] * A[2] + B[1] * B[2]) / (A[2] + B[2]); A[2] += B[2]; A[4] = B[4]
                lines.pop(j); merged = True
                break
    def inter(A, B):
        if A[0] == 'h' and B[0] == 'v': return np.array([B[1], A[1]])
        if A[0] == 'v' and B[0] == 'h': return np.array([A[1], B[1]])
        def pd(X):
            if X[0] == 'h': return np.array([0.0, X[1]]), np.array([1.0, 0.0])
            if X[0] == 'v': return np.array([X[1], 0.0]), np.array([0.0, 1.0])
            return X[1]
        (p1, d1), (p2, d2) = pd(A), pd(B)
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-6:
            return None
        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        return p1 + t * d1
    out = []
    m = len(lines)
    def proj(X, pt):
        if X[0] == 'h': return np.array([pt[0], X[1]])
        if X[0] == 'v': return np.array([X[1], pt[1]])
        p0, d0 = X[1]; return p0 + np.dot(pt - p0, d0) * d0
    for i in range(m):
        A, B = lines[i - 1], lines[i]
        v = inter(A, B)
        if v is not None:
            out.append(v)
        else:                       # droites parallèles non fusionnées : retour d'équerre à la jonction
            j = (A[4] + B[3]) / 2
            out.append(proj(A, j)); out.append(proj(B, j))
    q = np.array(out)
    # garde-fou : si le redressement déforme trop (surface), on garde l'original simplifié
    if len(q) < 3 or abs(abs(_area(q)) - a0) > 0.08 * a0 + 0.03:
        FALLBACK.append(len(pts))
        return np.asarray(pts, float).round(3).tolist()
    return q.round(3).tolist()


if __name__ == '__main__':
    sq = [[0, 0], [2.01, 0.015], [2.0, 0.6], [2.03, 0.61], [2.02, 1.0], [0.01, 1.01]]
    print(regularize(sq))
