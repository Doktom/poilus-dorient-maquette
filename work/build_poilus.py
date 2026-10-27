"""Construit la maquette 360 multi-etages (dossier + fichier autonome).
usage: python build_poilus.py <dossier_sortie> [config.json]
Entrees : site/ (build_assets_poilus.py), final/frames/<niveau>_NN.jpg (export_frames.py), polys_<niveau>.json"""
import os, sys, json, io, base64, shutil
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
WD = sys.argv[1]
cfg = json.load(open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'config_poilus.json'), encoding='utf8'))
OUT = os.path.join(WD, 'maquette-360')
shutil.rmtree(OUT, ignore_errors=True)
shutil.copytree(os.path.join(HERE, 'site', 'img'), os.path.join(OUT, 'img'))
shutil.copytree(os.path.join(HERE, 'site', 'pdf'), os.path.join(OUT, 'pdf'))
os.makedirs(os.path.join(OUT, 'frames'))
lots = json.load(open(os.path.join(HERE, 'site', 'lots.json'), encoding='utf8'))
levels = []
for L in cfg['niveaux']:
    fs = sorted(f for f in os.listdir(os.path.join(HERE, 'final', 'frames')) if f.startswith(L['id'] + '_'))
    for f in fs:
        shutil.copy(os.path.join(HERE, 'final', 'frames', f), os.path.join(OUT, 'frames', f))
    polys = None
    if L.get('polys'):
        pf = json.load(open(os.path.join(HERE, L['polys'])))
        polys = [{l: [[round(x, 1), round(y, 1)] for x, y in pts] for l, pts in pf[str(k)].items() if l in lots} for k in range(len(fs))]
    levels.append(dict(id=L['id'], label=L['label'], nom=L['nom'], n=len(fs), polys=polys))
prog = dict(name=cfg['programme'], start=cfg['niveau_initial'])
# centre horizontal du batiment par image (cadrage mobile en portrait) : boite englobante des lots de tous les niveaux
N = levels[0]['n']
focus = []
for k in range(N):
    xs = [x for L in levels if L['polys'] for pts in L['polys'][k].values() for x, _ in pts]
    focus.append(round((min(xs) + max(xs)) / 2) if xs else 1280)
tpl = open(os.path.join(HERE, 'template_poilus.html'), encoding='utf8').read()
html = (tpl.replace('__TITLE__', cfg['programme']).replace('__LOTS__', json.dumps(lots, ensure_ascii=False))
        .replace('__PROG__', json.dumps(prog, ensure_ascii=False)).replace('__LEVELS__', json.dumps(levels, ensure_ascii=False)).replace('__FOCUS__', json.dumps(focus)))
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf8').write(html)

def data_uri(path, mime, maxw=None, q=76):
    if mime == 'image/jpeg' and maxw:
        im = Image.open(path).convert('RGB')
        if im.width > maxw:
            im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True); raw = b.getvalue()
    else:
        raw = open(path, 'rb').read()
    return f'data:{mime};base64,' + base64.b64encode(raw).decode()

asset = {}
for f in sorted(os.listdir(os.path.join(OUT, 'frames'))):
    main = f.startswith(cfg['niveau_initial'] + '_')
    asset['frames/' + f] = data_uri(os.path.join(OUT, 'frames', f), 'image/jpeg', 1600 if main else 1280, 76 if main else 70)
for f in sorted(os.listdir(os.path.join(OUT, 'img'))):
    big = f.startswith('plan-lot')
    asset['img/' + f] = data_uri(os.path.join(OUT, 'img', f), 'image/jpeg', 1900 if big else 1280, 80 if big else 74)
for f in sorted(os.listdir(os.path.join(OUT, 'pdf'))):
    asset['pdf/' + f] = data_uri(os.path.join(OUT, 'pdf', f), 'application/pdf')
js = '<script>window.ASSET=' + json.dumps(asset) + ';</script>\n'
auto = html.replace('<script>\nconst A=', js + '<script>\nconst A=', 1)
assert js in auto
open(os.path.join(WD, 'maquette-360-autonome.html'), 'w', encoding='utf8').write(auto)
print('dossier', sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs) // 1024, 'Ko')
print('autonome', os.path.getsize(os.path.join(WD, 'maquette-360-autonome.html')) // 1024, 'Ko')
