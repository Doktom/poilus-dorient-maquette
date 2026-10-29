"""Fonds de carte IGN (Géoplateforme WMTS, Licence Ouverte) recalés dans le repère de la scène -> ../p3d/fond_{ortho,plan}.jpg
La scène : X,Z en mètres (env.json > calage), image couvrant X,Z dans [-R, R]."""
import os, io, json, math, urllib.request, numpy as np, cv2
from load import LAT0, LON0, KX, KY
cal = json.load(open('env.json'))['calage']; C = np.array(cal['centre_local_m']); Xd = np.array(cal['axe_X_est_nord']); Zd = np.array([Xd[1], -Xd[0]])
R, RES = 200.0, 0.25
LAYERS = {'ortho': ('ORTHOIMAGERY.ORTHOPHOTOS', 'image/jpeg', 19), 'plan': ('GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2', 'image/png', 18)}
def merc(lat, lon, z):
    n = 2 ** z; x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x * 256, y * 256
N = int(2 * R / RES)
g = (np.arange(N) + 0.5) * RES - R
GX, GZ = np.meshgrid(g, g)                                   # ligne = Z, colonne = X
E = C[0] + GX * Xd[0] + GZ * Zd[0]; NO = C[1] + GX * Xd[1] + GZ * Zd[1]
LON = LON0 + E / KX; LAT = LAT0 + NO / KY
for name, (layer, fmt, z) in LAYERS.items():
    px = np.zeros_like(LON); py = np.zeros_like(LAT)
    n = 2 ** z
    px = (LON + 180) / 360 * n * 256
    py = (1 - np.arcsinh(np.tan(np.radians(LAT))) / np.pi) / 2 * n * 256
    tx0, tx1 = int(px.min() // 256), int(px.max() // 256); ty0, ty1 = int(py.min() // 256), int(py.max() // 256)
    mos = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256, 3), np.uint8)
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            fn = f'tiles/{name}_{z}_{tx}_{ty}'
            if not os.path.exists(fn):
                url = (f'https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER={layer}&STYLE=normal'
                       f'&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={ty}&TILECOL={tx}&FORMAT={fmt}')
                req = urllib.request.Request(url, headers={'User-Agent': 'ATJ-Graphics-maquette/1.0'})
                open(fn, 'wb').write(urllib.request.urlopen(req, timeout=60).read())
            im = cv2.imdecode(np.frombuffer(open(fn, 'rb').read(), np.uint8), cv2.IMREAD_COLOR)
            if im is not None:
                mos[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = im
    out = cv2.remap(mos, (px - tx0 * 256).astype(np.float32), (py - ty0 * 256).astype(np.float32), cv2.INTER_LINEAR)
    cv2.imwrite(f'../p3d/fond_{name}.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 82])
    print(name, 'tuiles', (tx1 - tx0 + 1) * (ty1 - ty0 + 1), 'image', out.shape, os.path.getsize(f'../p3d/fond_{name}.jpg') // 1024, 'Ko')
json.dump(dict(R=R, res=RES), open('../p3d/fond.json', 'w'))
