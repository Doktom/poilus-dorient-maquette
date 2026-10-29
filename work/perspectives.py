"""Perspectives exterieures sur fond blanc pur, extraites des vues 360 du niveau Toit (batiment entier).
usage: python perspectives.py <dossier_images_toit> <sortie_dir>   -> persp_NN.jpg + perspectives.json"""
import sys, os, glob, json
import numpy as np
from PIL import Image
SRC, OUT = sys.argv[1:3]
os.makedirs(OUT, exist_ok=True)
# image -> titre (image 0 = facade sur rue, rotation de 12 deg par image)
VUES = [(0, "Façade sur rue"), (3, "Trois-quarts côté rue"), (7, "Pignon et accès"), (11, "Trois-quarts côté jardin"),
        (15, "Façade sur jardin"), (18, "Jardin et aire de jeux"), (22, "Pignon côté voisin"), (26, "Trois-quarts rue, côté droit")]
files = sorted(glob.glob(os.path.join(SRC, '*.jpg')))
meta = []
for k, (f, titre) in enumerate(VUES):
    a = np.asarray(Image.open(files[f]).convert('RGB')).astype(np.float32)
    h, w, _ = a.shape
    corners = np.concatenate([a[:40, :40].reshape(-1, 3), a[:40, -40:].reshape(-1, 3), a[-40:, :40].reshape(-1, 3), a[-40:, -40:].reshape(-1, 3)])
    bg = np.median(corners, 0)
    a = np.clip(a * (255.0 / bg), 0, 255)            # le fond devient blanc pur, l'image garde ses nuances (ombres douces)
    d = 255 - a.min(2)
    ys, xs = np.nonzero(d > 10)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    m = int(0.06 * max(x1 - x0, y1 - y0))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    W = (x1 - x0) + 2 * m; H = (y1 - y0) + 2 * m
    W = max(W, H * 3 / 2); H = W * 2 / 3                 # format 3:2
    box = [int(cx - W / 2), int(cy - H / 2), int(cx + W / 2), int(cy + H / 2)]
    canvas = Image.new('RGB', (box[2] - box[0], box[3] - box[1]), 'white')
    src = Image.fromarray(a.astype(np.uint8))
    canvas.paste(src.crop((max(0, box[0]), max(0, box[1]), min(w, box[2]), min(h, box[3]))), (max(0, -box[0]), max(0, -box[1])))
    fn = f'persp_{k:02d}.jpg'
    canvas.save(os.path.join(OUT, fn), quality=90)
    meta.append(dict(file='persp/' + fn, titre=titre, image=f, taille=list(canvas.size)))
    print(fn, f, titre, canvas.size)
json.dump(meta, open(os.path.join(OUT, 'perspectives.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
