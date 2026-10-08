# -*- coding: utf-8 -*-
# Generator animacji „57%” (SheBalance, reel 9:16, 20 s) → src/animacje/stres57.html
# Uruchom: python3 src/animacje/stres57/gen.py && python3 src/zbuduj_animacje.py stres57
# Sceny (start, s): 0 liczba · 1 chaos · 4.5 ponad połowa · 7 zatrzymanie · 10 SheBalance · 16 zaproszenie (koniec 20)
# Role: pod presją BRUNETKA (B), z zaproszeniem przychodzi BLONDYNKA (A, bez czapki – tylko /*FIG_A*/).
# Kinowo: każde ujęcie = warstwy z paralaksą (pcam), tła rozmyte statycznym feGaussianBlur, rim-light filtrem,
# kolor: akt 1 chłodny → akt 2 ocieplenie → akt 3 złota godzina. Match-cuty: twarz B → sylwetka w siatce (4,5 s),
# zamykana klapa laptopa → linia horyzontu (10 s), światełko z girlandy → poświata logo (16 s).
import sys, pathlib, math, random, itertools, json
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pomoc import *          # K, A, S, uid, f, rig, head, pupils, ghost, steam_paths, side_arm, ridge, smooth…
from pomoc import CSS

# ---------- TEKSTY DO PODMIANY ----------
DATA_CAMPU = "5–7.11 · Karolowy Dwór, Wisła"          # data i miejsce campu (plansza końcowa)
ZRODLO = ("Źródło: ManpowerGroup,", "Globalny Barometr Talentów 2025")   # = „Źródło: ManpowerGroup, Globalny Barometr Talentów 2025”
STAT1, STAT2 = "pracujących kobiet w Polsce", "codziennie odczuwa wysoki poziom stresu."
CTA1, CTA2 = "Zarezerwuj miejsce →", "shebalance.pl"
CLAIM = ("Tym razem", "wybierz siebie.")

DARK = '#3f524c'
CREAM_T = '#F4F0E8'
BSKIN, BSKIN2 = '#f3cdb3', '#efc4a8'
LOGO = json.loads((ROOT / 'logo/oryginal/logo-wektor.json').read_text())
SB = LOGO['signBox']; SGX, SGY = (SB[0] + SB[2]) / 2, (SB[1] + SB[3]) / 2

EV = []
def ev(t, what): EV.append((round(t, 2), what))
def f4(v): return ('%.4f' % v).rstrip('0').rstrip('.')
FR = 1 / 30

# ================= kamera z paralaksą =================
def cam_tf(x, p):
    t, fx, fy, z, sx, sy, rot = x[:7]
    zp = 1 + (z - 1) * p
    ax, ay = sx + (fx - sx) * p, sy + (fy - sy) * p
    return 'transform:translate(%spx,%spx) scale(%s) rotate(%sdeg) translate(%spx,%spx)' % (f(sx), f(sy), f4(zp), f(rot), f(-ax), f(-ay))

def pcam(cls, T, frames, p=1.0, ease=EIO):
    """frames: (t, fx, fy, z, sx, sy, rot[, easing]) – punkt świata (fx,fy) w punkcie ekranu (sx,sy), zoom z.
    Warstwa o współczynniku p porusza się/przybliża p razy słabiej (p<1 tło) lub mocniej (p>1 pierwszy plan)."""
    S('.%s{transform-origin:0 0}' % cls)
    A('.' + cls, K([(x[0], cam_tf(x, p)) + tuple(x[7:8]) for x in frames], T, ease))

def layers(name, T, frames, specs, ease=EIO):
    """specs: [(p, svg, filtr|None)] – kolejne warstwy (od tła do pierwszego planu)."""
    out = ''
    for i, sp in enumerate(specs):
        p, content, bl = sp[0], sp[1], sp[2]
        c = '%sL%d' % (name, i)
        pcam(c, T, frames, p, ease)
        inner = '<g filter="url(#%s)">%s</g>' % (bl, content) if bl else content
        out += '<g class="%s">%s</g>' % (c, inner)
    return out

def show_win(cls, T, t0, t1):
    fr = [(0, 'opacity:%d' % (1 if t0 <= 0 else 0), 'steps(1,end)')]
    if t0 > 0: fr.append((t0, 'opacity:1', 'steps(1,end)'))
    if t1 < T - 1e-6: fr.append((t1, 'opacity:0', 'steps(1,end)'))
    A('.' + cls, K(fr, T, 'linear'))

def jerk_cam(t0, t1, fx, fy, sx, sy, z1=1.04, kick=(10, -8, 1.08, 1.1), drift=(8, 0)):
    """kamera ujęcia w chaosie: szarpnięcie przy cięciu → szybkie osiadanie → powolny push."""
    dx, dy, z0, r0 = kick
    return [(t0, fx + dx, fy + dy, z0, sx, sy, r0, 'cubic-bezier(.15,.85,.3,1)'), (t0 + .13, fx - dx * .12, fy, .992, sx, sy, -r0 * .18, 'ease-in-out'),
            (t0 + .22, fx, fy, 1.0, sx, sy, 0, 'cubic-bezier(.35,0,.3,1)'), (t1, fx + drift[0], fy + drift[1], z1, sx, sy, 0)]

# ================= postacie =================
def FIGR(who, cls, cx, feet, s, wrap='', pre='', post='', rim=None):
    tx, ty = cx - 110 * s, feet - 712 * s
    fl = ' filter="url(#%s)"' % rim if rim else ''
    return '<g transform="translate(%s,%s) scale(%s)"><g%s><g class="%s">%s/*FIG_%s:%s*/%s</g></g></g>' % (f(tx), f(ty), f4(s), fl, wrap, pre, who, cls, post)

def W2L(cx, feet, s, wx, wy):
    return ((wx - cx) / s + 110, 712 - (feet - wy) / s)

def ghost_fore(who, inst, content, arm='R'):
    """rekwizyt obracający się RAZEM z przedramieniem (np. palce przy skroni – rysowane nad włosami)."""
    return '<g class="fig fig%s %s ghost"><g class="body"><g class="arm%s"><g class="fore%s">%s</g></g></g></g>' % (who, inst, arm, arm, content)

def fingers(x=170, skin=BSKIN):
    s = '<g><ellipse cx="%s" cy="455" rx="12.5" ry="15" fill="%s"/>' % (f(x), skin)
    for dx, h in [(-8.5, 22), (-3, 27), (2.5, 27), (8, 22)]:
        s += '<rect x="%s" y="458" width="6.6" height="%s" rx="3.3" fill="%s"/>' % (f(x + dx - 3.3), h, skin)
    s += '<path d="M%s,463 v18 M%s,463 v22 M%s,463 v20" stroke="#d6a284" stroke-width=".9" opacity=".7"/></g>' % (f(x - 5.7), f(x - .2), f(x + 5.3))
    return s

def rig_side(inst, who, T, side, frames, ease=EIO):
    """jedna ręka (side 'R'/'L') z własną osią czasu: frames (t, (x,y)[, easing od tej klatki[, łokieć]])."""
    rows = []
    for fr in frames:
        e = fr[2] if len(fr) > 2 and fr[2] else ease
        a1, a2 = ik(who, side, fr[1], fr[3] if len(fr) > 3 else 'down')
        rows.append((fr[0], a1, a2, e))
    arm = unwrap([r[1] for r in rows]); fore = unwrap([r[2] for r in rows])
    A('.fig.%s .arm%s' % (inst, side), K([(r[0], 'transform:rotate(%sdeg)' % f(v), r[3]) for r, v in zip(rows, arm)], T))
    A('.fig.%s .fore%s' % (inst, side), K([(r[0], 'transform:rotate(%sdeg)' % f(v), r[3]) for r, v in zip(rows, fore)], T))
    A('.%sc%s' % (inst, side), K([(r[0], 'transform:rotate(%sdeg)' % f(-(a + b)), r[3]) for r, a, b in zip(rows, arm, fore)], T))

def eyes_kf(inst, T, frames, ease=EIO):
    A('.fig.%s .eyes' % inst, K([(x[0], 'transform:scaleY(%s)' % f(x[1])) + tuple(x[2:3]) for x in frames], T, ease))

def blinks(times, base=1.0):
    fr = []
    for t in times:
        fr += [(t, base), (t + .06, .08), (t + .14, base)]
    return fr

def body_kf(inst, T, frames, ease=EIO):
    A('.fig.%s .body' % inst, K([(x[0], 'transform:translateY(%spx) scaleY(%s)' % (f(x[1]), f4(x[2]))) + tuple(x[3:4]) for x in frames], T, ease))

def smile_kf(inst, T, frames, ease=EIO):
    A('.fig.%s .smile' % inst, K([(x[0], 'transform:scale(%s,%s)' % (f(x[1]), f(x[2]))) + tuple(x[3:4]) for x in frames], T, ease))

# ================= tekst: maski, stagger =================
S('#stage .serif{font-family:"Forum",Georgia,serif}')
S('.scene.active .rvw.w{animation:rvw .5s cubic-bezier(.2,.8,.2,1) both;animation-delay:calc(var(--d0) + var(--w) * var(--st))}'
  '@keyframes rvw{from{transform:translateY(var(--h))}to{transform:translateY(0)}}')
S('.scene.active .fdw.w{animation:fdw .42s cubic-bezier(.2,.8,.25,1) both;animation-delay:calc(var(--d0) + var(--w) * var(--st))}'
  '@keyframes fdw{0%{opacity:0;transform:translateX(-10px)}45%{opacity:1}100%{opacity:1;transform:none}}')
S('.scene.active .pw.w{transform-box:fill-box;transform-origin:50% 80%;animation:pw .5s cubic-bezier(.2,.8,.25,1) both;animation-delay:calc(var(--d0) + var(--w) * var(--st))}'
  '@keyframes pw{0%{opacity:0;transform:translateY(20px) scale(.9)}40%{opacity:1}100%{opacity:1;transform:none}}')
S('.scene.active .ltr.w{animation:ltr .5s cubic-bezier(.2,.8,.25,1) both;animation-delay:calc(var(--d0) + var(--w) * var(--st))}'
  '@keyframes ltr{0%{opacity:0;transform:translateY(14px)}40%{opacity:1}100%{opacity:1;transform:none}}')

def T_(txt, x, y, fs, col, cls='', anchor='middle', serif=True, weight=None, style='', extra=''):
    st = style + (';font-weight:%s' % weight if weight else '')
    return '<text x="%s" y="%s" font-size="%s" text-anchor="%s" class="%s%s" fill="%s" style="%s" %s>%s</text>' % (
        f(x), f(y), f(fs), anchor, 'serif ' if serif else '', cls, col, st, extra, txt)

def line_up(T, txt, x, y, fs, t0, col=INK, anchor='middle', serif=True, weight=None, st=.075, t_out=None, out_dur=.2, xpad=(-200, 940)):
    """maska linii: słowa wjeżdżają od dołu spod krawędzi maski (stagger); wyjście: linia ucieka w górę."""
    cid, ex = uid('lc'), uid('lx')
    top, h = y - fs * 1.02, fs * 1.36
    s = '<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (cid, xpad[0], f(top), xpad[1], f(h))
    s += '<g clip-path="url(#%s)"><g class="%s">' % (cid, ex)
    s += T_(txt, x, y, fs, col, 'wsplit rvw', anchor, serif, weight, '--d0:%ss;--h:%spx;--st:%ss' % (f(t0), f(fs * 1.45), f(st)))
    s += '</g></g>'
    if t_out is not None:
        A('.' + ex, K([(0, 'transform:translateY(0)'), (t_out, 'transform:translateY(0)', 'cubic-bezier(.55,0,.75,.3)'), (t_out + out_dur, 'transform:translateY(-%spx)' % f(fs * 1.75))], T))
    return s

def line_wipe(T, txt, x, y, fs, t0, dur, col=INK, anchor='middle', serif=True, weight=None, st=.06, t_out=None, x0=30, w=480):
    """maska przesuwana w poziomie (linia odsłaniana od lewej) + słowa wsuwają się z lekkim staggerem."""
    cid, rc, ex = uid('wc'), uid('wr'), uid('wx')
    s = '<clipPath id="%s"><rect class="%s" x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (cid, rc, x0, f(y - fs * 1.05), w, f(fs * 1.4))
    S('.%s{transform-origin:%spx 0}' % (rc, x0))
    A('.' + rc, K([(0, 'transform:scaleX(0)'), (t0, 'transform:scaleX(0)', 'cubic-bezier(.3,0,.2,1)'), (t0 + dur, 'transform:scaleX(1)')], T))
    s += '<g clip-path="url(#%s)"><g class="%s">%s</g></g>' % (cid, ex, T_(txt, x, y, fs, col, 'wsplit fdw', anchor, serif, weight, '--d0:%ss;--st:%ss' % (f(t0), f(st))))
    if t_out is not None:
        A('.' + ex, K([(0, 'opacity:1;transform:translateY(0)'), (t_out, 'opacity:1;transform:translateY(0)', EOUT), (t_out + .18, 'opacity:0;transform:translateY(-8px)')], T))
    return s

def letters(T, txt, x, y, fs, t0, col, st=.035, t_out=None, serif=True):
    idx = [i for i, c in enumerate(txt) if c != ' ']
    ex = uid('lt')
    s = '<g class="%s">%s</g>' % (ex, T_(txt, x, y, fs, col, 'wsplit ltr', 'middle', serif, None, '--d0:%ss;--st:%ss' % (f(t0), f(st)), 'data-g="%s"' % ','.join(map(str, idx))))
    if t_out is not None:
        A('.' + ex, K([(0, 'opacity:1;transform:translateY(0)'), (t_out, 'opacity:1;transform:translateY(0)', EOUT), (t_out + .18, 'opacity:0;transform:translateY(-10px)')], T))
    return s

def source_block(op=.86):
    return ('<g opacity="%s">' % f(op) + T_(ZRODLO[0], 40, 724, 17, CREAM_T, '', 'start', False, 600) +
            T_(ZRODLO[1], 40, 745, 17, CREAM_T, '', 'start', False, 600) + '</g>')

def vign(op=.5, col='black'):
    return '<rect x="-20" y="-20" width="580" height="1000" fill="url(#vignette)" opacity="%s" pointer-events="none"/>' % f(op)

def overlay(fill, op, blend, cls=''):
    return '<rect x="-20" y="-20" width="580" height="1000" fill="%s" opacity="%s" class="%s" style="mix-blend-mode:%s" pointer-events="none"/>' % (fill, f(op), cls, blend)

def bokeh(n, box, cols, rr, seed, op=(.25, .5)):
    r = random.Random(seed); s = ''
    for i in range(n):
        x, y = r.uniform(box[0], box[2]), r.uniform(box[1], box[3])
        s += '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="%s"/>' % (f(x), f(y), f(r.uniform(*rr)), cols[i % len(cols)], f(r.uniform(*op)))
    return s

def drift(cls, T, dx, dy, ease='cubic-bezier(.45,0,.55,1)'):
    A('.' + cls, K([(0, 'transform:translate(0,0)'), (T, 'transform:translate(%spx,%spx)' % (f(dx), f(dy)))], T, ease))

# ================= rekwizyty =================
ICONS = {
    'mail': '<rect x="-12" y="-9" width="24" height="18" rx="3"/><path d="M-11,-7 L0,2 L11,-7"/>',
    'chat': '<path d="M-12,-10 H12 Q14,-10 14,-8 V4 Q14,6 12,6 H-1 L-8,12 V6 H-12 Q-14,6 -14,4 V-8 Q-14,-10 -12,-10 Z"/><path d="M-6,-2 h.1 M0,-2 h.1 M6,-2 h.1" stroke-width="3.4"/>',
    'phone': '<path d="M-10,-11 Q-7,-13 -4,-10 L-1,-5 Q0,-2 -3,0 Q-1,5 4,8 Q6,5 9,6 L13,9 Q15,12 12,14 Q8,16 2,13 Q-8,7 -12,-3 Q-13,-8 -10,-11 Z"/>',
    'cal': '<rect x="-12" y="-9" width="24" height="21" rx="3"/><path d="M-12,-3 H12 M-6,-13 V-6 M6,-13 V-6 M-6,3 h.1 M0,3 h.1 M6,3 h.1 M-6,8 h.1 M0,8 h.1" />',
    'bell': '<path d="M-9,5 V-2 Q-9,-11 0,-11 Q9,-11 9,-2 V5 L12,8 H-12 Z"/><path d="M-3,11 Q0,14 3,11"/>',
}

def badge(icon, num):
    return ('<g><rect x="-23" y="-23" width="46" height="46" rx="13" fill="#16201d" opacity=".22" transform="translate(2,5)"/>'
            '<rect x="-23" y="-23" width="46" height="46" rx="13" fill="#F1F3F1"/>'
            '<g fill="none" stroke="#4f6962" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" transform="translate(-1,1)">%s</g>' % ICONS[icon] +
            '<circle cx="18" cy="-18" r="11.5" fill="%s" stroke="#F1F3F1" stroke-width="2"/>' % RUST +
            '<text x="18" y="-13.4" font-size="13" text-anchor="middle" fill="#FBF9F6" style="font-weight:900">%s</text></g>' % num)

def badge_at(T, x, y, icon, num, t_in=None, t_out=None, out_kind='pop', idle=1.0, spring=True):
    """plakietka na sprężynie: wyskok z nadmiarem, kołysanie (ruch wtórny), ping, zgaszenie."""
    c, fl, pg = uid('bg'), uid('bf'), uid('pg')
    fr = []
    if t_in is None:
        fr += [(0, 'opacity:1;transform:scale(1) rotate(0deg)')]
    else:
        fr += [(0, 'opacity:0;transform:scale(.2) rotate(-16deg)'), (t_in, 'opacity:0;transform:scale(.2) rotate(-16deg)', 'cubic-bezier(.2,.8,.3,1)'),
               (t_in + .11, 'opacity:1;transform:scale(1.05) rotate(6deg)', 'ease-in-out'), (t_in + .21, 'opacity:1;transform:scale(.975) rotate(-3deg)', 'ease-in-out'),
               (t_in + .31, 'opacity:1;transform:scale(1.01) rotate(1.2deg)', 'ease-in-out'), (t_in + .42, 'opacity:1;transform:scale(1) rotate(0deg)')]
    if t_out is not None:
        if out_kind == 'pop':
            fr += [(t_out, 'opacity:1;transform:scale(1) rotate(0deg)', 'cubic-bezier(.3,0,.6,1)'), (t_out + .07, 'opacity:1;transform:scale(1.07) rotate(-2deg)', 'cubic-bezier(.5,0,.8,.4)'),
                   (t_out + .24, 'opacity:0;transform:scale(.15) rotate(10deg)')]
        else:  # gaśnie miękko
            fr += [(t_out, 'opacity:1;transform:scale(1) rotate(0deg)', 'cubic-bezier(.4,0,.6,1)'), (t_out + .32, 'opacity:0;transform:scale(.6) rotate(0deg)')]
    A('.' + c, K(fr, T))
    S('.%s{animation:bfl %ss ease-in-out infinite alternate;animation-delay:-%ss}' % (fl, f(1.6 * idle + random.Random(x * 7 + y).uniform(0, .6)), f(random.Random(x + y * 3).uniform(0, 1.5))))
    ring = ''
    if t_in is not None:
        ring = '<circle cx="18" cy="-18" r="11.5" fill="none" stroke="%s" stroke-width="2.6" class="%s"/>' % (RUST, pg)
        S('.%s{transform-origin:18px -18px}' % pg)
        A('.' + pg, K([(0, 'opacity:0;transform:scale(1)'), (t_in + .06, 'opacity:0;transform:scale(1)', 'linear'), (t_in + .08, 'opacity:.9;transform:scale(1)', 'cubic-bezier(.2,.7,.3,1)'), (t_in + .5, 'opacity:0;transform:scale(2.7)')], T))
    if t_out is not None and out_kind == 'pop':
        pf = uid('pf')
        ring += '<circle r="26" fill="none" stroke="#F4F2EF" stroke-width="2" class="%s"/>' % pf
        A('.' + pf, K([(0, 'opacity:0;transform:scale(.6)'), (t_out + .12, 'opacity:0;transform:scale(.6)', 'linear'), (t_out + .14, 'opacity:.8;transform:scale(.8)', 'cubic-bezier(.2,.7,.3,1)'), (t_out + .5, 'opacity:0;transform:scale(1.7)')], T))
    return '<g transform="translate(%s,%s)"><g class="%s"><g class="%s">%s</g>%s</g></g>' % (f(x), f(y), fl, c, badge(icon, num), ring)

