# Składa animacje.html z szablonu: wstawia fonty marki i oryginalny sygnet (../logo/oryginal/LOGO.svg).
import re, pathlib
here = pathlib.Path(__file__).parent
tpl = (here / 'szablon.html').read_text()
fonts = '\n  '.join(re.findall(r'@font-face\{[^}]*\}', (here.parent / 'index.html').read_text()))
P1, P2 = re.findall(r'<path d="([^"]+)"', (here.parent / 'logo/oryginal/LOGO.svg').read_text())
base, head = f'<path d="{P1}"/>', f'<path d="{P2}"/>'
import json
_d = json.loads((here.parent / 'logo/oryginal/logo-wektor.json').read_text())
_wx0, _wy0, _wx1, _wy1 = _d['wordBox']; _tx0, _ty0, _tx1, _ty1 = _d['tagBox']; _cx = (_wx0 + _wx1) / 2
_lets = ''.join(f'<g class="L" style="--i:{i};--dx:{(_cx - (l["x0"] + l["x1"]) / 2) * 0.55:.0f}px"><path d="{l["d"]}"/></g>' for i, l in enumerate(_d['letters']))
WORD = (f'<svg class="wsvg" viewBox="{_tx0 - 4:.1f} {_wy0 - 4:.1f} {_tx1 - _tx0 + 8:.1f} {_ty1 - _wy0 + 8:.1f}" fill-rule="evenodd">'
        f'<g class="W">{_lets}</g><g class="T"><path d="{_d["tag"]}"/></g></svg>')
TAG = ''
STAR = 'M0,-60 Q9,-9 60,0 Q9,9 0,60 Q-9,9 -60,0 Q-9,-9 0,-60Z'

