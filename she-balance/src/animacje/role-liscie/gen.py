# -*- coding: utf-8 -*-
# Generator animacji „Role opadają jak liście” (SheBalance, reel 9:16, 30 s).
# Uruchom: python3 src/animacje/role-liscie/gen.py  → zapisuje src/animacje/role-liscie.html
# Cała choreografia to statyczne SVG + keyframes CSS (deterministycznie, bez losowania w runtime).
# Czasy w keyframes są liczone od początku sceny (tak działa silnik).
import math, random, pathlib, itertools

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / 'role-liscie.html'
R = random.Random(20261105)

# ---------- paleta ----------
SAGE, DKG, BEIGE, CREAM, CREAM2, BROWN = '#A4B8B0', '#58756C', '#E3CCC1', '#F2EFEB', '#F4F2EF', '#6E5446'
RUST, MUST, GOLD2, WBEIGE = '#B5582F', '#D4A23A', '#E8C872', '#C6B8AA'
EIN = 'cubic-bezier(.2,.9,.25,1.15)'   # wejścia (lekki overshoot)
EOUT = 'cubic-bezier(.6,0,.8,.2)'      # wyjścia
EIO = 'cubic-bezier(.45,0,.2,1)'       # ruchy postaci / kamery
ESOFT = 'cubic-bezier(.3,0,.2,1)'

CSS = []
_ctr = itertools.count()

def K(frames, T=None, ease=EIO, it='1', fill='both', delay=0):
    """Keyframes na osi czasu: frames = [(t, 'props') | (t, 'props', 'easing')]; zwraca skrót animation."""
    name = 'k%d' % next(_ctr)
    T = T or frames[-1][0]
    if frames[0][0] > 0:
        frames = [(0,) + tuple(frames[0][1:2])] + list(frames)
    if frames[-1][0] < T - 1e-6:
        frames = list(frames) + [(T, frames[-1][1])]
    ks = []
    for fr in frames:
        body = fr[1]
        if len(fr) > 2: body += ';animation-timing-function:' + fr[2]
        ks.append('%.3f%%{%s}' % (min(100, fr[0] / T * 100), body))
    CSS.append('@keyframes %s{%s}' % (name, ''.join(ks)))
    return '%s %.3fs %s %.3fs %s %s' % (name, T, ease, delay, it, fill)

def A(sel, *anims, active=True, extra=''):
    sels = ','.join(('.active ' if active else '') + s.strip() for s in sel.split(','))
    CSS.append('%s{animation:%s%s}' % (sels, ','.join(anims), extra))

def S(css):
    CSS.append(css)

def uid(p='e'):
    return '%s%d' % (p, next(_ctr))

def f(v):
    return ('%.1f' % v).rstrip('0').rstrip('.')

def smooth(pts, closed=False):
    """Catmull-Rom → ścieżka Beziera przez punkty."""
    if closed: P = [pts[-1]] + pts + pts[:2]
    else: P = [pts[0]] + pts + [pts[-1]]
    d = 'M%s,%s' % (f(pts[0][0]), f(pts[0][1]))
    n = len(pts) if closed else len(pts) - 1
    for i in range(1, n + 1):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += ' C%s,%s %s,%s %s,%s' % tuple(map(f, (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])))
    return d + (' Z' if closed else '')

def ridge(x0, x1, pts, bottom, fill, extra=''):
    """Grzbiet: gładka linia przez pts, domknięta do bottom."""
    d = smooth([(x0, pts[0][1])] + pts + [(x1, pts[-1][1])])
    d += ' L%s,%s L%s,%s Z' % (f(x1), f(bottom), f(x0), f(bottom))
    return '<path d="%s" fill="%s" %s/>' % (d, fill, extra)

def rnd_ridge(x0, x1, y, amp, n, seed, bottom, fill, extra=''):
    r = random.Random(seed)
    pts = [(x0 + (x1 - x0) * i / n, y + r.uniform(-amp, amp)) for i in range(n + 1)]
    return ridge(x0 - 1, x1 + 1, pts, bottom, fill, extra)

# ---------- postacie ----------
def FIG(who, cls, cx, feet, s, wrap='', mirror=False, pre='', post=''):
    """Postać w całej sylwetce: cx = środek, feet = y stóp, s = skala. wrap = klasa grupy (np. do skoku/pochylenia)."""
    tx, ty = cx - 110 * s, feet - 712 * s
    inner = '/*FIG_%s:%s*/' % (who, cls)
    body = pre + inner + post
    if mirror: body = '<g transform="translate(220,0) scale(-1,1)">%s</g>' % body
    return '<g transform="translate(%s,%s) scale(%s)"><g class="%s">%s</g></g>' % (f(tx), f(ty), s, wrap, body)

def L2W(cx, feet, s, lx, ly, mirror=False):
    if mirror: lx = 220 - lx
    return (cx - 110 * s + lx * s, feet - 712 * s + ly * s)

def ghost(who, cls, arm, content):
    """„Duch” ramienia: ta sama hierarchia i klasy co w postaci → rekwizyt porusza się razem z dłonią."""
    return '<g class="fig fig%s %s ghost"><g class="body"><g class="arm%s"><g class="fore%s">%s</g></g></g></g>' % (who, cls, arm, arm, content)

# ---------- karteczki ----------
def card_w(label):
    return round(len(label) * 10.2 + 24)

def card_body(label, lines=None):
    lines = lines or [label]
    w = max(card_w(l) for l in lines); h = 36 if len(lines) == 1 else 56
    s = '<rect x="%s" y="%s" width="%s" height="%s" rx="3" fill="#000" opacity=".12" transform="translate(2,3)"/>' % (f(-w / 2), f(-h / 2), w, h)
    s += '<rect x="%s" y="%s" width="%s" height="%s" rx="3" fill="%s" stroke="#8f8f8f" stroke-width=".8"/>' % (f(-w / 2), f(-h / 2), w, h, CREAM)
    s += '<path d="M%s,%s h%s" stroke="#d9d4cc" stroke-width="1"/>' % (f(-w / 2 + 6), f(-h / 2 + 5), w - 12)
    for i, l in enumerate(lines):
        y = 6.5 if len(lines) == 1 else (-3 + 20 * i)
        s += '<text x="0" y="%s" font-size="18" text-anchor="middle" class="cardT">%s</text>' % (f(y), l)
    s += '<circle cx="0" cy="%s" r="1.8" fill="#8a8a8a"/>' % f(h / 2 - 1)
    return s, w, h

def loop_card(label, cx, cy, S_, ax=12, ay=6, rot=8, period=2.4, phase=0.0, sag=16, pop=None, lines=None,
              thread_col='#6f6f6f', n=16, cls=''):
    """Karteczka krążąca po ósemce + nitka do ramienia S_ (zsynchronizowane keyframes)."""
    body, w, h = card_body(label, lines)
    kc, kt = [], []
    for i in range(n + 1):
        u = i / n; a = 2 * math.pi * u + phase
        x = cx + ax * math.sin(a); y = cy + ay * math.sin(2 * a); r = rot * math.sin(a + .8)
        kc.append((u * period, 'transform:translate(%spx,%spx) rotate(%sdeg)' % (f(x), f(y), f(r))))
        px, py = x, y + h / 2 - 1
        mx, my = (S_[0] + px) / 2, (S_[1] + py) / 2 + sag
        kt.append((u * period, "d:path('M%s %s Q%s %s %s %s')" % tuple(map(f, (S_[0], S_[1], mx, my, px, py)))))
    c, t = uid('c'), uid('t')
    A('.' + c, K(kc, ease='linear', it='infinite'))
    A('.' + t, K(kt, ease='linear', it='infinite'))
    thread = '<path class="thr %s" d="M0 0" fill="none" stroke="%s" stroke-width=".9"/>' % (t, thread_col)
    pp = ''
    if pop is not None:
        pp = uid('p')
        A('.' + pp, K([(pop, 'transform:scale(0);opacity:0'), (pop + .22, 'transform:scale(1.06);opacity:1', 'ease-out'), (pop + .36, 'transform:scale(1)')], ease=EIN))
        tp = uid('p')
        A('.' + tp, K([(pop, 'opacity:0'), (pop + .2, 'opacity:1')]))
        thread = '<g class="%s">%s</g>' % (tp, thread)
    cardsvg = '<g class="%s %s"><g class="%s">%s</g></g>' % (c, cls, pp, body)
    return thread, cardsvg

# ---------- elementy wspólne ----------
def rain(n, seed, op=.3, col='#F4F4F4', speed=(.55, .8), x0=-60, x1=720):
    r = random.Random(seed); s = ''
    for i in range(n):
        x = r.uniform(x0, x1); y = r.uniform(-60, 0); dur = r.uniform(*speed)
        s += '<line class="rain" x1="%s" y1="%s" x2="%s" y2="%s" style="animation-duration:%.2fs;animation-delay:-%.2fs"/>' % (
            f(x), f(y), f(x - 2.6), f(y + 15), dur, r.uniform(0, dur))
    return '<g stroke="%s" stroke-width="1.3" stroke-linecap="round" opacity="%s">%s</g>' % (col, op, s)

S('.rain{animation:rainK .7s linear infinite}@keyframes rainK{to{transform:translate(-176px,1000px)}}')

