"""Prepare les fiches des lots (plans de vente PDF + image, vues 3D) a partir de config_poilus.json -> site/
usage: python build_assets_poilus.py [config.json]"""
import os, sys, json, shutil
import fitz
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
fitz.TOOLS.mupdf_display_errors(False)
HERE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'config_poilus.json'), encoding='utf8'))
OUT = os.path.join(HERE, 'site')
shutil.rmtree(OUT, ignore_errors=True)
for d in ('img', 'pdf'):
    os.makedirs(os.path.join(OUT, d))
lots = {}
for n, l in cfg['lots'].items():
    src = os.path.join(cfg['base'], cfg['pdf'].format(n=n))
    shutil.copy(src, os.path.join(OUT, 'pdf', f'lot-{int(n):02d}.pdf'))
    fitz.open(src)[0].get_pixmap(dpi=200).save(os.path.join(OUT, 'img', f'plan-lot{int(n):02d}.png'))
    im = Image.open(os.path.join(OUT, 'img', f'plan-lot{int(n):02d}.png')).convert('RGB')
    im.save(os.path.join(OUT, 'img', f'plan-lot{int(n):02d}.jpg'), quality=88)
    os.remove(os.path.join(OUT, 'img', f'plan-lot{int(n):02d}.png'))
    views = []
    for i, (f, label) in enumerate(l['vues']):
        im = Image.open(os.path.join(cfg['base'], l['dossier3d'], f)).convert('RGB')
        im.thumbnail((2200, 1400) if 'plan' in label.lower() else (1600, 1000), Image.LANCZOS)
        fn = f'lot{int(n):02d}_{i:02d}.jpg'
        im.save(os.path.join(OUT, 'img', fn), quality=82)
        views.append(dict(file='img/' + fn, label=label))
    lots[n] = dict(num=int(n), typo=l['typo'], etage=l['etage'], table=l['table'], views=views, utile=l.get('utile'))
    print('lot', n, l['typo'], len(views), 'vues')
json.dump(lots, open(os.path.join(OUT, 'lots.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
