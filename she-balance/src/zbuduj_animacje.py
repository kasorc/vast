# Buduje strony animacji z src/animacje/*.html do she-balance/animacje/*.html.
# Znaczniki do użycia w szablonie animacji:
#   /*FONTS*/ /*BASE_CSS*/ /*FIG_CSS*/  – w <style>
#   /*DEFS*/                          – w <defs> (gradienty, wzory, liść, gwiazdka, serce, kubek, filtr papieru #paper, #vignette)
#   /*DEFS*/ zawiera też aktualne logo: #logoWord (napis SHE BALANCE), #logoTag (hasło), #logoLockup (całość) – patrz defs-logo.svg
#   /*LOGO*/                          – ścieżki sygnetu (w viewBox 1500; np. <g transform="scale(.1) translate(-711,-738)">/*LOGO*/</g>)
#   /*FIG_A*/ /*FIG_B*/               – postać A/B w całej sylwetce (można wstawiać wiele razy; klasy póz dodaj przez /*FIG_A:walk has-pack*/)
#   /*BUST_A*/ /*BUST_B*/             – popiersia z machającą ręką (jak w pierwszym reelu)
#   /*ENGINE*/                        – w <script> PO zdefiniowaniu window.SCENES
import pathlib, re, sys
src = pathlib.Path(__file__).parent; root = src.parent
out_dir = root / 'animacje'; out_dir.mkdir(exist_ok=True)
logo = ''.join(f'<path d="{d}"/>' for d in re.findall(r'<path d="([^"]+)"', (root / 'logo/oryginal/LOGO.svg').read_text()))
figA = (src / 'figura-A.svg').read_text(); figB = (src / 'figura-B.svg').read_text()
busts = (src / 'postacie.svg').read_text(); bustA = busts[:busts.index('  <!-- Dziewczyna 2')]; bustB = busts[busts.index('  <!-- Dziewczyna 2'):]
common = {'/*FONTS*/': (src / 'fonty.css').read_text(), '/*BASE_CSS*/': (src / 'baza.css').read_text(), '/*FIG_CSS*/': (src / 'fig.css').read_text(),
          '/*DEFS*/': (src / 'defs.svg').read_text() + (src / 'defs-fig.svg').read_text() + (src / 'defs-logo.svg').read_text(), '/*LOGO*/': logo,
          '/*BUST_A*/': bustA, '/*BUST_B*/': bustB, '/*ENGINE*/': (src / 'silnik.js').read_text()}
def fig(m):
    who, cls = m.group(1), (m.group(2) or '').strip()
    base = figA if who == 'A' else figB
    return base.replace(f'class="fig fig{who}"', f'class="fig fig{who} {cls}"'.rstrip(), 1)

# Tylne włosy (.hairBack > .tiltBack) mają ruszać się razem z głową: każdą regułę CSS dla .tilt
# duplikujemy dla .tiltBack (a '.body > .tilt' – dawne tylne włosy – kierujemy na nową warstwę).
_TILT = re.compile(r'\.tilt(?![\w-])')
def _dup_tilt_rules(html):
    def fix_style(css):
        out, buf = [], []
        for part in re.split(r'([{}])', css):
            if part == '{':
                sel = ''.join(buf); buf = []
                last = max(sel.rfind(';'), sel.rfind('}'))
                head, s2 = sel[:last + 1], sel[last + 1:]
                if not s2.lstrip().startswith('@') and len(s2) < 2000 and _TILT.search(s2):
                    extra = [_TILT.sub('.tiltBack', q.replace('.body > .tilt', '.body > .hairBack > .tiltBack')) for q in s2.split(',') if _TILT.search(q)]
                    s2 = s2 + ',' + ','.join(extra)
                out.append(head + s2 + '{')
            elif part == '}':
                out.append(''.join(buf) + '}'); buf = []
            else:
                buf.append(part)
        out.append(''.join(buf)); return ''.join(out)
    pieces = re.split(r'(<style[^>]*>|</style>)', html); res = []; inside = False
    for pc in pieces:
        if pc.startswith('<style'): inside = True; res.append(pc)
        elif pc == '</style>': inside = False; res.append(pc)
        else: res.append(fix_style(pc) if inside else pc)
    return ''.join(res)

names = sys.argv[1:] or [p.stem for p in (src / 'animacje').glob('*.html')]
for n in names:
    html = (src / 'animacje' / f'{n}.html').read_text()
    html = re.sub(r'/\*FIG_([AB])(?::([^*]*))?\*/', fig, html)
    for k, v in common.items(): html = html.replace(k, v)
    html = _dup_tilt_rules(html)
    (out_dir / f'{n}.html').write_text(html); print('zbudowano', n, len(html))