S('@keyframes bfl{from{transform:translateY(-2px) rotate(-1.6deg)}to{transform:translateY(2.4px) rotate(1.4deg)}}')

def ticket():
    """zaproszenie SheBalance 192×116, środek (0,0)"""
    return ('<g><rect x="-96" y="-58" width="192" height="116" rx="10" fill="#3a2a20" opacity=".18" transform="translate(3,5)"/>'
            '<rect x="-96" y="-58" width="192" height="116" rx="10" fill="#FBF9F6" stroke="%s" stroke-width="1.6"/>' % DKG +
            '<path d="M-86,-58 H86 A10,10 0 0 1 96,-48 V-26 H-96 V-48 A10,10 0 0 1 -86,-58 Z" fill="%s"/>' % SAGE +
            '<use href="#logoWord" transform="translate(0,-42) scale(.21)" style="color:#FBF9F6"/>' +
            '<use href="#signCur" transform="translate(-64,16) scale(.075)" style="color:%s"/>' % DKG +
            '<text x="16" y="12" font-size="27" text-anchor="middle" class="serif" fill="%s">Zaproszenie</text>' % INK +
            '<path d="M-36,24 H70" stroke="%s" stroke-width="1.3" stroke-dasharray="4 4"/>' % SAGE +
            '<text x="16" y="44" font-size="13.5" text-anchor="middle" fill="%s" style="font-weight:800;letter-spacing:.1em">TYLKO DLA CIEBIE</text>' % BROWN +
            '</g>')

def mug_svg(body='#F7F3EC', band=SAGE, rim='#e2d9cc', steam=True, sc=1.0):
    """kubek stojący; (0,0) = środek dna"""
    s = '<g transform="scale(%s)">' % f(sc)
    s += '<ellipse cx="0" cy="1" rx="30" ry="5.5" fill="#000" opacity=".12"/>'
    s += '<path d="M-21,-48 L21,-48 L19,-7 Q18,0 11,0 L-11,0 Q-18,0 -19,-7 Z" fill="%s" stroke="%s" stroke-width="1.2"/>' % (body, rim)
    s += '<path d="M20,-37 Q36,-37 34,-22 Q32,-11 18,-12" fill="none" stroke="%s" stroke-width="6"/>' % body
    s += '<path d="M-20.4,-28 L20.4,-28 L19.8,-19 L-19.8,-19 Z" fill="%s"/>' % band
    s += '<ellipse cx="0" cy="-48" rx="21" ry="5" fill="#6d4128"/><ellipse cx="0" cy="-48" rx="21" ry="5" fill="none" stroke="#efe6da" stroke-width="1.4"/>'
    s += '<path d="M-14,-44 Q-15,-24 -12,-8" stroke="#fff" stroke-width="3" opacity=".55" fill="none" stroke-linecap="round"/>'
    if steam:
        s += '<g transform="translate(0,-56)">%s</g>' % steam_paths('stm', 3, 46, 7, 3, '#FFFBF4', 12, '#d9c3ad')
    return s + '</g>'

def spruce(x, base, h, col):
    w = h * .36
    return ('<path d="M%s,%s L%s,%s L%s,%s L%s,%s L%s,%s L%s,%s L%s,%s Z" fill="%s"/>' % (
        f(x), f(base - h), f(x + w * .55), f(base - h * .55), f(x + w * .3), f(base - h * .55), f(x + w), f(base), f(x - w), f(base),
        f(x - w * .3), f(base - h * .55), f(x - w * .55), f(base - h * .55), col))

def autumn_tree(x, base, h, col):
    return ('<rect x="%s" y="%s" width="3" height="%s" fill="#5e4a3e"/>' % (f(x - 1.5), f(base - h * .45), f(h * .45)) +
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (f(x), f(base - h * .62), f(h * .3), f(h * .38), col))

DEFS = []
def D(s): DEFS.append(s)
for n in ('1.5', '2', '3', '4', '6', '10'):
    D('<filter id="bl%s" x="-25%%" y="-25%%" width="150%%" height="150%%"><feGaussianBlur stdDeviation="%s"/></filter>' % (n.replace('.', ''), n))

def rim_filter(fid, dx, dy, col, op, blur=1.4):
    D('<filter id="%s" x="-20%%" y="-12%%" width="140%%" height="124%%" color-interpolation-filters="sRGB">' % fid +
      '<feOffset in="SourceAlpha" dx="%s" dy="%s" result="o"/>' % (dx, dy) +
      '<feComposite in="SourceAlpha" in2="o" operator="out" result="e"/>'
      '<feGaussianBlur in="e" stdDeviation="%s" result="eb"/>' % blur +
      '<feComposite in="eb" in2="SourceAlpha" operator="in" result="ei"/>'
      '<feFlood flood-color="%s" flood-opacity="%s"/>' % (col, op) +
      '<feComposite in2="ei" operator="in" result="rim"/>'
      '<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="rim"/></feMerge></filter>')
rim_filter('rimCoolR', -5, 1, '#E8F2F3', .85)
rim_filter('rimWarmL', 5, 1, '#FFE6BC', .9)
rim_filter('rimWarmR', -5, 1, '#FFD9A0', .9)
rim_filter('rimSunL', 6, 2, '#FFEBC8', 1, 1.8)

