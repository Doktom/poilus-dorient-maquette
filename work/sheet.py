import os, sys
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
d = sys.argv[1]; out = sys.argv[2]
fs = [f for f in sorted(os.listdir(d)) if os.path.isfile(os.path.join(d, f))]
W = Image.new('RGB', (4 * 300, ((len(fs) + 3) // 4) * 200), 'white'); dr = ImageDraw.Draw(W)
for i, f in enumerate(fs):
    try:
        im = Image.open(os.path.join(d, f)); sz = im.size; im = im.convert('RGB'); im.thumbnail((296, 170))
        W.paste(im, ((i % 4) * 300, (i // 4) * 200))
        dr.text(((i % 4) * 300 + 2, (i // 4) * 200 + 172), f'{f[:38]}\n{sz}', fill='black')
    except Exception as e:
        print(f, e)
W.save(out)
