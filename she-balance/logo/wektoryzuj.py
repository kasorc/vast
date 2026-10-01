# Zamienia aktualne logo (PNG z przezroczystym tłem) na wektor SVG: sygnet, napis SHE BALANCE (litery osobno) i hasło.
import json, pathlib
import numpy as np, potrace
from PIL import Image
here = pathlib.Path(__file__).parent
a = np.array(Image.open(here / 'oryginal/logo-aktualne-biale.png').convert('RGBA'))[:, :, 3]
H, W = a.shape
bm = potrace.Bitmap(a > 110)
plist = bm.trace(turdsize=4, alphamax=1.0, opticurve=True, opttolerance=0.2)
def d_of(curve):
    s = curve.start_point; out = [f'M{s.x:.2f},{s.y:.2f}']
    for seg in curve.segments:
        if seg.is_corner: out.append(f'L{seg.c.x:.2f},{seg.c.y:.2f}L{seg.end_point.x:.2f},{seg.end_point.y:.2f}')
        else: out.append(f'C{seg.c1.x:.2f},{seg.c1.y:.2f} {seg.c2.x:.2f},{seg.c2.y:.2f} {seg.end_point.x:.2f},{seg.end_point.y:.2f}')
    return ''.join(out) + 'Z'
def bbox(curve):
    pts = [curve.start_point] + [p for s in curve.segments for p in ((s.c,) if s.is_corner else (s.c1, s.c2)) + (s.end_point,)]
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; return min(xs), min(ys), max(xs), max(ys)
curves = [(d_of(c), bbox(c)) for c in plist]
curves = [t for t in curves if not (t[1][2]-t[1][0] > W*0.9 and t[1][3]-t[1][1] > H*0.9)]  # pomiń ramkę całego obrazu
sign, word, tag = [], [], []
for d, b in curves:
    cy = (b[1] + b[3]) / 2
    (sign if cy < 1040 else word if cy < 1150 else tag).append((d, b))
# litery napisu: grupowanie po zachodzących na siebie zakresach x
word.sort(key=lambda t: t[1][0]); letters = []
for d, b in word:
    if letters and b[0] < letters[-1]['x1'] - 1: letters[-1]['d'] += d; letters[-1]['x1'] = max(letters[-1]['x1'], b[2])
    else: letters.append({'d': d, 'x0': b[0], 'x1': b[2]})
def bb(lst): return [min(t[1][0] for t in lst), min(t[1][1] for t in lst), max(t[1][2] for t in lst), max(t[1][3] for t in lst)]
data = {'w': W, 'h': H, 'sign': ''.join(d for d, _ in sign), 'signBox': bb(sign), 'letters': letters, 'wordBox': bb(word),
        'tag': ''.join(d for d, _ in tag), 'tagBox': bb(tag)}
(here / 'oryginal/logo-wektor.json').write_text(json.dumps(data))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><g fill="#FFFFFF" fill-rule="evenodd">
<path d="{data['sign']}"/><path d="{''.join(l['d'] for l in letters)}"/><path d="{data['tag']}"/></g></svg>'''
(here / 'oryginal/logo-aktualne-wektor.svg').write_text(svg)
print('sygnet', len(sign), 'napis', len(word), 'liter', len(letters), 'haslo', len(tag), data['signBox'], data['wordBox'], data['tagBox'])
