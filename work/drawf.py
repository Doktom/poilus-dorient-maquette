import json, sys, glob, cv2, numpy as np
pf = json.load(open(sys.argv[1])); fs = [int(x) for x in sys.argv[2].split(',')]; out = sys.argv[3]
files = sorted(glob.glob(sys.argv[4] + '/*.jpg')) if len(sys.argv) > 4 else sorted(glob.glob('src/r1/*.jpg'))
tiles = []
for f in fs:
    im = cv2.imread(files[f])
    for l, pts in pf[str(f)].items():
        cv2.polylines(im, [np.array(pts, np.int32).reshape(-1, 1, 2)], True, (0, 0, 255) if l == '1' else (255, 0, 0), 2)
    cv2.putText(im, str(f), (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    tiles.append(cv2.resize(im, (960, 540)))
while len(tiles) % 2: tiles.append(np.full_like(tiles[0], 255))
rows = [np.hstack(tiles[i:i + 2]) for i in range(0, len(tiles), 2)]
cv2.imwrite(out, np.vstack(rows))
