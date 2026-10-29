"""Maquette 3D : dossier (maquette-3d/) + fichier autonome. usage: python p3d/build_3d.py <dossier_sortie>"""
import os, sys, json, shutil, base64, io
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
WD = sys.argv[1]; OUT = os.path.join(WD, 'maquette-3d')
cfg = json.load(open(os.path.join(ROOT, 'config_poilus.json'), encoding='utf8'))
LEVELS_WITH_LOTS = {'r1'}                       # prototype : lots cliquables au R+1
shutil.rmtree(OUT, ignore_errors=True)
for d in ('img', 'pdf'):
    shutil.copytree(os.path.join(ROOT, 'site', d), os.path.join(OUT, d))
shutil.copytree(os.path.join(HERE, 'lib'), os.path.join(OUT, 'lib'))
for f in ('fond_ortho.jpg', 'fond_plan.jpg'):
    shutil.copy(os.path.join(HERE, f), os.path.join(OUT, 'img', f))
lots = json.load(open(os.path.join(ROOT, 'site', 'lots.json'), encoding='utf8'))
sc = json.load(open(os.path.join(HERE, 'scene3d.json')))
sc['lots'] = {n: v for n, v in sc['lots'].items() if v['level'] in LEVELS_WITH_LOTS and n in lots}
lots = {n: v for n, v in lots.items() if n in sc['lots']}
# rendus des points de vue (views/out : base 3D ; views/magnific : version photoréaliste si disponible) et perspectives officielles
VW = os.path.join(ROOT, 'views'); os.makedirs(os.path.join(OUT, 'img', 'vues'), exist_ok=True)
def jpg(src, dst, maxw, q=86):
    im = Image.open(src).convert('RGB'); im.thumbnail((maxw, maxw)); im.save(dst, quality=q, optimize=True)
RENDERS, PERSP = {}, []
for f in sorted(os.listdir(os.path.join(VW, 'out'))) if os.path.isdir(os.path.join(VW, 'out')) else []:
    vid = os.path.splitext(f)[0]; mg = os.path.join(VW, 'magnific', vid + '.jpg')
    src = mg if os.path.exists(mg) else os.path.join(VW, 'out', f)
    jpg(src, os.path.join(OUT, 'img', 'vues', vid + '.jpg'), 2560); jpg(src, os.path.join(OUT, 'img', 'vues', vid + '_t.jpg'), 480, 80)
    RENDERS[vid] = dict(file=f'img/vues/{vid}.jpg', thumb=f'img/vues/{vid}_t.jpg',
                        credit='Rendu photoréaliste (Magnific AI) à partir de la maquette 3D' if os.path.exists(mg) else 'Rendu de la maquette 3D')
for key, name, sub, view in (('Vue Aerienne', 'Vue aérienne', 'Perspective du projet', 'aerienne'), ('Vue Pietonne', 'Vue depuis la rue', 'Perspective du projet', 'rue')):
    src = os.path.join(cfg['base'], f"20251201_Rue des Poilus d'Orient_{key}.jpg")
    if os.path.exists(src):
        vid = 'persp_' + view
        jpg(src, os.path.join(OUT, 'img', 'vues', vid + '.jpg'), 2560); jpg(src, os.path.join(OUT, 'img', 'vues', vid + '_t.jpg'), 480, 80)
        PERSP.append(dict(file=f'img/vues/{vid}.jpg', thumb=f'img/vues/{vid}_t.jpg', name=name, sub=sub, view=view,
                          credit='Illustration non contractuelle réalisée par ATJ Graphics'))
t = open(os.path.join(HERE, 'template_3d.html'), encoding='utf8').read()
rep = {'__CSS__': open(os.path.join(HERE, '_css.txt'), encoding='utf8').read(),
       '__MODAL__': open(os.path.join(HERE, '_modal.txt'), encoding='utf8').read(),
       '__FICHE__': open(os.path.join(HERE, '_fiche.txt'), encoding='utf8').read(),
       '__TITLE__': cfg['programme'], '__LOTS__': json.dumps(lots, ensure_ascii=False),
       '__SCENE__': json.dumps(sc), '__ENV__': open(os.path.join(ROOT, 'osm', 'env.json'), encoding='utf8').read(), '__FOND__': open(os.path.join(HERE, 'fond.json'), encoding='utf8').read(), '__PROG__': json.dumps(dict(name=cfg['programme'], start='r1', address=cfg.get('adresse', '')), ensure_ascii=False),
       '__RENDERS__': json.dumps(RENDERS, ensure_ascii=False), '__PERSPECTIVES__': json.dumps(PERSP, ensure_ascii=False)}
for k, v in rep.items():
    assert k in t, k
    t = t.replace(k, v)
LIBM = {}
for d in ('controls', 'postprocessing', 'shaders', 'math', 'environments'):
    for f in sorted(os.listdir(os.path.join(HERE, 'lib', d))):
        LIBM[d + '/' + f] = open(os.path.join(HERE, 'lib', d, f), encoding='utf8').read()
libm = '<script>window.LIBM=' + json.dumps(LIBM).replace('</', '<\\/') + ';</script>\n'
t = t.replace('<script>\nconst A=', libm + '<script>\nconst A=', 1)
assert libm in t
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf8').write(t)
def uri(path, mime, maxw=None, q=78):
    if maxw:
        im = Image.open(path).convert('RGB'); im.thumbnail((maxw, maxw))
        b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True); raw = b.getvalue()
    else:
        raw = open(path, 'rb').read()
    return f'data:{mime};base64,' + base64.b64encode(raw).decode()
asset = {}
for f in sorted(os.listdir(os.path.join(OUT, 'img'))):
    if not any(f.startswith(p) for p in [f'lot{int(n):02d}_' for n in lots] + [f'plan-lot{int(n):02d}' for n in lots]): continue
    big = f.startswith('plan-lot')
    asset['img/' + f] = uri(os.path.join(OUT, 'img', f), 'image/jpeg', 1900 if big else 1280, 80 if big else 74)
for f in sorted(os.listdir(os.path.join(OUT, 'img', 'vues'))):
    asset['img/vues/' + f] = uri(os.path.join(OUT, 'img', 'vues', f), 'image/jpeg')
for f in ('fond_ortho.jpg', 'fond_plan.jpg'):
    asset['img/' + f] = uri(os.path.join(OUT, 'img', f), 'image/jpeg')
for n in lots:
    f = f'lot-{int(n):02d}.pdf'; asset['pdf/' + f] = uri(os.path.join(OUT, 'pdf', f), 'application/pdf')
lib = dict(three=open(os.path.join(HERE, 'lib', 'three.module.min.js'), encoding='utf8').read())
emb = '<script>window.ASSET=' + json.dumps(asset) + ';window.LIB=' + json.dumps(lib).replace('</', '<\/') + ';</script>\n'
auto = t.replace('<script>\nconst A=', emb + '<script>\nconst A=', 1)
assert emb in auto
open(os.path.join(WD, 'maquette-3d-autonome.html'), 'w', encoding='utf8').write(auto)
print('dossier', sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs) // 1024, 'Ko',
      '| autonome', os.path.getsize(os.path.join(WD, 'maquette-3d-autonome.html')) // 1024, 'Ko')
