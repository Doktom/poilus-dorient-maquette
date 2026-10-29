"""Passage photoréaliste des rendus de points de vue avec Magnific AI (API Freepik « image-upscaler »).

Prérequis : variable d'environnement FREEPIK_API_KEY (clé API Freepik, offre donnant accès à Magnific).
usage : python magnific.py [id ...]          (par défaut : tous les rendus de views/out/)
Entrée : views/out/<id>.jpg (captures 2560x1440 de la maquette 3D) -> sortie : views/magnific/<id>.jpg
Ensuite : python p3d/build_3d.py out  (la galerie prend automatiquement la version Magnific si elle existe).
"""
import os, sys, json, time, base64, urllib.request

KEY = os.environ.get('FREEPIK_API_KEY')
API = 'https://api.freepik.com/v1/ai/image-upscaler'
HERE = os.path.dirname(os.path.abspath(__file__))
SRC, DST = os.path.join(HERE, 'out'), os.path.join(HERE, 'magnific')

BASE = ("photorealistic architectural visualization, new 4-storey residential building in Caen, Normandy, France: "
        "smooth off-white render facade, sand-beige fibre-cement panel volume, light quartz-zinc standing-seam mansard roof with zinc dormers, "
        "dark grey aluminium windows, white concrete balconies with white geometric perforated metal railings, white sectional garage door, "
        "white low wall with white square pillars and white geometric metal fence panels, sunny late afternoon, soft natural shadows, "
        "clear blue sky with light clouds, lush green hedges, pink flowering Judas tree, high-end real estate rendering, sharp, realistic materials")
CONTEXT = {
    'rue': "eye-level view from the asphalt street, sidewalk and parked cars, neighbouring Normandy villa with brown clay tile roof and chimney on the right",
    'aerienne': "high aerial view over the street, neighbouring houses with brown and red clay tile roofs, white apartment block behind, mature trees, parked cars, road markings",
    'angle': "three-quarter view from the street corner, blind gable wall, hedges along the property line, neighbouring houses",
    'jardin': "rear garden view with lawn, wooden terrace with planted green roofs, balconies, garden wall and hedges, neighbouring rooftops",
    'plongee': "top-down site plan view, roof, garden, street, neighbouring buildings and trees",
    'r1': "cutaway axonometric of the first floor showing apartment layouts, light oak floors, keep the cut walls and coloured floor areas unchanged",
}
NEG = "distorted geometry, extra floors, changed window layout, people deformed, text, watermark"


def call(method, url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None, method=method,
                                 headers={'x-freepik-api-key': KEY, 'Content-Type': 'application/json', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def run(vid):
    img = base64.b64encode(open(os.path.join(SRC, vid + '.jpg'), 'rb').read()).decode()
    body = dict(image=img, scale_factor='2x', optimized_for='3d_renders',
                prompt=BASE + '; ' + CONTEXT.get(vid, ''),
                creativity=4 if vid != 'r1' else 0, hdr=2, resemblance=4 if vid != 'r1' else 8, fractality=0, engine='magnific_sparkle')
    task = call('POST', API, body)['data']['task_id']
    print(vid, 'tâche', task, flush=True)
    for _ in range(120):
        time.sleep(5)
        d = call('GET', f'{API}/{task}')['data']
        if d.get('status') == 'COMPLETED':
            url = d['generated'][0]
            os.makedirs(DST, exist_ok=True)
            urllib.request.urlretrieve(url, os.path.join(DST, vid + '.jpg'))
            print(vid, '->', os.path.join(DST, vid + '.jpg'))
            return
        if d.get('status') == 'FAILED':
            raise RuntimeError(f'{vid} : échec Magnific {d}')
    raise TimeoutError(vid)


if __name__ == '__main__':
    if not KEY:
        sys.exit("FREEPIK_API_KEY manquante : définissez la variable d'environnement avec votre clé API Freepik/Magnific.")
    ids = sys.argv[1:] or [os.path.splitext(f)[0] for f in sorted(os.listdir(SRC)) if f.endswith('.jpg')]
    for v in ids:
        run(v)