def silhouette(x, feet, s, col, walk_dur=1.0, delay=0, umbrella=None, dx=0, T=2.0):
    """Anonimowa sylwetka przechodnia (bez twarzy): głowa + płaszcz + nogi; chód w miejscu i dryf dx."""
    cls = uid('sil')
    legs = uid('lg')
    g = '<g class="%s"><g transform="translate(%s,%s) scale(%s)">' % (cls, f(x), f(feet), s)
    g += '<g class="silBob" style="animation-duration:%.2fs;animation-delay:-%.2fs">' % (walk_dur / 2, delay)
    g += '<rect class="silLeg" x="-16" y="-120" width="13" height="120" rx="6" fill="%s" style="animation-duration:%.2fs;animation-delay:-%.2fs"/>' % (col, walk_dur, delay)
    g += '<rect class="silLeg" x="3" y="-120" width="13" height="120" rx="6" fill="%s" style="animation-duration:%.2fs;animation-delay:-%.2fs"/>' % (col, walk_dur, delay + walk_dur / 2)
    g += '<path d="M-30,-110 C-32,-190 -26,-236 0,-240 C26,-236 32,-190 30,-110 Z" fill="%s"/>' % col
    g += '<circle cx="0" cy="-262" r="24" fill="%s"/>' % col
    if umbrella:
        g += '<path d="M4,-250 L4,-330" stroke="%s" stroke-width="3"/><path d="M-62,-318 Q4,-386 70,-318 Q52,-326 37,-316 Q22,-328 4,-318 Q-14,-328 -29,-316 Q-44,-326 -62,-318Z" fill="%s"/>' % (col, umbrella)
    g += '</g></g></g>'
    if dx: A('.' + cls, K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(%dpx)' % dx)], ease='linear'))
    return g

S('.silBob{animation:silBob .5s ease-in-out infinite alternate}@keyframes silBob{to{transform:translateY(-6px)}}'
  '.silLeg{transform-box:fill-box;transform-origin:50% 0;animation:silLeg 1s ease-in-out infinite}@keyframes silLeg{0%,100%{transform:rotate(12deg)}50%{transform:rotate(-12deg)}}')

def paper_block(x, y, w, h, fill, win=None, cols=4, rows=6, winfill='#9a9a9a', accent=None):
    s = '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x), f(y), f(w), f(h), fill)
    if win:
        mx, my = w * .14, 18
        cw = (w - 2 * mx) / cols; rh = min(34, (h - my - 20) / rows)
        for r_ in range(rows):
            for c_ in range(cols):
                wx = x + mx + c_ * cw + cw * .2; wy = y + my + r_ * rh
                fc = accent if (accent and (r_, c_) == accent[0]) else winfill
                fc = fc if isinstance(fc, str) else accent[1]
                s += '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(wx), f(wy), f(cw * .6), f(rh * .55), fc)
    return s

SVG = {}   # sceny: id → svg
PHONE = '<g transform="rotate(-8 168 452)"><rect x="159" y="440" width="18" height="54" rx="4" fill="#2f2f33"/><rect x="162" y="446" width="12" height="40" rx="2" fill="#56565e"/></g>'

# =====================================================================
# 1a  MIASTO (0,00–1,85) – szare miasto, tłum, karteczki wyskakują, pull-out z „mama”
# =====================================================================
def sc_miasto():
    T = 1.85; s = []
    s.append('<g class="cam c1">')
    s.append('<rect x="-300" y="-300" width="1140" height="1600" fill="url(#gCity)"/>')
    # warstwa 1: bloki (0,2×)
    b = ''
    for x, w, h in [(-80, 120, 330), (50, 96, 270), (160, 126, 372), (300, 104, 300), (420, 132, 350), (566, 100, 306), (680, 120, 340)]:
        b += paper_block(x, 650 - h, w, h, '#BDBDBD', win=True, cols=3, rows=9, winfill='#B2B2B2')
    s.append('<g class="px1">%s</g>' % b)
    A('.px1', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(-26px)')], ease='linear'))
    s.append('<rect x="-300" y="560" width="1140" height="140" fill="url(#gHaze)"/>')
    # warstwa 2: kamienice (0,6×)
    k = ''
    cols = ['#A9A9A9', '#A2A2A2', '#AFAFAF', '#A6A6A6']
    for i, x in enumerate(range(-60, 820, 128)):
        h = [300, 360, 330, 390, 320, 350, 370][i % 7]; top = 795 - h
        k += '<rect x="%d" y="%d" width="124" height="%d" fill="%s"/>' % (x, top, h, cols[i % 4])
        k += '<rect x="%d" y="%d" width="132" height="10" fill="#979797"/>' % (x - 4, top)
        if i % 2 == 0: k += '<path d="M%d,%d L%d,%d L%d,%d Z" fill="#9B9B9B"/>' % (x, top, x + 62, top - 46, x + 124, top)
        for r_ in range(4):
            for c_ in range(3):
                wx, wy = x + 16 + c_ * 36, top + 30 + r_ * 62
                fc = '#8FA7BA' if (i == 3 and r_ == 1 and c_ == 1) else '#939393'
                k += '<path d="M%d,%d v-22 a10,10 0 0 1 20,0 v22 Z" fill="%s"/>' % (wx, wy + 34, fc)
    s.append('<g class="px2">%s</g>' % k)
    A('.px2', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(-67px)')], ease='linear'))
    # tłum tylny (sylwetki bez twarzy)
    crowd = ''
    for x, sc, col, dx, dl, um in [(40, .72, '#9A9A9A', -40, .1, None), (135, .66, '#A0A0A0', 30, .5, None),
                                     (300, .7, '#979797', -55, .3, '#7F95A8'), (455, .68, '#9D9D9D', 35, .7, None), (520, .74, '#999', -45, .2, None)]:
        crowd += silhouette(x, 792, sc, col, walk_dur=1.0, delay=dl, umbrella=um, dx=dx, T=T)
    s.append(crowd)
    # „mama” – ogólna rola przy anonimowej przechodzącej (nie przy bohaterkach)
    tm, cm = loop_card('mama', 458, 556, (458, 626), ax=5, ay=4, period=2.2, sag=10, phase=1.0, pop=.3)
    s.append('<g class="mDrift">%s%s</g>' % (tm, cm))
    A('.mDrift', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(35px)')], ease='linear'))
    # chodnik (1×)
    s.append('<rect x="-300" y="782" width="1140" height="520" fill="#8C8C8C"/><rect x="-300" y="778" width="1140" height="8" fill="#7C7C7C"/>')
    lines = ''.join('<path d="M%d,800 l-40,160" stroke="#848484" stroke-width="3"/>' % x for x in range(-200, 900, 90))
    lamps = ''
    for x in (30, 420, 810):
        lamps += '<rect x="%d" y="410" width="9" height="380" fill="#7A7A7A"/><path d="M%d,414 q0,-26 30,-26 h8" fill="none" stroke="#7A7A7A" stroke-width="7"/><rect x="%d" y="382" width="30" height="14" rx="4" fill="#6f6f6f"/>' % (x, x + 4, x + 30)
    s.append('<g class="px3">%s%s</g>' % (lines, lamps))
    A('.px3', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(-111px)')], ease='linear'))
    # nitki + karteczki (nitki za postaciami)
    SA_L = L2W(190, 800, .62, 52, 238); SB_R = L2W(350, 800, .62, 170, 238)
    th, cd = [], []
    for args in [dict(label='ogarniam wszystko', lines=['ogarniam', 'wszystko'], cx=190, cy=308, S_=SA_L, phase=0.3),
                 dict(label='szefowa', cx=66, cy=452, S_=SA_L, phase=2.0, pop=.55),
                 dict(label='córka', cx=352, cy=300, S_=SB_R, phase=4.0, pop=.85)]:
        t_, c_ = loop_card(ax=10, ay=6, period=2.2, **args); th.append(t_); cd.append(c_)
    s.append(''.join(th))
    # postacie: ciężki chód, głowy w dół; A z telefonem przy uchu, B z plecakiem i kubkiem na wynos
    phone = PHONE
    s.append(FIG('A', 'walk heavy phoneA', 190, 800, .62, post=ghost('A', 'walk heavy phoneA', 'R', phone)))
    s.append(FIG('B', 'walk heavy has-pack hold has-mug', 350, 800, .62))
    s.append(''.join(cd))
    # tłum przedni na krawędziach kadru
    s.append(silhouette(-22, 1010, 1.25, '#858585', walk_dur=1.1, delay=.3, dx=-20, T=T))
    s.append(silhouette(574, 1010, 1.3, '#888', walk_dur=1.05, delay=.8, dx=18, T=T))
    s.append('</g>')
    A('.c1', K([(0, 'transform:translate(-148px,-238px) scale(2.2)'),
                (.18, 'transform:translate(-146px,-234px) scale(2.18)', 'cubic-bezier(.55,0,.15,1)'),
                (1.2, 'transform:translate(0px,0px) scale(1)', 'cubic-bezier(.4,0,.6,1)'),
                (T, 'transform:translate(-6px,-10px) scale(1.03)')], ease='linear'))
    # ekran: mżawka, winieta, tekst
    s.append(rain(60, 1))
    s.append('<rect width="540" height="960" fill="url(#vignette)"/>')
    s.append('<g class="t1a"><text x="270" y="170" font-size="50" text-anchor="middle" class="serif" fill="#2f2f2f">Każdego dnia</text></g>')
    s.append('<text x="270" y="228" font-size="50" text-anchor="middle" class="serif wsplit w1" fill="#2f2f2f">jesteśmy w wielu rolach.</text>')
    A('.t1a', K([(0, 'transform:translateY(8px)'), (.5, 'transform:translateY(0)')], ease=ESOFT))
    S('.scene.active .w1.w{transform-box:fill-box;transform-origin:50%% 100%%;animation:wRise .5s %s both;animation-delay:calc(.28s + var(--w)*.09s)}'
      '@keyframes wRise{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}' % EIN)
    return ''.join(s)

# figura: ciężki chód i poza z telefonem
S('.fig .headWrap{transform-origin:110px 205px}'
  '.fig.heavy .body{animation:hvBob 1s ease-in-out infinite}@keyframes hvBob{0%,50%,100%{transform:translateY(0)}25%,75%{transform:translateY(-4px)}}'
  '.fig.heavy .legL,.fig.heavy .shinL{animation-duration:1s}.fig.heavy .legR,.fig.heavy .shinR{animation-duration:1s;animation-delay:-.5s}'
  '.fig.heavy .armL{animation-duration:1s;animation-delay:-.5s}.fig.heavy .armR{animation-duration:1s}'
  '.fig.heavy .headWrap{transform:translateY(8px)}.fig.heavy .pupils{animation:none;transform:translateY(3px)}'
  '.fig.phoneA .armR{animation:none;transform:rotate(-22deg)}.fig.phoneA .foreR{transform:rotate(186deg)}'
  '.fig.sit .shadow{display:none}.cardT{font-family:"Mulish",sans-serif;font-weight:600;fill:#333}')

SVG['miasto'] = sc_miasto()

# =====================================================================
# DEFS i lista scen
# =====================================================================
SCENES = [('miasto', 1.85, '#C8C8C8'), ('plecy', 1.85, '#C0C0C0'), ('swiatla', 2.3, '#BDBDBD'),
          ('bus1', 2.4, BEIGE), ('bus2', 2.4, BEIGE), ('przystanek', 1.7, CREAM), ('wiatr', 3.6, CREAM),
          ('montaz', 5.0, MUST), ('taras', 3.4, CREAM), ('kamienie', 1.9, WBEIGE), ('logo', 3.6, CREAM)]

DEFS = '''
<linearGradient id="gCity" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#DEDEDE"/><stop offset=".55" stop-color="#CACACA"/><stop offset="1" stop-color="#BDBDBD"/></linearGradient>
<linearGradient id="gHaze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D0D0D0" stop-opacity="0"/><stop offset=".6" stop-color="#D0D0D0" stop-opacity=".75"/><stop offset="1" stop-color="#D0D0D0" stop-opacity="0"/></linearGradient>
<linearGradient id="gGold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#D4A23A"/><stop offset=".55" stop-color="#E0B552"/><stop offset="1" stop-color="#E8C872"/></linearGradient>
<linearGradient id="gSheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#FFF8E0" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="gEdge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/><stop offset=".06" stop-color="#fff"/><stop offset="1" stop-color="#fff"/></linearGradient>
<linearGradient id="gSkyGold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4F2EF"/><stop offset=".55" stop-color="#F1E3C4"/><stop offset="1" stop-color="#EACB84"/></linearGradient>
<linearGradient id="gSkyDawn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E3CCC1"/><stop offset=".6" stop-color="#EFE0D4"/><stop offset="1" stop-color="#F6EEDF"/></linearGradient>
<linearGradient id="gSkyDusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2F433D"/><stop offset=".55" stop-color="#46605A"/><stop offset="1" stop-color="#7C7A62"/></linearGradient>
<linearGradient id="gWood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8A6A55"/><stop offset="1" stop-color="#6E5446"/></linearGradient>
<linearGradient id="gGreyWin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D8D8D8"/><stop offset="1" stop-color="#C4C4C4"/></linearGradient>
<radialGradient id="gGlow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFF4D6" stop-opacity=".95"/><stop offset=".45" stop-color="#F6DE9C" stop-opacity=".55"/><stop offset="1" stop-color="#F6DE9C" stop-opacity="0"/></radialGradient>
<radialGradient id="gWarm" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFE7A8" stop-opacity=".9"/><stop offset="1" stop-color="#FFD27A" stop-opacity="0"/></radialGradient>
<radialGradient id="gRed" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#B5582F" stop-opacity=".7"/><stop offset="1" stop-color="#B5582F" stop-opacity="0"/></radialGradient>
<radialGradient id="gSage" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#C9DAD2" stop-opacity=".95"/><stop offset="1" stop-color="#A4B8B0" stop-opacity="0"/></radialGradient>
<filter id="fB2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter>
<filter id="fB4" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="fB8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="fB16" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16"/></filter>
<filter id="fBx" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9 1"/></filter>
<path id="beech" d="M0,-22 C11,-17 16,-4 12,8 C9,16 4,20 0,24 C-4,20 -9,16 -12,8 C-16,-4 -11,-17 0,-22 Z"/>
<path id="beechV" d="M0,-20 L0,26 M0,-8 L8,-13 M0,0 L10,-4 M0,8 L9,4 M0,-8 L-8,-13 M0,0 L-10,-4 M0,8 L-9,4" fill="none"/>
<path id="maple" d="M0,24 L1.5,12 C6,15 11,15 14,13 L12,8 C16,6 21,1 22,-3 L16,-4 C18,-9 18,-14 17,-17 C13,-15 9,-12 7,-9 L6,-14 C4,-12 2,-9 1,-7 L0,-22 L-1,-7 C-2,-9 -4,-12 -6,-14 L-7,-9 C-9,-12 -13,-15 -17,-17 C-18,-14 -18,-9 -16,-4 L-22,-3 C-21,1 -16,6 -12,8 L-14,13 C-11,15 -6,15 -1.5,12 Z"/>
<linearGradient id="gSkyW" gradientUnits="userSpaceOnUse" x1="0" y1="-500" x2="0" y2="620"><stop offset="0" stop-color="#F4F2EF"/><stop offset=".6" stop-color="#F1E3C4"/><stop offset="1" stop-color="#EACB84"/></linearGradient>
<path id="beechR" vector-effect="non-scaling-stroke" d="M0,-22 C11,-17 16,-4 12,8 C9,16 4,20 0,24 C-4,20 -9,16 -12,8 C-16,-4 -11,-17 0,-22 Z"/>
<pattern id="pPlaid" patternUnits="userSpaceOnUse" width="24" height="24"><rect width="24" height="24" fill="#F2EFEB"/><rect width="24" height="8" fill="#E3CCC1" opacity=".8"/><rect width="8" height="24" fill="#E3CCC1" opacity=".6"/><path d="M0,16 H24 M16,0 V24" stroke="#B5582F" stroke-width="1.2" opacity=".7"/></pattern>
<clipPath id="cpBeech"><use href="#beech"/></clipPath>
<clipPath id="cpMaple"><use href="#maple"/></clipPath>
'''

# =====================================================================
# 1b  PLECY (1,85–3,70) – „na wczoraj” przykleja się do B, orbita się zacieśnia, licznik 3→5→7
# =====================================================================
def sc_plecy():
    T = 1.85; s = []
    s.append('<g class="cam c2">')
    s.append('<rect x="-300" y="-300" width="1140" height="1600" fill="#B4B4B4"/>')
    f_ = ''
    for i, x in enumerate(range(-60, 1000, 150)):
        f_ += '<rect x="%d" y="-100" width="150" height="760" fill="%s"/>' % (x, '#ADADAD' if i % 2 else '#A9A9A9')
        f_ += '<rect x="%d" y="-100" width="14" height="760" fill="#A0A0A0"/>' % x
        for wy in (40, 300):
            for wx in (x + 32, x + 88):
                f_ += '<rect x="%d" y="%d" width="40" height="150" fill="#979797"/><rect x="%d" y="%d" width="40" height="150" fill="none" stroke="#BDBDBD" stroke-width="5"/><path d="M%d,%d v150 M%d,%d h40" stroke="#BDBDBD" stroke-width="3"/>' % (wx, wy, wx, wy, wx + 20, wy, wx, wy + 60)
        f_ += '<rect x="%d" y="250" width="150" height="14" fill="#B9B9B9"/><rect x="%d" y="520" width="150" height="16" fill="#B9B9B9"/>' % (x, x)
        f_ += '<rect x="%d" y="560" width="120" height="270" fill="#8E8E8E"/><path d="M%d,570 l40,0 l-60,250" stroke="#A2A2A2" stroke-width="10" opacity=".5"/>' % (x + 15, x + 40)
        if i == 3:
            f_ += '<path d="M%d,556 h140 l-10,46 h-120 Z" fill="#7F95A8"/>' % (x + 5)
            f_ += ''.join('<path d="M%d,556 h14 l-2,46 h-14 Z" fill="#94A8B8"/>' % (x + 12 + j * 28) for j in range(5))
    s.append('<g class="px4">%s</g>' % f_)
    A('.px4', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(-170px)')], ease='linear'))
    s.append('<rect x="-300" y="832" width="1140" height="400" fill="#8C8C8C"/><rect x="-300" y="828" width="1140" height="7" fill="#7B7B7B"/>')
    SAL, SAR = L2W(160, 865, .8, 52, 238), L2W(160, 865, .8, 168, 238)
    SBL, SBR = L2W(385, 865, .8, 50, 238), L2W(385, 865, .8, 170, 238)
    th, cd = [], []
    for a in [dict(label='ogarniam wszystko', lines=['ogarniam', 'wszystko'], cx=118, cy=274, S_=SAL, phase=.2),
              dict(label='córka', cx=410, cy=262, S_=SBR, phase=2.2),
              dict(label='szefowa', cx=52, cy=560, S_=SAL, phase=4.1),
              dict(label='liderka', cx=490, cy=566, S_=SBR, phase=1.0, pop=.62),
              dict(label='żona', cx=276, cy=590, S_=SAR, phase=3.0, pop=.74),
              dict(label='ogarnij', cx=272, cy=301, S_=SBL, phase=5.0, pop=1.2),
              dict(label='przyjaciółka', cx=262, cy=250, S_=SAR, phase=.9, pop=1.34)]:
        t_, c_ = loop_card(ax=9, ay=5, rot=9, period=1.5, sag=7, **a); th.append(t_); cd.append(c_)
    s.append(''.join(th))
    s.append(FIG('A', 'walk heavy phoneA', 160, 865, .8, post=ghost('A', 'walk heavy phoneA', 'R', PHONE)))
    # „na wczoraj” – przylatuje i przykleja się do ramienia B (porusza się z tułowiem)
    body, w, h = card_body('na wczoraj')
    stick = '<g class="fig figB walk heavy"><g class="body"><g class="stick">%s</g></g></g>' % body
    A('.stick', K([(0, 'transform:translate(420px,40px) rotate(40deg) scale(1.25);opacity:0'),
                   (.28, 'transform:translate(420px,40px) rotate(40deg) scale(1.25);opacity:1', 'cubic-bezier(.5,0,.9,.6)'),
                   (.52, 'transform:translate(150px,300px) rotate(-16deg) scale(1.38,1.1)', 'ease-out'),
                   (.62, 'transform:translate(150px,300px) rotate(-14deg) scale(1.2,1.3)', 'ease-in-out'),
                   (.74, 'transform:translate(150px,300px) rotate(-14deg) scale(1.25)')]))
    s.append(FIG('B', 'walk heavy has-pack hold has-mug glanceB', 385, 865, .8, post=stick))
    A('.fig.glanceB .headWrap', K([(0, 'transform:translate(0,8px) rotate(0)'), (.5, 'transform:translate(0,8px) rotate(0)'),
                                    (.72, 'transform:translate(7px,4px) rotate(7deg)', EIN), (1.25, 'transform:translate(7px,4px) rotate(7deg)'),
                                    (1.55, 'transform:translate(0,8px) rotate(0)')]))
    A('.fig.glanceB .pupils', K([(0, 'transform:translate(0,3px)'), (.52, 'transform:translate(0,3px)'), (.66, 'transform:translate(5px,4px)'),
                                 (1.28, 'transform:translate(5px,4px)'), (1.45, 'transform:translate(0,3px)')]))
    s.append(''.join(cd))
    s.append('</g>')
    A('.c2', K([(0, 'transform:translate(270px,480px) scale(1.04) rotate(0deg) translate(-270px,-480px)'),
                (.45, 'transform:translate(264px,484px) scale(1.05) rotate(-.7deg) translate(-270px,-480px)'),
                (.9, 'transform:translate(275px,476px) scale(1.06) rotate(.6deg) translate(-270px,-480px)'),
                (1.35, 'transform:translate(266px,486px) scale(1.07) rotate(-.5deg) translate(-270px,-480px)'),
                (T, 'transform:translate(273px,478px) scale(1.09) rotate(.4deg) translate(-270px,-480px)')]))
    s.append(rain(60, 2))
    s.append('<rect width="540" height="960" fill="url(#vignette)"/>')
    # licznik ról – w formie karteczki
    cnt = '<g class="cnt"><rect x="-112" y="-44" width="224" height="88" rx="4" fill="#000" opacity=".12" transform="translate(3,4)"/>'
    cnt += '<rect x="-112" y="-44" width="224" height="88" rx="4" fill="%s" stroke="#8f8f8f"/><circle cx="0" cy="-34" r="3" fill="#8a8a8a"/>' % CREAM
    cnt += '<text x="-10" y="11" font-size="24" text-anchor="end" class="cardT" letter-spacing=".08em">ROLE:</text>'
    for i, (n, t0, t1) in enumerate([('3', 0, .8), ('5', .8, 1.4), ('7', 1.4, None)]):
        c = uid('n')
        fr = [(0, 'transform:translateY(16px) scale(.5);opacity:0'), (t0 + .02, 'transform:translateY(16px) scale(.5);opacity:0'),
              (t0 + .2, 'transform:none;opacity:1', EIN)]
        if t1: fr += [(t1 - .06, 'transform:none;opacity:1', EOUT), (t1 + .06, 'transform:translateY(-18px) scale(.8);opacity:0')]
        A('.' + c, K(fr, T=T))
        cnt += '<text x="4" y="22" font-size="58" class="%s" fill="%s" font-family="Mulish" font-weight="700" style="transform-box:fill-box;transform-origin:50%% 60%%">%s</text>' % (c, RUST, n)
    cnt += '</g>'
    s.append('<g transform="translate(270,178) rotate(-2)">%s</g>' % cnt)
    A('.cnt', K([(0, 'transform:translateY(-26px) rotate(-6deg);opacity:0'), (.22, 'transform:none;opacity:1', EIN)]))
    return ''.join(s)

SVG['plecy'] = sc_plecy()

# =====================================================================
# 1c  ŚWIATŁA (3,70–6,00) – przejście dla pieszych, czerwone światło, wydech, zielone z logo, zoom + iris
# =====================================================================
def sc_swiatla():
    T = 2.3; s = []
    LX, LY = 440, 414  # dolna lampa (szałwiowa)
    s.append('<g class="cam c3">')
    s.append('<rect x="-300" y="-300" width="1140" height="1600" fill="url(#gCity)"/>')
    far = ''
    for x, w, h in [(-40, 90, 360), (50, 120, 300), (170, 80, 390), (250, 130, 320), (380, 100, 420), (480, 110, 340)]:
        far += paper_block(x, 610 - h, w, h, '#B6B6B6', win=True, cols=3, rows=10, winfill='#ABABAB')
    s.append('<g class="px5">%s</g>' % far)
    A('.px5', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(-18px)')], ease='linear'))
    s.append('<rect x="-300" y="560" width="1140" height="100" fill="url(#gHaze)"/>')
    s.append('<rect x="-300" y="606" width="1140" height="36" fill="#9E9E9E"/><rect x="-300" y="640" width="1140" height="150" fill="#7E7E7E"/>')
    zeb = ''.join('<path d="M%d,646 h30 l-14,140 h-30 Z" fill="#C4C4C4"/>' % x for x in range(-20, 560, 58))
    s.append(zeb)
    s.append('<rect x="-300" y="786" width="1140" height="500" fill="#8F8F8F"/><rect x="-300" y="782" width="1140" height="8" fill="#A5A5A5"/>')
    # sygnalizator
    s.append('<rect x="435" y="280" width="11" height="520" fill="#626262"/>')
    s.append('<rect x="%d" y="290" width="76" height="170" rx="12" fill="#555"/><rect x="%d" y="296" width="64" height="158" rx="8" fill="#4B4B4B"/>' % (LX - 38, LX - 32))
    s.append('<circle cx="%d" cy="338" r="25" fill="#3f3f3f"/><circle cx="%d" cy="%d" r="25" fill="#3f3f3f"/>' % (LX, LX, LY))
    s.append('<g class="red"><circle cx="%d" cy="338" r="70" fill="url(#gRed)"/><circle cx="%d" cy="338" r="23" fill="%s"/>'
             '<path d="M%d,324 a6,6 0 1 1 0.1,0 M%d,332 v18 M%d,336 l-7,10 M%d,336 l7,10" stroke="#8C3F20" stroke-width="4" fill="none" stroke-linecap="round"/></g>' % (LX, LX, RUST, LX, LX, LX, LX))
    s.append('<g class="grn"><circle cx="%d" cy="%d" r="80" fill="url(#gSage)"/><circle cx="%d" cy="%d" r="23" fill="#8FB0A3"/>'
             '<use href="#logoSign" transform="translate(%d,%d) scale(.3)" style="color:%s"/></g>' % (LX, LY, LX, LY, LX, LY, CREAM))
    A('.red', K([(0, 'opacity:1'), (.95, 'opacity:1'), (1.1, 'opacity:.12')]))
    A('.grn', K([(0, 'opacity:0'), (1.0, 'opacity:0'), (1.18, 'opacity:1', 'ease-out')]))
    # postacie na krawężniku
    SAL, SBR = L2W(150, 800, .5, 52, 238), L2W(252, 800, .5, 170, 238)
    th, cd = [], []
    for a in [dict(label='liderka', cx=130, cy=416, S_=SAL, phase=.5), dict(label='szefowa', cx=262, cy=404, S_=SBR, phase=2.5),
              dict(label='na wczoraj', cx=352, cy=482, S_=SBR, phase=4.4)]:
        t_, c_ = loop_card(ax=6, ay=4, rot=5, period=2.6, sag=22, **a); th.append(t_); cd.append(c_)
    s.append(''.join(th))
    s.append(FIG('A', 'sighA', 150, 800, .5, wrap='sigh'))
    s.append(FIG('B', 'has-pack hold has-mug sighB', 252, 800, .5, wrap='sigh'))
    s.append(''.join(cd))
    s.append('</g>')
    A('.sigh', K([(0, 'transform:none'), (.35, 'transform:none'), (.62, 'transform:translateY(5px) scale(1.01,.985)', ESOFT), (1.0, 'transform:translateY(2px)')]))
    S('.sigh{transform-origin:110px 712px}')
    A('.fig.sighA .headWrap', K([(0, 'transform:translateY(8px)'), (.4, 'transform:translateY(8px)'), (.6, 'transform:translateY(11px)'),
                                 (.95, 'transform:translate(4px,0) rotate(6deg)', EIO), (1.5, 'transform:translate(4px,0) rotate(6deg)'), (1.8, 'transform:translate(2px,-3px) rotate(2deg)')]))
    A('.fig.sighB .headWrap', K([(0, 'transform:translateY(8px)'), (.45, 'transform:translateY(8px)'), (.65, 'transform:translateY(11px)'),
                                 (1.0, 'transform:translate(-4px,0) rotate(-6deg)', EIO), (1.5, 'transform:translate(-4px,0) rotate(-6deg)'), (1.8, 'transform:translate(-2px,-3px) rotate(-2deg)')]))
    A('.fig.sighA .pupils', K([(0, 'transform:translateY(3px)'), (.8, 'transform:translateY(3px)'), (.95, 'transform:translate(4px,0)'), (1.5, 'transform:translate(4px,0)'), (1.7, 'transform:translate(4px,-3px)')]))
    A('.fig.sighB .pupils', K([(0, 'transform:translateY(3px)'), (.85, 'transform:translateY(3px)'), (1.0, 'transform:translate(-4px,0)'), (1.5, 'transform:translate(-4px,0)'), (1.7, 'transform:translate(3px,-3px)')]))
    A('.fig.sighA .armL', K([(0, 'transform:rotate(9deg)'), (.4, 'transform:rotate(9deg)'), (.7, 'transform:rotate(3deg)')]))
    A('.fig.sighA .armR', K([(0, 'transform:rotate(-9deg)'), (.4, 'transform:rotate(-9deg)'), (.7, 'transform:rotate(-3deg)')]))
    S('.c3{transform-origin:%dpx %dpx}' % (LX, LY))
    A('.c3', K([(0, 'transform:translate(0,0) scale(1)'), (1.72, 'transform:translate(0px,0px) scale(1.08)', EOUT),
                (2.26, 'transform:translate(%dpx,%dpx) scale(4.3)' % (270 - LX, 480 - LY)), (T, 'transform:translate(%dpx,%dpx) scale(4.3)' % (270 - LX, 480 - LY))]))
    s.append(rain(40, 3, op=.22))
    s.append('<rect width="540" height="960" fill="url(#vignette)"/>')
    s.append('<g class="q"><text x="270" y="172" font-size="50" text-anchor="middle" class="serif split fast" fill="#2f2f2f" style="--d0:.02s">Kiedy ostatnio</text>'
             '<text x="270" y="230" font-size="50" text-anchor="middle" class="serif split fast" fill="#2f2f2f" style="--d0:.22s">byłaś tylko sobą?</text></g>')
    A('.q', K([(0, 'opacity:1'), (1.84, 'opacity:1'), (2.0, 'opacity:0')]))
    S('.scene.active .fast.ch{animation-delay:calc(var(--d0,0s) + var(--i) * 17ms);animation-duration:.42s}')
    # iris zamykający się na zielonym świetle
    s.append('<circle class="iris3" cx="270" cy="480" r="1500" fill="none" stroke="#58756C" stroke-width="1200"/>')
    A('.iris3', K([(0, 'r:1500px'), (1.9, 'r:1500px'), (2.26, 'r:704px', 'cubic-bezier(.5,0,.3,1)'), (T, 'r:704px')]))
    return ''.join(s)

SVG['swiatla'] = sc_swiatla()

# =====================================================================
# 2a  BUS 1 (6,00–8,40) – wnętrze busa, za oknem szarość → kolor; A chowa telefon, B rozkłada mapę
# =====================================================================
def strip(color):
    """Pas krajobrazu za oknem: przedmieścia → pola → wzgórza (szary albo kolorowy)."""
    C = (lambda g, c: c if color else g)
    s = ''
    r = random.Random(7)
    for x in range(0, 640, 70):
        h = r.choice([90, 120, 150, 110, 170])
        s += '<rect x="%d" y="%d" width="62" height="%d" fill="%s"/>' % (x, 420 - h, h, C('#B9B9B9', r.choice([BEIGE, WBEIGE, '#D8C3B6'])))
        for wy in range(420 - h + 14, 410, 22):
            s += '<rect x="%d" y="%d" width="42" height="7" fill="%s"/>' % (x + 10, wy, C('#A9A9A9', '#C9B2A5'))
    s += rnd_ridge(560, 1800, 372, 14, 16, 3, 520, C('#BDBDBD', '#B9CBC3'))
    s += rnd_ridge(1050, 1800, 320, 45, 10, 4, 520, C('#AFAFAF', SAGE))
    s += rnd_ridge(1250, 1800, 360, 30, 8, 5, 520, C('#9F9F9F', DKG))
    if color:
        rr = random.Random(9)
        for i in range(26):
            x = rr.uniform(1260, 1780); s += '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(x), f(rr.uniform(372, 400)), f(rr.uniform(7, 13)), rr.choice([MUST, '#C8932F', '#E0B85A', RUST]))
    s += '<rect x="0" y="412" width="1800" height="110" fill="%s"/>' % C('#B4B4B4', '#BFCBA6')
    for i, y in enumerate(range(426, 520, 18)):
        s += '<rect x="620" y="%d" width="1180" height="8" fill="%s"/>' % (y, C('#ABABAB', ['#D9C38A', SAGE][i % 2]))
    return s

def sc_bus1():
    T = 2.4; s = []
    WX, WY, WW, WH = 34, 84, 472, 416
    s.append('<g class="cam c4">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="%s"/>' % BEIGE)
    s.append(''.join('<path d="M%d,60 V960" stroke="#D8BFB3" stroke-width="2"/>' % x for x in (20, 520)))
    s.append('<rect x="-100" y="-100" width="740" height="170" fill="#D9BFB2"/><rect x="-100" y="46" width="740" height="7" rx="3" fill="%s"/>' % WBEIGE)
    straps = ''
    for i, x in enumerate((96, 206, 336, 446)):
        c = uid('st')
        straps += '<g class="%s" style="transform-origin:%dpx 50px"><path d="M%d,50 v34" stroke="%s" stroke-width="5"/><ellipse cx="%d" cy="96" rx="11" ry="13" fill="none" stroke="%s" stroke-width="5"/></g>' % (c, x, x, WBEIGE, x, WBEIGE)
        A('.' + c, 'strapK .6s ease-in-out -%.2fs infinite alternate' % (i * .17))
    S('@keyframes strapK{from{transform:rotate(-7deg)}to{transform:rotate(7deg)}}')
    s.append(straps)
    s.append('<clipPath id="cpW1"><rect x="%d" y="%d" width="%d" height="%d" rx="30"/></clipPath>' % (WX, WY, WW, WH))
    s.append('<mask id="mCol1" maskUnits="userSpaceOnUse" x="-200" y="0" width="1000" height="700"><rect class="edge1" x="0" y="0" width="1600" height="700" fill="url(#gEdge)"/></mask>')
    A('.edge1', K([(0, 'transform:translateX(560px)'), (.35, 'transform:translateX(560px)'), (2.1, 'transform:translateX(-130px)', EIO)]))
    s.append('<g clip-path="url(#cpW1)">')
    s.append('<rect x="0" y="0" width="540" height="600" fill="url(#gGreyWin)"/><g class="strip1">%s</g>' % strip(False))
    s.append('<g mask="url(#mCol1)"><rect x="0" y="0" width="540" height="600" fill="url(#gSkyGold)"/><g class="strip1">%s</g></g>' % strip(True))
    A('.strip1', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(-760px)')], ease='linear'))
    s.append('<path class="refl" d="M60,84 l90,0 l-150,416 l-90,0 Z M190,84 l30,0 l-150,416 l-30,0 Z" fill="#fff" opacity=".13"/>')
    A('.refl', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(120px)')], ease='linear'))
    # napis na zaparowanej szybie
    s.append('<ellipse class="fog1" cx="270" cy="196" rx="210" ry="66" fill="#fff" opacity=".6" filter="url(#fB16)"/>')
    A('.fog1', K([(0, 'opacity:0;transform:scale(.7)'), (.5, 'opacity:.62;transform:scale(1)', ESOFT)]))
    S('.fog1{transform-origin:270px 196px}')
    s.append('<mask id="mWy" maskUnits="userSpaceOnUse" x="0" y="0" width="540" height="400"><rect class="wyR" x="44" y="130" width="456" height="120" fill="#fff"/></mask>')
    A('.wyR', K([(0, 'transform:scaleX(0)'), (.42, 'transform:scaleX(0)'), (1.2, 'transform:scaleX(1)', 'cubic-bezier(.4,.1,.4,1)')]))
    S('.wyR{transform-origin:44px 0}')
    s.append('<text x="270" y="218" font-size="62" text-anchor="middle" class="serif" fill="#4A655C" mask="url(#mWy)">Wyjeżdżamy.</text>')
    s.append('</g>')
    s.append('<rect x="%d" y="%d" width="%d" height="%d" rx="30" fill="none" stroke="#D3B8AB" stroke-width="16"/>' % (WX, WY, WW, WH))
    s.append('<rect x="%d" y="%d" width="%d" height="%d" rx="24" fill="none" stroke="#EAD8CF" stroke-width="3"/>' % (WX + 7, WY + 7, WW - 14, WH - 14))
    # ławka, postacie, karteczki – wszystko buja się razem
    s.append('<g class="rock">')
    s.append('<rect x="14" y="520" width="512" height="130" rx="22" fill="%s"/><rect x="14" y="520" width="512" height="14" rx="7" fill="#6A877E"/>' % DKG)
    s.append('<rect x="8" y="640" width="524" height="34" rx="12" fill="#4E6961"/><rect x="24" y="672" width="492" height="96" fill="#48615A"/>')
    s.append('<rect x="-100" y="766" width="740" height="300" fill="%s"/><rect x="-100" y="766" width="740" height="6" fill="#B5A596"/>' % WBEIGE)
    SAR, SBL, SBR = L2W(185, 834, .66, 168, 238), L2W(355, 834, .66, 50, 238), L2W(355, 834, .66, 170, 238)
    t1, c1 = loop_card('szefowa', 176, 372, SAR, ax=8, ay=4, period=2.2, sag=10, phase=.4)
    t2, c2 = loop_card('na wczoraj', 372, 366, SBL, ax=8, ay=4, period=2.2, sag=10, phase=2.4)
    t3, c3 = loop_card('liderka', 480, 470, SBR, ax=6, ay=5, period=2.2, sag=12, phase=4.0)
    s.append('<g class="dim1">%s</g>%s%s' % (t1, t2, t3))
    phone = '<g class="ph1">%s</g>' % PHONE
    s.append(FIG('A', 'sit busA', 185, 834, .66, wrap='leanA', post=ghost('A', 'sit busA', 'R', phone)))
    mp = ('<g class="crMap"><g class="unf">'
          '<path d="M-4,-40 L40,-46 L82,-38 L124,-46 L124,40 L82,48 L40,40 L-4,46 Z" fill="%s" stroke="#C9BBAE" stroke-width="1.5"/>'
          '<path d="M40,-46 V40 M82,-38 V48" stroke="#D8CCBF" stroke-width="2"/>'
          '<path d="M6,24 C26,4 40,20 58,0 S96,-20 114,-30" fill="none" stroke="%s" stroke-width="4" stroke-dasharray="7 5"/>'
          '<path d="M60,30 l14,-26 l10,14 l8,-10 l16,22 Z" fill="%s"/><circle cx="96" cy="-22" r="6" fill="%s"/></g></g>') % (CREAM, DKG, SAGE, RUST)
    s.append(FIG('B', 'sit busB', 355, 834, .66, post=ghost('B', 'sit busB', 'L', '<g transform="translate(50,452)">%s</g>' % mp)))
    s.append('<g class="dim1">%s</g>%s%s' % (c1, c2, c3))
    # oparcia foteli rzędu przed nimi (zasłaniają nogi)
    s.append('<path d="M-10,700 q0,-26 30,-26 h210 q30,0 30,26 V980 H-10Z M290,700 q0,-26 30,-26 h210 q30,0 30,26 V980 H290Z" fill="#4E6961"/>'
             '<path d="M10,690 h220 M310,690 h220" stroke="#6A877E" stroke-width="6" stroke-linecap="round"/><rect x="-20" y="760" width="580" height="8" fill="#6E8A80"/>')
    s.append('</g>')
    A('.dim1', K([(0, 'opacity:1'), (.85, 'opacity:1'), (1.15, 'opacity:.28')]))
    A('.ph1', K([(0, 'opacity:1'), (.8, 'opacity:1'), (.95, 'opacity:0')]))
    A('.rock', 'rockK .6s ease-in-out infinite alternate')
    S('@keyframes rockK{from{transform:translateY(0) rotate(0)}to{transform:translateY(2.5px) rotate(.35deg)}}.rock{transform-origin:270px 760px}')
    # A: telefon → do kieszeni, potem zagląda w mapę
    A('.fig.busA .armR', K([(0, 'transform:rotate(14deg)'), (.45, 'transform:rotate(14deg)'), (.9, 'transform:rotate(-2deg)', EIO)]))
    A('.fig.busA .foreR', K([(0, 'transform:rotate(118deg)'), (.45, 'transform:rotate(118deg)'), (.9, 'transform:rotate(24deg)', EIO)]))
    A('.fig.busA .headWrap', K([(0, 'transform:translateY(7px)'), (.8, 'transform:translateY(7px)'), (1.05, 'transform:translateY(0)'),
                                (1.3, 'transform:translateY(0)'), (1.6, 'transform:translate(5px,3px) rotate(8deg)', EIO)]))
    A('.fig.busA .pupils', K([(0, 'transform:translateY(3px)'), (.85, 'transform:translateY(3px)'), (1.05, 'transform:translate(3px,0)'), (1.35, 'transform:translate(3px,0)'), (1.55, 'transform:translate(5px,3px)')]))
    A('.leanA', K([(0, 'transform:rotate(0)'), (1.3, 'transform:rotate(0)'), (1.7, 'transform:rotate(4deg)', EIO)]))
    S('.leanA{transform-origin:110px 460px}')
    # B: rozkłada mapę
    A('.fig.busB .armL', K([(0, 'transform:rotate(7deg)'), (.3, 'transform:rotate(7deg)'), (.75, 'transform:rotate(12deg)', EIO)]))
    A('.fig.busB .foreL', K([(0, 'transform:rotate(-6deg)'), (.3, 'transform:rotate(-6deg)'), (.75, 'transform:rotate(-152deg)', EIO)]))
    A('.fig.busB .crMap', K([(0, 'transform:rotate(-1deg)'), (.3, 'transform:rotate(-1deg)'), (.75, 'transform:rotate(140deg)', EIO)]))
    A('.fig.busB .unf', K([(0, 'transform:scale(.12,.5);opacity:0'), (.55, 'transform:scale(.12,.5);opacity:1'), (1.0, 'transform:scale(1)', EIN)]))
    A('.fig.busB .pupils', K([(0, 'transform:none'), (.8, 'transform:none'), (1.0, 'transform:translate(-3px,3px)')]))
    s.append('</g>')
    A('.c4', K([(0, 'transform:translate(270px,420px) scale(1) translate(-270px,-420px)'), (T, 'transform:translate(270px,420px) scale(1.06) translate(-270px,-420px)')]))
    # iris otwiera się z zielonego światła
    s.append('<circle class="iris4" cx="270" cy="480" r="704" fill="none" stroke="#58756C" stroke-width="1200"/>')
    A('.iris4', K([(0, 'r:704px'), (.55, 'r:1900px', 'cubic-bezier(.5,0,.2,1)')]))
    return ''.join(s)

SVG['bus1'] = sc_bus1()

# =====================================================================
# 2b  BUS 2 (8,40–10,80) – jesienne Beskidy w 5 warstwach, dłoń na szybie, push-in, hamowanie
# =====================================================================
def sc_bus2():
    T = 2.4; s = []
    s.append('<g class="cam c5">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="%s"/>' % BEIGE)
    s.append('<clipPath id="cpW2"><rect x="16" y="36" width="508" height="612" rx="40"/></clipPath>')
    s.append('<g clip-path="url(#cpW2)">')
    s.append('<rect x="0" y="0" width="540" height="700" fill="url(#gSkyGold)"/>')
    s.append('<circle cx="400" cy="440" r="170" fill="url(#gGlow)"/>')
    def layer(cls, svg, dx):
        A('.' + cls, K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(%dpx)' % dx)], ease='linear'))
        return '<g class="%s">%s</g>' % (cls, svg)
    s.append(layer('L1', rnd_ridge(-50, 1300, 360, 42, 18, 11, 700, '#C9D6CF'), -30))
    s.append(layer('L2', rnd_ridge(-50, 1300, 412, 32, 20, 12, 700, SAGE), -80))
    s.append(layer('Lm', '<ellipse cx="200" cy="452" rx="320" ry="22" fill="#fff" opacity=".7" filter="url(#fB8)"/><ellipse cx="700" cy="448" rx="300" ry="18" fill="#fff" opacity=".6" filter="url(#fB8)"/>', -70))
    rr = random.Random(21); beech = ''
    for i in range(70):
        x = rr.uniform(-40, 1500); beech += '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(x), f(470 + rr.uniform(-6, 26)), f(rr.uniform(8, 15)), rr.choice([MUST, '#C8932F', '#E0B85A', MUST, RUST]))
    s.append(layer('L3', rnd_ridge(-50, 1500, 482, 18, 30, 13, 700, DKG) + beech, -210))
    spr = ''
    x = -40
    while x < 1900:
        h = rr.uniform(60, 120); spr += '<path d="M%s,610 L%s,%s L%s,610 Z" fill="%s"/>' % (f(x - h * .28), f(x), f(610 - h), f(x + h * .28), rr.choice(['#3F5A52', '#46625A', '#3A534C']))
        x += rr.uniform(22, 40)
    s.append(layer('L4', spr + '<rect x="-60" y="600" width="2000" height="60" fill="#3F5A52"/>', -560))
    for i, t0 in enumerate((.35, 1.35)):
        c = uid('rt')
        s.append('<g class="%s" filter="url(#fBx)"><rect x="-8" y="250" width="16" height="420" fill="#4A3A30"/><circle cx="0" cy="250" r="80" fill="%s"/><circle cx="-50" cy="300" r="55" fill="%s"/></g>' % (c, MUST if i == 0 else RUST, '#C8932F'))
        A('.' + c, K([(0, 'transform:translateX(760px)'), (t0, 'transform:translateX(760px)'), (t0 + .55, 'transform:translateX(-260px)', 'linear')]))
    s.append('<path class="refl2" d="M40,36 l70,0 l-200,612 l-70,0 Z" fill="#fff" opacity=".12"/>')
    A('.refl2', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(90px)')], ease='linear'))
    s.append('<ellipse class="print" cx="449" cy="515" rx="30" ry="36" fill="#fff" opacity=".45" filter="url(#fB8)"/>')
    A('.print', K([(0, 'opacity:0'), (.9, 'opacity:0'), (1.3, 'opacity:.5')]))
    s.append('</g>')
    s.append('<rect x="16" y="36" width="508" height="612" rx="40" fill="none" stroke="#D6BCAF" stroke-width="18"/>')
    s.append('<rect x="30" y="820" width="480" height="300" rx="40" fill="%s"/><rect x="30" y="820" width="480" height="16" rx="8" fill="#6A877E"/>' % DKG)
    s.append(FIG('B', 'bB', 365, 1240.6, 1.05))
    s.append(FIG('A', 'bA', 150, 1319.6, 1.05, wrap='leanA2'))   # A nad ramieniem B, głowa niżej, obok twarzy B
    s.append('</g>')
    A('.leanA2', K([(0, 'transform:rotate(3deg)'), (.9, 'transform:rotate(3deg)'), (1.5, 'transform:rotate(8deg)', EIO)]))
    S('.leanA2{transform-origin:110px 712px}')
    A('.fig.bA .headWrap', K([(0, 'transform:rotate(0)'), (.95, 'transform:rotate(0)'), (1.55, 'transform:rotate(7deg) translate(2px,2px)', EIO)]))
    A('.fig.bA .eyes', K([(0, 'transform:scaleY(1)'), (1.4, 'transform:scaleY(1)'), (1.6, 'transform:scaleY(.12)')]))
    A('.fig.bB .armR', K([(0, 'transform:rotate(-7deg)'), (.3, 'transform:rotate(-7deg)'), (.9, 'transform:rotate(-174deg)', EIO)]))
    A('.fig.bB .foreR', K([(0, 'transform:rotate(6deg)'), (.3, 'transform:rotate(6deg)'), (.9, 'transform:rotate(-2deg)', EIO)]))
    A('.fig.bB .pupils', K([(0, 'transform:none'), (.4, 'transform:none'), (.6, 'transform:translate(3px,-3px)')]))
    A('.fig.bB .smile', K([(0, 'transform:scale(1)'), (1.2, 'transform:scale(1)'), (1.45, 'transform:scale(1.14,1.3)', EIN)]))
    A('.c5', K([(0, 'transform:translate(270px,700px) scale(1) translate(-270px,-700px)'),
                (2.08, 'transform:translate(270px,700px) scale(1.25) translate(-270px,-700px)', EIO),
                (2.16, 'transform:translate(270px,708px) scale(1.255) translate(-270px,-700px)', 'ease-out'),
                (2.26, 'transform:translate(270px,696px) scale(1.25) translate(-270px,-700px)', 'ease-in-out'),
                (T, 'transform:translate(270px,701px) scale(1.25) translate(-270px,-700px)')]))
    s.append('<rect width="540" height="960" fill="url(#vignette)" opacity=".6"/>')
    s.append('<text x="270" y="150" font-size="56" text-anchor="middle" class="serif wsplit w2" fill="#2f2f2f" style="--d0:.2s">Im wyżej,</text>')
    s.append('<text x="270" y="214" font-size="56" text-anchor="middle" class="serif wsplit w2" fill="#2f2f2f" style="--d0:.8s">tym lżej.</text>')
    S('.scene.active .w2.w{transform-box:fill-box;transform-origin:50%% 100%%;animation:wDrop .55s %s both;animation-delay:calc(var(--d0) + var(--w)*.2s)}'
      '@keyframes wDrop{from{opacity:0;transform:translateY(-30px) rotate(-7deg)}to{opacity:1;transform:none}}' % EIN)
    return ''.join(s)

SVG['bus2'] = sc_bus2()

# =====================================================================
# 3a  PRZYSTANEK (10,80–12,50) – drzwi busa, A i B zeskakują, B poprawia plecak, A łapie daszek
# =====================================================================
def beech_tree(x, base, h, seed, cls=''):
    r = random.Random(seed)
    s = '<g class="%s" style="transform-origin:%dpx %dpx">' % (cls, x, base)
    s += '<path d="M%d,%d q-4,-%d 2,-%d M%d,%d q-20,-30 -40,-44 M%d,%d q20,-24 34,-40" stroke="#5A4539" stroke-width="%d" fill="none" stroke-linecap="round"/>' % (
        x, base, h * .5, h * .9, x, base - h * .55, x, base - h * .7, max(4, h // 18))
    for i in range(16):
        s += '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(x + r.uniform(-h * .42, h * .42)), f(base - h * .8 + r.uniform(-h * .3, h * .22)), f(r.uniform(h * .1, h * .18)),
                                                            r.choice([MUST, '#C8932F', '#E0B85A', MUST, '#CF8F34']))
    return s + '</g>'

def sc_przystanek():
    T = 1.7; s = []
    s.append('<g class="cam c6">')
    s.append('<rect x="-300" y="-300" width="1200" height="1600" fill="url(#gSkyGold)"/><circle cx="140" cy="430" r="200" fill="url(#gGlow)"/>')
    s.append(rnd_ridge(-100, 700, 400, 30, 10, 31, 900, '#C9D6CF'))
    s.append(rnd_ridge(-100, 700, 450, 26, 10, 32, 900, SAGE))
    s.append('<ellipse class="mist6" cx="300" cy="488" rx="420" ry="20" fill="#fff" opacity=".7" filter="url(#fB8)"/>')
    A('.mist6', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(40px)')], ease='linear'))
    s.append(rnd_ridge(-100, 700, 540, 16, 10, 33, 900, DKG))
    s.append('<path d="M180,720 C260,700 300,660 220,640 S160,600 260,586 S380,570 330,552" fill="none" stroke="#E6DCCB" stroke-width="7" stroke-linecap="round"/>')
    rr = random.Random(34)
    s.append(''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(rr.uniform(-60, 660)), f(rr.uniform(535, 575)), f(rr.uniform(8, 14)), rr.choice([MUST, '#C8932F', '#E0B85A', RUST])) for _ in range(34)))
    s.append('<rect x="-300" y="640" width="1200" height="700" fill="#8FA79E"/><rect x="-300" y="640" width="1200" height="30" fill="#9DB2A9"/>')
    s.append(beech_tree(520, 700, 190, 35, 'sw1'))
    A('.sw1', 'swayK 1.4s ease-in-out infinite alternate')
    S('@keyframes swayK{from{transform:rotate(-2deg)}to{transform:rotate(3deg)}}')
    s.append('<rect x="-300" y="800" width="1200" height="80" fill="%s"/><rect x="-300" y="800" width="1200" height="6" fill="#D6CABD"/><rect x="-300" y="878" width="1200" height="400" fill="#9DB2A9"/>' % WBEIGE)
    # wiata
    s.append('<g><rect x="440" y="600" width="12" height="202" fill="%s"/><rect x="600" y="600" width="12" height="202" fill="%s"/>' % (BROWN, BROWN) +
             ''.join('<rect x="452" y="%d" width="160" height="22" fill="%s"/>' % (y, '#8A6A55' if (y // 24) % 2 else '#7D5F4C') for y in range(612, 740, 24)) +
             '<path d="M420,612 L520,560 L640,612 Z" fill="#5A4539"/><rect x="460" y="746" width="140" height="10" rx="4" fill="#5A4539"/></g>')
    # bus (drzwi szerokie – postacie wychodzą z dwóch różnych miejsc w drzwiach)
    s.append('<g><rect x="-240" y="430" width="445" height="392" rx="34" fill="%s"/><rect x="-240" y="740" width="445" height="60" fill="%s"/>' % (SAGE, DKG) +
             '<rect x="-210" y="470" width="250" height="120" rx="14" fill="#E9EFEC"/><path d="M-160,470 l50,0 l-60,120 l-50,0 Z" fill="#fff" opacity=".5"/>'
             '<rect x="62" y="452" width="138" height="352" rx="8" fill="#3F5750"/><rect x="64" y="790" width="134" height="14" fill="#6E8A80"/>'
             '<g class="doorL"><rect x="62" y="452" width="69" height="352" fill="#C8D6D0" stroke="#8FA79E" stroke-width="3"/></g>'
             '<g class="doorR"><rect x="131" y="452" width="69" height="352" fill="#C8D6D0" stroke="#8FA79E" stroke-width="3"/></g>'
             '<circle cx="-130" cy="822" r="30" fill="#2F3B37"/><circle cx="-130" cy="822" r="12" fill="#8FA79E"/><circle cx="10" cy="822" r="30" fill="#2F3B37"/><circle cx="10" cy="822" r="12" fill="#8FA79E"/></g>')
    S('.doorL{transform-origin:62px 0;transform:scaleX(.12)}.doorR{transform-origin:200px 0;transform:scaleX(.12)}')
    # skaczące postacie z karteczkami (B pierwsza, A 0,32 s później; różne punkty startu)
    def jumper(who, cls, cx, x0, t0, cards):
        jx, jy, sq = uid('jx'), uid('jy'), uid('sq')
        th = ''.join(c[0] for c in cards); cd = ''.join(c[1] for c in cards)
        g = '<g class="%s"><g class="%s"><g class="%s">%s%s%s</g></g></g>' % (jx, jy, sq, th, FIG(who, cls, cx, 850, .5), cd)
        dx = x0 - cx
        A('.' + jx, K([(0, 'transform:translateX(%dpx)' % dx), (t0, 'transform:translateX(%dpx)' % dx), (t0 + .46, 'transform:translateX(0)', 'cubic-bezier(.3,.6,.5,1)')]))
        A('.' + jy, K([(0, 'transform:translateY(-46px)'), (t0, 'transform:translateY(-46px)'), (t0 + .18, 'transform:translateY(-104px)', 'cubic-bezier(.2,.7,.4,1)'),
                       (t0 + .46, 'transform:translateY(0)', 'cubic-bezier(.6,0,.9,.5)')]))
        A('.' + sq, K([(0, 'transform:none'), (max(0, t0 - .12), 'transform:none'), (t0, 'transform:scale(1.04,.93)'), (t0 + .1, 'transform:scale(.97,1.04)'),
                       (t0 + .46, 'transform:none'), (t0 + .54, 'transform:scale(1.06,.9)', 'ease-out'), (t0 + .7, 'transform:none', EIN)]))
        S('.%s{transform-origin:%dpx 850px}' % (sq, cx))
        return g
    SA = L2W(280, 850, .5, 168, 238); SB = L2W(400, 850, .5, 170, 238); SBL = L2W(400, 850, .5, 50, 238)
    ca = [loop_card('szefowa', 262, 452, SA, ax=8, ay=5, period=2, sag=14, phase=.2, pop=.62)]
    cb = [loop_card('córka', 372, 430, SBL, ax=7, ay=5, period=2, sag=14, phase=1.2), loop_card('liderka', 440, 386, SB, ax=5, ay=5, period=2, sag=14, phase=3.2)]
    s.append(jumper('A', 'capA', 280, 102, .42, ca))
    s.append(jumper('B', 'has-pack packB', 400, 170, .1, cb))
    A('.fig.capA .armR', K([(0, 'transform:rotate(-7deg)'), (.98, 'transform:rotate(-7deg)'), (1.22, 'transform:rotate(-150deg)', EIO), (1.5, 'transform:rotate(-150deg)'), (1.7, 'transform:rotate(-10deg)', EIO)]))
    A('.fig.capA .foreR', K([(0, 'transform:rotate(6deg)'), (.98, 'transform:rotate(6deg)'), (1.22, 'transform:rotate(-75deg)', EIO), (1.5, 'transform:rotate(-75deg)'), (1.7, 'transform:rotate(4deg)', EIO)]))
    A('.fig.capA .headWrap', K([(0, 'transform:none'), (1.15, 'transform:none'), (1.28, 'transform:translateY(3px) rotate(-3deg)'), (1.55, 'transform:none')]))
    A('.fig.packB .body', K([(0, 'transform:none'), (.75, 'transform:none'), (.9, 'transform:translateY(-6px)', EIO), (1.0, 'transform:translateY(-6px)'), (1.15, 'transform:none', EIN)]))
    A('.fig.packB .armL', K([(0, 'transform:rotate(7deg)'), (.7, 'transform:rotate(7deg)'), (.9, 'transform:rotate(-12deg)'), (1.2, 'transform:rotate(7deg)')]))
    A('.fig.packB .foreL', K([(0, 'transform:rotate(-6deg)'), (.7, 'transform:rotate(-6deg)'), (.9, 'transform:rotate(-120deg)'), (1.2, 'transform:rotate(-6deg)')]))
    A('.fig.packB .armR', K([(0, 'transform:rotate(-7deg)'), (.7, 'transform:rotate(-7deg)'), (.9, 'transform:rotate(12deg)'), (1.2, 'transform:rotate(-7deg)')]))
    A('.fig.packB .foreR', K([(0, 'transform:rotate(6deg)'), (.7, 'transform:rotate(6deg)'), (.9, 'transform:rotate(120deg)'), (1.2, 'transform:rotate(6deg)')]))
    # trawa na pierwszym planie
    s.append(grass(-40, 580, 915, 7, 'g6'))
    A('.g6', 'grassK 1.1s ease-in-out infinite alternate')
    s.append('</g>')
    S('.c6{transform-origin:250px 900px}')
    A('.c6', K([(0, 'transform:translateX(0) scale(1.2)'), (T, 'transform:translateX(-8px) scale(1.25)')]))
    s.append('<rect width="540" height="960" fill="url(#vignette)" opacity=".5"/>')
    return ''.join(s)

def grass(x0, x1, y, seed, cls, h=(26, 46), col=DKG):
    r = random.Random(seed); s = ''
    x = x0
    while x < x1:
        hh = r.uniform(*h)
        s += '<g class="%s" style="transform-origin:%spx %dpx;animation-delay:-%.2fs"><path d="M%s,%d q-4,-%s 6,-%s M%s,%d q6,-%s 14,-%s M%s,%d q-6,-%s -10,-%s" stroke="%s" stroke-width="3" fill="none" stroke-linecap="round"/></g>' % (
            cls, f(x), y, r.uniform(0, 1), f(x), y, f(hh * .6), f(hh), f(x + 3), y, f(hh * .5), f(hh * .8), f(x - 2), y, f(hh * .5), f(hh * .7), col)
        x += r.uniform(14, 30)
    return s
S('@keyframes grassK{from{transform:rotate(-4deg)}to{transform:rotate(5deg)}}')

SVG['przystanek'] = sc_przystanek()

# =====================================================================
# 3b+3c  WIATR (12,50–16,10) – KULMINACJA: nitki pękają, karteczki zwijają się w złote liście i wirują ku szczytom
# =====================================================================
def catmull(pts, n):
    """Próbki (n+1) krzywej Catmulla-Roma przez pts (równomiernie po segmentach)."""
    P = [pts[0]] + pts + [pts[-1]]; out = []
    segs = len(pts) - 1
    for k in range(n + 1):
        u = k / n * segs; i = min(int(u), segs - 1); t = u - i
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        t2, t3 = t * t, t * t * t
        out.append(tuple(.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    return out

def gold_leaf(kind, sc=1.4, sheen_delay=0.0):
    shape = '#beech' if kind == 'b' else '#maple'
    cp = 'cpBeech' if kind == 'b' else 'cpMaple'
    sh = uid('sh')
    A('.' + sh, 'sheenK 1.1s ease-in-out -%.2fs infinite' % sheen_delay)
    veins = '<use href="#beechV" stroke="#B07F22" stroke-width="1" opacity=".7"/>' if kind == 'b' else '<path d="M0,22 V-18 M0,4 L13,-12 M0,4 L-13,-12 M0,12 L14,4 M0,12 L-14,4" stroke="#B07F22" stroke-width="1" fill="none" opacity=".7"/>'
    return ('<g transform="scale(%s)"><use href="%s" fill="url(#gGold)" stroke="#C08A2A" stroke-width=".8"/>%s'
            '<g clip-path="url(#%s)"><rect class="%s" x="-12" y="-30" width="14" height="60" fill="url(#gSheen)" transform="rotate(20)"/></g>'
            '<path d="M0,22 q1,5 -2,9" stroke="#8C6414" stroke-width="1.6" fill="none"/></g>') % (sc, shape, veins, cp, sh)
S('@keyframes sheenK{0%{transform:translateX(-26px) rotate(20deg)}60%,100%{transform:translateX(30px) rotate(20deg)}}')

def flight(pts, t0, dur, n=18, ease_pow=1.6):
    """Keyframes translate wzdłuż krzywej (start szybki, koniec wolniejszy)."""
    smp = catmull(pts, 60)
    fr = []
    for k in range(n + 1):
        tau = k / n
        u = 1 - (1 - tau) ** ease_pow
        p = smp[min(60, int(round(u * 60)))]
        fr.append((t0 + tau * dur, 'transform:translate(%spx,%spx)' % (f(p[0]), f(p[1]))))
    return fr

def sc_wiatr():
    T = 3.6; s = []
    FEET, SA, SB, SC = 830, 175, 365, .72
    s.append('<g class="punch"><g class="cam c7">')
    s.append('<rect x="-400" y="-800" width="1400" height="2200" fill="url(#gSkyW)"/>')
    s.append('<circle cx="120" cy="300" r="260" fill="url(#gGlow)" opacity=".8"/>')
    s.append(ridge(-400, 1000, [(-300, 120), (-120, 40), (60, 110), (190, -20), (300, 50), (430, -130), (520, -50), (620, -100), (780, 60)], 1200, '#C9D6CF'))
    s.append('<path d="M400,-104 L430,-130 L462,-100 L446,-96 L430,-108 L414,-94 Z" fill="#F4F2EF" opacity=".8"/>')
    s.append(ridge(-400, 1000, [(-300, 270), (-60, 200), (120, 270), (300, 180), (470, 120), (580, 170), (800, 230)], 1200, SAGE))
    s.append('<ellipse class="mist7" cx="250" cy="330" rx="520" ry="26" fill="#fff" opacity=".75" filter="url(#fB8)"/>')
    A('.mist7', K([(0, 'transform:translateX(-30px)'), (T, 'transform:translateX(60px)')], ease='linear'))
    s.append(ridge(-400, 1000, [(-300, 420), (0, 380), (240, 430), (480, 360), (800, 410)], 1200, '#7F978E'))
    rr = random.Random(71)
    s.append(ridge(-400, 1000, [(-300, 560), (100, 540), (330, 575), (600, 530), (900, 560)], 1200, DKG))
    s.append(''.join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(rr.uniform(-80, 620)), f(rr.uniform(535, 580)), f(rr.uniform(8, 15)), rr.choice([MUST, '#C8932F', '#E0B85A', MUST])) for _ in range(40)))
    s.append(beech_tree(-10, 790, 260, 72, 'tw1') + beech_tree(560, 800, 240, 73, 'tw2'))
    gust = [(0, 'transform:rotate(0)'), (.3, 'transform:rotate(-1deg)'), (.5, 'transform:rotate(7deg)'), (.7, 'transform:rotate(3deg)'), (.9, 'transform:rotate(8deg)'),
            (1.1, 'transform:rotate(4deg)'), (1.3, 'transform:rotate(7deg)'), (1.6, 'transform:rotate(3deg)'), (2.2, 'transform:rotate(1deg)'), (T, 'transform:rotate(0)')]
    A('.tw1,.tw2', K(gust))
    s.append('<rect x="-400" y="760" width="1400" height="700" fill="#8FA79E"/><rect x="-400" y="760" width="1400" height="26" fill="#9DB2A9"/>')
    # smugi wiatru (spirale od lewej) – omijają strefę twarzy
    for i, (y0, t0, w_) in enumerate([(250, .0, 5), (700, .08, 6), (290, .25, 3), (790, .3, 4), (220, .5, 4), (640, .6, 7), (270, .85, 3), (760, 1.0, 5), (600, 1.25, 3), (240, 1.4, 4)]):
        up = y0 < 400
        k = -1 if up else 1
        pts = [(-160, y0), (40, y0 - 20 * k), (170, y0 + 12 * k), (250, y0 - 40 * k * (-1 if up else 1)), (210, y0 - 85 * (1 if up else -1) * 0 - 80), (160, y0 - 40), (240, y0 - 8), (420, y0 - 34), (720, y0 - 110)]
        if not up: pts = [(x, y + 60) if j in (3, 4, 5) else (x, y) for j, (x, y) in enumerate(pts)]
        pts = [(x, max(min(y, 330) if up else max(y, 530), -300)) for x, y in pts]
        c = uid('wd')
        s.append('<path class="%s" d="%s" pathLength="100" fill="none" stroke="#fff" stroke-width="%d" stroke-linecap="round" opacity=".6" stroke-dasharray="26 120"/>' % (c, smooth(pts), w_))
        A('.' + c, K([(0, 'stroke-dashoffset:126'), (t0, 'stroke-dashoffset:126'), (t0 + .9, 'stroke-dashoffset:-102', 'cubic-bezier(.4,.1,.6,.9)')]))
    # postacie
    shA, shA2 = L2W(SA, FEET, SC, 52, 238), L2W(SA, FEET, SC, 168, 238)
    shB, shB2 = L2W(SB, FEET, SC, 50, 238), L2W(SB, FEET, SC, 170, 238)
    cards = [  # etykieta, pozycja, ramię, trasa lotu (omija twarze), liść
        ('żona', (52, 470), shA, [(40, 400), (72, 300), (180, 212), (330, 130), (430, 40), (458, -24)], 'b'),
        ('szefowa', (130, 282), shA, [(170, 232), (262, 184), (360, 110), (470, 22), (500, -70)], 'm'),
        (['ogarniam', 'wszystko'], (270, 160), shA2, [(320, 118), (392, 60), (440, -20), (418, -112)], 'b'),
        ('przyjaciółka', (270, 228), shB, [(338, 200), (424, 150), (492, 62), (520, -8)], 'm'),
        ('ogarnij', (58, 604), shA, [(40, 486), (60, 330), (170, 230), (300, 150), (400, 70), (440, -40)], 'b'),
        ('na wczoraj', (414, 284), shB2, [(462, 230), (502, 140), (474, 40), (482, -82)], 'm'),
        ('liderka', (488, 470), shB2, [(510, 380), (478, 262), (522, 150), (530, 20)], 'b'),
        ('córka', (484, 604), shB2, [(514, 480), (502, 330), (452, 200), (400, 100), (396, 0)], 'm'),
        ('mama', (270, 596), shA2, [(340, 660), (452, 640), (506, 520), (500, 380), (470, 250), (440, 130), (470, -40)], 'b')]
    th, cd, fl = [], [], []
    for i, (lab, P, Sh, route, kind) in enumerate(cards):
        ts = .55 + .1 * i
        lines = lab if isinstance(lab, list) else None
        body, w, h = card_body(lab if isinstance(lab, str) else lab[0], lines)
        Ps = (P[0] + 14, P[1] - 9)                   # pozycja napięta przez wiatr
        pin = lambda p: (p[0], p[1] + h / 2 - 1)
        # nitka: luźna → napięta → pęka (koniec wraca i opada), błysk w miejscu pęknięcia
        Bp = (Sh[0] + (pin(Ps)[0] - Sh[0]) * .86, Sh[1] + (pin(Ps)[1] - Sh[1]) * .86)
        def qd(a, c, b): return "d:path('M%s %s Q%s %s %s %s')" % tuple(map(f, (a[0], a[1], c[0], c[1], b[0], b[1])))
        mid = lambda a, b, sag: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + sag)
        droop = (Sh[0] + (Bp[0] - Sh[0]) * .45 - 8, Sh[1] + (Bp[1] - Sh[1]) * .45 + 50)
        tc = uid('tw')
        A('.' + tc, K([(0, qd(Sh, mid(Sh, pin(P), 16), pin(P))), (.25, qd(Sh, mid(Sh, pin(P), 16), pin(P))),
                       (ts - .12, qd(Sh, mid(Sh, pin(Ps), 0), pin(Ps)), EIO), (ts - .06, qd(Sh, mid(Sh, pin(Ps), 1.5), pin(Ps))), (ts, qd(Sh, mid(Sh, pin(Ps), 0), pin(Ps))),
                       (ts + .01, qd(Sh, mid(Sh, Bp, 0), Bp)), (ts + .3, qd(Sh, mid(Sh, droop, 10), droop), 'cubic-bezier(.2,.8,.3,1)'), (T, qd(Sh, mid(Sh, droop, 10), droop))]),
          K([(0, 'opacity:1'), (ts + .25, 'opacity:1'), (ts + .6, 'opacity:0')]))
        th.append('<path class="%s" fill="none" stroke="#6E5446" stroke-width="1" d="M0 0"/>' % tc)
        fc = uid('fl')
        A('.' + fc, K([(0, 'transform:scale(0) rotate(0);opacity:0'), (ts - .005, 'transform:scale(0) rotate(0);opacity:0'), (ts + .07, 'transform:scale(1.5) rotate(60deg);opacity:1', 'ease-out'),
                       (ts + .22, 'transform:scale(0) rotate(120deg);opacity:0')]))
        fl.append('<g transform="translate(%s,%s)"><g class="%s"><use href="#star" fill="#FFF6D8" transform="scale(1.3)"/><circle r="4" fill="#fff"/></g></g>' % (f(Bp[0]), f(Bp[1]), fc))
        # karteczka → liść
        fly, spin, fold, cf, lf, sp = [uid(x) for x in ('fy', 'sp', 'fo', 'cf', 'lf', 'sk')]
        route_pts = [Ps] + route
        fr = [(0, 'transform:translate(%spx,%spx)' % (f(P[0]), f(P[1]))), (.25, 'transform:translate(%spx,%spx)' % (f(P[0]), f(P[1])))]
        fr += [(ts - .3, 'transform:translate(%spx,%spx)' % (f(Ps[0] - 2), f(Ps[1] + 1))), (ts - .2, 'transform:translate(%spx,%spx)' % (f(Ps[0] + 2), f(Ps[1] - 2))),
               (ts - .1, 'transform:translate(%spx,%spx)' % (f(Ps[0] - 1), f(Ps[1] + 2)))]
        dur = min(1.75, 2.95 - ts)
        fr += flight(route_pts, ts, dur)
        A('.' + fly, K(fr, ease='linear'))
        rsign = 1 if i % 2 == 0 else -1
        A('.' + spin, K([(0, 'transform:rotate(%ddeg)' % (-4 * rsign)), (.25, 'transform:rotate(%ddeg)' % (5 * rsign)), (ts - .1, 'transform:rotate(%ddeg)' % (-10 * rsign)),
                         (ts, 'transform:rotate(%ddeg)' % (12 * rsign)), (ts + dur, 'transform:rotate(%ddeg)' % (rsign * (380 + 40 * i)), 'cubic-bezier(.25,.6,.4,1)')]))
        ffr = [(0, 'transform:scale(1,1)'), (ts + .06, 'transform:scale(1,1)'), (ts + .24, 'transform:scale(.1,1.05)', 'cubic-bezier(.5,0,.9,.5)'),
               (ts + .44, 'transform:scale(1,1)', 'cubic-bezier(.2,.8,.3,1)')]
        t_ = ts + .44; k_ = 1.0; j = 0
        while t_ + .22 < ts + dur - .1:
            t_ += .22; j += 1; k_ = max(.3, 1 - (t_ - ts - .44) / (dur - .44) * .75)
            ffr.append((t_, 'transform:scale(%.2f,%.2f)' % (k_ * (.7 if j % 2 else 1.25) * .95, k_)))
        ffr.append((ts + dur, 'transform:scale(.16,.16)'))
        A('.' + fold, K(ffr, ease='ease-in-out'), K([(0, 'opacity:1'), (ts + dur - .15, 'opacity:1'), (ts + dur + .12, 'opacity:0')]))
        A('.' + cf, K([(0, 'opacity:1'), (ts + .235, 'opacity:1'), (ts + .245, 'opacity:0')]))
        A('.' + lf, K([(0, 'opacity:0'), (ts + .235, 'opacity:0'), (ts + .245, 'opacity:1')]))
        # 5 iskier z rozpadającego się napisu
        sparks = ''
        r2 = random.Random(100 + i)
        for q in range(5):
            a = r2.uniform(0, 2 * math.pi); d = r2.uniform(22, 40); c = uid('ik')
            A('.' + c, K([(0, 'transform:translate(0,0) scale(0);opacity:0'), (ts + .1, 'transform:translate(0,0) scale(0);opacity:0'),
                          (ts + .16, 'transform:translate(%spx,%spx) scale(1);opacity:1' % (f(math.cos(a) * d * .3), f(math.sin(a) * d * .3))),
                          (ts + .5, 'transform:translate(%spx,%spx) scale(.3);opacity:0' % (f(math.cos(a) * d), f(math.sin(a) * d - 10)), 'ease-out')]))
            sparks += '<circle class="%s" r="2.6" fill="#F3D27A"/>' % c
        cd.append('<g class="%s"><g class="%s"><g class="%s"><g class="%s">%s</g><g class="%s">%s</g></g></g>%s</g>' % (
            fly, spin, fold, cf, body, lf, gold_leaf(kind, 1.45, i * .13), sparks))
    # dodatkowe liście zerwane z drzew (razem ≤ 15 liści)
    for i, (start, route, t0) in enumerate([((10, 560), [(30, 420), (90, 290), (220, 200), (380, 90), (450, -60)], .75),
                                             ((-20, 640), [(20, 500), (60, 320), (200, 230), (360, 150), (500, -30)], .95),
                                             ((30, 480), [(60, 360), (150, 250), (300, 170), (420, 60), (410, -100)], 1.15),
                                             ((560, 560), [(530, 440), (500, 300), (520, 170), (480, 40), (500, -120)], .85),
                                             ((-30, 300), [(80, 240), (220, 170), (360, 90), (460, 0), (430, -130)], 1.35),
                                             ((570, 640), [(540, 500), (520, 330), (460, 180), (420, 60), (452, -60)], 1.5)]):
        fly, spin, fold = uid('xf'), uid('xs'), uid('xo')
        dur = 1.5
        A('.' + fly, K([(0, 'transform:translate(%spx,%spx)' % (f(start[0]), f(start[1])))] + flight([start] + route, t0, dur), ease='linear'),
          K([(0, 'opacity:0'), (t0, 'opacity:0'), (t0 + .1, 'opacity:1'), (t0 + dur - .1, 'opacity:1'), (t0 + dur + .1, 'opacity:0')]))
        A('.' + spin, K([(0, 'transform:rotate(0)'), (t0, 'transform:rotate(0)'), (t0 + dur, 'transform:rotate(%ddeg)' % (420 + 60 * i), 'cubic-bezier(.25,.6,.4,1)')]))
        A('.' + fold, K([(0, 'transform:scale(1,1)'), (t0 + .3, 'transform:scale(.7,1)'), (t0 + .6, 'transform:scale(1.2,1)'), (t0 + .9, 'transform:scale(.6,.8)'), (t0 + 1.2, 'transform:scale(.8,.6)'), (t0 + dur, 'transform:scale(.15,.15)')], ease='ease-in-out'))
        cd.append('<g class="%s"><g class="%s"><g class="%s">%s</g></g></g>' % (fly, spin, fold, gold_leaf('m' if i % 2 else 'b', 1.1, i * .2)))
    s.append(''.join(th))
    s.append('<g class="hopB">%s</g>' % FIG('B', 'has-pack wB', SB, FEET, SC, wrap='wLeanB'))
    s.append(FIG('A', 'wA', SA, FEET, SC, wrap='wLeanA'))
    s.append(''.join(fl) + ''.join(cd))
    s.append(grass(-200, 760, 900, 17, 'g7', h=(30, 60)))
    s.append(grass(-200, 760, 1010, 18, 'g7', h=(40, 80), col='#4E6961') + '</g>')
    A('.g7', K([(0, 'transform:rotate(0)'), (.3, 'transform:rotate(-3deg)'), (.5, 'transform:rotate(24deg)'), (.7, 'transform:rotate(14deg)'), (.9, 'transform:rotate(26deg)'),
                (1.2, 'transform:rotate(15deg)'), (1.5, 'transform:rotate(20deg)'), (2.0, 'transform:rotate(6deg)'), (T, 'transform:rotate(2deg)')]))
    s.append('</g>')
    # --- postacie: zasłaniają się, patrzą w górę, A rozkłada ramiona, B podskakuje i bierze A pod ramię
    S('.wLeanA,.wLeanB{transform-origin:110px 712px}.hopB{transform-origin:%dpx %dpx}' % (SB, FEET))
    lean = K([(0, 'transform:rotate(0)'), (.12, 'transform:rotate(0)'), (.4, 'transform:rotate(-5deg)', EIO), (1.2, 'transform:rotate(-4deg)'), (1.5, 'transform:rotate(0)', EIO)])
    A('.wLeanA', lean); A('.wLeanB', lean)
    A('.fig.wA .armL', K([(0, 'transform:rotate(7deg)'), (.1, 'transform:rotate(7deg)'), (.42, 'transform:rotate(160deg)', EIO), (1.3, 'transform:rotate(160deg)'),
                          (1.62, 'transform:rotate(104deg)', EIN), (2.5, 'transform:rotate(100deg)'), (2.9, 'transform:rotate(30deg)', EIO)]))
    A('.fig.wA .foreL', K([(0, 'transform:rotate(-6deg)'), (.1, 'transform:rotate(-6deg)'), (.42, 'transform:rotate(22deg)', EIO), (1.3, 'transform:rotate(22deg)'),
                           (1.62, 'transform:rotate(-12deg)', EIN), (2.5, 'transform:rotate(-8deg)'), (2.9, 'transform:rotate(-10deg)')]))
    A('.fig.wA .armR', K([(0, 'transform:rotate(-7deg)'), (.1, 'transform:rotate(-7deg)'), (.42, 'transform:rotate(-150deg)', EIO), (1.3, 'transform:rotate(-150deg)'),
                          (1.62, 'transform:rotate(-104deg)', EIN), (2.3, 'transform:rotate(-100deg)'), (2.65, 'transform:rotate(-38deg)', EIO)]))
    A('.fig.wA .foreR', K([(0, 'transform:rotate(6deg)'), (.1, 'transform:rotate(6deg)'), (.42, 'transform:rotate(-75deg)', EIO), (1.3, 'transform:rotate(-75deg)'),
                           (1.62, 'transform:rotate(12deg)', EIN), (2.3, 'transform:rotate(10deg)'), (2.65, 'transform:rotate(-58deg)', EIO)]))
    A('.fig.wA .headWrap', K([(0, 'transform:none'), (.1, 'transform:none'), (.4, 'transform:translateY(4px) rotate(-4deg)'), (1.2, 'transform:translateY(4px) rotate(-3deg)'),
                              (1.45, 'transform:translateY(-6px)', EIO), (2.4, 'transform:translateY(-6px)'), (2.7, 'transform:translate(2px,-2px) rotate(4deg)')]))
    A('.fig.wA .pupils', K([(0, 'transform:none'), (1.25, 'transform:none'), (1.4, 'transform:translate(1px,-4px)'), (2.4, 'transform:translate(2px,-4px)'), (2.6, 'transform:translate(4px,0)')]))
    A('.fig.wA .smile', K([(0, 'transform:scale(1)'), (1.5, 'transform:scale(1)'), (1.7, 'transform:scale(1.14,1.32)', EIN)]))
    A('.fig.wB .armL', K([(0, 'transform:rotate(7deg)'), (.15, 'transform:rotate(7deg)'), (.47, 'transform:rotate(160deg)', EIO), (1.3, 'transform:rotate(160deg)'),
                          (1.6, 'transform:rotate(25deg)', EIO), (2.35, 'transform:rotate(25deg)'), (2.7, 'transform:rotate(58deg)', EIO)]))
    A('.fig.wB .foreL', K([(0, 'transform:rotate(-6deg)'), (.15, 'transform:rotate(-6deg)'), (.47, 'transform:rotate(22deg)', EIO), (1.3, 'transform:rotate(22deg)'),
                           (1.6, 'transform:rotate(-4deg)', EIO), (2.35, 'transform:rotate(-4deg)'), (2.7, 'transform:rotate(-40deg)', EIO)]))
    A('.fig.wB .armR', K([(0, 'transform:rotate(-7deg)'), (.2, 'transform:rotate(-7deg)'), (.5, 'transform:rotate(10deg)', EIO), (1.3, 'transform:rotate(10deg)'), (1.6, 'transform:rotate(-7deg)')]))
    A('.fig.wB .foreR', K([(0, 'transform:rotate(6deg)'), (.2, 'transform:rotate(6deg)'), (.5, 'transform:rotate(100deg)', EIO), (1.3, 'transform:rotate(100deg)'), (1.6, 'transform:rotate(6deg)')]))
    A('.fig.wB .headWrap', K([(0, 'transform:none'), (.15, 'transform:none'), (.45, 'transform:translateY(4px) rotate(-5deg)'), (1.25, 'transform:translateY(4px) rotate(-4deg)'),
                              (1.5, 'transform:translateY(-6px)', EIO), (2.3, 'transform:translateY(-6px)'), (2.6, 'transform:translate(-3px,-2px) rotate(-5deg)')]))
    A('.fig.wB .pupils', K([(0, 'transform:none'), (1.3, 'transform:none'), (1.45, 'transform:translate(1px,-4px)'), (2.3, 'transform:translate(0,-4px)'), (2.5, 'transform:translate(-4px,0)')]))
    A('.fig.wB .smile', K([(0, 'transform:scale(1)'), (1.6, 'transform:scale(1)'), (1.8, 'transform:scale(1.14,1.32)', EIN)]))
    A('.fig.wB .body > .tilt', K([(0, 'transform:none'), (.2, 'transform:none'), (.45, 'transform:translateX(7px) rotate(7deg) skewX(-6deg)', EIO),
                                  (.58, 'transform:translateX(4px) rotate(4deg) skewX(-3deg)'), (.72, 'transform:translateX(8px) rotate(8deg) skewX(-7deg)'),
                                  (.88, 'transform:translateX(5px) rotate(5deg) skewX(-4deg)'), (1.04, 'transform:translateX(8px) rotate(8deg) skewX(-6deg)'),
                                  (1.2, 'transform:translateX(5px) rotate(5deg) skewX(-4deg)'), (1.4, 'transform:translateX(6px) rotate(6deg) skewX(-5deg)'), (2.1, 'transform:translateX(1px) rotate(1deg)', EIO)]))
    S('.figB .body > .tilt{transform-origin:110px 70px}')
    A('.hopB', K([(0, 'transform:none'), (1.85, 'transform:none'), (1.98, 'transform:translate(0,3px) scale(1.04,.95)'), (2.18, 'transform:translate(-18px,-44px) scale(.98,1.03)', 'cubic-bezier(.2,.7,.4,1)'),
                  (2.4, 'transform:translate(-36px,0)', 'cubic-bezier(.6,0,.9,.5)'), (2.48, 'transform:translate(-36px,0) scale(1.05,.93)'), (2.62, 'transform:translate(-36px,0)', EIN)]))
    # uderzenie przy pierwszym pęknięciu: zbliżenie + biały błysk + mocniejsze ziarno
    S('.punch{transform-origin:270px 400px}')
    A('.punch', K([(0, 'transform:scale(1)'), (.5, 'transform:scale(1)'), (.56, 'transform:scale(1.08)', 'ease-out'), (.9, 'transform:scale(1)', EIO)]))
    s.append('<rect class="snapFl" width="540" height="960" fill="#fff"/><rect class="snapGr" width="540" height="960" filter="url(#paper)" style="mix-blend-mode:multiply"/>')
    A('.snapFl', K([(0, 'opacity:0'), (.54, 'opacity:0'), (.57, 'opacity:.6'), (.66, 'opacity:0', 'ease-out')]))
    A('.snapGr', K([(0, 'opacity:0'), (.54, 'opacity:0'), (.57, 'opacity:.45'), (.66, 'opacity:0')]))
    # kamera: zoom-out + mikrowstrząsy, potem pan w górę za liśćmi
    S('.c7{transform-origin:270px 480px}')
    cam = [(0, 'transform:scale(1) translate(0px,0px)'), (.3, 'transform:scale(1) translate(0px,0px)')]
    for j, tt in enumerate([.42, .52, .62, .72, .82, .92, 1.02, 1.12, 1.22, 1.32]):
        sc_ = 1 - .15 * (tt - .3) / 1.2
        cam.append((tt, 'transform:scale(%.3f) translate(%dpx,%dpx)' % (sc_, [2, -2, 3, -1, 2, -3, 1, -2, 2, -1][j], [-1, 2, -2, 1, -1, 2, -1, 1, -1, 0][j])))
    cam += [(1.5, 'transform:scale(.85) translate(0px,0px)', EIO), (2.6, 'transform:scale(.85) translate(0px,222px)', EIO), (T, 'transform:scale(.86) translate(0px,236px)')]
    A('.c7', K(cam, ease='ease-in-out'))
    # tekst „Zostaw role.” – litery wnosi wiatr
    s.append('<g class="zr"><text x="44" y="358" font-size="72" class="serif split windch" fill="#2f2f2f" style="--d0:1.72s">Zostaw</text>'
             '<text x="44" y="432" font-size="72" class="serif split windch" fill="#2f2f2f" style="--d0:1.9s">role.</text></g>')
    S('.scene.active .windch.ch{transform-origin:50%% 80%%;animation:windIn .62s %s both;animation-delay:calc(var(--d0) + var(--i)*34ms)}'
      '@keyframes windIn{0%%{opacity:0;transform:translate(-70px,-26px) rotate(-50deg) scale(.5)}55%%{opacity:1}100%%{opacity:1;transform:none}}' % EIN)
    A('.zr', K([(0, 'opacity:1'), (3.02, 'opacity:1'), (3.16, 'opacity:0')]))
    # ostatni liść leci na kamerę → złoty kadr
    s.append('<g class="bigLeaf"><g class="bigLeafR"><use href="#beech" fill="url(#gGold)"/><use class="blv" href="#beechV" stroke="#B07F22" stroke-width=".6"/></g></g>')
    A('.bigLeaf', K([(0, 'transform:translate(480px,210px) scale(0);opacity:0'), (2.9, 'transform:translate(480px,210px) scale(0);opacity:0'),
                     (3.0, 'transform:translate(470px,220px) scale(.9);opacity:1', 'ease-out'), (3.52, 'transform:translate(270px,480px) scale(46);opacity:1', 'cubic-bezier(.55,0,.85,.35)')]))
    A('.bigLeafR', K([(0, 'transform:rotate(0)'), (2.9, 'transform:rotate(-30deg)'), (3.52, 'transform:rotate(150deg)', 'ease-in')]))
    A('.blv', K([(0, 'opacity:.8'), (3.2, 'opacity:.8'), (3.4, 'opacity:0')]))
    s.append('<rect class="goldEnd" width="540" height="960" fill="%s"/>' % MUST)
    A('.goldEnd', K([(0, 'opacity:0'), (3.46, 'opacity:0'), (3.53, 'opacity:1')]))
    return ''.join(s)

SVG['wiatr'] = sc_wiatr()

# =====================================================================
# 4  MONTAŻ (16,10–21,10): RANO: RUCH → POPOŁUDNIE: REGENERACJA → WIECZÓR: RAZEM, przejścia maską złotego liścia
# =====================================================================
def leaf_mask(mid, t0, cx, cy, r0, r1, dur=.48, s0=.3):
    """Maska liścia: okno w kształcie liścia rośnie; wokół niego złoty liść (większy) – przejście „złotym liściem”."""
    g = uid('lm')
    pre = [(0, 'transform:translate(%dpx,%dpx) rotate(%ddeg) scale(0)' % (cx, cy, r0)), (t0 - .01, 'transform:translate(%dpx,%dpx) rotate(%ddeg) scale(0)' % (cx, cy, r0))] if t0 > 0 else []
    A('.' + g, K(pre + [(t0, 'transform:translate(%dpx,%dpx) rotate(%ddeg) scale(%s)' % (cx, cy, r0, s0)),
                  (t0 + dur, 'transform:translate(270px,480px) rotate(%ddeg) scale(52)' % r1, 'cubic-bezier(.5,0,.75,.35)')]))
    m = ('<mask id="%s" maskUnits="userSpaceOnUse" x="0" y="0" width="540" height="960"><rect width="540" height="960" fill="#000"/>'
         '<g class="%s"><use href="#beech" fill="#fff"/></g></mask>') % (mid, g)
    rim = '<g class="%s"><g class="%s"><use href="#beechR" fill="none" stroke="#FFF1C4" stroke-width="3"/></g></g>' % (uid('rimo'), g)
    A('.' + rim.split('"')[1], K([(0, 'opacity:0'), (t0, 'opacity:0'), (t0 + .02, 'opacity:.9'), (t0 + dur - .05, 'opacity:.9'), (t0 + dur + .05, 'opacity:0')]))
    gc = uid('gl')
    gold = '<g class="%s"><g class="%s"><g transform="scale(1.45)"><use href="#beech" fill="url(#gGold)"/><use href="#beechV" stroke="#B07F22" stroke-width=".7" opacity=".6"/></g></g></g>' % (gc, g)
    A('.' + gc, K([(0, 'opacity:0'), (t0, 'opacity:0'), (t0 + .01, 'opacity:1'), (t0 + dur, 'opacity:1'), (t0 + dur + .01, 'opacity:0')]))
    return m, rim, gold

def sc_montaz():
    T = 5.0; s = []
    s.append('<rect width="540" height="960" fill="url(#gGold)"/><rect class="gSh" x="-300" y="-200" width="260" height="1400" fill="url(#gSheen)" opacity=".7" transform="rotate(18)"/>')
    A('.gSh', K([(0, 'transform:translateX(0) rotate(18deg)'), (.4, 'transform:translateX(760px) rotate(18deg)', ESOFT)]))
    # ---------- 4a RANO: RUCH ----------
    m1, rim1, gold1 = leaf_mask('mM1', 0, 270, 480, -70, 30, dur=.42, s0=5)
    a = ['<g class="cam m1c">']
    a.append('<rect x="-100" y="-100" width="760" height="1160" fill="url(#gSkyDawn)"/>')
    a.append('<circle cx="410" cy="520" r="230" fill="url(#gGlow)"/><circle cx="410" cy="540" r="34" fill="#F7E7BE"/>')
    rays = ''.join('<path d="M410,540 L%s,%s L%s,%s Z" fill="#FFF8E8"/>' % (f(410 + 900 * math.cos(math.radians(a_))), f(540 + 900 * math.sin(math.radians(a_))),
                                                                        f(410 + 900 * math.cos(math.radians(a_ + 5))), f(540 + 900 * math.sin(math.radians(a_ + 5)))) for a_ in (140, 158, 176, 196, 214, 236, 262))
    a.append('<g class="rays" opacity=".22">%s</g>' % rays)
    A('.rays', K([(0, 'transform:rotate(-3deg);opacity:.14'), (1.0, 'transform:rotate(0deg);opacity:.26'), (2.0, 'transform:rotate(3deg);opacity:.16')]))
    S('.rays{transform-origin:410px 540px}')
    a.append(rnd_ridge(-100, 700, 560, 22, 8, 41, 900, '#CBD6D0'))
    a.append(rnd_ridge(-100, 700, 610, 18, 8, 42, 900, SAGE))
    for i, (y, dx, op) in enumerate([(560, 70, .7), (620, -60, .75), (690, 50, .6)]):
        c = uid('fog')
        a.append('<ellipse class="%s" cx="270" cy="%d" rx="460" ry="26" fill="#fff" opacity="%s" filter="url(#fB16)"/>' % (c, y, op))
        A('.' + c, K([(0, 'transform:translateX(%dpx)' % (-dx / 2)), (2.0, 'transform:translateX(%dpx)' % (dx / 2))]))
    a.append('<rect x="-100" y="650" width="760" height="500" fill="#9DB2A9"/><rect x="-100" y="650" width="760" height="18" fill="#B3C4BC" opacity=".8"/>')
    a.append('<path d="M74,740 H228 L216,772 H58 Z" fill="%s"/><path d="M312,740 H466 L482,772 H324 Z" fill="#C9D6CF"/>' % BEIGE)
    a.append(FIG('A', 'flow', 148, 756, .56))
    a.append(FIG('B', 'flow', 392, 756, .56))
    a.append('<ellipse class="fogF" cx="270" cy="800" rx="480" ry="24" fill="#fff" opacity=".55" filter="url(#fB16)"/>')
    A('.fogF', K([(0, 'transform:translateX(40px)'), (2.0, 'transform:translateX(-40px)')]))
    a.append('</g>')
    A('.m1c', K([(0, 'transform:translate(0px,0px) scale(1)'), (2.0, 'transform:translate(-40px,-10px) scale(1.03)')]))
    flow = [(0, 'L:168;R:-168;fL:14;fR:-14;b:0'), (.35, 'L:168;R:-168;fL:14;fR:-14;b:0'), (.8, 'L:176;R:-146;fL:10;fR:-30;b:9'),
            (1.25, 'L:146;R:-176;fL:30;fR:-10;b:-9'), (1.7, 'L:46;R:-46;fL:0;fR:0;b:0'), (2.0, 'L:40;R:-40;fL:-4;fR:4;b:0')]
    def fk(key, fmt):
        out = []
        for t_, sp in flow:
            d = dict(x.split(':') for x in sp.split(';'))
            out.append((t_, 'transform:' + fmt % float(d[key])))
        return K(out)
    A('.fig.flow .armL', fk('L', 'rotate(%gdeg)')); A('.fig.flow .armR', fk('R', 'rotate(%gdeg)'))
    A('.fig.flow .foreL', fk('fL', 'rotate(%gdeg)')); A('.fig.flow .foreR', fk('fR', 'rotate(%gdeg)'))
    A('.fig.flow .body', fk('b', 'rotate(%gdeg)'))
    A('.fig.flow .eyes', K([(0, 'transform:scaleY(1)'), (.3, 'transform:scaleY(1)'), (.4, 'transform:scaleY(.12)'), (1.2, 'transform:scaleY(.12)'), (1.32, 'transform:scaleY(1)')]))
    s.append(m1 + '<g mask="url(#mM1)">%s</g>' % ''.join(a))
    # ---------- 4b POPOŁUDNIE: REGENERACJA ----------
    t2 = 1.55
    m2, rim2, gold2 = leaf_mask('mM2', t2, 400, 300, 40, 160)
    b = ['<g class="cam m2c">']
    b.append('<rect x="-100" y="-100" width="760" height="1160" fill="#4E6961"/><rect x="-100" y="-100" width="760" height="300" fill="#C9D6CF"/>')
    b.append('<circle cx="430" cy="230" r="260" fill="url(#gGlow)" opacity=".7"/>')
    rr = random.Random(51)
    for layer, (y, col, hmin, hmax) in enumerate([(360, '#6A877E', 120, 190), (470, DKG, 150, 240), (560, '#46625A', 110, 170)]):
        x = -60; tr = ''
        while x < 620:
            h = rr.uniform(hmin, hmax); tr += '<path d="M%s,%d L%s,%s L%s,%d Z" fill="%s"/>' % (f(x - h * .26), y, f(x), f(y - h), f(x + h * .26), y, col)
            x += rr.uniform(34, 60)
        b.append(tr + '<rect x="-100" y="%d" width="760" height="600" fill="%s"/>' % (y - 2, col))
    b.append('<rect x="-100" y="690" width="760" height="400" fill="url(#gWood)"/>' + ''.join('<path d="M-100,%d H660" stroke="#5E4739" stroke-width="2"/>' % y for y in range(720, 980, 34)))
    b.append('<ellipse cx="270" cy="604" rx="206" ry="44" fill="#5A4539"/><ellipse cx="270" cy="606" rx="188" ry="34" fill="#8FB0A8"/>')
    b.append('<clipPath id="cpTub"><rect x="-100" y="-100" width="740" height="712"/></clipPath><g clip-path="url(#cpTub)">')
    b.append(FIG('A', 'spaA', 205, 955, .72))
    b.append(FIG('B', 'spaB', 338, 955, .72) + '</g>')
    b.append('<path d="M82,606 A188,34 0 0 0 458,606 L458,612 A188,40 0 0 1 82,612 Z" fill="#A9C4BE" opacity=".95"/>')
    b.append('<path d="M82,606 A188,34 0 0 0 458,606" fill="none" stroke="#C9DDD7" stroke-width="3" opacity=".8"/>')
    b.append('<path d="M64,604 L80,800 Q270,836 460,800 L476,604 A206,44 0 0 1 64,604 Z" fill="url(#gWood)"/>')
    b.append(''.join('<path d="M%d,%d L%d,%d" stroke="#5E4739" stroke-width="2" opacity=".6"/>' % (x, 640 + abs(x - 270) // 12, x + (x - 270) // 30, 814 - abs(x - 270) // 10) for x in range(96, 460, 30)))
    b.append('<path d="M70,670 Q270,712 470,670 M76,760 Q270,800 464,760" fill="none" stroke="#3F3A36" stroke-width="7"/>')
    b.append('<path d="M64,604 A206,44 0 0 0 476,604" fill="none" stroke="#8A6A55" stroke-width="10"/>')
    b.append('<g><rect x="482" y="560" width="22" height="44" rx="3" fill="%s"/><circle cx="493" cy="548" r="30" fill="url(#gWarm)"/><path class="flame" d="M493,534 q8,10 0,20 q-8,-10 0,-20Z" fill="#F6C75A"/></g>' % CREAM)
    for i, (x, dl) in enumerate([(96, 0), (130, .5), (430, .25), (462, .8), (112, 1.0), (448, 1.2)]):
        c = uid('stm')
        b.append('<ellipse class="%s" cx="%d" cy="590" rx="30" ry="40" fill="#fff" filter="url(#fB8)"/>' % (c, x))
        A('.' + c, 'steamK 1.6s ease-out %.2fs infinite' % (t2 + dl - 1.6))
    S('@keyframes steamK{0%{opacity:0;transform:translateY(0) scale(.7)}35%{opacity:.5}100%{opacity:0;transform:translateY(-190px) scale(1.4)}}')
    drops = ''
    for i in range(5):
        c = uid('dr')
        A('.' + c, K([(0, 'transform:translate(0,0);opacity:0'), (2.5 + i * .12, 'transform:translate(0,0);opacity:0'), (2.56 + i * .12, 'transform:translate(0,0);opacity:1'),
                      (2.95 + i * .12, 'transform:translate(%dpx,56px);opacity:0' % ((i - 2) * 5), 'cubic-bezier(.5,0,1,.6)')]))
        drops += '<ellipse class="%s" cx="%d" cy="552" rx="2.4" ry="3.6" fill="#E8F1EE"/>' % (c, 452 + (i % 3) * 5)
    b.append(drops)
    b.append('</g>')
    S('.m2c{transform-origin:270px 540px}')
    A('.m2c', K([(0, 'transform:scale(1)'), (t2, 'transform:scale(1)'), (3.7, 'transform:scale(1.08)')]))
    A('.fig.spaA .headWrap', K([(0, 'transform:none'), (1.85, 'transform:none'), (2.3, 'transform:translate(-2px,-3px) rotate(-8deg)', EIO)]))
    A('.fig.spaA .eyes', K([(0, 'transform:scaleY(1)'), (2.0, 'transform:scaleY(1)'), (2.15, 'transform:scaleY(.1)')]))
    A('.fig.spaA .smile', K([(0, 'transform:scale(1)'), (2.1, 'transform:scale(1)'), (2.4, 'transform:scale(1.1,1.2)')]))
    A('.fig.spaB .armR', K([(0, 'transform:rotate(-7deg)'), (2.05, 'transform:rotate(-7deg)'), (2.45, 'transform:rotate(-80deg)', EIO)]))
    A('.fig.spaB .foreR', K([(0, 'transform:rotate(6deg)'), (2.05, 'transform:rotate(6deg)'), (2.5, 'transform:rotate(-100deg)', EIO), (2.9, 'transform:rotate(-92deg)'), (3.3, 'transform:rotate(-102deg)')]))
    A('.fig.spaB .pupils', K([(0, 'transform:none'), (2.4, 'transform:none'), (2.55, 'transform:translate(4px,-3px)')]))
    s.append(gold2 + m2 + '<g mask="url(#mM2)">%s</g>' % ''.join(b))
    # ---------- 4c WIECZÓR: RAZEM ----------
    t3 = 3.25
    m3, rim3, gold3 = leaf_mask('mM3', t3, 170, 640, -20, 120)
    c_ = ['<g class="cam m3c">']
    c_.append('<rect x="-200" y="-600" width="940" height="1800" fill="url(#gSkyDusk)"/>')
    rr = random.Random(61)
    for i in range(14):
        x, y = rr.uniform(20, 520), rr.uniform(-180, 150)
        c = uid('str')
        c_.append('<g transform="translate(%s,%s) scale(%s)"><use class="twinkle" href="#star" fill="#F4EBD0" style="animation-delay:-%.2fs"/></g>' % (f(x), f(y), f(rr.uniform(.3, .6)), rr.uniform(0, 1.4)))
    for i in range(6):
        x0, y0 = rr.uniform(40, 500), rr.uniform(200, 360)
        c = uid('ff')
        c_.append('<g class="%s"><circle cx="%s" cy="%s" r="10" fill="url(#gWarm)"/><circle cx="%s" cy="%s" r="2.2" fill="#FFF2C4"/></g>' % (c, f(x0), f(y0), f(x0), f(y0)))
        A('.' + c, K([(0, 'opacity:0;transform:translate(0,0)'), (4.1 + i * .1, 'opacity:0;transform:translate(0,0)'), (4.4 + i * .1, 'opacity:1;transform:translate(%dpx,-14px)' % (rr.choice([-1, 1]) * 12)),
                      (5.0, 'opacity:.9;transform:translate(%dpx,6px)' % (rr.choice([-1, 1]) * 24))]))
    c_.append(rnd_ridge(-200, 740, 470, 22, 12, 62, 900, '#2F433D'))
    gpath = 'M-20,300 Q270,420 560,300'
    c_.append('<path d="%s" fill="none" stroke="#1F2B28" stroke-width="2"/>' % gpath)
    for i in range(11):
        tt = (i + .5) / 11; x = (1 - tt) ** 2 * -20 + 2 * (1 - tt) * tt * 270 + tt * tt * 560; y = (1 - tt) ** 2 * 300 + 2 * (1 - tt) * tt * 420 + tt * tt * 300
        c_.append('<circle cx="%s" cy="%s" r="22" fill="url(#gWarm)" class="twinkle" style="animation-duration:2.2s;animation-delay:-%.2fs"/><circle cx="%s" cy="%s" r="4.5" fill="#FFE9A8"/>' % (f(x), f(y + 8), i * .37, f(x), f(y + 8)))
    # uczestniczki (uproszczone sylwetki, bez twarzy) wznoszą kubki
    for i, (x, base, sc, col) in enumerate([(34, 700, 1.0, '#8A6A55'), (96, 690, .82, '#C6B8AA'), (150, 650, .62, '#7F978E'),
                                            (392, 650, .62, '#B5A596'), (446, 690, .82, '#A4B8B0'), (508, 700, 1.0, '#E3CCC1')]):
        arm = uid('pa'); side = 1 if x > 270 else -1
        c_.append('<g transform="translate(%d,%d) scale(%s)"><path d="M-40,0 C-42,-70 -30,-104 0,-108 C30,-104 42,-70 40,0 Z" fill="%s"/><circle cx="0" cy="-132" r="26" fill="%s"/>'
                  '<g class="%s" style="transform-origin:%dpx -90px"><rect x="%d" y="-92" width="14" height="70" rx="7" fill="%s"/><rect x="%d" y="-34" width="18" height="20" rx="3" fill="%s"/></g></g>' % (
                      x, base, sc, col, col, arm, -30 * side, -37 * side - (14 if side > 0 else 0) + (0 if side > 0 else 0), col, -39 * side - (18 if side > 0 else 0) + 2, CREAM))
        A('.' + arm, K([(0, 'transform:rotate(0)'), (3.7 + i * .04, 'transform:rotate(0)'), (4.0 + i * .04, 'transform:rotate(%ddeg)' % (-150 * side * -1), EIO), (4.6, 'transform:rotate(%ddeg)' % (-140 * side * -1))]))
    mug = ('<g class="crT"><path d="M-12,-26 L12,-26 L10,4 Q0,9 -10,4 Z" fill="%s"/><path d="M11,-20 q10,2 7,12 q-2,5 -8,5" fill="none" stroke="%s" stroke-width="3.5"/>'
           '<ellipse cx="0" cy="-26" rx="12" ry="3" fill="#8a5a3c"/></g>') % (CREAM, CREAM)
    c_.append(FIG('A', 'toast', 200, 872, .66, post=ghost('A', 'toast', 'R', '<g transform="translate(168,452)">%s</g>' % mug)))
    c_.append(FIG('B', 'toast toastB', 340, 872, .66, mirror=True, post=ghost('B', 'toast toastB', 'R', '<g transform="translate(170,452)">%s</g>' % mug)))
    c_.append('<g transform="translate(270,548)">' + ''.join('<g class="%s"><use href="#star" fill="#FFE9A8" transform="scale(.7)"/></g>' % uid('tsp') for _ in range(6)) + '</g>')
    # stół
    c_.append('<rect x="-40" y="668" width="620" height="40" rx="6" fill="%s"/><rect x="-40" y="700" width="620" height="400" fill="#E3D9CD"/><rect x="-40" y="700" width="620" height="16" fill="#D5C9BB"/>' % CREAM)
    c_.append(''.join('<path d="M%d,716 q%d,120 %d,260" stroke="#D2C5B6" stroke-width="3" fill="none"/>' % (x, (x - 270) // 12, (x - 270) // 8) for x in range(10, 540, 58)))
    c_.append('<rect x="-40" y="716" width="620" height="260" fill="url(#fadeBottom)"/><path d="M-40,706 H580" stroke="%s" stroke-width="3" opacity=".5"/>' % SAGE)
    c_.append('<ellipse cx="150" cy="676" rx="42" ry="16" fill="#C08A5A"/><path d="M128,670 l10,-6 M146,670 l10,-6 M164,670 l10,-6" stroke="#9A6A42" stroke-width="3"/>')
    c_.append('<ellipse cx="396" cy="668" rx="34" ry="26" fill="%s"/><path d="M380,650 q16,18 0,36 M412,650 q-16,18 0,36" stroke="#B8862A" stroke-width="2" fill="none"/><rect x="393" y="638" width="6" height="12" fill="#5A4539"/>' % MUST)
    c_.append(''.join('<circle cx="%d" cy="%d" r="6" fill="%s"/>' % (470 + dx, 680 + dy, DKG if (dx + dy) % 3 else '#7F978E') for dx, dy in ((0, 0), (10, 0), (5, -8), (-5, -8), (5, 8), (15, -8))))
    for x in (70, 270, 470):
        c_.append('<rect x="%d" y="632" width="14" height="42" rx="2" fill="%s"/><circle cx="%d" cy="622" r="32" fill="url(#gWarm)"/><path class="flame" d="M%d,606 q8,10 0,20 q-8,-10 0,-20Z" fill="#F6C75A"/>' % (x - 7, CREAM, x, x))
    c_.append('</g>')
    tsp = [x for x in CSS if False]
    S('.m3c{transform-origin:270px 560px}')
    A('.m3c', K([(0, 'transform:translateY(0px) scale(1.12)'), (t3, 'transform:translateY(0px) scale(1.12)'), (4.3, 'transform:translateY(40px) scale(1.04)', EIO), (5.0, 'transform:translateY(140px) scale(1.0)', EIO)]))
    A('.fig.toast .armR', K([(0, 'transform:rotate(-7deg)'), (3.6, 'transform:rotate(-7deg)'), (4.0, 'transform:rotate(-38deg)', EIO), (4.6, 'transform:rotate(-36deg)')]))
    A('.fig.toast .foreR', K([(0, 'transform:rotate(6deg)'), (3.6, 'transform:rotate(6deg)'), (4.0, 'transform:rotate(196deg)', EIO), (4.6, 'transform:rotate(190deg)')]))
    A('.fig.toast .crT', K([(0, 'transform:rotate(1deg)'), (3.6, 'transform:rotate(1deg)'), (4.0, 'transform:rotate(-158deg)', EIO), (4.6, 'transform:rotate(-154deg)')]))
    A('.fig.toastB .headWrap', K([(0, 'transform:none'), (4.1, 'transform:none'), (4.2, 'transform:rotate(-5deg) translateY(-3px)'), (4.3, 'transform:rotate(3deg)'),
                                  (4.4, 'transform:rotate(-4deg) translateY(-2px)'), (4.5, 'transform:rotate(2deg)'), (4.65, 'transform:none')]))
    A('.fig.toastB .smile', K([(0, 'transform:scale(1)'), (4.05, 'transform:scale(1)'), (4.2, 'transform:scale(1.2,1.45)', EIN)]))
    A('.fig.toast .eyes', K([(0, 'transform:scaleY(1)'), (4.15, 'transform:scaleY(1)'), (4.25, 'transform:scaleY(.4)'), (4.6, 'transform:scaleY(.4)'), (4.7, 'transform:scaleY(1)')]))
    s.append(gold3 + m3 + '<g mask="url(#mM3)">%s</g>' % ''.join(c_))
    s.append(rim1 + rim2 + rim3)
    # iskry toastu (poza maską – nad kadrem stołu, w tym samym miejscu)
    # podpisy
    s.append('<g class="cap1"><text x="270" y="170" font-size="30" text-anchor="middle" class="caps capT" fill="#2f2f2f">Rano: ruch</text>'
             '<path class="cap1l" d="M190,194 H350" stroke="%s" stroke-width="2.5" pathLength="1"/></g>' % DKG)
    s.append('<mask id="mCap1" maskUnits="userSpaceOnUse" x="0" y="0" width="540" height="300"><rect class="cap1m" x="120" y="130" width="300" height="70" fill="#fff"/></mask>')
    S('.cap1{mask:url(#mCap1)}.cap1m{transform-origin:120px 0}.capT{font-weight:600;letter-spacing:.12em}')
    A('.cap1m', K([(0, 'transform:scaleX(0)'), (.42, 'transform:scaleX(0)'), (.8, 'transform:scaleX(1)', 'cubic-bezier(.3,.1,.2,1)')]))
    A('.cap1', K([(0, 'opacity:1'), (1.4, 'opacity:1'), (1.52, 'opacity:0')]))
    A('.cap1l', K([(0, 'stroke-dasharray:1;stroke-dashoffset:1'), (.6, 'stroke-dasharray:1;stroke-dashoffset:1'), (1.0, 'stroke-dasharray:1;stroke-dashoffset:0', EIO)]))
    s.append('<rect class="cap2b" x="36" y="136" width="468" height="50" rx="25" fill="%s" opacity=".92"/>' % CREAM)
    A('.cap2b', K([(0, 'opacity:0;transform:scaleX(.3)'), (1.98, 'opacity:0;transform:scaleX(.3)'), (2.3, 'opacity:.92;transform:scaleX(1)', EIN), (3.12, 'opacity:.92;transform:scaleX(1)'), (3.24, 'opacity:0;transform:scaleX(1)')]))
    S('.cap2b{transform-origin:270px 161px}')
    s.append('<text x="270" y="170" font-size="27" text-anchor="middle" class="caps capT cap2" fill="#2f2f2f">Popołudnie: regeneracja</text>')
    A('.cap2', K([(0, 'opacity:0;letter-spacing:.5em'), (2.05, 'opacity:0;letter-spacing:.5em'), (2.55, 'opacity:1;letter-spacing:.1em', 'cubic-bezier(.2,.8,.2,1)'),
                  (3.12, 'opacity:1;letter-spacing:.1em'), (3.24, 'opacity:0;letter-spacing:.1em')]))
    s.append('<g class="cap3"><text x="270" y="170" font-size="30" text-anchor="middle" class="caps capT split flick" fill="%s" style="--d0:3.75s">Wieczór: razem</text></g>' % CREAM)
    S('.scene.active .flick.ch{animation:flickK .5s linear both;animation-delay:calc(var(--d0) + var(--i)*28ms)}'
      '@keyframes flickK{0%{opacity:0;transform:none}30%{opacity:1}45%{opacity:.25}62%{opacity:1}78%{opacity:.6}100%{opacity:1;transform:none}}')
    s.append('<rect class="flashM" width="540" height="960" fill="#FFF3D6"/>')
    A('.flashM', K([(0, 'opacity:0'), (4.8, 'opacity:0'), (5.0, 'opacity:.9', 'ease-in')]))
    return ''.join(s)

SVG['montaz'] = sc_montaz()

# =====================================================================
# 5  TARAS (21,10–24,50) – złota godzina, herbata, liść wraca, „Przez 3 dni nic nie musisz.”, toast
# =====================================================================
def sc_taras():
    T = 3.4; s = []
    s.append('<g class="cam c9">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="url(#gSkyGold)"/><circle cx="300" cy="470" r="260" fill="url(#gGlow)"/>')
    s.append(rnd_ridge(-100, 700, 410, 30, 9, 81, 900, '#C9D6CF'))
    s.append('<ellipse class="mA" cx="270" cy="458" rx="400" ry="18" fill="#fff" opacity=".7" filter="url(#fB8)"/>')
    s.append(rnd_ridge(-100, 700, 470, 24, 9, 82, 900, SAGE))
    s.append('<ellipse class="mB" cx="270" cy="512" rx="420" ry="20" fill="#fff" opacity=".65" filter="url(#fB8)"/>')
    s.append(rnd_ridge(-100, 700, 530, 18, 9, 83, 900, '#7F978E'))
    s.append(rnd_ridge(-100, 700, 580, 12, 9, 84, 900, DKG))
    A('.mA', K([(0, 'transform:translateX(-30px)'), (T, 'transform:translateX(30px)')], ease='linear'))
    A('.mB', K([(0, 'transform:translateX(30px)'), (T, 'transform:translateX(-36px)')], ease='linear'))
    birds = ''.join('<path class="wing" d="M%d,%d q8,-7 14,0 q6,-7 14,0" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" style="animation-delay:-%.2fs"/>' % (x, y, BROWN, d)
                    for x, y, d in ((420, 350, .1), (448, 338, .3), (442, 366, .45)))
    s.append('<g class="birds">%s</g>' % birds)
    A('.birds', K([(0, 'transform:translate(30px,6px)'), (T, 'transform:translate(-80px,-14px)')], ease='linear'))
    S('.wing{transform-box:fill-box;transform-origin:50% 100%;animation:wingK .5s ease-in-out infinite alternate}@keyframes wingK{to{transform:scaleY(-.6)}}')
    # taras
    s.append('<rect x="-100" y="590" width="740" height="16" rx="3" fill="%s"/><rect x="-100" y="700" width="740" height="12" fill="%s"/>' % (BROWN, BROWN))
    s.append(''.join('<rect x="%d" y="606" width="11" height="96" fill="#7D5F4C"/>' % x for x in range(-20, 600, 42)))
    s.append('<g><path d="M440,584 h92 v146 l-14,6 l-12,-6 l-14,6 l-14,-6 l-14,6 l-12,-6 l-12,6 Z" fill="url(#pPlaid)"/><path d="M440,584 h92 v10 h-92Z" fill="#000" opacity=".08"/></g>')
    s.append('<rect x="-100" y="760" width="740" height="400" fill="url(#gWood)"/>' + ''.join('<path d="M-100,%d H640" stroke="#5E4739" stroke-width="2"/>' % y for y in range(790, 960, 30)))
    s.append('<rect x="70" y="600" width="400" height="16" rx="5" fill="#8A6A55"/><rect x="70" y="628" width="400" height="16" rx="5" fill="#8A6A55"/><rect x="84" y="600" width="12" height="96" fill="#5A4539"/><rect x="444" y="600" width="12" height="96" fill="#5A4539"/>'
             '<rect x="60" y="690" width="420" height="18" rx="4" fill="#8A6A55"/><rect x="80" y="706" width="12" height="80" fill="#5A4539"/><rect x="448" y="706" width="12" height="80" fill="#5A4539"/>')
    mug = ('<g class="crT2"><path d="M-12,-26 L12,-26 L10,4 Q0,9 -10,4 Z" fill="%s"/><path d="M11,-20 q10,2 7,12 q-2,5 -8,5" fill="none" stroke="%s" stroke-width="3.5"/>'
           '<ellipse cx="0" cy="-26" rx="12" ry="3" fill="#8a5a3c"/><path class="steam" d="M-4,-32 q-6,-8 0,-16 q6,-8 0,-16" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>'
           '<path class="steam" style="animation-delay:.6s" d="M5,-32 q-6,-8 0,-16 q6,-8 0,-16" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/></g>') % (BEIGE, BEIGE)
    s.append(FIG('A', 'sit terA', 205, 866, .6, post=ghost('A', 'sit terA', 'R', '<g transform="translate(168,452)">%s</g>' % mug)))
    s.append(FIG('B', 'sit terB', 335, 866, .6, mirror=True, post=ghost('B', 'sit terB', 'R', '<g transform="translate(170,452)">%s</g>' % mug)))
    # koc w kratę na kolanach (zasłania nogi), dzbanek i świeca na deskach obok
    s.append('<path d="M112,700 C160,690 220,712 270,700 C320,690 380,712 428,700 L440,790 C400,806 360,784 320,800 C280,814 240,788 200,804 C160,816 126,796 100,792 Z" fill="url(#pPlaid)"/>'
             '<path d="M112,700 C160,690 220,712 270,700 C320,690 380,712 428,700" fill="none" stroke="#C9B6A9" stroke-width="3"/>'
             '<path d="M160,712 q6,40 -4,80 M270,712 q-4,40 6,86 M360,712 q6,40 -2,82" stroke="#000" stroke-opacity=".06" stroke-width="10" fill="none"/>')
    s.append('<g transform="translate(478,808)"><path d="M-22,0 C-26,-30 26,-30 22,0 Z" fill="%s"/><path d="M22,-14 q16,-6 20,-18" stroke="%s" stroke-width="5" fill="none"/><rect x="-6" y="-30" width="12" height="6" rx="3" fill="%s"/></g>'
             '<g transform="translate(66,810)"><rect x="-8" y="-26" width="16" height="26" rx="2" fill="%s"/><circle cx="0" cy="-34" r="22" fill="url(#gWarm)"/><path class="flame" d="M0,-44 q7,9 0,17 q-7,-9 0,-17Z" fill="#F6C75A"/></g>' % (SAGE, SAGE, DKG, CREAM))
    # liść wraca jak wahadło i ląduje na barierce
    s.append('<g class="lfT"><g class="lfTr">%s</g></g>' % gold_leaf('b', 1.1))
    A('.lfT', K([(0, 'transform:translate(580px,250px)'), (.25, 'transform:translate(580px,250px)'), (.6, 'transform:translate(470px,318px)'), (.95, 'transform:translate(515px,392px)'),
                 (1.3, 'transform:translate(446px,468px)'), (1.6, 'transform:translate(482px,536px)'), (1.85, 'transform:translate(430px,582px)', 'ease-out')], ease='ease-in-out'))
    A('.lfTr', K([(0, 'transform:rotate(-40deg)'), (.25, 'transform:rotate(-40deg)'), (.6, 'transform:rotate(35deg)'), (.95, 'transform:rotate(-35deg)'), (1.3, 'transform:rotate(30deg)'),
                  (1.6, 'transform:rotate(-20deg)'), (1.85, 'transform:rotate(78deg) scale(1,.8)'), (2.0, 'transform:rotate(72deg) scale(1,.8)')], ease='ease-in-out'))
    s.append('<g transform="translate(270,560)"><g class="clk"><use href="#star" fill="#FFF3C8" transform="scale(2)"/><circle r="5" fill="#fff"/></g></g>')
    A('.clk', K([(0, 'transform:scale(0);opacity:0'), (2.78, 'transform:scale(0);opacity:0'), (2.86, 'transform:scale(1.4) rotate(40deg);opacity:1', 'ease-out'), (3.1, 'transform:scale(0) rotate(90deg);opacity:0')]))
    s.append('</g>')
    S('.c9{transform-origin:270px 540px}')
    A('.c9', K([(0, 'transform:scale(1)'), (T, 'transform:scale(1.12)')], ease=ESOFT))
    # A: dmucha na herbatę, B trzyma kubek na kolanach, zauważa liść; toast
    A('.fig.terA .armR', K([(0, 'transform:rotate(14deg)'), (2.45, 'transform:rotate(14deg)'), (2.82, 'transform:rotate(-35deg)', EIO), (T, 'transform:rotate(-33deg)')]))
    A('.fig.terA .foreR', K([(0, 'transform:rotate(128deg)'), (.4, 'transform:rotate(140deg)'), (1.3, 'transform:rotate(140deg)'), (1.6, 'transform:rotate(128deg)'), (2.45, 'transform:rotate(128deg)'),
                             (2.82, 'transform:rotate(209deg)', EIO), (T, 'transform:rotate(206deg)')]))
    A('.fig.terA .crT2', K([(0, 'transform:rotate(-142deg)'), (.4, 'transform:rotate(-154deg)'), (1.3, 'transform:rotate(-154deg)'), (1.6, 'transform:rotate(-142deg)'), (2.45, 'transform:rotate(-142deg)'),
                            (2.82, 'transform:rotate(-174deg)', EIO), (T, 'transform:rotate(-173deg)')]))
    A('.fig.terA .headWrap', K([(0, 'transform:none'), (.4, 'transform:translateY(3px) rotate(3deg)'), (1.3, 'transform:translateY(3px) rotate(3deg)'), (1.6, 'transform:none'),
                                (2.5, 'transform:none'), (2.8, 'transform:rotate(5deg)')]))
    A('.fig.terA .eyes', K([(0, 'transform:scaleY(1)'), (.5, 'transform:scaleY(1)'), (.7, 'transform:scaleY(.1)'), (1.2, 'transform:scaleY(.1)'), (1.45, 'transform:scaleY(1)')]))
    A('.fig.terB .armR', K([(0, 'transform:rotate(10deg)'), (2.45, 'transform:rotate(10deg)'), (2.82, 'transform:rotate(-35deg)', EIO), (T, 'transform:rotate(-33deg)')]))
    A('.fig.terB .foreR', K([(0, 'transform:rotate(70deg)'), (2.45, 'transform:rotate(70deg)'), (2.82, 'transform:rotate(209deg)', EIO), (T, 'transform:rotate(206deg)')]))
    A('.fig.terB .crT2', K([(0, 'transform:rotate(-80deg)'), (2.45, 'transform:rotate(-80deg)'), (2.82, 'transform:rotate(-174deg)', EIO), (T, 'transform:rotate(-173deg)')]))
    A('.fig.terB .headWrap', K([(0, 'transform:rotate(-3deg)'), (1.9, 'transform:rotate(-3deg)'), (2.1, 'transform:translate(-4px,2px) rotate(-7deg)', EIO), (2.5, 'transform:translate(-4px,2px) rotate(-7deg)'), (2.8, 'transform:rotate(4deg)')]))
    A('.fig.terB .pupils', K([(0, 'transform:none'), (1.85, 'transform:none'), (2.0, 'transform:translate(-5px,3px)'), (2.5, 'transform:translate(-5px,3px)'), (2.7, 'transform:translate(4px,0)')]))
    A('.fig.terB .eyes', K([(0, 'transform:scaleY(1)'), (1.0, 'transform:scaleY(1)'), (1.25, 'transform:scaleY(.1)'), (1.55, 'transform:scaleY(1)')]))
    A('.fig.terB .smile', K([(0, 'transform:scale(1)'), (2.0, 'transform:scale(1)'), (2.2, 'transform:scale(1.12,1.28)', EIN)]))
    s.append('<text x="270" y="152" font-size="56" text-anchor="middle" class="serif wsplit w3" fill="#2f2f2f" style="--d0:.45s">Przez 3 dni</text>')
    s.append('<text x="270" y="220" font-size="56" text-anchor="middle" class="serif wsplit w3" fill="#2f2f2f" data-hl="0" style="--d0:1.05s">nic nie musisz.</text>')
    S('.scene.active .w3.w{transform-box:fill-box;transform-origin:50%% 100%%;animation:fogIn .7s cubic-bezier(.25,.8,.3,1) both;animation-delay:calc(var(--d0) + var(--w)*.15s)}'
      '@keyframes fogIn{from{opacity:0;transform:translateY(16px) scale(.96)}to{opacity:1;transform:none}}.w3.hl{fill:#8A5F10}')
    s.append('<ellipse class="tmist" cx="270" cy="190" rx="300" ry="70" fill="#fff" filter="url(#fB16)"/>')
    A('.tmist', K([(0, 'opacity:.75;transform:translateX(-20px)'), (.8, 'opacity:.7;transform:translateX(0)'), (1.9, 'opacity:0;transform:translateX(40px)')]))
    s.append('<rect class="flashT" width="540" height="960" fill="#FFF3D6"/>')
    A('.flashT', K([(0, 'opacity:.9'), (.35, 'opacity:0', 'ease-out')]))
    return ''.join(s)

SVG['taras'] = sc_taras()

# =====================================================================
# 5b  KAMIENIE (24,50–26,60) – tilt w dół za liściem, liść dotyka kamieni → złote iskry → koło na krem
# =====================================================================
STONES = [((0, 32.9), 49.7, 25.9, DKG), ((0, -11.6), 24, 18.5, SAGE), ((0, -47), 11.8, 11.8, BEIGE)]

def stone(cx, cy, rx, ry, col, rot=0):
    return ('<g transform="translate(%s,%s) rotate(%s)"><ellipse cx="3" cy="%s" rx="%s" ry="%s" fill="#000" opacity=".18" filter="url(#fB4)"/>'
            '<path d="M%s,0 C%s,%s %s,%s 0,%s C%s,%s %s,%s %s,0 C%s,%s %s,%s 0,%s C%s,%s %s,%s %s,0Z" fill="%s"/>'
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#fff" opacity=".22"/></g>') % (
        f(cx), f(cy), rot, f(ry * .7), f(rx * 1.02), f(ry * .6),
        f(-rx), f(-rx), f(-ry * .7), f(-rx * .5), f(-ry * 1.02), f(-ry * 1.02), f(rx * .6), f(-ry * 1.02), f(rx), f(-ry * .6), f(rx),
        f(rx), f(ry * .8), f(rx * .5), f(ry), f(ry * .95), f(-rx * .55), f(ry), f(-rx), f(ry * .7), f(-rx), col,
        f(-rx * .3), f(-ry * .4), f(rx * .35), f(ry * .25))

def sc_kamienie():
    T = 1.9; s = []
    s.append('<g class="cam c10">')
    s.append('<rect x="-100" y="-100" width="740" height="560" fill="url(#gSkyGold)"/>')
    s.append(rnd_ridge(-100, 700, 250, 22, 9, 91, 460, SAGE) + rnd_ridge(-100, 700, 310, 14, 9, 92, 460, DKG))
    s.append('<rect x="-100" y="340" width="740" height="30" rx="4" fill="%s"/>' % BROWN + ''.join('<rect x="%d" y="370" width="18" height="120" fill="#7D5F4C"/>' % x for x in range(-20, 600, 64)))
    s.append('<rect x="-100" y="480" width="740" height="1200" fill="#B5A596"/>')
    s.append(''.join('<rect x="-100" y="%d" width="740" height="56" fill="%s"/><path d="M-100,%d H640" stroke="#8C7A66" stroke-width="3"/>' % (y, '#BCAC9A' if (y // 58) % 2 else '#B0A08C', y) for y in range(490, 1600, 58)))
    s.append('<g opacity=".28">%s</g>' % ''.join('<path d="M%d,480 l160,0 l-420,1200 l-160,0Z" fill="#FFF2CF"/>' % x for x in (260, 520, 760)))
    SX, SY = 290, 1150
    s.append('<circle class="sGlow" cx="%d" cy="%d" r="150" fill="url(#gGlow)"/>' % (SX, SY))
    A('.sGlow', K([(0, 'opacity:0'), (1.25, 'opacity:0'), (1.55, 'opacity:1')]))
    s.append(stone(SX - 100, SY + 18, 72, 44, DKG, -6) + stone(SX + 40, SY + 30, 54, 36, SAGE, 8) + stone(SX + 138, SY - 6, 30, 28, BEIGE, 0))
    s.append('<g class="lfK"><g class="lfKr">%s</g></g>' % gold_leaf('b', 1.3))
    A('.lfK', K([(0, 'transform:translate(310px,334px)'), (.12, 'transform:translate(310px,334px)'), (.4, 'transform:translate(360px,470px)'), (.65, 'transform:translate(250px,640px)'),
                 (.9, 'transform:translate(340px,820px)'), (1.1, 'transform:translate(262px,990px)'), (1.28, 'transform:translate(300px,1116px)', 'ease-out')], ease='ease-in-out'))
    A('.lfKr', K([(0, 'transform:rotate(78deg) scale(1,.8)'), (.12, 'transform:rotate(78deg) scale(1,.8)'), (.4, 'transform:rotate(-30deg)'), (.65, 'transform:rotate(35deg)'),
                  (.9, 'transform:rotate(-30deg)'), (1.1, 'transform:rotate(25deg)'), (1.28, 'transform:rotate(-8deg)')], ease='ease-in-out'))
    sp = ''
    for q in range(8):
        a = q / 8 * 2 * math.pi + .3; c = uid('ks')
        A('.' + c, K([(0, 'transform:translate(0,0) scale(0);opacity:0'), (1.26, 'transform:translate(0,0) scale(0);opacity:0'),
                      (1.36, 'transform:translate(%spx,%spx) scale(1);opacity:1' % (f(math.cos(a) * 30), f(math.sin(a) * 22))),
                      (1.8, 'transform:translate(%spx,%spx) scale(.2);opacity:0' % (f(math.cos(a) * 90), f(math.sin(a) * 64 - 20)), 'ease-out')]))
        sp += '<g class="%s"><use href="#star" fill="#F6D77A" transform="scale(.8)"/></g>' % c
    s.append('<g transform="translate(%d,%d)">%s</g>' % (SX, SY - 10, sp))
    s.append('</g>')
    A('.c10', K([(0, 'transform:translateY(0)'), (.15, 'transform:translateY(0)'), (1.15, 'transform:translateY(-690px)', EIO), (T, 'transform:translateY(-700px)')]))
    s.append('<circle class="wipeK" cx="%d" cy="%d" r="1200" fill="%s"/>' % (SX, SY - 690, CREAM))
    A('.wipeK', K([(0, 'transform:scale(0)'), (1.42, 'transform:scale(0)'), (1.86, 'transform:scale(1)', 'cubic-bezier(.7,0,.25,1)')]))
    S('.wipeK{transform-origin:%dpx %dpx}' % (SX, SY - 690))
    return ''.join(s)

SVG['kamienie'] = sc_kamienie()

# =====================================================================
# 6  LOGO + CTA (26,60–30,00)
# =====================================================================
def sc_logo():
    T = 3.6; s = []
    LXc, LYc, LS = 270, 296, 1.7
    s.append('<rect width="540" height="960" fill="%s"/><g class="cam c11">' % CREAM)
    s.append('<g opacity=".22">%s%s</g>' % (rnd_ridge(-20, 560, 800, 26, 8, 95, 960, SAGE), rnd_ridge(-20, 560, 850, 18, 8, 96, 960, '#7F978E')))
    # trzy kamienie wskakują od dołu i układają wieżę
    st = ''
    for i, ((cx, cy), rx, ry, col) in enumerate(STONES):
        t0 = .0 + .17 * i; c = uid('ls')
        A('.' + c, K([(0, 'transform:translateY(460px)'), (t0, 'transform:translateY(460px)'), (t0 + .26, 'transform:translateY(-6px)', 'cubic-bezier(.2,.7,.3,1)'),
                      (t0 + .36, 'transform:translateY(2px)', 'ease-in-out'), (t0 + .44, 'transform:translateY(0)')]))
        st += '<g class="%s"><ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/><ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#fff" opacity=".22"/></g>' % (
            c, f(cx), f(cy), f(rx), f(ry), col, f(cx - rx * .3), f(cy - ry * .4), f(rx * .35), f(ry * .25))
    s.append('<g transform="translate(%d,%d) scale(%s)"><g class="tower"><g class="fillSt">%s</g>' % (LXc, LYc, LS, st))
    mk = ''.join('<ellipse class="%s" cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="#fff" stroke-width="9" pathLength="1" stroke-dasharray="1"/>' % (
        'dr%d' % i, f(cx), f(cy), f(rx), f(ry)) for i, ((cx, cy), rx, ry, col) in enumerate(STONES))
    for i in range(3):
        A('.dr%d' % i, K([(0, 'stroke-dashoffset:1'), (.55 + .08 * i, 'stroke-dashoffset:1'), (1.0 + .08 * i, 'stroke-dashoffset:0', EIO)]))
    s.append('<mask id="mLogo" maskUnits="userSpaceOnUse" x="-80" y="-80" width="160" height="160">%s<rect class="mkAll" x="-80" y="-80" width="160" height="160" fill="#fff"/></mask>' % mk)
    A('.mkAll', K([(0, 'opacity:0'), (1.15, 'opacity:0'), (1.35, 'opacity:1')]))
    s.append('<g mask="url(#mLogo)"><use href="#logoSign" style="color:%s"/></g></g></g>' % DKG)
    A('.fillSt', K([(0, 'opacity:1'), (.65, 'opacity:1'), (1.1, 'opacity:0', EOUT)]))
    A('.tower', K([(0, 'transform:rotate(0)'), (.62, 'transform:rotate(0)'), (.76, 'transform:rotate(2.2deg)'), (.92, 'transform:rotate(-1.6deg)'), (1.06, 'transform:rotate(.8deg)'), (1.2, 'transform:rotate(0)')]))
    S('.tower{transform-origin:0 58px}')
    sp = ''
    for q in range(6):
        a = q / 6 * 2 * math.pi - .5; c = uid('lsp')
        A('.' + c, K([(0, 'transform:translate(0,0) scale(0);opacity:0'), (.95, 'transform:translate(0,0) scale(0);opacity:0'),
                      (1.1, 'transform:translate(%spx,%spx) scale(1);opacity:1' % (f(math.cos(a) * 110), f(math.sin(a) * 110))),
                      (1.65, 'transform:translate(%spx,%spx) scale(.2);opacity:0' % (f(math.cos(a) * 150), f(math.sin(a) * 150)), 'ease-out')]))
        sp += '<g class="%s"><use href="#star" fill="%s" transform="scale(.9)"/></g>' % (c, MUST)
    s.append('<g transform="translate(%d,%d)">%s</g></g>' % (LXc, LYc, sp))
    S('.c11{transform-origin:270px 420px}')
    A('.c11', K([(0, 'transform:scale(1.06) translateY(10px)'), (1.6, 'transform:scale(1.01) translateY(0)', ESOFT), (T, 'transform:scale(1)')]))
    s.append('<text x="270" y="530" font-size="60" text-anchor="middle" class="serif split" fill="%s" style="--d0:.72s">SheBalance</text>' % DKG)
    s.append('<text x="270" y="580" font-size="24" text-anchor="middle" class="wsplit w4 capT2" fill="%s" data-g="0,7,17" style="--d0:1.1s">5–7.11 · Beskidy · 20 miejsc</text>' % DKG)
    S('.capT2{font-family:"Mulish",sans-serif;font-weight:700;letter-spacing:.06em}'
      '.scene.active .w4.w{transform-box:fill-box;animation:wRise2 .4s %s both;animation-delay:calc(var(--d0) + var(--w)*.15s)}'
      '@keyframes wRise2{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}' % EIN)
    s.append('<g transform="translate(270,648)"><g class="cta"><g class="ctaP"><rect x="-232" y="-32" width="464" height="64" rx="32" fill="%s"/>'
             '<text x="0" y="10" font-size="28" text-anchor="middle" class="capT2" fill="%s" style="letter-spacing:.02em">Zapisz się → shebalance.pl</text></g></g></g>' % (DKG, CREAM))
    A('.cta', K([(0, 'transform:scale(0);opacity:0'), (1.3, 'transform:scale(0);opacity:0'), (1.52, 'transform:scale(1.04);opacity:1', 'cubic-bezier(.3,1.4,.5,1)'), (1.6, 'transform:scale(1)')]))
    A('.ctaP', 'ctaPulse .9s ease-in-out 1.8s infinite')
    S('@keyframes ctaPulse{0%,100%{transform:scale(1)}40%{transform:scale(1.05)}}')
    s.append('<text class="hnd" x="270" y="724" font-size="20" text-anchor="middle" fill="%s" style="font-family:Mulish,sans-serif;font-weight:600;letter-spacing:.04em">@shebalance_camp</text>' % BROWN)
    A('.hnd', K([(0, 'opacity:0;transform:translateY(8px)'), (1.65, 'opacity:0;transform:translateY(8px)'), (1.9, 'opacity:1;transform:none', EIN)]))
    s.append('<g class="lfL"><g class="lfLr">%s</g></g>' % gold_leaf('m', 1.2))
    # ostatni liść przelatuje i ląduje tam, gdzie w klatce 0 była karteczka (pętla)
    A('.lfL', K([(0, 'transform:translate(-40px,130px)'), (2.25, 'transform:translate(-40px,130px)'), (2.6, 'transform:translate(120px,170px)'), (2.9, 'transform:translate(420px,210px)'),
                 (3.2, 'transform:translate(440px,420px)'), (3.5, 'transform:translate(270px,446px)', 'ease-out')], ease='ease-in-out'))
    A('.lfLr', K([(0, 'transform:rotate(-30deg)'), (2.25, 'transform:rotate(-30deg)'), (2.6, 'transform:rotate(40deg) scale(.8,1)'), (2.9, 'transform:rotate(-20deg)'),
                  (3.2, 'transform:rotate(50deg) scale(.7,1)'), (3.5, 'transform:rotate(80deg) scale(1,.8)')], ease='ease-in-out'))
    return ''.join(s)

SVG['logo'] = sc_logo()
