"""Range les 2 derniers PNG Magnific téléchargés : usage python grab.py <vue>  -> views/magnific/cand/<vue>_1.jpg, <vue>_2.jpg (ordre de téléchargement)"""
import os, glob, sys
from PIL import Image
v = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
fs = sorted(glob.glob(r'C:/Users/tom/Downloads/magnific__*.png'), key=os.path.getmtime)[-n:]
d = r'C:/Users/tom/Temp/pdo/views/magnific/cand'; os.makedirs(d, exist_ok=True)
for i, f in enumerate(fs, 1):
    Image.open(f).convert('RGB').save(f'{d}/{v}_{i}.jpg', quality=92); print(v, i, os.path.basename(f), Image.open(f).size)
