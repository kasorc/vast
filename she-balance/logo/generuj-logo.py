# Zestaw logo SheBalance z AKTUALNEGO logo klientki (wektor z oryginal/logo-wektor.json).
import json, pathlib
here = pathlib.Path(__file__).parent
d = json.loads((here / 'oryginal/logo-wektor.json').read_text())
word = ''.join(l['d'] for l in d['letters']); sign, tag = d['sign'], d['tag']
sx0, sy0, sx1, sy1 = d['signBox']; wx0, wy0, wx1, wy1 = d['wordBox']; tx0, ty0, tx1, ty1 = d['tagBox']
DARK, SAGE, WHITE = '#58756C', '#A4B8B0', '#FFFFFF'
def svg(vb, body, bg=None, size=None):
    x, y, w, h = vb; W, H = size or (round(w), round(h))
    bgr = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.1f} {y:.1f} {w:.1f} {h:.1f}" width="{W}" height="{H}">{bgr}{body}</svg>\n'
def g(c, *paths, tf=''): return f'<g fill="{c}" fill-rule="evenodd"{f" transform={chr(34)}{tf}{chr(34)}" if tf else ""}>' + ''.join(f'<path d="{p}"/>' for p in paths) + '</g>'
m = 70
full_vb = (tx0 - m, sy0 - m, (tx1 - tx0) + 2 * m, (ty1 - sy0) + 2 * m)
sq = (0, 0, d['w'], d['h'])
out = {
  'she-balance-logo': svg(full_vb, g(DARK, sign, word, tag)),
  'she-balance-logo-bialy': svg(full_vb, g(WHITE, sign, word, tag)),
  'she-balance-logo-na-szalwii': svg(sq, g(WHITE, sign, word, tag), SAGE),
  'she-balance-napis': svg((tx0 - 30, wy0 - 30, (tx1 - tx0) + 60, (ty1 - wy0) + 60), g(DARK, word, tag)),
  'she-balance-napis-bialy': svg((tx0 - 30, wy0 - 30, (tx1 - tx0) + 60, (ty1 - wy0) + 60), g(WHITE, word, tag)),
}
# poziome: sygnet po lewej, napis + hasło po prawej
sh = sy1 - sy0; k = 0.36; shift_x = (sx1 - sx0) * k + 60
tf_sign = f'translate({-sx0 * k:.1f},{-sy0 * k:.1f}) scale({k})'
tw = tx1 - tx0; tf_text = f'translate({shift_x - tx0:.1f},{sh * k / 2 - (wy0 + ty1) / 2:.1f})'
out['she-balance-logo-poziome'] = svg((-20, -20, shift_x + tw + 40, sh * k + 40), g(DARK, sign, tf=tf_sign) + g(DARK, word, tag, tf=tf_text))
# avatar: sam sygnet w kole szałwii
cx, cy, r = (sx0 + sx1) / 2, (sy0 + sy1) / 2, (sy1 - sy0) * 0.82
out['she-balance-avatar'] = svg((cx - r, cy - r, 2 * r, 2 * r), f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{SAGE}"/>' + g(WHITE, sign), size=(800, 800))
for n, s in out.items(): (here / f'{n}.svg').write_text(s)
(here / 'podglad.html').write_text('<!doctype html><meta charset="utf-8"><title>SheBalance – logo</title><style>body{margin:0;display:grid;grid-template-columns:1fr 1fr}div{display:flex;align-items:center;justify-content:center;padding:30px;min-height:300px}img{max-width:90%;max-height:260px}</style>'
  '<div style="background:#F4F2EF"><img src="she-balance-logo.svg"></div><div style="background:#A4B8B0"><img src="she-balance-logo-bialy.svg"></div>'
  '<div style="background:#F4F2EF"><img src="she-balance-logo-poziome.svg"></div><div style="background:#F4F2EF"><img src="she-balance-avatar.svg" style="width:220px"></div>'
  '<div style="background:#F4F2EF"><img src="she-balance-napis.svg"></div><div style="background:#58756C"><img src="she-balance-napis-bialy.svg"></div>')
print('ok', list(out))
