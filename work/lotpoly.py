import cv2, numpy as np
from wall import wallmask


def segment(path):
    im, m = wallmask(path)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    H, Wd = m.shape
    inner = (st[1:, 0] > 0) & (st[1:, 1] > 0) & (st[1:, 0] + st[1:, 2] < Wd) & (st[1:, 1] + st[1:, 3] < H)
    k = 1 + np.argmax(np.where(inner, st[1:, 4], 0))
    W = (lab == k).astype(np.uint8)
    cs, _ = cv2.findContours(W, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    outer = np.zeros_like(W); cv2.drawContours(outer, cs, -1, 1, -1)
    holes = (outer & (1 - W)).astype(np.uint8)
    n2, lab2, st2, cen = cv2.connectedComponentsWithStats(holes, connectivity=4)
    return im, W, lab2, st2, cen

def lot_contour(mask, close=31, eps=2.0):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close, close))
    mk = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, k)
    cs, _ = cv2.findContours(mk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    ap = cv2.approxPolyDP(c, eps, True)[:, 0, :]
    return ap, c, mk

def segment_rooms(path, min_area=300):
    """Pieces = zones non blanches fermees (ne touchant pas le bord de l'image). Fonctionne meme si le dessus des
    murs touche le fond blanc."""
    im, m = wallmask(path)
    n, lab, st, cen = cv2.connectedComponentsWithStats((m == 0).astype(np.uint8), connectivity=4)
    H, W = m.shape
    border = (st[:, 0] == 0) | (st[:, 1] == 0) | (st[:, 0] + st[:, 2] >= W) | (st[:, 1] + st[:, 3] >= H)
    keep = (~border) & (st[:, 4] >= min_area); keep[0] = False
    lab = np.where(keep[lab], lab, 0)
    return im, (m > 0).astype(np.uint8), lab, st, cen
