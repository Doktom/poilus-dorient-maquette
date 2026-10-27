import fitz, os, re, json
fitz.TOOLS.mupdf_display_errors(False)
B = r"C:\Users\tom\OneDrive\Documents\ATJ\ATJ GRAPHICS\PROJETS CLIENTS\2026\INOVA - Poilus d'Orient\plans_de_vente_PDF"
def table(n):
    pg = fitz.open(os.path.join(B, f"Plans de vente CEPIA - RUE DES POILUS-{n}.pdf"))[0]
    ws = [w for w in pg.get_text('words') if w[0] > 560 and w[1] > 330]
    rows = {}
    for x0, y0, x1, y1, t, *_ in ws:
        yc = (y0 + y1) / 2
        k = next((k for k in rows if abs(k - yc) < 4), yc)
        rows.setdefault(k, []).append((x0, t))
    out = []
    for k in sorted(rows):
        ws_ = sorted(rows[k]); txt = ' '.join(t for _, t in ws_)
        lab = ' '.join(t for x, t in ws_ if x < 700); val = ' '.join(t for x, t in ws_ if x >= 700)
        out.append((round(k), lab, val))
    return out
for n in (1, 2):
    for r in table(n): print(n, r)