def lg(id_, stops, x2=0, y2=1, x1=0, y1=0):
    D('<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>' % (id_, x1, y1, x2, y2, ''.join(
        '<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (o, c, a) for o, c, a in stops)))
def rg(id_, stops, cx=.5, cy=.5, r=.5):
    D('<radialGradient id="%s" cx="%s" cy="%s" r="%s">%s</radialGradient>' % (id_, cx, cy, r, ''.join(
        '<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (o, c, a) for o, c, a in stops)))

rg('coolGlow', [(0, '#7a948b', .55), (.6, '#5e766e', .2), (1, '#3f524c', 0)])
rg('rustGlow', [(0, RUST, .55), (.5, RUST, .18), (1, RUST, 0)])
rg('screenGlow', [(0, '#E6F3F5', .95), (.45, '#D8EAEE', .45), (1, '#D8EAEE', 0)])
rg('warmGlow', [(0, '#FFE2B0', .9), (.5, '#FFD9A0', .35), (1, '#FFD9A0', 0)])
rg('sunDisc', [(0, '#FFF6DE', 1), (.55, '#FCE6B8', 1), (1, '#F8D9A0', 1)])
rg('sunHalo', [(0, '#FFF0CC', .95), (.3, '#FBE1B0', .55), (1, '#F6D6A6', 0)])
rg('bulbG', [(0, '#FFF0C4', 1), (.35, '#FFD98A', .55), (1, '#FFD98A', 0)])
rg('fireG', [(0, '#FFD58A', .9), (.4, '#F6A55A', .45), (1, '#E9874A', 0)])
rg('haloEnd', [(0, '#FFF7E6', 1), (.55, '#F8EBD6', .7), (1, '#F2EFEB', 0)])
rg('logoHalo', [(0, '#FBEBD0', .95), (.5, '#F6E7D2', .55), (1, '#F2EFEB', 0)])
lg('scrimTop', [(0, DARK, .97), (.3, DARK, .9), (.62, DARK, .5), (1, DARK, 0)])
lg('scrimBot', [(0, '#1f2b27', 0), (1, '#1f2b27', .5)])
rg('srcShade', [(0, '#1b2622', .78), (.6, '#1b2622', .5), (1, '#1b2622', 0)])
lg('lidG', [(0, '#3d4945', 1), (1, '#2b3532', 1)], x2=1, y2=1)
lg('dawnSky', [(0, '#E9E3DA', 1), (.38, '#F1DFCB', 1), (.5, '#F6D7B0', 1), (.56, '#F8CF9E', 1), (1, '#F6D2A8', 1)])
lg('daySky', [(0, '#EFE6DA', 1), (.45, '#F5DFC4', 1), (.6, '#F7D6AE', 1), (1, '#F4D2AC', 1)])
lg('duskSky', [(0, '#4e6862', 1), (.32, '#7f948c', 1), (.52, '#C9AE98', 1), (.62, '#E7BC94', 1), (1, '#EDC39A', 1)])
lg('mistH', [(0, '#FBF4EA', 0), (.32, '#FBF4EA', .9), (.68, '#FBF4EA', .9), (1, '#FBF4EA', 0)], x2=1, y2=0)
lg('mistBand', [(0, '#FBF2E6', 0), (.5, '#FBF2E6', .9), (1, '#FBF2E6', 0)])
lg('hairOts', [(0, '#5e3a22', 1), (.45, '#7d5132', 1), (.8, '#a5723f', 1), (1, '#cf9b5e', 1)])
lg('kdBay', [(0, '#FFF8EC', 1), (.55, '#F3ECE1', 1), (1, '#DCD2C4', 1)], x2=1, y2=0)
lg('veilEdge', [(0, '#F1E3CF', 1), (1, '#F1E3CF', 0)])
lg('skyHill', [(0, '#E6ECE8', 1), (.3, '#EEF0E8', 1), (.45, '#F4EBDA', 1), (.6, '#F6E3C6', 1), (1, '#F2DCBA', 1)])
lg('valleyG', [(0, '#93AC92', 0), (.22, '#96AF90', 1), (1, '#A2BA8C', 1)])
lg('slopeG', [(0, '#A9C686', 1), (.45, '#94B573', 1), (1, '#7A9C60', 1)])
lg('hillGreen', [(0, '#89AC66', 1), (.3, '#7A9E5C', 1), (1, '#55774A', 1)])
lg('woodTop', [(0, '#a5826c', 1), (.25, '#8a6a56', 1), (1, '#7a5c4a', 1)])
lg('hillG', [(0, '#6c867c', 1), (1, '#4c655c', 1)])
lg('grassG', [(0, '#8fa896', 1), (1, '#6f8a7c', 1)])
lg('raysG', [(0, '#FFE7BD', .75), (1, '#FFE7BD', 0)])
lg('phoneScr', [(0, '#43524d', 1), (1, '#2a3431', 1)])
D('<g id="signCur" fill="currentColor" fill-rule="evenodd"><g transform="translate(%s,%s)"><path d="%s"/></g></g>' % (f(-SGX), f(-SGY), LOGO['sign']))
D('<g id="wIco"><ellipse cx="0" cy="-7.5" rx="8.6" ry="9.8" opacity=".55"/><circle cx="0" cy="-9.5" r="7"/><path d="M-12.5,15 C-12.5,5 -7.5,1.2 0,1.2 C7.5,1.2 12.5,5 12.5,15 Z"/></g>')
D('<clipPath id="btnClip"><rect x="-172" y="-46" width="344" height="92" rx="46"/></clipPath>')

# ================= SCENA 1: Liczba (0–1 s) =================
NUM_X, NUM_Y, NUM_FS = 281.2, 545, 200
RING_C, RING_R = (270, 470), 214
CAM1 = [(0, 270, 480, 1.0, 270, 480, -.7, 'cubic-bezier(.3,0,.25,1)'), (.7, 270, 480, 1.035, 270, 480, 0, 'cubic-bezier(.2,.8,.3,1)'), (.76, 270, 480, 1.055, 270, 480, 0, 'ease-out'), (1.0, 270, 480, 1.062, 270, 480, 0)]

def counter_vals():
    out = []
    for i in range(22):
        t = i * FR
        v = 57 if i == 21 else int(57 * (t / .7) ** 2.3 + 1e-9)
        if not out or out[-1][1] != v: out.append((t, v))
    return out

def ring_svg(lit_fn=None):
    """100 kresek (1 kreska = 1%); lit_fn(k) → klasa okna dla rdzawej kreski albo None (wszystkie 57 świecą)."""
    s = '<g>'
    for k in range(100):
        a = math.radians(-90 + k * 3.6); L = 16 if k % 10 == 0 else 10
        x1, y1 = RING_C[0] + math.cos(a) * RING_R, RING_C[1] + math.sin(a) * RING_R
        x2, y2 = RING_C[0] + math.cos(a) * (RING_R + L), RING_C[1] + math.sin(a) * (RING_R + L)
        s += '<path d="M%s,%s L%s,%s" stroke="#F2EFEB" stroke-opacity=".2" stroke-width="2" stroke-linecap="round"/>' % (f(x1), f(y1), f(x2), f(y2))
        if k < 57:
            cls = lit_fn(k) if lit_fn else ''
            s += '<path class="%s" d="M%s,%s L%s,%s" stroke="%s" stroke-width="3.4" stroke-linecap="round"/>' % (cls, f(x1), f(y1), f(x2), f(y2), '#D0683A')
    return s + '</g>'

def bokeh1():
    return ('<rect x="-300" y="-300" width="1140" height="1560" fill="%s"/>' % DARK +
            '<circle cx="270" cy="440" r="420" fill="url(#coolGlow)"/>' +
            bokeh(9, (-40, 60, 580, 900), ['#56706a', '#4b6159', '#62796f'], (34, 90), 57, (.35, .75)))

def sc_liczba():
    T = 1.0; s = []
    vals = counter_vals()
    for t, v in vals: ev(t, 'licznik: %d%%' % v)
    s.append('<rect x="-20" y="-20" width="580" height="1000" fill="%s"/>' % DARK)
    # rdzawe kreski zapalają się razem z licznikiem
    def lit(k):
        tk = next(t for t, v in vals if v >= k + 1)
        c = uid('rk'); show_win(c, T, tk, 99); return c
    s.append(layers('s1', T, CAM1, [(.25, bokeh1(), 'bl10'), (.6, ring_svg(lit), None)], 'linear'))
    # poświata przy 57
    s.append('<g class="gl1"><circle cx="270" cy="470" r="250" fill="url(#rustGlow)"/></g>')
    A('.gl1', K([(0, 'opacity:0'), (.68, 'opacity:0', 'cubic-bezier(.2,.8,.3,1)'), (.78, 'opacity:.85'), (1.0, 'opacity:.4')], T))
    # liczba (warstwa poza kamerą – ciągłość z kolejną sceną)
    num = '<g class="n1">'
    # smugi ruchu (motion blur) – tylko 2 pierwsze klatki
    for i, (dx, op) in enumerate([(-34, .32), (-70, .16)]):
        c = uid('mb')
        num += '<g class="%s" transform="translate(%s,0)">' % (c, dx) + T_('0%', 270, NUM_Y, NUM_FS, CREAM_T) + '</g>'
        A('.' + c, K([(0, 'opacity:%s' % op), (2 * FR, 'opacity:0')], T, 'linear'))
    for i, (t, v) in enumerate(vals):
        c = uid('d')
        t1 = vals[i + 1][0] if i + 1 < len(vals) else 99
        num += '<g class="%s">%s</g>' % (c, T_('%d%%' % v, 270, NUM_Y, NUM_FS, CREAM_T))
        show_win(c, T, t, t1)
    num += '</g>'
    s.append(num)
    S('.n1{transform-origin:270px 475px}')
    A('.n1', K([(0, 'transform:translateX(-62px) skewX(-15deg) scale(1.17,1)', 'linear'), (FR, 'transform:translateX(-16px) skewX(-6deg) scale(1.05,1)', 'linear'),
                (2 * FR, 'transform:translateX(5px) skewX(2deg) scale(.985,1)', 'cubic-bezier(.3,0,.3,1)'), (.16, 'transform:translateX(0) skewX(0deg) scale(1,1)'),
                (.7, 'transform:translateX(0) skewX(0deg) scale(1,1)', 'cubic-bezier(.2,.8,.3,1)'), (.79, 'transform:translateX(0) skewX(0deg) scale(1.05,1.05)', 'ease-in-out'),
                (.88, 'transform:translateX(0) skewX(0deg) scale(.995,.995)', 'ease-in-out'), (.96, 'transform:translateX(0) skewX(0deg) scale(1,1)')], T))
    ev(.7, 'licznik staje na 57% – „puls” (akcent)')
    s.append(vign(.55))
    s.append(source_block())
    return ''.join(s), T

# ================= SCENA 2: Chaos (1–4,5 s) =================
HEAD_57 = (-340, .6)          # przesunięcie i skala „57%” w nagłówku
BADGES = [  # (t, x, y, ikona, liczba)
    (.30, 70, 410, 'mail', '9+'), (.48, 470, 440, 'chat', '3'), (.66, 118, 520, 'phone', '3'), (.84, 486, 566, 'mail', '24'),
    (1.00, 62, 632, 'bell', '!'), (1.18, 470, 676, 'cal', '5'), (1.36, 150, 842, 'chat', '12'), (1.52, 396, 846, 'mail', '41'),
    (1.70, 66, 896, 'cal', '8'), (1.86, 270, 900, 'bell', '2'), (2.04, 478, 898, 'phone', '1'), (2.24, 160, 430, 'chat', '7'),
    (2.44, 438, 800, 'mail', '87'), (2.66, 300, 822, 'bell', '!')]
CUTS = [0, .62, 1.12, 1.62, 2.12, 3.5]
B5 = dict(cx=300, s=1.5, face=(300, 545))

def office_wall(col='#BAC4BF', win_x=-60, blinds='#DCE5E2', shelf=True):
    s = '<rect x="-400" y="-400" width="1340" height="1800" fill="%s"/>' % col
    s += '<rect x="%s" y="250" width="240" height="380" fill="%s"/>' % (win_x, blinds)
    s += ''.join('<rect x="%s" y="%s" width="240" height="7" fill="#c3cecb"/>' % (win_x, 256 + i * 15) for i in range(25))
    s += '<rect x="%s" y="250" width="240" height="380" fill="none" stroke="#a9b5b1" stroke-width="10"/>' % win_x
    if shelf:
        s += '<rect x="360" y="330" width="320" height="10" fill="#8f9893"/>'
        x = 372
        for i, (w, h, c) in enumerate([(18, 70, '#7f8f89'), (14, 82, '#9a958c'), (22, 64, '#6f7d78'), (16, 76, '#a3a9a2'), (26, 58, '#8a8278'), (14, 80, '#788883')]):
            s += '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (x, 330 - h, w, h, c); x += w + 3
        s += '<rect x="360" y="470" width="320" height="10" fill="#8f9893"/><ellipse cx="420" cy="452" rx="26" ry="20" fill="#6c7f78"/><rect x="404" y="452" width="32" height="20" fill="#9a958c"/>'
    return s

def cut_laptop(T, t0, t1):
    fx, fy = 270, 540
    frames = [(x[0], x[1], x[2], x[3] * 1.12) + x[4:] for x in jerk_cam(t0, t1, fx, fy, 270, 592, 1.045, (12, -6, 1.075, -1.1))]
    bg = office_wall()
    mid = ''.join('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#55695f" transform="rotate(%s %s %s)"/>' % (x, y, rx, ry, a, x, y) for x, y, rx, ry, a in
                  [(500, 470, 40, 90, 20), (470, 520, 34, 80, -25), (530, 560, 40, 86, 35), (490, 600, 30, 70, -10)])
    mid += '<rect x="455" y="600" width="80" height="60" rx="6" fill="#8f8a82"/>'
    # biurko i laptop
    foc = '<rect x="-300" y="640" width="1140" height="700" fill="#A7A39B"/><rect x="-300" y="640" width="1140" height="5" fill="#bdb9b1"/>'
    foc += '<path d="M60,642 L480,642 L462,668 L78,668 Z" fill="#c9cdca"/><path d="M60,642 L480,642 L478,646 L62,646 Z" fill="#e0e3e1"/>'
    foc += '<rect x="92" y="402" width="356" height="244" rx="13" fill="#2b3532"/>'
    foc += '<rect x="104" y="414" width="332" height="216" rx="4" fill="#EEF2F0"/>'
    foc += '<rect x="104" y="414" width="332" height="26" fill="#9db0a9"/><circle cx="118" cy="427" r="4" fill="#EEF2F0"/><circle cx="131" cy="427" r="4" fill="#EEF2F0"/>'
    foc += '<rect x="104" y="440" width="74" height="190" fill="#e1e7e4"/>' + ''.join('<rect x="114" y="%s" width="%s" height="6" rx="3" fill="#b9c6c1"/>' % (456 + i * 20, w) for i, w in enumerate((48, 36, 44, 30, 40)))
    # lista maili płynie w dół (nowe od góry)
    cid = uid('scr')
    foc += '<clipPath id="%s"><rect x="250" y="440" width="186" height="190"/></clipPath><g clip-path="url(#%s)"><g class="ml2">' % (cid, cid)
    for i in range(-8, 7):
        y = 456 + i * 30
        foc += '<circle cx="266" cy="%s" r="8" fill="%s"/><rect x="282" y="%s" width="%s" height="6" rx="3" fill="%s"/><rect x="282" y="%s" width="%s" height="5" rx="2.5" fill="#c9d2ce"/>' % (
            y, ['#9db0a9', '#c9a58f', '#8fa39c'][i % 3], y - 7, 90 + (i * 37) % 50, '#3d4a46' if i < 0 else '#8b9792', y + 4, 120 - (i * 23) % 40)
    foc += '</g></g>'
    A('.ml2', K([(0, 'transform:translateY(0)'), (t0 + .06, 'transform:translateY(0)', 'cubic-bezier(.4,0,.3,1)'), (t0 + .52, 'transform:translateY(240px)')], T))
    # koperta + licznik 12 → 87
    foc += '<g transform="translate(176,540)"><rect x="-44" y="-32" width="88" height="64" rx="7" fill="none" stroke="%s" stroke-width="5"/><path d="M-42,-28 L0,6 L42,-28" fill="none" stroke="%s" stroke-width="5" stroke-linejoin="round"/></g>' % (DKG, DKG)
    vals = [12, 16, 21, 27, 34, 42, 50, 58, 66, 73, 79, 84, 87]
    foc += '<g transform="translate(222,500)"><circle r="33" fill="%s"/><circle r="33" fill="none" stroke="#EEF2F0" stroke-width="3"/>' % RUST
    for i, v in enumerate(vals):
        c = uid('mv'); ta = t0 + .06 + i * .035; tb = t0 + .06 + (i + 1) * .035 if i + 1 < len(vals) else 99
        foc += '<g class="%s">%s</g>' % (c, T_(str(v), 0, 10.5, 30, '#FBF9F6', serif=False, weight=900))
        show_win(c, T, ta if i else 0, tb)
    foc += '</g>'
    ev(1 + t0 + .06, 'laptop: licznik maili rusza (12)'); ev(1 + t0 + .06 + 12 * .035, 'laptop: 87 maili')
    foc += '<ellipse cx="270" cy="520" rx="340" ry="260" fill="url(#screenGlow)" opacity=".28" style="mix-blend-mode:screen"/>'
    fg = mug_svg('#e9ece9', '#8fa39c', '#cfd6d3', steam=False, sc=2.6).replace('<g transform="scale(2.6)">', '<g transform="translate(40,880) scale(2.6)">', 1)
    return layers('cu1', T, frames, [(.3, bg, 'bl3'), (.62, mid, 'bl2'), (1, foc, None), (1.6, fg, 'bl6')], 'linear')

def cut_phone(T, t0, t1):
    frames = jerk_cam(t0, t1, 270, 585, 270, 610, 1.04, (-12, 8, 1.08, 1.2), (-6, 4))
    bg = '<rect x="-400" y="-400" width="1340" height="1800" fill="#AEB3AC"/>'
    bg += ''.join('<rect x="-400" y="%s" width="1340" height="3" fill="#a3a8a1"/>' % y for y in range(300, 1100, 46))
    bg += '<g transform="translate(70,420) rotate(-14)"><rect x="-90" y="-60" width="180" height="130" rx="4" fill="#E6E4DE"/><path d="M0,-60 V70" stroke="#cfccc4" stroke-width="3"/>' + ''.join('<path d="M%s,%s h70" stroke="#c4c1b9" stroke-width="3"/>' % (x, y) for x in (-80, 10) for y in range(-36, 60, 16)) + '</g>'
    bg += '<g transform="translate(455,770) rotate(18)" fill="none" stroke="#3a4643" stroke-width="7"><circle cx="-34" cy="0" r="26"/><circle cx="34" cy="0" r="26"/><path d="M-8,0 Q0,-8 8,0"/></g>'
    bg += '<circle cx="440" cy="400" r="40" fill="none" stroke="#9a8f84" stroke-width="5" opacity=".6"/>'
    ph = uid('ph')
    foc = '<g transform="translate(270,585) rotate(-10)"><g class="%s">' % ph
    foc += '<rect x="-104" y="-204" width="208" height="408" rx="32" fill="#1c2422" opacity=".3" transform="translate(8,12)"/>'
    foc += '<rect x="-104" y="-204" width="208" height="408" rx="32" fill="#232b29"/><rect x="-94" y="-194" width="188" height="388" rx="24" fill="url(#phoneScr)"/>'
    foc += '<rect x="-30" y="-188" width="60" height="12" rx="6" fill="#1a2120"/>'
    foc += '<g opacity=".55"><circle cx="0" cy="-104" r="38" fill="none" stroke="#9fb3ad" stroke-width="2"/><circle cx="0" cy="-112" r="12" fill="#9fb3ad"/><path d="M-20,-80 Q0,-100 20,-80" fill="#9fb3ad"/></g>'
    foc += '<rect x="-90" y="-30" width="180" height="74" rx="14" fill="#F4F2EF" opacity=".96"/>'
    foc += '<circle cx="-66" cy="7" r="15" fill="%s"/><g transform="translate(-66,7) scale(.66)" fill="#FBF9F6">%s</g>' % (RUST, ICONS['phone'].replace('<path ', '<path fill="#FBF9F6" '))
    foc += T_('3 nieodebrane', -44, 3, 18.5, INK, '', 'start', False, 800) + '<rect x="-44" y="16" width="86" height="6" rx="3" fill="#b9c2be"/>'
    foc += '<rect x="-84" y="56" width="168" height="40" rx="12" fill="#F4F2EF" opacity=".35"/>'
    foc += '</g>'
    # łuki wibracji
    for side in (-1, 1):
        for k in range(3):
            c = uid('vb')
            foc += '<path class="%s" d="M%s,-40 Q%s,0 %s,40" fill="none" stroke="%s" stroke-width="3.4" stroke-linecap="round"/>' % (c, f(side * (122 + k * 14)), f(side * (134 + k * 14)), f(side * (122 + k * 14)), RUST)
            fr = [(0, 'opacity:0')]
            for tb in (t0 + .04, t0 + .27):
                fr += [(tb + k * .03, 'opacity:0', 'linear'), (tb + k * .03 + .04, 'opacity:.85', 'linear'), (tb + .17, 'opacity:0')]
            A('.' + c, K(fr, T, 'linear'))
    foc += '</g>'
    fr = [(0, 'transform:translate(0,0) rotate(0deg)')]
    for tb in (t0 + .04, t0 + .27):
        fr.append((tb - .01, 'transform:translate(0,0) rotate(0deg)'))
        for i in range(6): fr.append((tb + .028 * (i + 1), 'transform:translate(%spx,%spx) rotate(%sdeg)' % (f(3.2 * (-1) ** i), f(1.2 * (-1) ** (i // 2)), f(1.6 * (-1) ** i))))
        fr.append((tb + .2, 'transform:translate(0,0) rotate(0deg)'))
    A('.' + ph, K(fr, T, 'ease-in-out'))
    ev(1 + t0 + .04, 'telefon wibruje (1) – „3 nieodebrane”'); ev(1 + t0 + .27, 'telefon wibruje (2)')
    fg = '<g transform="translate(470,930) rotate(-38)"><rect x="-150" y="-9" width="300" height="18" rx="9" fill="#2f3b37"/><rect x="120" y="-9" width="30" height="18" rx="4" fill="%s"/></g>' % RUST
    return layers('cu2', T, frames, [(.35, bg, 'bl3'), (1, foc, None), (1.6, fg, 'bl6')], 'linear')

def cut_calendar(T, t0, t1):
    frames = jerk_cam(t0, t1, 270, 590, 270, 612, 1.05, (14, 10, 1.08, -1.3), (10, -6))
    bg = office_wall('#B7C1BC', 400, '#D6DFDC', False) + '<circle cx="90" cy="360" r="56" fill="#E6EAE8"/><circle cx="90" cy="360" r="56" fill="none" stroke="#8f9b96" stroke-width="6"/><path d="M90,360 V322 M90,360 L114,372" stroke="#5d6b66" stroke-width="5" stroke-linecap="round"/>'
    foc = '<g transform="rotate(3 270 590)">'
    foc += '<rect x="58" y="402" width="424" height="378" rx="8" fill="#2a3532" opacity=".25" transform="translate(6,10)"/>'
    foc += '<rect x="58" y="402" width="424" height="378" rx="8" fill="#F5F3EE"/>'
    foc += '<rect x="58" y="402" width="424" height="52" rx="8" fill="#6f857e"/><rect x="58" y="440" width="424" height="14" fill="#6f857e"/>'
    foc += ''.join('<rect x="%s" y="390" width="8" height="28" rx="4" fill="#5d6b66"/>' % x for x in range(92, 470, 44))
    days = ['PN', 'WT', 'ŚR', 'CZ', 'PT']
    cw, chh, gx, gy = 78, 44, 78, 470
    for i, d in enumerate(days):
        foc += T_(d, gx + i * cw + cw / 2 - 4, 436, 16, '#F4F2EF', '', 'middle', False, 800, 'letter-spacing:.08em')
    foc += ''.join('<path d="M%s,%s h%s" stroke="#e1ddd5" stroke-width="1.4"/>' % (gx - 6, gy + j * chh, cw * 5) for j in range(8))
    rr = random.Random(9)
    cols = ['#9db0a9', '#8fa39c', RUST, '#C9B3A6', '#b5bfbb', '#C9A55A', '#7f958d']
    k = 0
    order = [(i, j) for j in range(7) for i in range(5)]
    rr.shuffle(order)
    for (i, j) in order:
        c = uid('cb'); x = gx + i * cw + 3; y = gy + j * chh + 3
        col = cols[rr.randrange(len(cols))]
        h = chh - 6 if rr.random() > .25 else chh * 2 - 6
        foc += '<g class="%s"><rect x="%s" y="%s" width="%s" height="%s" rx="6" fill="%s"/><rect x="%s" y="%s" width="%s" height="5" rx="2.5" fill="#FBF9F6" opacity=".7"/></g>' % (
            c, x, y, cw - 10, f(min(h, gy + 7 * chh - y - 3)), col, x + 8, y + 9, rr.randint(24, 50))
        S('.%s{transform-box:fill-box;transform-origin:50%% 50%%}' % c)
        tk = t0 + .03 + k * .011
        A('.' + c, K([(0, 'opacity:0;transform:scale(.4)'), (tk, 'opacity:0;transform:scale(.4)', 'cubic-bezier(.2,.8,.3,1)'), (tk + .12, 'opacity:1;transform:scale(1)')], T))
        k += 1
    # podwójnie zajęty termin
    foc += '<g transform="translate(%s,%s) rotate(-6)"><rect x="-40" y="-20" width="80" height="40" rx="7" fill="%s" stroke="#FBF9F6" stroke-width="2.5"/>' % (gx + 2 * cw + cw / 2, gy + 3 * chh + 18, RUST)
    foc += T_('!', 0, 9, 26, '#FBF9F6', serif=False, weight=900) + '</g>'
    foc += '</g>'
    ev(1 + t0 + .03, 'kalendarz zapełnia się blokami (do %.2f)' % (1 + t0 + .03 + k * .011))
    fg = '<g transform="translate(60,930) rotate(28)"><rect x="-160" y="-10" width="320" height="20" rx="4" fill="%s"/><path d="M160,-10 L190,0 L160,10 Z" fill="#e9d8c4"/></g>' % MUST
    return layers('cu3', T, frames, [(.3, bg, 'bl3'), (1, foc, None), (1.6, fg, 'bl6')], 'linear')

def cut_alarm(T, t0, t1):
    frames = [(x[0], x[1], x[2], x[3] * 1.1) + x[4:] for x in jerk_cam(t0, t1, 270, 600, 270, 622, 1.05, (-14, -10, 1.085, 1.4), (-8, 0))]
    bg = '<rect x="-400" y="-400" width="1340" height="1800" fill="#97A4A1"/>'
    bg += '<rect x="300" y="200" width="300" height="420" fill="#C7D3D4"/><rect x="300" y="200" width="300" height="420" fill="none" stroke="#7f8d8a" stroke-width="12"/><path d="M450,200 V620 M300,410 H600" stroke="#7f8d8a" stroke-width="8"/>'
    bg += '<path d="M260,180 Q300,420 250,700 L180,700 Q230,420 200,180 Z" fill="#8a9895"/>'
    mid = '<g transform="translate(70,520)"><path d="M-50,-90 L50,-90 L70,10 L-70,10 Z" fill="#D7D2C8"/><rect x="-6" y="10" width="12" height="150" fill="#6f7a76"/></g>'
    foc = '<rect x="-300" y="690" width="1140" height="700" fill="#857d73"/><rect x="-300" y="690" width="1140" height="6" fill="#9a9288"/>'
    cl = uid('al')
    foc += '<g transform="translate(270,600)"><g class="%s">' % cl
    foc += '<path d="M-110,92 L-130,112 M110,92 L130,112" stroke="#4d5a56" stroke-width="10" stroke-linecap="round"/>'
    foc += '<g class="hm%s"><path d="M0,-118 V-96" stroke="#4d5a56" stroke-width="7"/><circle cx="0" cy="-122" r="8" fill="#4d5a56"/></g>' % cl
    for sx in (-1, 1):
        foc += '<path d="M%s,-92 A44,44 0 0 1 %s,-92 Z" fill="#E9EDEA" stroke="#4d5a56" stroke-width="5" transform="rotate(%s %s -92)"/>' % (f(sx * 72 - 44), f(sx * 72 + 44), f(sx * 22), f(sx * 72))
    foc += '<rect x="-136" y="-92" width="272" height="190" rx="40" fill="#20292a" opacity=".25" transform="translate(6,10)"/>'
    foc += '<rect x="-136" y="-92" width="272" height="190" rx="40" fill="#E9EDEA" stroke="#4d5a56" stroke-width="5"/>'
    foc += '<rect x="-104" y="-58" width="208" height="120" rx="14" fill="#232c2a"/>'
    foc += '<ellipse cx="0" cy="2" rx="92" ry="50" fill="url(#warmGlow)" opacity=".35"/>'
    foc += T_('6:00', 0, 30, 78, '#F2C46B', '', 'middle', False, 800, 'letter-spacing:.02em')
    foc += '</g></g>'
    S('.hm%s{transform-origin:0 -96px}' % cl)
    fr = [(0, 'transform:rotate(0deg) translateY(0px)')]; fh = [(0, 'transform:rotate(0deg)')]
    i = 0; t = t0 + .02
    while t < t1 - 1e-6:
        fr.append((t, 'transform:rotate(%sdeg) translateY(%spx)' % (f(3.4 * (-1) ** i), f(-2 if i % 2 else 0))))
        fh.append((t, 'transform:rotate(%sdeg)' % f(26 * (-1) ** i)))
        t += FR; i += 1
    S('.%s{transform-origin:0 98px}' % cl)
    A('.' + cl, K(fr, T, 'ease-in-out'))
    A('.hm' + cl, K(fh, T, 'ease-in-out'))
    for sx in (-1, 1):
        for k in range(3):
            c = uid('rg'); r = 62 + k * 17
            a0, a1 = (-160, -105) if sx < 0 else (-75, -20)
            bx, by = 270 + sx * 72, 508
            foc += '<path class="%s" d="M%s,%s A%s,%s 0 0 1 %s,%s" fill="none" stroke="%s" stroke-width="3.6" stroke-linecap="round"/>' % (
                c, f(bx + r * math.cos(math.radians(a0))), f(by + r * math.sin(math.radians(a0))), r, r, f(bx + r * math.cos(math.radians(a1))), f(by + r * math.sin(math.radians(a1))), MUST)
            A('.' + c, K([(0, 'opacity:0'), (t0 + .03 + k * .05, 'opacity:0', 'linear'), (t0 + .08 + k * .05, 'opacity:.9', 'linear'), (t0 + .3 + k * .05, 'opacity:.25', 'linear'), (t0 + .42, 'opacity:.85')], T, 'linear'))
    ev(1 + t0 + .02, 'budzik 6:00 dzwoni')
    fg = '<path d="M-200,1000 Q40,860 200,900 Q330,930 420,1000 Z" fill="#E7E9E6"/>'
    return layers('cu4', T, frames, [(.3, bg, 'bl4'), (.6, mid, 'bl2'), (1, foc, None), (1.6, fg, 'bl6')], 'linear')

TEMPLE = (190, 152)

def cut_brunetka(T, t0, t1, inst='sB2'):
    fx, fy = B5['face']; s = B5['s']; cx = B5['cx']
    feet = fy + (712 - 135) * s
    frames = jerk_cam(t0, t0 + .98, fx, fy, fx, fy, 1.075, (-10, 6, 1.1, -1), (0, 0)) + [(T, fx, fy, 1.08, fx, fy, 0)]
    bg = office_wall('#B3BDB8', 330, '#E1E9E6', False)
    bg += '<rect x="-200" y="300" width="300" height="12" fill="#8f9893"/>' + ''.join('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (x, 300 - h, w, h, c) for x, w, h, c in [(-60, 22, 80, '#7f8f89'), (-34, 16, 92, '#9a958c'), (-14, 26, 70, '#6f7d78'), (16, 18, 86, '#a3a9a2'), (38, 30, 64, '#8a8278')])
    mid = ''.join('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#4f6560" transform="rotate(%s %s %s)"/>' % (x, y, rx, ry, a, x, y) for x, y, rx, ry, a in
                  [(30, 520, 50, 110, -20), (90, 580, 44, 100, 25), (10, 660, 56, 110, -40), (110, 700, 40, 90, 40)])
    post = ghost_fore('B', inst, fingers())
    foc = FIGR('B', inst, cx, feet, s, post=post, rim='rimCoolR')
    foc += '<ellipse cx="200" cy="760" rx="300" ry="280" fill="url(#screenGlow)" opacity=".42" style="mix-blend-mode:screen"/>'
    fg = '<g><rect x="-160" y="790" width="380" height="260" rx="22" fill="#26302d"/><rect x="-160" y="790" width="380" height="10" rx="5" fill="#cfe2e6" opacity=".8"/></g>'
    # poza: dłoń przy skroni, oczy zamknięte, ciężki oddech
    tt = TEMPLE
    rig_side(inst, 'B', T, 'R', [(0, tt, None, 'out'), (t0 + .3, (tt[0] + 2, tt[1] - 3), None, 'out'), (t0 + .55, (tt[0] - 1, tt[1] + 2), None, 'out'), (t0 + .8, (tt[0] + 2, tt[1] - 2), None, 'out'), (T, tt, None, 'out')])
    head(inst, T, [(0, 7, 3, 3), (t0 + .5, 8, 3, 5), (T, 9, 4, 6)])
    eyes_kf(inst, T, [(0, .1), (t0 + .4, .1), (t0 + .5, .04), (t0 + .75, .04), (t0 + .85, .12), (T, .1)])
    smile_kf(inst, T, [(0, .9, .7), (T, .88, .65)])
    body_kf(inst, T, [(0, 0, 1), (t0 + .2, -3, 1.006), (t0 + .75, 5, .996), (T, 6, .995)])
    return layers('cu5', T, frames, [(.3, bg, 'bl4'), (.6, mid, 'bl2'), (1, foc, None), (1.5, fg, 'bl6')], 'linear')

def sc_chaos():
    T = 3.5; s = []
    cell0 = (90, 290.5)
    s.append('<rect x="-20" y="-20" width="580" height="1000" fill="%s"/>' % DARK)
    s.append('<g class="bq2"><g filter="url(#bl10)">%s</g></g>' % bk3())
    A('.bq2', K([(0, 'opacity:0'), (3.08, 'opacity:0', EIO), (3.42, 'opacity:1')], T))
    makers = [cut_laptop, cut_phone, cut_calendar, cut_alarm]
    for i, fn in enumerate(makers):
        c = uid('cut'); show_win(c, T, CUTS[i], CUTS[i + 1])
        s.append('<g class="%s">%s</g>' % (c, fn(T, CUTS[i], CUTS[i + 1])))
        ev(1 + CUTS[i], 'cięcie: %s' % ['laptop', 'telefon', 'kalendarz', 'budzik'][i])
    ev(1 + CUTS[4], 'cięcie: brunetka przy biurku, dłoń przy skroni')
    # ujęcie 5 + przejście irysem do sylwetki w siatce (match-cut)
    c5 = uid('cut'); show_win(c5, T, CUTS[4], 99)
    FX, FY = B5['face'][0], B5['face'][1] - 5
    k = 8.6 / 82
    iw, ic, it = uid('iw'), uid('ic'), uid('it')
    s.append('<g class="%s"><g class="%s"><clipPath id="irisC"><circle class="%s" cx="%s" cy="%s" r="82"/></clipPath><g clip-path="url(#irisC)">%s%s'
             '<circle class="%s" cx="%s" cy="%s" r="90" fill="%s"/></g></g></g>' % (c5, iw, ic, FX, FY, cut_brunetka(T, CUTS[4], T), overlay('#8DA19C', .2, 'multiply'), it, FX, FY, RUST))
    S('.%s{transform-origin:%spx %spx}' % (ic, FX, FY))
    A('.' + ic, K([(0, 'transform:scale(12)'), (3.06, 'transform:scale(12)', 'cubic-bezier(.65,0,.3,1)'), (3.34, 'transform:scale(1)')], T))
    S('.%s{transform-origin:0 0}' % iw)
    A('.' + iw, K([(0, 'transform:translate(0px,0px) scale(1) translate(0px,0px)'), (3.2, 'transform:translate(%spx,%spx) scale(1) translate(%spx,%spx)' % (FX, FY, -FX, -FY), 'cubic-bezier(.55,0,.2,1)'),
                   (3.5, 'transform:translate(%spx,%spx) scale(%s) translate(%spx,%spx)' % (cell0[0], cell0[1], f4(k), -FX, -FY))], T))
    A('.' + it, K([(0, 'opacity:0'), (3.3, 'opacity:0', 'ease-in'), (3.47, 'opacity:1')], T))
    ev(4.2, 'MATCH-CUT start: kadr z brunetką zamyka się w kółko (irys)'); ev(4.5, '… twarz brunetki = pierwsza rdzawa sylwetka w siatce')
    # chłodna korekcja (akt 1) nad ujęciami 1–4
    s.append('<g class="gr2">%s</g>' % overlay('#8DA19C', .2, 'multiply'))
    show_win('gr2', T, 0, CUTS[4])
    s.append('<g class="sb2"><rect x="-20" y="700" width="580" height="280" fill="url(#scrimBot)"/><ellipse cx="170" cy="734" rx="230" ry="62" fill="url(#srcShade)"/></g>')
    A('.sb2', K([(0, 'opacity:0'), (.2, 'opacity:0'), (.45, 'opacity:1'), (3.0, 'opacity:1', EIO), (3.25, 'opacity:0')], T))
    s.append(vign(.55))
    # nagłówek: ciemny panel unosi się z pełnego kadru do góry
    ring_end = cam_tf(CAM1[-1], .6)
    s.append('<g class="pn2"><rect x="-20" y="-1400" width="580" height="1651" fill="%s"/><rect x="-20" y="250" width="580" height="230" fill="url(#scrimTop)"/>' % DARK +
             '<g class="bk2" style="%s"><g filter="url(#bl10)">%s</g></g></g>' % (cam_tf(CAM1[-1], .25), bokeh1()))
    A('.pn2', K([(0, 'opacity:1;transform:translateY(710px)'), (.05, 'opacity:1;transform:translateY(710px)', 'cubic-bezier(.5,0,.15,1)'), (.42, 'opacity:1;transform:translateY(-4px)', 'ease-in-out'),
                 (.52, 'opacity:1;transform:translateY(0)'), (3.0, 'opacity:1;transform:translateY(0)', EIO), (3.22, 'opacity:0;transform:translateY(0)')], T))
    A('.bk2', K([(0, 'opacity:1;' + cam_tf(CAM1[-1], .25)), (.4, 'opacity:0;' + cam_tf(CAM1[-1], .25))], T))
    ev(1.05, 'ciemny panel odsłania chaos (wipe w górę)')
    # pierścień ze sceny 1 – wylatuje do przodu i gaśnie
    s.append('<g class="rg2" style="transform-origin:270px 470px"><g style="%s">%s</g></g>' % (ring_end, ring_svg()))
    A('.rg2', K([(0, 'opacity:1;transform:scale(1)'), (.3, 'opacity:0;transform:scale(1.35)')], T, 'cubic-bezier(.4,0,.6,1)'))
    # plakietki
    for i, (tb, x, y, ic_, num) in enumerate(BADGES):
        s.append(badge_at(T, x, y, ic_, num, tb, 2.94 + (i % 5) * .045, 'fade'))
        ev(1 + tb, 'plakietka %d (ping) %s' % (i + 1, num))
    # „57%” – z rozmiaru sceny 1 do nagłówka (antycypacja, rozciągnięcie, osiadanie)
    s.append('<g class="n2">' + T_('57%', 270, NUM_Y, NUM_FS, CREAM_T) + '</g>')
    S('.n2{transform-origin:270px %spx}' % NUM_Y)
    dy, sc = HEAD_57
    A('.n2', K([(0, 'opacity:1;transform:translateY(0) scale(1,1)'), (.07, 'opacity:1;transform:translateY(12px) scale(1.02,.98)', 'cubic-bezier(.6,0,.4,1)'),
                (.24, 'opacity:1;transform:translateY(%spx) scale(%s,%s)' % (f(dy * .8), f(sc * 1.04), f(sc * 1.22)), 'cubic-bezier(.2,.6,.3,1)'),
                (.33, 'opacity:1;transform:translateY(%spx) scale(%s,%s)' % (f(dy - 6), f(sc), f(sc * .96)), 'ease-in-out'), (.42, 'opacity:1;transform:translateY(%spx) scale(%s,%s)' % (f(dy), f(sc), f(sc))),
                (3.0, 'opacity:1;transform:translateY(%spx) scale(%s,%s)' % (f(dy), f(sc), f(sc)), 'cubic-bezier(.55,0,.75,.3)'), (3.2, 'opacity:0;transform:translateY(%spx) scale(%s,%s)' % (f(dy - 30), f(sc), f(sc)))], T))
    s.append(line_up(T, STAT1, 270, 262, 34, .26, CREAM_T, st=.07, t_out=2.98))
    s.append(line_up(T, STAT2, 270, 299, 25, .46, CREAM_T, st=.06, t_out=3.04))
    ev(1.26, 'napis: „pracujących kobiet w Polsce”'); ev(1.46, 'napis: „codziennie odczuwa wysoki poziom stresu.”')
    s.append('<g class="src2">%s</g>' % source_block())
    return ''.join(s), T

# ================= SCENA 3: Ponad połowa (4,5–7 s) =================
def bk3():
    return ('<rect x="-300" y="-300" width="1140" height="1560" fill="%s"/><circle cx="270" cy="470" r="460" fill="url(#coolGlow)"/>' % DARK +
            bokeh(8, (-60, 40, 600, 920), ['#56706a', '#4b6159', '#62796f'], (40, 100), 7, (.3, .7)))

GRID0, CELL = (90, 300), 40

def sc_polowa():
    T = 2.5; s = []
    s.append('<rect x="-20" y="-20" width="580" height="1000" fill="%s"/>' % DARK)
    cam = [(0, 270, 480, 1.0, 270, 480, 0, 'cubic-bezier(.35,0,.25,1)'), (T, 282, 482, 1.06, 270, 480, 0)]
    bk = bk3()
    grid = ''
    times = {}
    for kk in range(1, 57):
        y = kk / 56
        times[kk] = .32 + 1.18 * math.acos(1 - 2 * y) / math.pi
    for j in range(10):
        for i in range(10):
            kk = j * 10 + i
            x, y = GRID0[0] + i * CELL, GRID0[1] + j * CELL
            d = math.hypot(i, j) / math.hypot(9, 9)
            g = '<g transform="translate(%s,%s)">' % (x, y)
            if kk > 0:
                g += '<g class="gin" style="--dl:%ss"><use href="#wIco" fill="%s" opacity=".42"/></g>' % (f(d * .3), SAGE)
            if kk < 57:
                dl = -1 if kk == 0 else times[kk]
                g += '<g class="lit" style="--dl:%ss;--k:%s"><circle r="17" fill="url(#rustGlow)"/><use href="#wIco" fill="#C9653A"/></g>' % (f(dl), kk)
            grid += g + '</g>'
    S('.scene.active .gin{transform-box:fill-box;transform-origin:50% 50%;animation:gin .34s cubic-bezier(.2,.9,.25,1) both;animation-delay:var(--dl)}'
      '@keyframes gin{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}')
    S('.scene.active .lit{transform-box:fill-box;transform-origin:50% 50%;animation:lit .34s cubic-bezier(.2,.9,.25,1.02) both, lpu .42s ease-in-out forwards;'
      'animation-delay:var(--dl), calc(1.62s + var(--k) * 7ms)}'
      '@keyframes lit{from{opacity:0;transform:scale(1.5)}to{opacity:1;transform:none}}@keyframes lpu{0%,100%{transform:none}45%{transform:scale(1.14)}}')
    ev(4.5 + times[1], 'sylwetki: zapalanie start (2/57)'); ev(4.5 + times[50], 'sylwetki: 50/100 zapalone'); ev(4.5 + times[56], 'sylwetki: 57/100 – koniec zapalania')
    ev(4.5 + 1.62, 'fala/puls 57 sylwetek')
    motes = bokeh(7, (0, 120, 540, 880), ['#F2EFEB'], (5, 12), 3, (.08, .16))
    s.append(layers('s3', T, cam, [(.25, bk, 'bl10'), (1, grid, None), (1.6, motes, 'bl4')], 'linear'))
    s.append(vign(.55))
    ttl = T_('Ponad połowa.', 270, 222, 64, CREAM_T, 'wsplit pw', style='--d0:1.28s;--st:.12s')
    s.append(ttl)
    ev(4.5 + 1.28, 'napis „Ponad połowa.”')
    s.append(source_block())
    return ''.join(s), T

# ================= SCENA 4: Zatrzymanie (7–10 s) =================
A4 = dict(cx=140, feet=900, s=.8); B4 = dict(cx=335, feet=900, s=.8)
DESK4 = 660
LAP = dict(cx=452, w=210, h=136)

def office4():
    s = '<rect x="-400" y="-400" width="1340" height="1800" fill="#D7D3CB"/>'
    s += '<rect x="-60" y="120" width="250" height="440" fill="#EEF0EA"/>'
    s += ''.join('<rect x="-60" y="%s" width="250" height="9" fill="#d9dbd4"/>' % (126 + i * 17) for i in range(26))
    s += '<rect x="-60" y="120" width="250" height="440" fill="none" stroke="#bdb6aa" stroke-width="12"/>'
    s += '<rect x="420" y="240" width="300" height="12" fill="#a99f92"/><rect x="420" y="400" width="300" height="12" fill="#a99f92"/>'
    x = 430
    for w, h, c in [(20, 84, '#9a8a7e'), (16, 96, '#b7a99c'), (26, 70, '#7f8f89'), (18, 90, '#c3b6a8'), (30, 62, '#8f7f73'), (16, 88, '#a6b3ad')]:
        s += '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (x, 240 - h, w, h, c); x += w + 3
    s += '<ellipse cx="480" cy="380" rx="34" ry="26" fill="#7d917f"/><rect x="460" y="378" width="40" height="22" fill="#c9b8a8"/>'
    s += '<rect x="250" y="150" width="110" height="140" fill="#e6e0d6" stroke="#bdb2a4" stroke-width="6"/><path d="M262,262 L292,222 L312,244 L330,214 L350,262 Z" fill="#a9b8b0"/>'
    return s

def laptop_back(lid, glow):
    cx, w, h = LAP['cx'], LAP['w'], LAP['h']
    s = '<rect x="%s" y="%s" width="%s" height="13" rx="4" fill="#27302d"/>' % (f(cx - w / 2 - 6), DESK4 - 9, w + 12)
    s += '<g class="%s"><rect x="%s" y="%s" width="%s" height="%s" rx="9" fill="url(#lidG)"/>' % (lid, f(cx - w / 2), DESK4 - h - 4, w, h)
    s += '<use href="#signCur" transform="translate(%s,%s) scale(.07)" style="color:#56645f"/>' % (cx, DESK4 - h / 2 - 4)
    s += '<rect x="%s" y="%s" width="%s" height="3" rx="1.5" fill="#56645f"/></g>' % (f(cx - w / 2 + 6), DESK4 - h - 3, w - 12)
    s += '<g class="%s"><rect x="%s" y="%s" width="%s" height="4" rx="2" fill="#E8F4F6" opacity=".95"/><ellipse cx="%s" cy="%s" rx="%s" ry="16" fill="url(#screenGlow)" opacity=".8"/></g>' % (
        glow, f(cx - w / 2 + 4), DESK4 - h - 7, w - 8, cx, DESK4 - h - 6, f(w * .62))
    return s

def sc_zatrzymanie():
    T = 3.0; s = []
    iA, iB = 'sA4', 'sB4'
    a, b = A4, B4
    lid, lgl = uid('lid'), uid('lgl')
    # ---- B: dłoń przy skroni → oddech → bierze zaproszenie → zamyka laptop ----
    P = (238, 605)                                   # punkt przekazania biletu (świat)
    bP = W2L(b['cx'], b['feet'], b['s'], *P); aP = W2L(a['cx'], a['feet'], a['s'], *P)
    lidTop = W2L(b['cx'], b['feet'], b['s'], 420, DESK4 - LAP['h'] - 2)
    lidDown = W2L(b['cx'], b['feet'], b['s'], 420, DESK4 - 12)
    tt = TEMPLE
    T_SWAP, T_CL0, T_CL1 = 2.12, 2.5, 2.82
    rig_side(iB, 'B', T, 'R', [(0, tt, None, 'out'), (.5, (tt[0] + 2, tt[1] - 2), None, 'out'), (.95, tt, None, 'out'), (1.3, (198, 422)), (2.3, (198, 422)),
                               (T_CL0 - .07, (lidTop[0] - 6, lidTop[1] - 16), 'cubic-bezier(.3,0,.3,1)'), (T_CL0, lidTop, 'cubic-bezier(.55,0,.8,.45)'),
                               (T_CL1, lidDown, 'cubic-bezier(.2,.7,.3,1)'), (T, (lidDown[0] - 4, lidDown[1] + 2))])
    rig_side(iB, 'B', T, 'L', [(0, (56, 452)), (1.9, (56, 452)), (2.06, (bP[0] - 6, bP[1] + 4), ESNAP), (T_SWAP, bP), (2.44, (44, 352)), (T, (44, 354))])
    head(iB, T, [(0, 7, 3, 4), (.9, 7, 3, 4), (1.1, -5, -3, 0, ESNAP), (1.3, -4, -2, -2), (1.62, -2, -1, -4, 'ease-in-out'), (2.0, -5, -2, 2), (2.3, -6, -3, 1), (2.5, 3, 1, 2, EIO), (T, 4, 2, 3)])
    pupils(iB, T, [(0, 0), (1.05, -3.4), (1.7, -3.4), (1.95, -2.6), (2.36, -2.6), (2.5, 2.4), (T, 2.4)])
    eyes_kf(iB, T, [(0, .12), (.95, .12), (1.06, 1.0, ESNAP), (1.3, 1), (1.42, .1), (1.85, .1), (1.98, 1), (2.6, 1), (2.66, .1), (2.74, 1), (T, 1)])
    smile_kf(iB, T, [(0, .9, .7), (1.0, .9, .7), (1.9, .92, .75), (2.2, 1.1, 1.22), (T, 1.12, 1.25)])
    body_kf(iB, T, [(0, 6, .996), (1.28, 6, .996), (1.66, -5, 1.014, 'cubic-bezier(.45,0,.55,1)'), (2.04, 3, .998, 'cubic-bezier(.45,0,.55,1)'), (2.3, 0, 1), (T, 0, 1)])
    ev(8.28, 'oddech brunetki – wdech (ramiona w górę) do 8.66'); ev(8.66, 'oddech – wydech do 9.04')
    # ---- A: wchodzi, dłoń na ramieniu, podaje zaproszenie ----
    shoulder = W2L(a['cx'], a['feet'], a['s'], 291, 517)
    rig(iA, 'A', T, [(0, {'R': (164, 452), 'L': (56, 452)}), (.6, {'R': (170, 440)}), (.84, {'R': (shoulder[0] + 6, shoulder[1] - 8)}, ESNAP), (.94, {'R': shoulder}, 'ease-in-out'),
                     (1.62, {'L': (56, 452)}), (1.9, {'L': (aP[0] - 10, aP[1] + 10)}, 'cubic-bezier(.3,0,.2,1)'), (2.04, {'L': aP}), (T_SWAP, {'L': aP}), (2.4, {'L': (58, 452)}, EIO),
                     (2.5, {'R': shoulder}), (2.75, {'R': (shoulder[0] - 8, shoulder[1] + 4)}), (T, {'R': (shoulder[0] - 8, shoulder[1] + 4)})])
    head(iA, T, [(0, 5, 2, 0), (.85, 6, 3, 0), (1.3, 7, 3, 2), (1.9, 4, 2, 4), (2.3, 6, 3, 2), (T, 6, 3, 2)])
    pupils(iA, T, [(0, 3), (1.85, 3), (2.0, 1.5), (2.3, 3), (T, 3)])
    eyes_kf(iA, T, blinks([.7, 2.3]) + [(T, 1)])
    smile_kf(iA, T, [(0, 1.02, 1.05), (1.2, 1.08, 1.15), (T, 1.12, 1.22)])
    tixA = '<g class="tA4"><g transform="translate(30,-30) scale(.75)">%s</g></g>' % ticket()
    tixB = '<g class="tB4"><g transform="translate(30,-30) scale(.75)">%s</g></g>' % ticket()
    A('.tA4', K([(0, 'opacity:0'), (1.66, 'opacity:0', 'ease-out'), (1.8, 'opacity:1', 'steps(1,end)'), (T_SWAP, 'opacity:0')], T)); show_win('tB4', T, T_SWAP, 99)
    ev(8.92, 'A podnosi zaproszenie (bilet z logo)'); ev(7 + T_SWAP, 'brunetka bierze zaproszenie')
    figB = FIGR('B', iB, b['cx'], b['feet'], b['s'], post=ghost('B', iB, '', tixB, arm='L') + ghost_fore('B', iB, fingers()), rim='rimWarmL')
    figA = FIGR('A', iA, a['cx'], a['feet'], a['s'], wrap='aw4', pre='', post=ghost('A', iA, '', tixA, arm='L'), rim='rimWarmL')
    figA = '<g class="ai4">%s</g>' % figA
    S('.aw4{transform-origin:%spx %spx}' % (a['cx'], a['feet']))
    A('.ai4', K([(0, 'transform:translateX(-300px)'), (.2, 'transform:translateX(-300px)', 'cubic-bezier(.3,.1,.25,1)'), (.86, 'transform:translateX(5px)', 'ease-in-out'), (1.0, 'transform:translateX(0)')], T))
    A('.aw4', K([(0, 'transform:translateY(0) rotate(0deg)'), (.2, 'transform:translateY(0) rotate(-1.5deg)', 'ease-in-out'), (.32, 'transform:translateY(-6px) rotate(2deg)', 'ease-in-out'),
                 (.44, 'transform:translateY(0) rotate(1.8deg)', 'ease-in-out'), (.56, 'transform:translateY(-5px) rotate(1.6deg)', 'ease-in-out'), (.68, 'transform:translateY(0) rotate(1.2deg)', 'ease-in-out'),
                 (.8, 'transform:translateY(-3px) rotate(.6deg)', 'ease-in-out'), (.96, 'transform:translateY(0) rotate(-.4deg)', 'ease-in-out'), (1.12, 'transform:translateY(0) rotate(0deg)')], T))
    ev(7.2, 'blondynka wchodzi (kroki do 7.9)'); ev(7.94, 'dłoń blondynki na ramieniu brunetki')
    # ---- warstwy ----
    bg = office4()
    rays = '<path d="M190,130 L420,130 L760,980 L330,980 Z" fill="url(#raysG)"/><path d="M190,300 L260,300 L520,980 L380,980 Z" fill="url(#raysG)" opacity=".8"/>'
    mid = ''.join('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#677d70" transform="rotate(%s %s %s)"/>' % (x, y, rx, ry, ang, x, y) for x, y, rx, ry, ang in
                  [(-10, 520, 40, 96, -25), (40, 470, 36, 90, 15), (-30, 600, 46, 92, -50), (60, 560, 34, 80, 40)])
    mid += '<path d="M-40,660 L70,660 L56,560 L-26,560 Z" fill="#b39c88"/>'
    foc = figB + figA
    # badges zawieszone w ciszy – gasną jedno po drugim w rytm wydechu
    B4B = [(238, 300, 'chat', '7', 1.32), (52, 312, 'bell', '!', 1.46), (484, 452, 'mail', '87', 1.6), (458, 334, 'cal', '5', 1.74), (430, 582, 'phone', '3', 1.88)]
    bdg = ''
    for x, y, ic_, num, tout in B4B:
        bdg += badge_at(T, x, y, ic_, num, None, tout, 'pop', idle=1.8)
        ev(7 + tout, 'plakietka gaśnie (%s)' % num)
    foc += '<ellipse class="sg4" cx="380" cy="470" rx="160" ry="150" fill="url(#screenGlow)" style="mix-blend-mode:screen"/>'
    foc += '<rect x="-300" y="%s" width="1140" height="16" fill="#B89B80"/><rect x="-300" y="%s" width="1140" height="4" fill="#D2BBA2"/>' % (DESK4, DESK4)
    foc += '<rect x="-300" y="%s" width="1140" height="700" fill="%s"/><rect x="-300" y="%s" width="1140" height="12" fill="#000" opacity=".14"/>' % (DESK4 + 16, DKG, DESK4 + 16)
    foc += ''.join('<rect x="%s" y="%s" width="200" height="150" rx="6" fill="none" stroke="#4d675f" stroke-width="2.5"/><rect x="%s" y="%s" width="60" height="8" rx="4" fill="#B89B80"/>' % (x, DESK4 + 46, x + 70, DESK4 + 70) for x in (-140, 80, 300, 520))
    foc += '<g transform="translate(250,%s) rotate(-4)"><rect x="-46" y="-8" width="92" height="9" fill="#F4F2EF"/><rect x="-42" y="-14" width="88" height="7" fill="#ECE8E1" transform="rotate(3)"/></g>' % DESK4
    foc += laptop_back(lid, lgl)
    S('.%s{transform-origin:%spx %spx}' % (lid, LAP['cx'], DESK4 - 4))
    A('.' + lid, K([(0, 'transform:scaleY(1)'), (T_CL0, 'transform:scaleY(1)', 'cubic-bezier(.55,0,.8,.45)'), (T_CL1, 'transform:scaleY(.03)', 'cubic-bezier(.2,.7,.3,1)'), (T_CL1 + .06, 'transform:scaleY(.06)', 'ease-in'), (T_CL1 + .12, 'transform:scaleY(.025)')], T))
    A('.' + lgl, K([(0, 'opacity:1;transform:translateY(0)'), (T_CL0, 'opacity:1;transform:translateY(0)', 'cubic-bezier(.55,0,.8,.45)'), (T_CL1, 'opacity:.7;transform:translateY(%spx)' % (LAP['h'] * .97 - 1), 'cubic-bezier(.2,.7,.3,1)'),
                    (T_CL1 + .06, 'opacity:.6;transform:translateY(%spx)' % f(LAP['h'] * .94)), (T_CL1 + .12, 'opacity:.55;transform:translateY(%spx)' % f(LAP['h'] * .975 - 1)), (T, 'opacity:.35;transform:translateY(%spx)' % f(LAP['h'] * .975 - 1))], T))
    A('.sg4', K([(0, 'opacity:.55'), (T_CL0, 'opacity:.5', 'ease-in'), (T_CL1, 'opacity:0')], T))
    ev(7 + T_CL0, 'brunetka zamyka laptop'); ev(7 + T_CL1, 'klapa zamknięta (klik)')
    foc += bdg
    fg = ('<g transform="translate(18,900)"><path d="M-30,-150 L-12,-260 M0,-150 L10,-250 M20,-150 L40,-240" stroke="#3a3f3c" stroke-width="10" stroke-linecap="round"/><path d="M40,-240 L46,-262" stroke="%s" stroke-width="10" stroke-linecap="round"/>' % RUST +
          '<path d="M-62,-160 L62,-160 L54,60 L-54,60 Z" fill="#b9a48f"/><rect x="-62" y="-166" width="124" height="14" rx="6" fill="#cdbba7"/></g>')
    W = (LAP['cx'], DESK4 - 9)
    z2 = 1.13; F2 = (266, 520); S2 = (262, 520); t2 = 2.42
    SW = (S2[0] + z2 * (W[0] - F2[0]), S2[1] + z2 * (W[1] - F2[1]))
    cam = [(0, 330, 470, 1.26, 300, 500, 0, 'cubic-bezier(.4,0,.2,1)'), (.95, 262, 520, 1.1, 262, 520, 0, 'cubic-bezier(.4,0,.6,1)'), (t2, F2[0], F2[1], z2, S2[0], S2[1], 0),
           (t2 + .01, W[0], W[1], z2, SW[0], SW[1], 0, 'cubic-bezier(.62,0,.22,1)'), (T, W[0], W[1], 3.1, 270, 480, 0)]
    s.append(layers('s4', T, cam, [(.3, bg, 'bl3'), (.35, rays, None), (.6, mid, 'bl2'), (1, foc, None), (1.6, fg, 'bl6')]))
    S('.s4L1{mix-blend-mode:screen}')
    A('.s4L1 > path', K([(0, 'opacity:0'), (.9, 'opacity:0', 'cubic-bezier(.4,0,.4,1)'), (2.6, 'opacity:.46'), (T, 'opacity:.5')], T))
    ev(8.0, 'światło zaczyna się ocieplać (promienie przez okno) do 9.6')
    # korekcja koloru: chłód → ciepło
    s.append('<g class="cg4">%s</g>' % overlay('#8DA19C', .26, 'multiply'))
    A('.cg4', K([(0, 'opacity:1'), (.8, 'opacity:1', EIO), (2.5, 'opacity:0')], T))
    s.append('<g class="wg4">%s</g>' % overlay('#F0B878', .24, 'soft-light'))
    A('.wg4', K([(0, 'opacity:0'), (.8, 'opacity:0', EIO), (2.6, 'opacity:1')], T))
    s.append('<g class="wr4"><ellipse cx="40" cy="180" rx="400" ry="400" fill="url(#warmGlow)" style="mix-blend-mode:screen" opacity=".34"/></g>')
    A('.wr4', K([(0, 'opacity:0'), (.9, 'opacity:0', EIO), (2.6, 'opacity:1')], T))
    s.append(vign(.45))
    # napisy
    c1 = uid('aty')
    s.append('<g class="%s">%s</g>' % (c1, T_('A Ty?', 270, 214, 82, INK)))
    S('.%s{transform-origin:270px 190px}' % c1)
    A('.' + c1, K([(0, 'opacity:0;transform:scale(1.1)'), (.14, 'opacity:0;transform:scale(1.1)', 'cubic-bezier(.2,.7,.25,1)'), (.36, 'opacity:1;transform:scale(1.015)', 'cubic-bezier(.3,0,.3,1)'),
                   (.8, 'opacity:1;transform:scale(1)', EOUT), (.92, 'opacity:0;transform:scale(.97)')], T))
    s.append(line_wipe(T, 'Kiedy ostatnio naprawdę', 270, 196, 42, .88, .42, INK, t_out=2.34))
    s.append(line_wipe(T, 'zadbałaś o siebie?', 270, 250, 42, 1.04, .36, INK, t_out=2.38))
    ev(7.14, 'napis „A Ty?”'); ev(7.88, 'napis „Kiedy ostatnio naprawdę zadbałaś o siebie?”'); ev(9.43, 'kamera wjeżdża w laptop (dolly-in do 10.0)')
    ev(10.0, 'MATCH-CUT: linia zamkniętego laptopa → linia horyzontu w Beskidach')
    return ''.join(s), T

# ================= SCENA 5: SheBalance (10–16 s) =================
SH = [0, 1.5, 3.0, 4.5, 6.0]

def birds(cls):
    return ('<g class="%s">' % cls + ''.join('<g transform="translate(%s,%s)"><path class="wing" d="M-9,0 Q-4,-6 0,0 Q4,-6 9,0" fill="none" stroke="#6b5448" stroke-width="1.8" stroke-linecap="round"/></g>' % (dx, dy) for dx, dy in [(0, 0), (22, 10)]) + '</g>')
S('.wing{transform-box:fill-box;transform-origin:50% 100%;animation:wing .32s ease-in-out infinite alternate}@keyframes wing{from{transform:scaleY(1)}to{transform:scaleY(-.6)}}')

# ================= KAROLOWY DWÓR (Wisła) – prawdziwe miejsce campu, wg zdjęcia src/zdjecia/karolowy-dwor.jpg =================
KD = dict(wall='#F8F0E3', wall_sh='#E2D9CC', wall_lit='#FFF8EC', roof='#CF5D35', roof_d='#A8462A', roof_l='#E3794A', roof_e='#8A3820',
          wood='#7A5236', wood_d='#5A3B26', wood_l='#9C6C46', win='#F8D79A', frame='#6E5446',
          ch_wood='#C99A5E', ch_wood_l='#D6AA6E', ch_roof='#45413E', ch_roof_l='#5f5853', pool='#9DCFD2', pool_l='#D3EEEE',
          pave='#DCCFBF', lawn='#93AE7F', umb='#F6F0E6', rim='#FFE2B0')

def _arch(x, y0, y1, w, fill=None, sw=1.1):
    """okno łukowe: x – lewa krawędź, y0 – dół, y1 – szczyt łuku"""
    r = w / 2
    return '<path d="M%s,%s V%s A%s,%s 0 0 1 %s,%s V%s Z" fill="%s" stroke="%s" stroke-width="%s"/>' % (
        f(x), f(y0), f(y1 + r), f(r), f(r), f(x + w), f(y1 + r), f(y0), fill or KD['win'], KD['frame'], sw)

def _win(x, y, w, h):
    return ('<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="%s" stroke-width="1.1"/><path d="M%s,%s V%s" stroke="%s" stroke-width=".9"/>' % (
        f(x), f(y), f(w), f(h), KD['win'], KD['frame'], f(x + w / 2), f(y), f(y + h), KD['frame']))

def _gallery(x0, x1, y):
    """drewniana galeria/balkon: płyta w y, balustrada nad nią"""
    s = '<rect x="%s" y="%s" width="%s" height="3.6" fill="%s"/>' % (f(x0), f(y), f(x1 - x0), KD['wood_d'])
    s += '<rect x="%s" y="%s" width="%s" height="10" fill="%s" opacity=".35"/>' % (f(x0), f(y - 10), f(x1 - x0), KD['wood_d'])
    s += '<path d="%s" stroke="%s" stroke-width="1.5"/>' % (''.join('M%s,%sv9' % (f(x), f(y - 9)) for x in [x0 + 2 + 3.6 * i for i in range(int((x1 - x0 - 2) / 3.6))]), KD['wood'])
    s += '<rect x="%s" y="%s" width="%s" height="2.4" fill="%s"/>' % (f(x0), f(y - 11), f(x1 - x0), KD['wood_l'])
    s += ''.join('<path d="M%s,%s l5,0 l-5,6 Z" fill="%s"/>' % (f(x), f(y + 3.6), KD['wood_d']) for x in [x0 + 6 + 26 * i for i in range(int((x1 - x0 - 8) / 26) + 1)])
    return s

def _dormer(x, y):
    return ('<rect x="%s" y="%s" width="16" height="12" fill="%s"/>' % (f(x), f(y - 11), KD['wall']) + _win(x + 5, y - 8, 6, 7) +
            '<path d="M%s,%s L%s,%s L%s,%s Z" fill="%s" stroke="%s" stroke-width="1"/>' % (f(x - 3), f(y - 10), f(x + 8), f(y - 21), f(x + 19), f(y - 10), KD['roof'], KD['roof_e']))

def _tiles(xl0, xl1, xr0, xr1, ytop, ybot, step=7):
    """faktura dachówki na połaci trapezowej (lewa krawędź xl0@ybot→xl1@ytop, prawa xr0@ybot→xr1@ytop)"""
    s = ''
    y = ybot - 4
    while y > ytop + 2:
        k = (ybot - y) / (ybot - ytop)
        s += 'M%s,%sH%s' % (f(xl0 + (xl1 - xl0) * k + 2), f(y), f(xr0 + (xr1 - xr0) * k - 2))
        y -= step
    return '<path d="%s" stroke="%s" stroke-width="1" opacity=".45"/>' % (s, KD['roof_d'])

def _umbrella(x, y, sc=1.0):
    return ('<g transform="translate(%s,%s) scale(%s)"><ellipse cx="-7" cy="1" rx="11" ry="3.4" fill="#2e2620" opacity=".16"/>' % (f(x), f(y), f(sc)) +
            '<rect x="-3.5" y="-3" width="7" height="3" rx="1" fill="%s"/><path d="M0,0 V-12" stroke="%s" stroke-width="1.2"/>' % (KD['wood'], KD['wood_d']) +
            '<path d="M-11,-11 Q0,-19 11,-11 Q0,-8 -11,-11 Z" fill="%s"/><path d="M0,-17 V-11" stroke="#e2d8ca" stroke-width=".8"/>' % KD['umb'] +
            '<circle cx="-6" cy="-1" r="1.6" fill="%s"/><circle cx="6" cy="-1" r="1.6" fill="%s"/></g>' % (KD['wood_d'], KD['wood_d']))

def karolowy_dwor(x, y, s=1.0, chalet=True, grounds=True, glow=True, chalet_dx=-130):
    """Ilustracja Karolowego Dworu (Wisła) w stylu marki, widok z drona z przodu-z lewej (wg src/zdjecia/karolowy-dwor.jpg).
    (x,y) = środek linii gruntu przed głównym budynkiem, s = skala. Jednostki lokalne: główny budynek x -160…168 (wys. do -188).
    Chalet odsunięty w lewo (chalet_dx), przy nim basen (po prawej, lekko z przodu) i zielony kort z siatką ciągnący się wzdłuż skarpy
    w stronę dworu; między chaletem a dworem trawnik i szary parking z autami; przed dworem taras z parasolami i płot nad skarpą (do y≈70).
    chalet=False – sam główny budynek; grounds=False – bez trawnika, kortu, basenu, parkingu, tarasu, parasoli i płotu (np. fragment w tle)."""
    o = '<g transform="translate(%s,%s) scale(%s)">' % (f(x), f(y), f4(s))
    CY, CX = -30, chalet_dx                     # chalet: lekko wyżej, odsunięty w lewo
    if grounds:
        o += '<path d="M%s,-62 C%s,-82 -260,-84 -166,-72 C-146,-40 -146,0 -152,46 C-210,72 %s,80 %s,58 Z" fill="%s"/>' % (f(-340 + CX), f(-280 + CX), f(-210 + CX), f(-340 + CX), KD['lawn'])
        # parking (szary placyk z autami) między chaletem a dworem
        o += '<path d="M-200,-46 L-150,-48 L-136,-6 L-184,-2 Z" fill="#CFC9C0"/><path d="M-200,-46 L-150,-48" stroke="#bdb6ac" stroke-width="1.5"/>'
        for cx_, cy_, col in [(-190, -38, '#F4F2EF'), (-176, -38, '#8f9893'), (-162, -39, '#3f4a47'), (-186, -22, '#b9c2be'), (-171, -23, '#6E5446'), (-156, -23, '#F4F2EF')]:
            o += '<rect x="%s" y="%s" width="10" height="6.5" rx="2.4" fill="%s"/><rect x="%s" y="%s" width="6" height="3.2" rx="1.2" fill="#2f3b37" opacity=".55"/>' % (cx_, cy_, col, cx_ + 2, cy_ + 1.6)
    if chalet:
        o += '<g transform="translate(%s,%s)">' % (f(-12 + CX), CY)
        # zaplecze/garaż za chaletem (długi, ciemny dach)
        o += '<rect x="-180" y="-62" width="66" height="30" fill="#E9E1D5"/><rect x="-184" y="-68" width="74" height="8" fill="#3f3b38"/>' + ''.join(_win(xx, -55, 9, 10) for xx in (-172, -154, -136))
        o += '<path d="M-224,-110 L-280,-50 L-296,-58 L-240,-118 Z" fill="%s"/>' % KD['ch_roof_l']
        o += '<path d="M-262,-56 L-276,-62 L-276,-20 L-262,-14 Z" fill="#A9814E"/>'
        o += '<rect x="-262" y="-56" width="76" height="44" fill="%s"/>' % KD['ch_wood']
        o += '<path d="%s" stroke="#A87E4A" stroke-width="1.1"/>' % ''.join('M-262,%sH-186' % yy for yy in range(-50, -12, 5))
        o += ''.join(_win(xx, -46, 11, 15) for xx in (-256, -238, -204)) + '<rect x="-222" y="-38" width="12" height="24" fill="%s"/>' % KD['wood_d']
        o += '<path d="M-278,-50 L-224,-110 L-170,-50 Z" fill="%s"/><path d="M-264,-54 L-224,-98 L-184,-54 Z" fill="%s"/>' % (KD['ch_roof'], KD['ch_wood_l'])
        o += '<path d="%s" stroke="#B88D58" stroke-width="1"/>' % ''.join('M%s,-54V%s' % (xx, f(-54 - (40 - abs(xx + 224)) * 1.1)) for xx in range(-256, -190, 6))
        o += _win(-232, -86, 16, 14) + _gallery(-256, -192, -62)
        o += '<rect x="-264" y="-14" width="80" height="4" fill="#bdb3a6"/>'
        o += '<path d="M-170,-50 L-224,-110" stroke="%s" stroke-width="1.6" opacity=".7"/></g>' % KD['rim']
    if grounds and chalet:
        # basen tuż przy chalecie (po jego prawej, lekko z przodu)
        bx = -12 + CX - 182 + 60          # prawa krawędź chaletu + odstęp
        o += '<path d="M%s,6 L%s,6 L%s,-20 L%s,-20 Z" fill="#EFE9DF"/>' % (f(bx - 6), f(bx + 62), f(bx + 56), f(bx))
        o += '<path d="M%s,2 L%s,2 L%s,-16 L%s,-16 Z" fill="%s"/>' % (f(bx), f(bx + 56), f(bx + 52), f(bx + 4), KD['pool'])
        o += '<path d="M%s,-10 h20 M%s,-4 h24 M%s,-1 h12" stroke="%s" stroke-width="1.4" stroke-linecap="round"/>' % (f(bx + 10), f(bx + 22), f(bx + 8), KD['pool_l'])
        # zielony kort z siatką: od basenu po skosie wzdłuż skarpy w stronę dworu
        k0 = bx + 66
        kp = [(k0, -18), (k0 + 40, -24), (-146, 48), (-188, 54)]
        o += '<path d="M%s Z" fill="#4e7d5a"/>' % ' L'.join('%s,%s' % (f(px), f(py)) for px, py in kp)
        for t in (.2, .4, .6, .8):
            ax, ay = kp[0][0] + (kp[3][0] - kp[0][0]) * t, kp[0][1] + (kp[3][1] - kp[0][1]) * t
            bx2, by2 = kp[1][0] + (kp[2][0] - kp[1][0]) * t, kp[1][1] + (kp[2][1] - kp[1][1]) * t
            o += '<path d="M%s,%s L%s,%s" stroke="#3a6347" stroke-width="1.1"/>' % (f(ax), f(ay), f(bx2), f(by2))
        for t in (.33, .66):
            ax, ay = kp[0][0] + (kp[1][0] - kp[0][0]) * t, kp[0][1] + (kp[1][1] - kp[0][1]) * t
            bx2, by2 = kp[3][0] + (kp[2][0] - kp[3][0]) * t, kp[3][1] + (kp[2][1] - kp[3][1]) * t
            o += '<path d="M%s,%s L%s,%s" stroke="#3a6347" stroke-width="1.1"/>' % (f(ax), f(ay), f(bx2), f(by2))
        o += '<path d="M%s Z" fill="none" stroke="#2f5039" stroke-width="2"/>' % ' L'.join('%s,%s' % (f(px), f(py)) for px, py in kp)
        o += '<path d="%s" stroke="#2f5039" stroke-width="1.6"/>' % ''.join('M%s,%sv-9' % (f(kp[0][0] + (kp[3][0] - kp[0][0]) * t), f(kp[0][1] + (kp[3][1] - kp[0][1]) * t)) for t in (0, .25, .5, .75, 1))
        # podjazd/taras przed dworem
        o += '<path d="M-140,-6 L178,8 L198,42 L60,60 L-70,62 L-130,46 Z" fill="%s"/><path d="M-130,46 L-70,62 L60,60 L198,42" fill="none" stroke="#c7b8a6" stroke-width="2"/>' % KD['pave']
        o += '<path d="M-132,0 L176,6 L172,14 L-140,8 Z" fill="#2e2620" opacity=".12"/>'
    # tylne połacie (wiele dachów)
    o += '<path d="M-124,-146 L-86,-188 L-48,-146 Z" fill="%s"/><path d="M-86,-188 L-124,-146 L-134,-150 L-98,-190 Z" fill="%s"/>' % (KD['roof'], KD['roof_d'])
    o += '<path d="M-34,-150 L-6,-178 L22,-150 Z" fill="%s"/>' % KD['roof_d']
    # główny budynek (widoczna lewa ściana boczna – ujęcie z przodu-z lewej)
    o += '<path d="M-130,0 L-130,-70 L-146,-78 L-146,-8 Z" fill="%s"/>' % KD['wall_sh']
    o += ''.join(_win(-142, yy, 7, 13) for yy in (-60,)) + _arch(-142, -10, -32, 7)
    o += '<rect x="-130" y="-70" width="160" height="70" fill="%s"/>' % KD['wall']
    o += '<rect x="-130" y="-70" width="160" height="6" fill="#000" opacity=".08"/>'
    o += ''.join(_win(-124 + i * 19.5, -63, 10, 15) for i in range(8))
    o += _gallery(-136, 34, -40)
    for i in range(8):
        xx = -124 + i * 19.5
        o += _arch(xx - 2, -1, -32, 14, KD['wood_d']) if i == 3 else _arch(xx, -4, -29, 10)
    o += '<rect x="-130" y="-4" width="160" height="4" fill="#d8cfc2"/>'
    o += '<path d="M-142,-70 L-104,-152 L-114,-154 L-160,-80 Z" fill="%s"/>' % KD['roof_d']
    o += '<path d="M-142,-70 L42,-70 L4,-152 L-104,-152 Z" fill="%s"/>' % KD['roof']
    o += _tiles(-142, -104, 42, 4, -152, -70)
    o += '<path d="M-104,-152 L4,-152" stroke="%s" stroke-width="2.4"/><path d="M-142,-70 L42,-70" stroke="%s" stroke-width="2"/>' % (KD['roof_e'], KD['roof_e'])
    o += '<rect x="-82" y="-166" width="8" height="15" fill="%s"/><rect x="-83.5" y="-168" width="11" height="3" fill="#5a4a42"/>' % KD['wall']
    o += '<rect x="-22" y="-164" width="8" height="13" fill="%s"/><rect x="-23.5" y="-166" width="11" height="3" fill="#5a4a42"/>' % KD['wall']
    o += _dormer(-120, -100) + _dormer(-8, -100) + _dormer(-32, -128) + _dormer(-110, -132)
    # środkowy szczyt z balkonem (lewa połać widoczna)
    o += '<path d="M-60,-142 L-100,-66 L-112,-72 L-72,-148 Z" fill="%s"/>' % KD['roof_d']
    o += '<path d="M-100,-66 L-60,-142 L-20,-66 Z" fill="%s"/><path d="M-88,-68 L-60,-126 L-32,-68 Z" fill="%s"/>' % (KD['roof'], KD['wall'])
    o += _arch(-66, -84, -106, 12) + _gallery(-84, -36, -74)
    o += '<path d="M-20,-66 L-60,-142" stroke="%s" stroke-width="1.6" opacity=".8"/>' % KD['rim']
    # prawe skrzydło z dużym szczytem (lewa połać i lewa ściana boczna widoczne)
    o += '<path d="M72,-168 L16,-74 L-4,-82 L52,-176 Z" fill="%s"/>' % KD['roof_d']
    o += '<path d="M30,6 L30,-80 L18,-86 L18,0 Z" fill="%s"/>' % KD['wall_sh']
    o += '<rect x="30" y="-80" width="86" height="86" fill="%s"/>' % KD['wall_lit']
    o += '<path d="M16,-74 L72,-168 L130,-74 Z" fill="%s"/><path d="M30,-78 L72,-152 L114,-78 Z" fill="%s"/>' % (KD['roof'], KD['wall_lit'])
    o += '<path d="M18,-74 L72,-168" stroke="%s" stroke-width="1.6"/><path d="M130,-74 L72,-168" stroke="%s" stroke-width="2" opacity=".85"/>' % (KD['roof_e'], KD['rim'])
    o += _arch(65, -116, -140, 14) + _gallery(46, 98, -96) + ''.join(_win(xx, -92, 10, 13) for xx in (52, 67, 82))
    o += ''.join(_win(xx, -66, 11, 16) for xx in (40, 62, 84)) + _gallery(26, 118, -42)
    o += ''.join(_arch(xx, 3, -26, 13) for xx in (37, 60, 83)) + '<rect x="30" y="2" width="86" height="4" fill="#d8cfc2"/>'
    # półokrągły wykusz na rogu
    o += '<path d="M112,8 L112,-54 A25,8 0 0 1 162,-54 L162,8 A25,8 0 0 1 112,8 Z" fill="url(#kdBay)"/>'
    o += _arch(116, 2, -34, 8) + _arch(131, 3, -36, 11) + _arch(149, 2, -34, 8)
    o += '<path d="M112,-40 A25,8 0 0 0 162,-40 L162,-37 A25,8 0 0 1 112,-37 Z" fill="%s"/>' % KD['wood']
    o += '<path d="M106,-54 L137,-88 L168,-54 Q137,-46 106,-54 Z" fill="%s"/><path d="M137,-88 L168,-54 Q154,-49 140,-47 Z" fill="%s"/>' % (KD['roof'], KD['roof_l'])
    o += '<path d="M137,-88 L168,-54" stroke="%s" stroke-width="1.6" opacity=".85"/>' % KD['rim']
    if grounds:
        for ux, uy in [(-84, 26), (-58, 36), (-28, 42), (4, 44), (38, 42), (72, 38), (106, 32), (140, 26), (168, 20)]:
            o += _umbrella(ux, uy)
        pts = [(-146, 50), (-122, 55), (-100, 58), (-82, 60), (-58, 66), (-30, 70), (0, 71), (30, 69), (60, 66), (90, 62), (120, 57), (152, 52), (184, 47), (214, 42), (244, 38)]
        o += '<path d="M%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (' L'.join('%s,%s' % p for p in pts), KD['wood'])
        o += '<path d="M%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (' L'.join('%s,%s' % (px, py - 4) for px, py in pts), KD['wood_l'])
        o += '<path d="%s" stroke="%s" stroke-width="2"/>' % (''.join('M%s,%sv-7' % (px, py + 1) for px, py in pts), KD['wood_d'])
    if glow:
        o += '<ellipse cx="-20" cy="-40" rx="230" ry="90" fill="url(#warmGlow)" opacity=".28" style="mix-blend-mode:screen"/>'
    return o + '</g>'

def forest(x0, x1, base0, base1, n, seed, hmin, hmax, decid=.35, avoid=None):
    """las: świerki + jaśniejsze drzewa liściaste (złota godzina); avoid=(x0,x1,ymax) – pas bez drzew"""
    r = random.Random(seed); items = []
    for i in range(n):
        x = r.uniform(x0, x1); b = r.uniform(base0, base1); h = r.uniform(hmin, hmax)
        if avoid and avoid[0] < x < avoid[1] and b - h < avoid[2]: continue
        items.append((b, x, h, r.random() < decid, r.random()))
    s = ''
    for b, x, h, d, c in sorted(items):
        if d:
            col = ['#9DB083', '#B5A66A', '#8C9F70', '#A89F66'][int(c * 4)]
            s += '<rect x="%s" y="%s" width="2.4" height="%s" fill="#5e4a3e"/><ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (f(x - 1.2), f(b - h * .35), f(h * .35), f(x), f(b - h * .6), f(h * .3), f(h * .4), col)
        else:
            s += spruce(x, b, h, ['#3f5a52', '#4a655c', '#557062', '#38524a'][int(c * 4)])
    return s

def range_svg(pts, col, crest=None, trees=None, seed=1, bottom=1500, meadows=None):
    """pasmo górskie: gładki grzbiet przez pts, ciepłe światło na grani (crest), zalesienie (trees=(kolor, gęstość, wys.)), polany"""
    d = smooth(pts) + ' L%s,%s L%s,%s Z' % (f(pts[-1][0]), bottom, f(pts[0][0]), bottom)
    s = '<path d="%s" fill="%s"/>' % (d, col)
    r = random.Random(seed)
    if meadows:
        mc, n = meadows
        for i in range(n):
            k = r.uniform(.05, .95); i0 = int(k * (len(pts) - 1)); p0, p1 = pts[i0], pts[min(i0 + 1, len(pts) - 1)]
            t = k * (len(pts) - 1) - i0; mx = p0[0] + (p1[0] - p0[0]) * t; my = p0[1] + (p1[1] - p0[1]) * t + r.uniform(18, 70)
            s += '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" transform="rotate(%s %s %s)"/>' % (f(mx), f(my), f(r.uniform(22, 48)), f(r.uniform(7, 14)), mc, f(r.uniform(-18, 18)), f(mx), f(my))
    if trees:
        tc, step, th = trees
        cols = tc if isinstance(tc, (list, tuple)) else [tc]
        items = []
        x = pts[0][0]
        while x < pts[-1][0]:
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                if ax <= x <= bx:
                    yy = ay + (by - ay) * (x - ax) / (bx - ax); break
            for k in range(3):                                                                           # rozsiany po zboczu
                if r.random() < .75: items.append((yy + r.uniform(th * 1.1, th * 7), x + r.uniform(-step, step), th * r.uniform(.7, 1.2)))
            x += step
        for b_, x_, h_ in sorted(items):
            s += spruce(x_, b_, h_, cols[int(r.random() * len(cols))])
    if crest:
        s += '<path d="%s" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" opacity=".75"/>' % (smooth(pts), crest)
    return s

def cloud(x, y, w, op=.85, col='#FBF8F2'):
    """miękka chmura z kilku elips (środek dołu = x,y, szerokość w)"""
    s = '<g opacity="%s">' % f(op)
    for dx, dy, rx, ry in [(-.32, -.12, .22, .16), (-.08, -.26, .26, .22), (.2, -.18, .24, .18), (.38, -.06, .16, .11), (0, -.04, .5, .12)]:
        s += '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (f(x + dx * w), f(y + dy * w), f(rx * w), f(ry * w), col)
    return s + '</g>'

def small_house(x, y, s=1.0, roof='#C9553A'):
    return ('<g transform="translate(%s,%s) scale(%s)"><rect x="-9" y="-10" width="18" height="10" fill="#F6F0E6"/><rect x="-5" y="-7" width="3" height="3" fill="%s"/><rect x="2" y="-7" width="3" height="3" fill="%s"/>'
            '<path d="M-12,-9 L0,-19 L12,-9 Z" fill="%s"/><path d="M0,-19 L12,-9 L15,-11 L3,-21 Z" fill="#a8472c"/></g>' % (f(x), f(y), f(s), KD['win'], KD['win'], roof))

def shot_manor(T, t0, t1):
    """Karolowy Dwór z drona (10,0–11,5), wg zdjęcia: kompleks na ramieniu wzgórza w środku kadru, pod nim stroma skarpa z lasem,
    z lewej głęboka dolina z Wisłą, daleko za doliną przymglone pasma Beskidów (horyzont ~ na wysokości dachu), z prawej wzgórze łagodnie się wznosi.
    Start = linia czubków drzew pod poranną mgłą (match-cut z linią laptopa); mgła i drzewa rozstępują się (dron się wznosi), potem powolny przelot w bok."""
    cam = [(t0, 270, 482, 1.55, 270, 480, 0, 'cubic-bezier(.3,.05,.2,1)'), (t0 + 1.2, 276, 600, 1.0, 270, 600, 0, 'cubic-bezier(.4,0,.6,1)'), (t1 + .3, 250, 598, 1.035, 270, 600, 0)]
    sky = '<rect x="-400" y="-500" width="1340" height="2000" fill="url(#skyHill)"/>'
    clouds = cloud(70, 96, 150, .9) + cloud(470, 110, 170, .85) + cloud(330, 300, 200, .7) + cloud(60, 318, 150, .65) + cloud(560, 280, 140, .7)
    sun = '<g class="sun5"><circle cx="430" cy="262" r="220" fill="url(#sunHalo)" opacity=".75"/><circle cx="430" cy="262" r="30" fill="url(#sunDisc)"/></g>'
    A('.sun5', K([(0, 'transform:translateY(36px)'), (t1, 'transform:translateY(-14px)')], T, 'cubic-bezier(.3,0,.4,1)'))
    # daleko za doliną: przymglone, niebieskawo-szałwiowe pasma; z lewej wyższy, zalesiony grzbiet
    far = (range_svg([(-400, 378), (-200, 366), (-40, 372), (90, 360), (220, 368), (350, 356), (470, 364), (600, 352), (940, 362)], '#C8D3D2', '#F7E6C8', seed=11) +
           range_svg([(-400, 398), (-180, 392), (-20, 400), (120, 386), (250, 396), (380, 384), (520, 392), (700, 380), (940, 390)], '#B2C3C0', '#F4DFBC', seed=12))
    lridge = range_svg([(-400, 300), (-120, 296), (-20, 306), (60, 330), (140, 372), (210, 410), (270, 434), (330, 446)], '#7C9884', '#F2D3A0',
                       (['#6d8a74', '#66826c', '#5e7a64'], 10, 10), 13, meadows=('#9DB585', 3))
    # dno doliny: Wisła (drobne dachy) + mgiełka
    town = '<path d="M-400,446 C-200,440 0,438 160,444 C260,450 340,462 420,476 L420,620 L-400,620 Z" fill="url(#valleyG)"/>'
    r = random.Random(17)
    for i in range(34):
        hx, hy = r.uniform(-60, 300), r.uniform(468, 512)
        town += small_house(hx, hy, r.uniform(.35, .55), r.choice(['#C9553A', '#B5582F', '#8a6a56', '#C9553A', '#7d6a5c']))
    town += forest(-200, 330, 470, 520, 40, 18, 10, 18, .4)
    town += '<ellipse cx="120" cy="468" rx="260" ry="18" fill="#FBF6EE" opacity=".6"/><ellipse cx="200" cy="500" rx="200" ry="14" fill="#FBF6EE" opacity=".45"/>'
    # wzgórze: ramię z dworem, z lewej opada w dolinę, z prawej łagodnie rośnie; pod dworem stroma skarpa w dół do krawędzi kadru
    hill = '<path d="M-400,800 L-120,752 C-50,720 -6,640 14,590 C70,576 200,576 430,572 C490,564 560,536 660,508 L940,490 L940,1600 L-400,1600 Z" fill="url(#hillGreen)"/>'
    hill += '<path d="M14,590 C70,576 200,576 430,572 C490,564 560,536 660,508" fill="none" stroke="#C9DBA0" stroke-width="3" opacity=".7"/>'
    hill += ''.join('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" transform="rotate(-14 %s %s)"/>' % (x, y, rx, ry, c, x, y) for x, y, rx, ry, c in
                    [(520, 560, 70, 16, '#A9C584'), (600, 530, 60, 12, '#B3CC8C'), (470, 600, 50, 10, '#9FBD7A'), (560, 600, 46, 12, '#A9C584')])
    hill += forest(430, 940, 520, 640, 50, 31, 18, 40, .45) + small_house(486, 556, 1.15) + small_house(560, 522, .8)
    hill += forest(20, 440, 556, 590, 40, 32, 24, 48, .55)        # drzewa za dworem i chaletem na grzbiecie (brzozy, świerki)
    hill += karolowy_dwor(300, 600, .62, chalet=False)  # klientka: bez drewnianego domku i basenu
    hill += '<g transform="translate(252,488)">' + steam_paths('stm', 2, 34, 6, 2.6, '#F6EDE2', 10, '#e9dccd') + '</g>'
    # skarpa pod tarasem: trawa + las schodzący do dolnej krawędzi
    slope = '<path d="M40,640 C120,656 300,664 440,646 C470,700 470,800 430,1000 L70,1000 C40,860 20,720 40,640 Z" fill="url(#slopeG)"/>'
    slope += ''.join('<path d="M%s,%s C%s,%s %s,%s %s,%s" fill="none" stroke="#8CAE6A" stroke-width="2" opacity=".5"/>' % (110 + i * 4, 670 + i * 34, 200, 684 + i * 36, 320, 690 + i * 36, 450 - i * 3, 676 + i * 38) for i in range(8))
    slope += forest(-200, 150, 650, 980, 110, 41, 30, 80, .3) + forest(400, 940, 620, 980, 110, 42, 30, 80, .3) + forest(60, 470, 900, 1010, 40, 43, 50, 90, .25)
    near = forest(-200, 160, 900, 1100, 50, 44, 90, 160, .25) + forest(420, 940, 880, 1100, 50, 45, 90, 160, .25)
    bird = birds('bd5')
    A('.bd5', K([(0, 'transform:translate(80px,270px)'), (t1, 'transform:translate(330px,240px)')], T, 'cubic-bezier(.3,0,.7,1)'))
    bok = bokeh(5, (350, 200, 530, 330), ['#FFF1D6', '#FFF8EA'], (8, 18), 11, (.25, .45))
    fg = ''.join(spruce(x, b_, h, '#2f4540') for x, b_, h in [(-40, 1150, 400), (30, 1180, 320), (590, 1160, 380), (520, 1200, 300)])
    # start: czubki drzew przed obiektywem (linia na wys. 480 = zamknięty laptop), opadają – dron się wznosi
    crane = '<g class="cr5a"><rect x="-400" y="489" width="1340" height="1300" fill="#2b3f39"/>' + ''.join(
        spruce(x, 494, h, c) for x, h, c in zip(range(-380, 940, 18), itertools.cycle([16, 24, 19, 27, 21]), itertools.cycle(['#2b3f39', '#314740', '#283a35']))) + '</g>'
    A('.cr5a', K([(0, 'transform:translateY(0)'), (t0 + .12, 'transform:translateY(0)', 'cubic-bezier(.45,0,.3,1)'), (t0 + 1.0, 'transform:translateY(900px)')], T))
    ev(10.12, 'dron wznosi się nad czubkami drzew, poranna mgła się rozstępuje – odsłania wzgórze z Karolowym Dworem i dolinę (do 11.0)')
    out = layers('a5', T, cam, [(.04, sky, None), (.07, clouds, 'bl3'), (.08, sun, None), (.1, far, 'bl3'), (.16, lridge, 'bl2'), (.24, town, 'bl15'),
                                (.8, hill, None), (.95, slope, None), (1.15, near, 'bl2'), (.45, bird, None), (1.3, bok, 'bl4'), (1.7, fg, 'bl6'), (1.45, crane, 'bl6')])
    veil = '<g class="vl5"><rect x="-20" y="-40" width="580" height="524" fill="#F1E3CF"/><rect x="-20" y="482" width="580" height="60" fill="url(#veilEdge)"/></g>'
    A('.vl5', K([(0, 'opacity:1;transform:translateY(0)'), (t0 + .14, 'opacity:1;transform:translateY(0)', 'cubic-bezier(.45,0,.35,1)'), (t0 + .95, 'opacity:0;transform:translateY(-140px)')], T))
    return out + veil

def shot_coffee(T, t0, t1):
    cam = [(t0, 300, 650, 1.0, 300, 650, 0, 'cubic-bezier(.3,0,.4,1)'), (t1 - .28, 314, 640, 1.07, 300, 650, 0, 'cubic-bezier(.6,0,.85,.35)'), (t1, 314, 330, 1.09, 300, 650, 0)]
    sky = '<rect x="-400" y="-900" width="1340" height="2400" fill="url(#daySky)"/><circle cx="440" cy="300" r="300" fill="url(#sunHalo)"/><circle cx="440" cy="300" r="34" fill="url(#sunDisc)"/>'
    far = (ridge(-400, 940, 470, 16, 8, 61, 1500, '#C9D3CC') + ridge(-400, 940, 525, 22, 9, 62, 1500, SAGE) +
           ''.join(autumn_tree(x, 560 + random.Random(x).uniform(-6, 10), random.Random(x * 7).uniform(26, 40), c) for x, c in zip(range(-380, 940, 22), itertools.cycle([RUST, MUST, '#c47a3c', DKG, MUST, '#d08a4a']))) +
           ridge(-400, 940, 600, 18, 9, 63, 1500, '#7f978e'))
    mist = '<g class="ms5c"><rect x="-400" y="540" width="1340" height="60" fill="url(#mistBand)"/></g>'
    drift('ms5c', T, -26, 0)
    RY = 748
    rail = '<rect x="-400" y="%s" width="1340" height="34" fill="url(#woodTop)"/><rect x="-400" y="%s" width="1340" height="5" fill="#b8957c"/>' % (RY, RY)
    rail += ''.join('<path d="M-400,%s H940" stroke="#6f5343" stroke-width="1.2" opacity=".5"/>' % y for y in (RY + 13, RY + 24))
    rail += '<rect x="-400" y="%s" width="1340" height="900" fill="#6b5141"/>' % (RY + 34) + ''.join('<rect x="%s" y="%s" width="12" height="900" fill="#5e4638"/>' % (x, RY + 34) for x in range(-380, 940, 70))
    rail += '<g transform="translate(150,%s) rotate(-5)"><rect x="-64" y="-14" width="128" height="18" rx="3" fill="%s"/><rect x="-64" y="-14" width="11" height="18" fill="%s"/><path d="M-34,-17 L60,-27" stroke="%s" stroke-width="4" stroke-linecap="round"/></g>' % (RY + 2, BEIGE, BROWN, RUST)
    mg, hd = uid('mg'), uid('hd')
    sk = BSKIN2
    handsvg = ('<g transform="scale(2.9)"><g class="%s">' % hd +
               '<path d="M-150,62 C-110,30 -70,0 -36,-22 L-26,-6 C-60,20 -100,52 -130,90 Z" fill="#f8f4ea"/>'
               '<path d="M-118,52 C-92,30 -66,10 -44,-6" fill="none" stroke="#e3dbc9" stroke-width="2.2"/>'
               '<ellipse cx="-38" cy="-12" rx="9" ry="11" fill="#efe8da"/>'
               '<ellipse cx="-27" cy="-24" rx="8" ry="13" fill="%s"/>' % sk +
               ''.join('<rect x="-25" y="%s" width="%s" height="6.4" rx="3.2" fill="%s"/>' % (f(-39 + i * 7), f(15.5 - i * 1.3), sk) for i in range(4)) +
               ''.join('<path d="M%s,%s h3" stroke="#d29a7c" stroke-width=".8" opacity=".8"/>' % (f(-13 - i * 1.3), f(-36 + i * 7)) for i in range(4)) +
               '<rect x="-30" y="-50" width="12" height="6" rx="3" fill="%s" transform="rotate(-24 -24 -47)"/>' % sk +
               '</g></g>')
    rail += '<g transform="translate(338,%s)"><g class="%s">%s%s</g></g>' % (RY + 4, mg, mug_svg('#F7F3EC', SAGE, '#e2d9cc', True, 2.9), handsvg)
    hand = ''
    tl = t0 + .55
    A('.' + hd, K([(0, 'opacity:0;transform:translate(-90px,40px)'), (tl, 'opacity:0;transform:translate(-90px,40px)', 'cubic-bezier(.25,.8,.3,1)'), (tl + .08, 'opacity:1;transform:translate(-60px,26px)', 'cubic-bezier(.25,.8,.3,1)'),
                   (tl + .34, 'opacity:1;transform:translate(1.5px,-.5px)', 'ease-in-out'), (tl + .45, 'opacity:1;transform:translate(0,0)')], T))
    A('.' + mg, K([(0, 'transform:translate(0,0) rotate(0deg)'), (tl + .6, 'transform:translate(0,0) rotate(0deg)', 'cubic-bezier(.45,0,.3,1)'), (t1, 'transform:translate(0,-16px) rotate(-1deg)')], T))
    ev(10 + tl, 'dłoń brunetki obejmuje kubek z parą'); ev(10 + tl + .6, 'unosi kubek')
    bok = bokeh(8, (300, 180, 540, 420), ['#FFE9C2', '#FFF3DC', '#F9D9A6'], (10, 26), 12, (.3, .55))
    ots = ('<path d="M-220,430 C-120,400 -10,420 40,470 C90,520 70,580 104,640 C136,700 104,760 136,830 C160,890 140,960 150,1100 L-220,1100 Z" fill="url(#hairOts)"/>'
           '<path d="M-20,470 C40,540 20,610 60,680 C92,740 66,810 96,880" fill="none" stroke="#a5723f" stroke-width="26" stroke-linecap="round"/>'
           '<path d="M40,520 C84,590 70,660 104,720 C128,770 110,840 126,900" fill="none" stroke="#cf9b5e" stroke-width="16" stroke-linecap="round" opacity=".85"/>'
           '<ellipse cx="-10" cy="1000" rx="230" ry="140" fill="#f6f1e6"/><path d="M-200,960 Q-10,900 200,950" fill="none" stroke="#e3dbc9" stroke-width="8"/>')
    dwor = ('<g opacity=".72">' + karolowy_dwor(600, 768, 1.2, chalet=False, grounds=False) + '</g>' +
            '<rect x="380" y="690" width="300" height="90" fill="url(#mistBand)" opacity=".8"/><rect x="380" y="500" width="300" height="300" fill="#F6E2C6" opacity=".18"/>')
    out = layers('b5', T, cam, [(.2, sky, None), (.24, far, 'bl3'), (.3, mist, 'bl6'), (.42, dwor, 'bl3'), (1, rail + hand, None), (1.25, bok, 'bl4'), (1.75, ots, 'bl6')])
    return out

def shot_yoga(T, t0, t1):
    cam = [(t0, 270, 250, 1.06, 270, 480, 0, 'cubic-bezier(.15,.7,.25,1)'), (t0 + .5, 268, 556, 1.0, 270, 560, 0, 'cubic-bezier(.4,0,.6,1)'), (t1, 276, 566, 1.05, 270, 560, 0)]
    sky = '<rect x="-400" y="-900" width="1340" height="2400" fill="url(#daySky)"/><circle cx="430" cy="330" r="320" fill="url(#sunHalo)"/><circle cx="430" cy="330" r="36" fill="url(#sunDisc)"/>'
    far = ridge(-400, 940, 540, 18, 8, 71, 1500, '#C7D3CC')
    midr = ridge(-400, 940, 600, 20, 9, 72, 1500, SAGE) + ''.join(autumn_tree(x, 626 + random.Random(x).uniform(-5, 8), random.Random(x * 3).uniform(30, 48), c) for x, c in zip(range(-380, 940, 26), itertools.cycle([MUST, RUST, DKG, '#c47a3c', MUST])))
    meadow = '<path d="M-400,720 C-100,680 200,690 400,700 C600,708 800,690 940,700 L940,1500 L-400,1500 Z" fill="#8FA898"/>'
    iA, iB = 'sA5', 'sB5'
    sF, feet = .6, 834
    ground = '<path d="M-400,770 C0,756 400,760 940,772 L940,1500 L-400,1500 Z" fill="url(#grassG)"/>'
    ground += ''.join('<path d="M%s,%s q3,-12 6,0" fill="none" stroke="#6c8777" stroke-width="2"/>' % (x, y) for x, y in [(random.Random(i).uniform(-60, 600), random.Random(i * 3).uniform(790, 960)) for i in range(60)])
    for cx, col in ((172, RUST), (368, SAGE)):
        ground += '<path d="M%s,%s L%s,%s L%s,%s L%s,%s Z" fill="%s"/><path d="M%s,%s L%s,%s" stroke="#fff" stroke-opacity=".25" stroke-width="2"/>' % (
            cx - 64, feet + 18, cx + 64, feet + 18, cx + 52, feet - 12, cx - 52, feet - 12, col, cx - 52, feet - 10, cx + 52, feet - 10)
    figs = FIGR('A', 'yoga ' + iA, 172, feet, sF, rim='rimSunL') + FIGR('B', 'yoga ' + iB, 368, feet, sF, rim='rimSunL')
    for inst, d in ((iA, 0), (iB, .06)):
        A('.fig.%s .armL' % inst, K([(0, 'transform:rotate(7deg)'), (t0 + .3 + d, 'transform:rotate(14deg)', 'ease-in-out'), (t0 + .42 + d, 'transform:rotate(18deg)', 'cubic-bezier(.3,0,.2,1)'),
                                     (t0 + .86 + d, 'transform:rotate(172deg)', 'ease-in-out'), (t0 + 1.0 + d, 'transform:rotate(167deg)', 'ease-in-out'), (t0 + 1.12 + d, 'transform:rotate(168deg)')], T))
        A('.fig.%s .armR' % inst, K([(0, 'transform:rotate(-7deg)'), (t0 + .3 + d, 'transform:rotate(-14deg)', 'ease-in-out'), (t0 + .42 + d, 'transform:rotate(-18deg)', 'cubic-bezier(.3,0,.2,1)'),
                                     (t0 + .86 + d, 'transform:rotate(-172deg)', 'ease-in-out'), (t0 + 1.0 + d, 'transform:rotate(-167deg)', 'ease-in-out'), (t0 + 1.12 + d, 'transform:rotate(-168deg)')], T))
        A('.fig.%s .foreL' % inst, K([(0, 'transform:rotate(-6deg)'), (t0 + .42 + d, 'transform:rotate(-10deg)', 'cubic-bezier(.3,0,.2,1)'), (t0 + .86 + d, 'transform:rotate(20deg)', 'ease-in-out'), (t0 + 1.12 + d, 'transform:rotate(14deg)')], T))
        A('.fig.%s .foreR' % inst, K([(0, 'transform:rotate(6deg)'), (t0 + .42 + d, 'transform:rotate(10deg)', 'cubic-bezier(.3,0,.2,1)'), (t0 + .86 + d, 'transform:rotate(-20deg)', 'ease-in-out'), (t0 + 1.12 + d, 'transform:rotate(-14deg)')], T))
        eyes_kf(inst, T, [(0, 1), (t0 + .7 + d, 1), (t0 + .82 + d, .12), (T, .12)])
        smile_kf(inst, T, [(0, 1.05, 1.1), (t0 + .8, 1.05, 1.1), (T, 1.12, 1.25)])
        head(inst, T, [(0, 0, 0, 0), (t0 + .4 + d, 0, 0, 2), (t0 + .9 + d, 0, 0, -3), (T, (-2 if inst == iA else 2), 0, -3)])
    ev(10 + t0 + .42, 'joga: ręce w górę (pozycja drzewa) do %.2f' % (10 + t0 + 1.12))
    fgr = ''
    for x0, sgn in ((-40, 1), (580, -1)):
        for k in range(9):
            x = x0 + sgn * k * 14
            fgr += '<path d="M%s,1010 Q%s,%s %s,%s" fill="none" stroke="#3f5a4c" stroke-width="7" stroke-linecap="round"/>' % (x, x + sgn * 10, 930 - k * 6, x + sgn * 26, 860 - (k % 4) * 22)
        fgr += '<circle cx="%s" cy="880" r="9" fill="%s"/><circle cx="%s" cy="915" r="7" fill="%s"/>' % (x0 + sgn * 60, MUST, x0 + sgn * 90, BEIGE)
    fgw = '<g class="gr5">%s</g>' % fgr
    S('.gr5{transform-origin:270px 1010px}')
    A('.gr5', 'grs 1.9s ease-in-out infinite alternate'); S('@keyframes grs{from{transform:skewX(-2deg)}to{transform:skewX(2.5deg)}}')
    bok = bokeh(8, (340, 240, 540, 440), ['#FFE9C2', '#FFF3DC', '#F9D9A6'], (8, 24), 21, (.3, .55))
    out = layers('y5', T, cam, [(.08, sky, None), (.2, far, 'bl3'), (.38, midr, 'bl2'), (.6, meadow, 'bl15'), (1, ground + figs, None), (1.3, bok, 'bl4'), (1.7, fgw, 'bl6')])
    return out

def shot_table(T, t0, t1):
    cam = [(t0, 270, 520, 1.07, 270, 520, 0, 'cubic-bezier(.3,0,.4,1)'), (t1, 282, 514, 1.13, 270, 520, 0)]
    sky = '<rect x="-400" y="-900" width="1340" height="2400" fill="url(#duskSky)"/>'
    sky += ''.join('<g transform="translate(%s,%s) scale(%s)"><g class="twinkle" style="animation-delay:-%ss"><use href="#star" fill="#F4EEDF"/></g></g>' % (x, y, sc, d) for x, y, sc, d in [(70, 120, .35, .2), (470, 140, .3, .9), (420, 320, .25, .5), (110, 330, .28, 1.1)])
    rid = ridge(-400, 940, 560, 22, 8, 81, 1500, '#6f8a82') + ridge(-400, 940, 610, 18, 9, 82, 1500, '#58756C')
    wire = smooth([(-60, 360), (120, 392), (270, 404), (420, 392), (600, 360)])
    lights = '<path d="%s" fill="none" stroke="#3c4a45" stroke-width="2"/>' % wire
    for i in range(14):
        x = -40 + i * 46; y = 360 + 44 * math.sin(math.pi * (x + 60) / 660) * .98
        c = uid('bl')
        lights += '<g class="%s" style="animation-delay:-%ss"><circle cx="%s" cy="%s" r="16" fill="url(#bulbG)"/><circle cx="%s" cy="%s" r="4.5" fill="#FFF1C9"/></g>' % (c, f(i * .23 % 1.3), f(x), f(y + 9), f(x), f(y + 9))
        S('.%s{animation:bulb 1.3s ease-in-out infinite alternate}' % c)
    S('@keyframes bulb{from{opacity:.75}to{opacity:1}}')
    iA, iB = 'sA6', 'sB6'
    sF = .75; table = 728; feet = table + (712 - 425) * sF
    figs = FIGR('B', iB, 378, feet, sF, rim='rimWarmR') + FIGR('A', iA, 162, feet, sF, post=ghost('A', iA, '', mug_hand('st6'), arm='R'), rim='rimWarmR')
    rig(iA, 'A', T, [(0, {'R': R_HOLD, 'L': (60, 452)}), (t0 + .9, {'R': R_HOLD}), (t0 + 1.1, {'R': (190, 250)}), (T, {'R': (190, 252)})])
    rig_side(iB, 'B', T, 'L', [(0, (56, 452)), (t0 + .06, (56, 452), 'cubic-bezier(.2,.8,.3,1)'), (t0 + .26, (28, 300), 'ease-in-out'), (t0 + .4, (20, 288), 'ease-in-out'),
                               (t0 + .54, (30, 304), 'ease-in-out'), (t0 + .7, (26, 296), 'cubic-bezier(.3,0,.2,1)'), (t0 + .86, (100, 312), 'ease-in-out'), (t0 + 1.0, (104, 318), 'ease-in-out'), (T, (102, 314))])
    # rozmowa → śmiech
    laughA = [(0, 6, 3, 0), (t0 + .5, 6, 3, 0), (t0 + .62, 9, 4, -4, ESNAP)] + [(t0 + .62 + .1 * k, 9 - k % 2 * 2, 4, -4 + (k % 2) * 4, 'ease-in-out') for k in range(1, 8)] + [(T, 8, 4, -2)]
    laughB = [(0, -6, -3, 0), (t0 + .55, -6, -3, 0), (t0 + .68, -10, -4, -5, ESNAP)] + [(t0 + .68 + .1 * k, -10 + k % 2 * 2, -4, -5 + (k % 2) * 4, 'ease-in-out') for k in range(1, 8)] + [(T, -8, -4, -3)]
    head(iA, T, laughA); head(iB, T, laughB)
    pupils(iA, T, [(0, 3.2), (T, 3.2)]); pupils(iB, T, [(0, -3.2), (T, -3.2)])
    eyes_kf(iA, T, [(0, 1), (t0 + .6, 1), (t0 + .7, .3), (t0 + 1.35, .3), (t0 + 1.45, 1)])
    eyes_kf(iB, T, [(0, 1), (t0 + .3, 1), (t0 + .36, .1), (t0 + .44, 1), (t0 + .66, 1), (t0 + .76, .3), (T, .3)])
    smile_kf(iA, T, [(0, 1.08, 1.15), (t0 + .6, 1.1, 1.2), (t0 + .7, 1.2, 1.55), (T, 1.18, 1.45)])
    smile_kf(iB, T, [(0, 1.05, 1.1), (t0 + .66, 1.1, 1.2), (t0 + .76, 1.22, 1.6), (T, 1.2, 1.5)])
    for inst, dl in ((iA, .62), (iB, .68)):
        body_kf(inst, T, [(0, 0, 1), (t0 + dl, 0, 1)] + [(t0 + dl + .1 * k, -2.5 if k % 2 else .5, 1.004 if k % 2 else 1, 'ease-in-out') for k in range(1, 8)] + [(T, 0, 1)])
    ev(10 + t0 + .25, 'brunetka opowiada (gest dłonią)'); ev(10 + t0 + .62, 'obie wybuchają śmiechem (do %.2f)' % (10 + t0 + 1.4))
    tab = '<rect x="-400" y="%s" width="1340" height="18" fill="url(#woodTop)"/><rect x="-400" y="%s" width="1340" height="800" fill="#5d463b"/>' % (table, table + 18)
    tab += ''.join('<path d="M-400,%s H940" stroke="#4c392f" stroke-width="2"/>' % (table + 60 + i * 52) for i in range(5))
    # lampion ze świecą
    tab += '<g transform="translate(270,%s)"><ellipse cx="0" cy="-40" rx="90" ry="70" fill="url(#warmGlow)" opacity=".7" style="mix-blend-mode:screen"/>' % table
    tab += '<rect x="-24" y="-74" width="48" height="74" rx="6" fill="#F6E7C8" opacity=".55" stroke="#3c2f28" stroke-width="3"/><path d="M-24,-74 L0,-90 L24,-74" fill="#3c2f28"/>'
    tab += '<rect x="-9" y="-34" width="18" height="30" rx="3" fill="#FBF6EC"/><g class="flame"><path d="M0,-52 Q8,-42 0,-34 Q-8,-42 0,-52 Z" fill="#F8C66A"/></g></g>'
    tab += '<g transform="translate(424,%s)">%s</g>' % (table + 2, mug_svg('#F7F3EC', BEIGE, '#e2d9cc', True, 1.05))
    tab += '<g transform="translate(118,%s)"><ellipse cx="0" cy="-6" rx="36" ry="10" fill="#E9DED0"/><circle cx="-12" cy="-14" r="9" fill="%s"/><circle cx="6" cy="-15" r="9" fill="%s"/><circle cx="16" cy="-10" r="7" fill="%s"/></g>' % (table + 2, RUST, MUST, '#c47a3c')
    glow = '<g class="fl5"><ellipse cx="80" cy="900" rx="420" ry="360" fill="url(#fireG)" style="mix-blend-mode:screen"/></g>'
    A('.fl5', 'flk .9s ease-in-out infinite alternate'); S('@keyframes flk{0%{opacity:.55}40%{opacity:.8}70%{opacity:.62}100%{opacity:.85}}')
    fire = ('<g transform="translate(46,978)"><path d="M-110,0 L110,0 L90,-30 L-90,-30 Z" fill="#3c2f28"/>' +
            ''.join('<g class="flame" style="animation-delay:-%ss;animation-duration:%ss"><path d="M%s,-20 Q%s,%s %s,%s Q%s,%s %s,-20 Z" fill="%s"/></g>' % (
                f(i * .13), f(.3 + i * .04), x - w, x - w * .6, -20 - h * .5, x, -20 - h, x + w * .6, -20 - h * .5, x + w, c)
                for i, (x, w, h, c) in enumerate([(-50, 34, 120, '#E9874A'), (10, 40, 170, MUST), (60, 30, 110, '#E9874A'), (0, 22, 100, '#FBE3A8')])) + '</g>')
    sparks = ''
    for i in range(7):
        c = uid('sp'); x = 30 + i * 18
        sparks += '<circle class="%s" cx="%s" cy="900" r="2.6" fill="#FFD27A"/>' % (c, x)
        S('.%s{animation:spk%s 1.4s cubic-bezier(.2,.6,.4,1) infinite;animation-delay:-%ss}@keyframes spk%s{0%%{opacity:0;transform:translate(0,0)}15%%{opacity:1}100%%{opacity:0;transform:translate(%spx,-%spx)}}' % (
            c, c, f(i * .2), c, f(random.Random(i).uniform(-30, 40)), f(random.Random(i * 5).uniform(180, 300))))
    out = layers('d5', T, cam, [(.08, sky, None), (.22, rid, 'bl2'), (.55, lights, 'bl15'), (1, figs + tab, None), (1.0, glow, None), (1.7, fire + sparks, 'bl6')])
    return out

def sc_shebalance():
    T = 6.0; s = []
    names = ['dwór o poranku', 'kawa na tarasie', 'joga na trawie', 'wieczór przy stole – śmiech']
    for i, fn in enumerate([shot_manor, shot_coffee, shot_yoga, shot_table]):
        c = uid('sh'); show_win(c, T, SH[i], SH[i + 1])
        s.append('<g class="%s">%s</g>' % (c, fn(T, SH[i], SH[i + 1])))
        ev(10 + SH[i], 'ujęcie 5%s: %s' % ('abcd'[i], names[i]))
    # złota godzina – korekcja
    s.append('<g class="gh5">%s</g>' % overlay('#F5C48A', .22, 'soft-light'))
    A('.gh5', K([(0, 'opacity:.4'), (1.3, 'opacity:.4', EIO), (1.7, 'opacity:1')], T))
    s.append(vign(.38))
    # przejście a→b: przepływająca mgła
    s.append('<g class="mw5"><rect x="0" y="-20" width="1500" height="1000" fill="url(#mistH)"/></g>')
    A('.mw5', K([(0, 'transform:translateX(560px)'), (1.2, 'transform:translateX(560px)', 'cubic-bezier(.45,0,.55,1)'), (1.8, 'transform:translateX(-1520px)')], T))
    ev(11.2, 'przejście: mgła przepływa przez kadr (do 11.8)')
    # przejście b→c: smugi ruchu przy pionowym „whip-tilt”
    s.append('<g class="wt5"><g filter="url(#bl2)">' + ''.join('<rect x="%s" y="-40" width="%s" height="1040" fill="#FFF6E6" opacity="%s"/>' % (f(random.Random(i).uniform(20, 520)), f(random.Random(i * 3).uniform(1.5, 3.5)), f(random.Random(i * 7).uniform(.15, .35))) for i in range(8)) + '</g></g>')
    A('.wt5', K([(0, 'opacity:0'), (2.9, 'opacity:0', 'ease-in'), (3.0, 'opacity:1', 'ease-out'), (3.1, 'opacity:0')], T))
    ev(12.72, 'przejście: szybki ruch kamery w górę za parą z kubka → w dół na łąkę (13.0)')
    # przejście c→d: rozjaśnienie złotym światłem
    s.append('<g class="gd5">%s<ellipse cx="420" cy="300" rx="420" ry="420" fill="url(#warmGlow)" style="mix-blend-mode:screen"/></g>' % overlay('#FFEFD4', 1, 'screen'))
    A('.gd5', K([(0, 'opacity:0'), (4.24, 'opacity:0', 'cubic-bezier(.5,0,.8,.4)'), (4.5, 'opacity:.82', 'cubic-bezier(.2,.6,.3,1)'), (4.86, 'opacity:0')], T))
    ev(14.5, 'przejście: rozbłysk złotego światła → wieczór')
    # przejście d→logo: światełko girlandy rośnie w poświatę
    s.append('<g class="ho5"><circle cx="270" cy="413" r="60" fill="url(#haloEnd)"/></g>')
    S('.ho5{transform-origin:270px 413px}')
    A('.ho5', K([(0, 'opacity:0;transform:scale(.2)'), (5.5, 'opacity:0;transform:scale(.3)', 'cubic-bezier(.4,0,.2,1)'), (5.66, 'opacity:1;transform:scale(1.2)', 'cubic-bezier(.55,0,.3,1)'), (6.0, 'opacity:1;transform:scale(24)')], T))
    s.append('<g class="cr5"><rect x="-20" y="-20" width="580" height="1000" fill="#F2EFEB"/></g>')
    A('.cr5', K([(0, 'opacity:0'), (5.72, 'opacity:0', 'cubic-bezier(.5,0,.6,1)'), (5.98, 'opacity:1')], T))
    ev(15.6, 'MATCH: światełko girlandy rośnie w poświatę logo (do 16.0)')
    # napisy
    s.append(line_up(T, '3 dni w Beskidach.', 270, 198, 56, .32, '#3a302b', st=.09, t_out=1.62))
    ev(10.32, 'napis „3 dni w Beskidach.”')
    for k, (w, t) in enumerate([('Rozmowy.', 1.84), ('Ruch.', 2.44), ('Inspiracja.', 3.04)]):
        s.append(line_wipe(T, w, 44, 186 + k * 62, 58, t, .34, '#3a302b', 'start', t_out=4.24 + k * .04, x0=30, w=460))
        ev(10 + t, 'napis „%s”' % w)
    s.append(letters(T, 'Czas na równowagę.', 266, 206, 52, 4.56, '#FBF6EE', st=.032, t_out=5.5))
    ev(14.56, 'napis „Czas na równowagę.”')
    return ''.join(s), T

# ================= SCENA 6: Zaproszenie (16–20 s) =================
def sc_logo():
    T = 4.0; s = []
    cam = [(0, 270, 470, 1.06, 270, 470, 0, 'cubic-bezier(.3,0,.25,1)'), (T, 270, 470, 1.0, 270, 470, 0)]
    bg = '<rect x="-400" y="-400" width="1340" height="1800" fill="#F2EFEB"/><circle cx="270" cy="300" r="420" fill="url(#logoHalo)"/>'
    lnd = uid('ln')
    line = '<path class="%s" pathLength="1" d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linecap="round" opacity=".7"/>' % (lnd, smooth([(-40, 860), (60, 820), (140, 846), (230, 790), (320, 840), (400, 806), (480, 838), (580, 812)]), SAGE)
    line += '<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-linecap="round" opacity=".45"/>' % (smooth([(-40, 900), (90, 870), (200, 890), (300, 862), (420, 888), (580, 866)]), SAGE)
    S('.%s{stroke-dasharray:1}' % lnd)
    A('.' + lnd, K([(0, 'stroke-dashoffset:1'), (.3, 'stroke-dashoffset:1', EIO), (1.6, 'stroke-dashoffset:0')], T))
    # sygnet: kamienie odsłaniane od dołu
    sg, sgc = uid('sg'), uid('sgc')
    logo = '<clipPath id="%s"><rect class="%s" x="150" y="130" width="240" height="170"/></clipPath>' % (sgc, sg)
    logo += '<g clip-path="url(#%s)"><g class="sgm"><use href="#signCur" transform="translate(270,212) scale(.25)" style="color:%s"/></g></g>' % (sgc, DKG)
    S('.%s{transform-origin:0 300px}' % sg)
    A('.' + sg, K([(0, 'transform:scaleY(0)'), (.08, 'transform:scaleY(0)', 'cubic-bezier(.3,0,.2,1)'), (.62, 'transform:scaleY(1)')], T))
    A('.sgm', K([(0, 'transform:translateY(14px)'), (.08, 'transform:translateY(14px)', 'cubic-bezier(.2,.8,.25,1)'), (.7, 'transform:translateY(0)')], T))
    wc = uid('wc')
    logo += '<clipPath id="%sc"><rect class="%s" x="60" y="290" width="420" height="50"/></clipPath>' % (wc, wc)
    logo += '<g clip-path="url(#%sc)"><use href="#logoWord" transform="translate(270,318) scale(.6)" style="color:%s"/></g>' % (wc, DKG)
    S('.%s{transform-origin:60px 0}' % wc)
    A('.' + wc, K([(0, 'transform:scaleX(0)'), (.48, 'transform:scaleX(0)', 'cubic-bezier(.4,0,.2,1)'), (1.02, 'transform:scaleX(1)')], T))
    logo += '<g class="tg6"><use href="#logoTag" transform="translate(270,354) scale(.41)" style="color:%s"/></g>' % BROWN
    A('.tg6', K([(0, 'opacity:0;transform:translateY(10px)'), (.92, 'opacity:0;transform:translateY(10px)', ESNAP), (1.18, 'opacity:1;transform:translateY(0)')], T))
    ev(16.08, 'logo: sygnet wyrasta (kamienie od dołu)'); ev(16.48, 'logo: napis SHE BALANCE'); ev(16.92, 'hasło logo')
    bk = bokeh(3, (-10, 600, 120, 760), ['#F6DDA8', '#FBEBD0'], (10, 20), 31, (.18, .3)) + bokeh(3, (440, 120, 560, 300), ['#F6DDA8', '#FBEBD0'], (10, 22), 32, (.18, .3))
    s.append(layers('l6', T, cam, [(.3, bg, None), (.6, line, None), (1, logo, None), (1.35, bk, 'bl4')]))
    s.append(vign(.22))
    # data, przycisk, hasło
    s.append(line_up(T, DATA_CAMPU, 270, 428, 26, 1.24, INK, serif=False, weight=800, st=.05))
    ev(17.24, 'data i miejsce: %s' % DATA_CAMPU)
    s.append('<g transform="translate(270,526)"><g class="bt6"><rect x="-172" y="-46" width="344" height="92" rx="46" fill="#3a2a20" opacity=".16" transform="translate(0,6)"/>'
             '<rect x="-172" y="-46" width="344" height="92" rx="46" fill="%s"/>' % BROWN +
             T_(CTA1, 0, -5, 30, CREAM2, '', 'middle', False, 800) + T_(CTA2, 0, 27, 22, '#F1E2D3', '', 'middle', False, 700, 'letter-spacing:.03em') +
             '<g clip-path="url(#btnClip)"><rect class="bsh6" x="-60" y="-70" width="44" height="140" fill="url(#shine)" transform="rotate(18)"/></g></g></g>')
    S('.bt6{transform-origin:0 0}')
    A('.bt6', K([(0, 'opacity:0;transform:scale(.7)'), (1.5, 'opacity:0;transform:scale(.7)', 'cubic-bezier(.2,.8,.3,1)'), (1.72, 'opacity:1;transform:scale(1.03)', 'ease-in-out'), (1.86, 'opacity:1;transform:scale(1)'),
                 (3.3, 'opacity:1;transform:scale(1)', 'ease-in-out'), (3.45, 'opacity:1;transform:scale(1.04)', 'ease-in-out'), (3.62, 'opacity:1;transform:scale(1)')], T))
    A('.bsh6', K([(0, 'transform:rotate(18deg) translateX(-190px)'), (2.0, 'transform:rotate(18deg) translateX(-190px)', EIO), (2.55, 'transform:rotate(18deg) translateX(270px)')], T))
    ev(17.5, 'przycisk „Zarezerwuj miejsce → shebalance.pl”'); ev(18.0, 'połysk na przycisku'); ev(19.3, 'puls przycisku')
    s.append(line_up(T, CLAIM[0], 270, 652, 58, 2.24, INK, st=.1))
    s.append(line_up(T, CLAIM[1], 270, 716, 58, 2.44, INK, st=.1))
    ev(18.24, 'hasło „Tym razem wybierz siebie.”')
    return ''.join(s), T

SCENES = [('liczba', sc_liczba, DARK), ('chaos', sc_chaos, DARK), ('polowa', sc_polowa, DARK), ('zatrzymanie', sc_zatrzymanie, '#D7D3CB'),
          ('shebalance', sc_shebalance, CREAM), ('zaproszenie', sc_logo, CREAM)]

def build():
    parts, sj = [], []
    t = 0; starts = []
    for sid, fn, bg in SCENES:
        svg, T = fn()
        parts.append('<g class="scene" data-s="%s">%s</g>' % (sid, svg))
        sj.append("{id:'%s',d:%s,bg:'%s'}" % (sid, f(T), bg)); starts.append(t); t += T
    tpl = (HERE / 'szablon.html').read_text(encoding='utf-8')
    html = (tpl.replace('@@CSS@@', '\n'.join(CSS)).replace('@@DEFS@@', DEFS_EXTRA + ''.join(DEFS))
            .replace('@@SCENES@@', '\n'.join(parts)).replace('@@SCJS@@', ','.join(sj)))
    OUT.write_text(html, encoding='utf-8')
    print('ok', OUT, len(html), 'reguł', len(CSS), 'czas', t, 'starty', starts)
    for tt, w in sorted(EV): print('  %6.2f  %s' % (tt, w))

if __name__ == '__main__':
    build()