anims = [
 ('rysowanie', 'Rysowanie', 5, False, 'Znak rysuje się kamień po kamieniu, potem wjeżdża napis. Idealne na początek rolki.',
  f'''<svg class="sign" viewBox="0 0 1500 1500"><defs><mask id="m-draw" maskUnits="userSpaceOnUse" x="-200" y="-200" width="1900" height="1900">
  <circle class="pie p1" cx="711" cy="268" r="80" stroke-width="160" pathLength="1" transform="rotate(-90 711 268)"/>
  <circle class="pie p2" cx="711" cy="657" r="145" stroke-width="290" pathLength="1" transform="rotate(-90 711 657)"/>
  <circle class="pie p3" cx="711" cy="1063" r="270" stroke-width="540" pathLength="1" transform="rotate(-90 711 1063)"/>
  </mask></defs><g mask="url(#m-draw)" fill="currentColor">{base}{head}</g></svg>{WORD}'''),
 ('balans', 'Balans', 5.5, False, 'Głowa spada na kamienie, odbija się, a cały znak szuka równowagi. Lekko i z humorem.',
  f'<svg class="sign" viewBox="0 0 1500 1500"><g class="tip fb" fill="currentColor"><g class="base">{base}</g><g class="head fb">{head}</g></g></svg>{WORD}'),
 ('oddech', 'Oddech', 6, True, 'Znak spokojnie oddycha, a od kamieni rozchodzą się kręgi jak na wodzie. Zapętlona – na tło, stories, koniec filmu.',
  f'''<svg class="sign" viewBox="0 0 1500 1500"><ellipse class="ring r1" cx="711" cy="1290" rx="520" ry="95"/><ellipse class="ring r2" cx="711" cy="1290" rx="520" ry="95"/><ellipse class="ring r3" cx="711" cy="1290" rx="520" ry="95"/>
  <g class="breathe fb" fill="currentColor">{base}{head}</g></svg>{WORD}'''),
 ('pieczatka', 'Pieczątka', 8, True, 'Napis krąży dookoła znaku jak na pieczęci. Zapętlona – świetna jako naklejka w rogu wideo.',
  f'''<svg class="ring-text" viewBox="0 0 1080 1080"><defs><path id="circ" d="M540,540 m-400,0 a400,400 0 1,1 800,0 a400,400 0 1,1 -800,0"/></defs>
  <g class="spin"><text><textPath href="#circ" textLength="2500" lengthAdjust="spacing">SHE BALANCE · HEALTHY · NETWORKING · SELF-DEVELOPMENT · </textPath></text></g>
  <circle cx="540" cy="540" r="470" fill="none" stroke="currentColor" stroke-width="2.5"/><circle cx="540" cy="540" r="352" fill="none" stroke="currentColor" stroke-width="2.5"/></svg>
  <svg class="sign" viewBox="0 0 1500 1500"><g fill="currentColor">{base}{head}</g></svg>'''),
 ('litery', 'Litery', 5, False, 'Znak wyłania się z mgły, a litery pojawiają się jedna po drugiej. Elegancko i spokojnie.',
  f'<svg class="sign" viewBox="0 0 1500 1500"><g fill="currentColor">{base}{head}</g></svg>{WORD}{TAG}'),
 ('wschod', 'Wschód', 5.5, False, 'Rysuje się horyzont, za znakiem wschodzi słońce w pudrowym kolorze marki. Poranny klimat campu.',
  f'''<svg class="sky" viewBox="0 0 1080 1080"><defs><clipPath id="hz"><rect x="0" y="0" width="1080" height="560"/></clipPath></defs>
  <g clip-path="url(#hz)"><circle class="sun" cx="540" cy="330" r="250"/></g><line class="horizon" x1="160" y1="560" x2="920" y2="560"/></svg>
  <svg class="sign" viewBox="0 0 1500 1500"><g fill="currentColor">{base}{head}</g></svg>{WORD}'''),
 ('polysk', 'Połysk', 4, True, 'Złoty refleks przesuwa się po znaku i napisie, na końcu mały błysk. Zapętlona.',
  f'''<svg class="sign" viewBox="0 0 1500 1500"><defs><linearGradient id="gb" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <mask id="m-gl" maskUnits="userSpaceOnUse" x="-600" y="-600" width="2700" height="2700"><rect class="band" x="0" y="-300" width="420" height="2100" fill="url(#gb)"/></mask></defs>
  <g fill="currentColor">{base}{head}</g><g class="gl" mask="url(#m-gl)">{base}{head}</g>
  <g transform="translate(875 175)"><path class="spark fb" d="{STAR}"/></g></svg>{WORD}'''),
 ('liscie', 'Liście', 5.5, False, 'Liście w kolorach marki wirują i składają się w znak. Jesienny, ciepły akcent.',
  f'<svg class="sign" viewBox="0 0 1500 1500"><g fill="currentColor">{base}{head}</g></svg>{WORD}'),
]
cards = []
for i, (aid, name, d, loop, desc, inner) in enumerate(anims, 1):
    tag = f'Pętla · {d:g} s' if loop else f'Intro · {d:g} s'
    cards.append(f'''<section class="card" data-id="{aid}" data-d="{d}"{' data-loop="1"' if loop else ''}>
  <div class="view"><div class="stage a-{aid}">{inner}</div></div>
  <div class="meta"><span class="tag">{i:02d} · {tag}</span><h2>{name}</h2><p>{desc}</p>
    <div class="dl"><a data-file="pliki/{aid}-{{k}}.mov" download>MOV</a><a data-file="pliki/{aid}-{{k}}.webm" download>WEBM</a>{'' if loop else '<button class="replay">Powtórz</button>'}</div></div>
</section>''')
html = tpl.replace('/*FONTS*/', fonts).replace('<!--CARDS-->', '\n'.join(cards))
(here / 'animacje.html').write_text(html)
import json; (here / 'lista.json').write_text(json.dumps([{'id': a[0], 'd': a[2], 'loop': a[3]} for a in anims]))
print('ok', len(html))
