import json, sys, glob, cv2, numpy as np
pf = json.load(open(sys.argv[1])); out = sys.argv[3]
files = sorted(glob.glob((sys.argv[4] if len(sys.argv) > 4 else 'src/r1') + '/*.jpg'))
tiles = []
for spec in sys.argv[2].split(';'):
    f, l, j = map(int, spec.split(','))
    im = cv2.imread(files[f])
    for ll, pts in pf[str(f)].items():
        cv2.polylines(im, [np.round(np.array(pts)).astype(np.int32).reshape(-1, 1, 2)], True, (0, 0, 255) if ll == '1' else (255, 0, 0), 1, cv2.LINE_AA)
    x, y = np.round(pf[str(f)][str(l)][j]).astype(int)
    c = im[max(0, y - 60):y + 60, max(0, x - 80):x + 80]
    c = cv2.resize(c, (480, 360), interpolation=cv2.INTER_NEAREST)
    cv2.putText(c, f'img {f} lot {l} s{j}', (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    tiles.append(c)
while len(tiles) % 3: tiles.append(np.full_like(tiles[0], 255))
cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)]))
