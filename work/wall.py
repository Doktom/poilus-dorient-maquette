import cv2, numpy as np, sys
def wallmask(path, thr=242):
    im = cv2.imread(path); g = im.astype(int)
    mn = g.min(2); mx = g.max(2)
    return im, ((mn >= thr) & (mx - mn < 12)).astype(np.uint8) * 255
if __name__ == '__main__':
    im, m = wallmask(sys.argv[1])
    # keep components inside building bbox, largest
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    order = np.argsort(-st[1:, 4]) + 1
    for k in order[:8]:
        print(k, st[k])
