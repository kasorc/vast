# Składa she-balance/index.html z plików w src/: szablon, fonty, definicje SVG, postacie i oryginalny sygnet.
import re, pathlib
src = pathlib.Path(__file__).parent
root = src.parent
logo = ''.join(f'<path d="{d}"/>' for d in re.findall(r'<path d="([^"]+)"', (root / 'logo/oryginal/LOGO.svg').read_text()))
html = ((src / 'szablon.html').read_text()
        .replace('/*FONTS*/', (src / 'fonty.css').read_text())
        .replace('/*DEFS*/', (src / 'defs.svg').read_text() + (src / 'defs-logo.svg').read_text())
        .replace('/*LOGO*/', logo)
        .replace('/*CHARS*/', (src / 'postacie.svg').read_text()))
(root / 'index.html').write_text(html)
print('index.html', len(html))
