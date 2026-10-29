import fitz, sys, os, cv2, numpy as np
fitz.TOOLS.mupdf_display_errors(False)
B = r"C:\Users\tom\OneDrive\Documents\ATJ\ATJ GRAPHICS\PROJETS CLIENTS\2026\INOVA - Poilus d'Orient\plans_poilus d'orient"
def items(pdf, width, color, S=4.0):
    pg = fitz.open(os.path.join(B, pdf))[0]
    segs = []
    for d in pg.get_drawings():
        if d['type'] != 's' or round(d.get('width') or 0, 2) != width: continue
        if tuple(round(x, 2) for x in d['color']) != color: continue
        for it in d['items']:
            if it[0] == 'l': segs.append((it[1].x, it[1].y, it[2].x, it[2].y))
            elif it[0] == 're':
                r = it[1]; segs += [(r.x0, r.y0, r.x1, r.y0), (r.x1, r.y0, r.x1, r.y1), (r.x1, r.y1, r.x0, r.y1), (r.x0, r.y1, r.x0, r.y0)]
            elif it[0] == 'c':
                segs.append((it[1].x, it[1].y, it[4].x, it[4].y))
            elif it[0] == 'qu':
                q = it[1]; pts = [q.ul, q.ur, q.lr, q.ll]
                segs += [(pts[i].x, pts[i].y, pts[(i+1)%4].x, pts[(i+1)%4].y) for i in range(4)]
    return segs
if __name__ == '__main__':
    pdf = sys.argv[1]; S = 2.0
    im = np.full((int(842 * S), int(1191 * S), 3), 255, np.uint8)
    cols = [(0, 0, 255), (255, 0, 0), (0, 160, 0)]
    for k, spec in enumerate(sys.argv[3:]):
        w, c = spec.split('@'); c = tuple(float(x) for x in c.split(','))
        for x0, y0, x1, y1 in items(pdf, float(w), c):
            cv2.line(im, (int(x0 * S), int(y0 * S)), (int(x1 * S), int(y1 * S)), cols[k], 1)
    cv2.imwrite(sys.argv[2], im)
