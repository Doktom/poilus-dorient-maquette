import sys
from PIL import Image, ImageDraw
src, x0, y0, w, h, s, out = sys.argv[1], *map(int, sys.argv[2:7]), sys.argv[7]
im = Image.open(src).convert('RGB').crop((x0, y0, x0+w, y0+h)).resize((w*s, h*s), Image.LANCZOS)
d = ImageDraw.Draw(im)
for x in range((x0//10+1)*10, x0+w, 10):
    c = (255,0,0) if x % 50 == 0 else (255,180,180)
    if x % 50 == 0 or s >= 3:
        d.line([((x-x0)*s, 0), ((x-x0)*s, h*s)], fill=c, width=1)
    if x % 50 == 0: d.text(((x-x0)*s+2, 2), str(x), fill=(200,0,0))
for y in range((y0//10+1)*10, y0+h, 10):
    c = (0,0,255) if y % 50 == 0 else (180,180,255)
    if y % 50 == 0 or s >= 3:
        d.line([(0, (y-y0)*s), (w*s, (y-y0)*s)], fill=c, width=1)
    if y % 50 == 0: d.text((2, (y-y0)*s+2), str(y), fill=(0,0,200))
im.save(out)
