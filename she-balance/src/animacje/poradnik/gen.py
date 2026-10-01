# -*- coding: utf-8 -*-
# Generator animacji „Poradnik: Jak odpocząć w 5 prostych krokach (wersja dla kobiet)” (SheBalance, reel 9:16, 25 s)
# → src/animacje/poradnik.html.  Uruchom: python3 src/animacje/poradnik/gen.py && python3 src/zbuduj_animacje.py poradnik
# Sceny (start): 0 studio · 2 krok1 · 5 krok2 · 8 krok3 · 11 krok4 · 14 krok5 · 17 serio · 19 prawdziwy · 22 logo (koniec 25)
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pomoc import *          # K, A, S, uid, f, rig, head, pupils, FIG, L2W, ghost, cam, bubble, place_bubble, side_arm, ridge, tree…
from pomoc import CSS

def tree(x, base, h, col, trunk=BROWN):
    return ('<rect x="%s" y="%s" width="4" height="%s" fill="%s"/>' % (f(x - 2), f(base - h * .45), f(h * .45), trunk) +
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (f(x), f(base - h * .62), f(h * .3), f(h * .38), col))

SKB = '#f3cdb3'      # dłoń B
PANTS = '#2a2a2e'
EBOUNCE = 'cubic-bezier(.2,.9,.3,1.04)'   # overshoot ≤ 5 %

# ================= wspólne elementy „telezakupów” =================
def star_path(ro, ri, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        r = ro if i % 2 == 0 else ri
        a = math.radians(rot + i * 180 / n)
        pts.append('%s,%s' % (f(r * math.cos(a)), f(r * math.sin(a))))
    return 'M' + ' L'.join(pts) + ' Z'

def sunburst(n, rr, col):
    s = ''
    for i in range(n):
        a0 = math.radians(i * 360 / n); a1 = math.radians((i + .5) * 360 / n)
        s += 'M0,0 L%s,%s L%s,%s Z ' % (f(rr * math.cos(a0)), f(rr * math.sin(a0)), f(rr * math.cos(a1)), f(rr * math.sin(a1)))
    return '<path d="%s" fill="%s"/>' % (s, col)

def sparkle(x, y, sc, col, delay, dur=1.4):
    return ('<g transform="translate(%s,%s) scale(%s)"><g class="twinkle" style="animation-delay:-%ss;animation-duration:%ss"><use href="#star" fill="%s"/></g></g>'
            % (f(x), f(y), f(sc), f(delay), f(dur), col))

def card(x, y, w, h, fill=CREAM2, edge=BEIGE, rot=0):
    cx, cy = x + w / 2, y + h / 2
    return ('<g transform="rotate(%s %s %s)">' % (f(rot), f(cx), f(cy)) +
            '<rect x="%s" y="%s" width="%s" height="%s" rx="26" fill="#3a2a20" opacity=".16" transform="translate(4,7)"/>' % (f(x), f(y), f(w), f(h)) +
            '<rect x="%s" y="%s" width="%s" height="%s" rx="26" fill="%s"/>' % (f(x), f(y), f(w), f(h), fill) +
            '<rect x="%s" y="%s" width="%s" height="%s" rx="19" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="2 7" stroke-linecap="round"/>' % (f(x + 8), f(y + 8), f(w - 16), f(h - 16), edge) +
            '</g>')

def card_in(cls, T, t0=0.0, kind='drop'):
    """wejście planszy (nie tytułu)"""
    if kind == 'drop':
        fr = [(0, 'opacity:0;transform:translateY(-40px) scale(.96)'), (t0, 'opacity:0;transform:translateY(-40px) scale(.96)', ESNAP), (t0 + .3, 'opacity:1;transform:translateY(0) scale(1)')]
    else:
        fr = [(0, 'opacity:0;transform:translateY(40px) scale(.96)'), (t0, 'opacity:0;transform:translateY(40px) scale(.96)', ESNAP), (t0 + .3, 'opacity:1;transform:translateY(0) scale(1)')]
    A('.' + cls, K(fr, T))

def badge(n, x, y, T, t0):
    c = uid('bdg')
    S('.%s{transform-origin:%spx %spx}' % (c, f(x), f(y)))
    A('.' + c, K([(0, 'opacity:0;transform:translateY(-26px) rotate(-6deg)'), (t0, 'opacity:0;transform:translateY(-26px) rotate(-6deg)', EBOUNCE),
                  (t0 + .3, 'opacity:1;transform:translateY(0) rotate(0deg)'), (t0 + .8, 'opacity:1;transform:translateY(0) rotate(0deg)', EIO),
                  (t0 + 1.0, 'opacity:1;transform:translateY(0) rotate(-2deg)'), (t0 + 1.2, 'opacity:1;transform:translateY(0) rotate(0deg)')], T))
    return ('<g class="%s"><rect x="%s" y="%s" width="196" height="44" rx="22" fill="%s"/>' % (c, f(x - 98), f(y - 22), DKG) +
            '<rect x="%s" y="%s" width="186" height="34" rx="17" fill="none" stroke="%s" stroke-opacity=".45" stroke-width="1.4"/>' % (f(x - 93), f(y - 17), CREAM2) +
            '<use href="#star" transform="translate(%s,%s) scale(.75)" fill="%s"/><use href="#star" transform="translate(%s,%s) scale(.75)" fill="%s"/>' % (f(x - 74), f(y), '#F6DDA8', f(x + 74), f(y), '#F6DDA8') +
            '<text x="%s" y="%s" font-size="21" text-anchor="middle" fill="%s" style="font-weight:800;letter-spacing:.14em">KROK %d/5</text></g>' % (f(x + 1), f(y + 7.5), CREAM2, n))

def check(x, y, T, t0, r=34):
    """Duży ✔ wskakujący (pieczątka) + pierścień + 4 gwiazdki."""
    c, cd, cr = uid('ck'), uid('cd'), uid('cr')
    s = '<g transform="translate(%s,%s)">' % (f(x), f(y))
    s += '<g class="%s"><circle r="%s" fill="none" stroke="%s" stroke-width="4"/></g>' % (cr, f(r), DKG)
    s += ('<g class="%s"><circle r="%s" fill="#3a2a20" opacity=".16" transform="translate(2,4)"/><circle r="%s" fill="%s"/>' % (c, f(r), f(r), DKG) +
          '<circle r="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="2 5" stroke-linecap="round" opacity=".7"/>' % (f(r - 6), CREAM2) +
          '<path class="%s" d="M%s,%s L%s,%s L%s,%s" pathLength="1" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"/></g>'
          % (cd, f(-r * .42), f(r * .02), f(-r * .12), f(r * .32), f(r * .45), f(-r * .36), CREAM2, f(r * .22)))
    for k in range(4):
        a = math.radians(-60 + k * 90 + 20)
        cs = uid('cs')
        s += '<g class="%s"><use href="#star" fill="%s" transform="scale(.9)"/></g>' % (cs, '#F6DDA8' if k % 2 else CREAM2)
        dx, dy = math.cos(a) * r * 2.0, math.sin(a) * r * 2.0
        A('.' + cs, K([(0, 'opacity:0;transform:translate(0,0) scale(.3)'), (t0 + .12, 'opacity:0;transform:translate(0,0) scale(.3)', ESNAP),
                       (t0 + .2, 'opacity:1;transform:translate(%spx,%spx) scale(1)' % (f(dx * .5), f(dy * .5)), ESOFT),
                       (t0 + .7, 'opacity:0;transform:translate(%spx,%spx) scale(.5)' % (f(dx), f(dy)))], T))
    s += '</g>'
    A('.' + c, K([(0, 'opacity:0;transform:scale(0) rotate(-40deg)'), (t0, 'opacity:0;transform:scale(0) rotate(-40deg)', 'cubic-bezier(.2,.8,.3,1)'),
                  (t0 + .2, 'opacity:1;transform:scale(1.05) rotate(4deg)', ESOFT), (t0 + .34, 'opacity:1;transform:scale(1) rotate(0deg)')], T))
    S('.%s{stroke-dasharray:1}' % cd)
    A('.' + cd, K([(0, 'stroke-dashoffset:1'), (t0 + .12, 'stroke-dashoffset:1', EIO), (t0 + .36, 'stroke-dashoffset:0')], T))
    A('.' + cr, K([(0, 'opacity:0;transform:scale(.8)'), (t0 + .1, 'opacity:0;transform:scale(.8)', 'linear'), (t0 + .14, 'opacity:.8;transform:scale(1)', ESOFT), (t0 + .65, 'opacity:0;transform:scale(2.1)')], T))
    return s

def stext(txt, x, y, fs, col=INK, shadow=SAGE, cls='', extra='', anchor='middle', dxy=(2.5, 3)):
    """tytuł Forum z retro cieniem (kicz premium)"""
    return ('<text x="%s" y="%s" font-size="%s" text-anchor="%s" class="serif %s" fill="%s" %s>%s</text>' % (f(x + dxy[0]), f(y + dxy[1]), fs, anchor, cls, shadow, extra, txt) +
            '<text x="%s" y="%s" font-size="%s" text-anchor="%s" class="serif %s" fill="%s" %s>%s</text>' % (f(x), f(y), fs, anchor, cls, col, extra, txt))

def mtext(txt, x, y, fs, col=INK, weight=700, cls='', anchor='middle', extra=''):
    return '<text x="%s" y="%s" font-size="%s" text-anchor="%s" class="%s" fill="%s" style="font-weight:%s" %s>%s</text>' % (f(x), f(y), fs, anchor, cls, col, weight, extra, txt)

def mic(fingers=True, skin=SKB):
    """Mikrofon w dłoni; (0,0) = środek dłoni, rączka w górę."""
    s = ('<g transform="rotate(-10)"><rect x="-6" y="-48" width="12" height="54" rx="5" fill="#2f3b37"/>'
         '<rect x="-9" y="-46" width="18" height="16" rx="3" fill="%s"/>' % SAGE +
         '<text x="0" y="-34.5" font-size="8.5" text-anchor="middle" fill="%s" style="font-weight:900;letter-spacing:.04em">TV</text>' % CREAM2 +
         '<circle cx="0" cy="-60" r="14" fill="#cfc8bd"/><circle cx="0" cy="-60" r="14" fill="none" stroke="#9c958b" stroke-width="1.6"/>'
         '<path d="M-12,-64 H12 M-13,-58 H13 M-10,-52 H10 M-6,-71 V-48 M0,-74 V-46 M6,-71 V-48" stroke="#a9a196" stroke-width="1.1"/>'
         '<circle cx="-5" cy="-66" r="3.4" fill="#fff" opacity=".7"/></g>')
    if fingers:
        s += ('<ellipse cx="0" cy="-2" rx="11" ry="12" fill="%s"/><path d="M-10,-8 Q0,-14 10,-8 M-10,-2 Q0,-8 10,-2" stroke="#d8a88c" stroke-width="1.3" fill="none"/>'
              '<ellipse cx="-9" cy="-12" rx="4.6" ry="7" fill="%s" transform="rotate(-30 -9 -12)"/>' % (skin, skin))
    return s

def mask_reveal(cls, T, t0, dur, x0, y0, w, h, direction='up'):
    """maska: tekst wjeżdża z dołu w prostokącie"""
    cid = uid('cp')
    A('.' + cls, K([(0, 'transform:translateY(%spx)' % f(h)), (t0, 'transform:translateY(%spx)' % f(h), 'cubic-bezier(.2,.9,.3,1)'), (t0 + dur, 'transform:translateY(0)')], T))
    return cid, '<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (cid, f(x0), f(y0), f(w), f(h))

def swipe(T, phase, cols=(SAGE, CREAM2, DKG, CREAM2, SAGE), t0=None, t1=None):
    """Ukośne pastelowe pasy – przejście krok→krok (koniec sceny: phase='in', początek następnej: 'out')."""
    c = uid('sw')
    widths = [70, 46, 1500, 46, 70]
    x = 1500 + 46 + 70
    rects = ''
    xs = []
    cur = 1500 + 46 + 70
    # od prawej (przód) do lewej
    pos = [(1546, 70, cols[0]), (1500, 46, cols[1]), (0, 1500, cols[2]), (-46, 46, cols[3]), (-116, 70, cols[4])]
    for px, w, col in pos:
        rects += '<rect x="%s" y="-700" width="%s" height="2400" fill="%s"/>' % (f(px), f(w), col)
    cover = 270 - 750
    if phase == 'in':
        fr = [(0, 'transform:translateX(-2300px)'), (t0, 'transform:translateX(-2300px)', 'cubic-bezier(.55,0,.75,.6)'), (T, 'transform:translateX(%spx)' % f(cover))]
    else:
        fr = [(0, 'transform:translateX(%spx)' % f(cover), 'cubic-bezier(.25,.4,.45,1)'), (t1, 'transform:translateX(1100px)')]
    A('.' + c, K(fr, T))
    return '<g transform="rotate(-16 270 480)"><g class="%s">%s</g></g>' % (c, rects)

def vignette2(op=.4):
    return '<rect width="540" height="960" fill="url(#vignette)" opacity="%s" pointer-events="none"/>' % f(op)

# ================= SCENA 1: Studio (0–2 s) =================
def sc_studio():
    T = 2.0; s = []
    inst = 'pB1'
    cx, feet, sc = 302, 992, .98
    s.append('<g class="c1">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="%s"/>' % BEIGE)
    s.append('<g transform="translate(270,640)"><g class="ray1">%s</g></g>' % sunburst(28, 1200, '#EBD9CF'))
    A('.ray1', K([(0, 'transform:rotate(0deg)'), (T, 'transform:rotate(14deg)')], T, 'cubic-bezier(.3,0,.6,1)'))
    # łuk sceny z żarówkami
    s.append('<path d="M44,1000 V560 A226,226 0 0 1 496,560 V1000 Z" fill="%s"/>' % CREAM2)
    s.append('<path d="M62,1000 V560 A208,208 0 0 1 478,560 V1000" fill="none" stroke="%s" stroke-width="3" stroke-dasharray="1 9" stroke-linecap="round"/>' % SAGE)
    bulbs = ''
    for i in range(17):
        a = math.radians(180 + i * 180 / 16)
        bx, by = 270 + 238 * math.cos(a), 560 + 238 * math.sin(a)
        bulbs += '<circle cx="%s" cy="%s" r="6" fill="#F6E7C4" stroke="%s" stroke-width="1.5" class="%s"/>' % (f(bx), f(by), '#d9bfae', 'bl1a' if i % 2 else 'bl1b')
    for yy in range(600, 960, 44):
        for xx in (32, 508):
            bulbs += '<circle cx="%s" cy="%s" r="6" fill="#F6E7C4" stroke="#d9bfae" stroke-width="1.5" class="%s"/>' % (xx, yy, 'bl1a' if (yy // 44) % 2 else 'bl1b')
    s.append(bulbs)
    S('.active .bl1a{animation:blk .5s steps(1) infinite}.active .bl1b{animation:blk .5s steps(1) infinite;animation-delay:-.25s}'
      '@keyframes blk{0%{fill:#F6E7C4}50%{fill:#FFFBF1}}')
    # snopy światła
    s.append('<g transform="translate(40,-20)"><g class="sp1"><path d="M0,0 L120,980 L330,980 Z" fill="#FFF8EA" opacity=".38"/></g></g>')
    s.append('<g transform="translate(500,-20)"><g class="sp2"><path d="M0,0 L-330,980 L-120,980 Z" fill="#FFF8EA" opacity=".3"/></g></g>')
    A('.sp1', K([(0, 'transform:rotate(-6deg)'), (T, 'transform:rotate(5deg)')], T))
    A('.sp2', K([(0, 'transform:rotate(5deg)'), (T, 'transform:rotate(-4deg)')], T))
    # podłoga studia
    s.append('<rect x="-100" y="900" width="740" height="200" fill="%s"/><rect x="-100" y="900" width="740" height="6" fill="#93A99F"/>' % SAGE)
    # B – prowadząca z mikrofonem
    s.append(FIG('B', inst, cx, feet, sc, post=ghost('B', inst, '', mic(), arm='R')))
    s.append('</g>')
    rig(inst, 'B', T, [(0, {'R': (150, 300), 'L': (60, 452)}), (.12, {'L': (60, 452)}), (.42, {'L': (-62, 168)}, EBOUNCE), (.62, {'L': (-56, 176)}),
                       (.8, {'L': (-64, 160)}), (1.0, {'L': (-58, 172)}), (1.3, {'L': (-40, 200), 'R': (150, 300)}), (1.55, {'L': (-62, 160), 'R': (154, 292)}, ESNAP), (T, {'L': (-60, 166)})])
    head(inst, T, [(0, -3, -1, 0), (.42, -7, -3, 0, ESNAP), (.9, -6, -2, 0), (1.05, 4, 2, 0, ESNAP), (1.5, 3, 2, 0), (1.62, -5, -2, -2, ESNAP), (T, -5, -2, -2)])
    pupils(inst, T, [(0, 0), (.4, -3), (.95, -3), (1.05, 0), (T, 0)])
    A('.fig.%s .smile' % inst, K([(0, 'transform:scale(1.14,1.32)'), (T, 'transform:scale(1.14,1.32)')], T))
    A('.fig.%s .body' % inst, K([(0, 'transform:translateY(0)'), (.42, 'transform:translateY(-6px)', ESOFT), (.6, 'transform:translateY(0)'), (1.55, 'transform:translateY(-5px)', ESOFT), (1.72, 'transform:translateY(0)')], T))
    cam('cm1', T, [(0, 270, 520, 1.0, 270, 520, 0), (.34, 270, 520, 1.012, 270, 520, 0, ESNAP), (.44, 270, 520, 1.045, 270, 520, -.6), (1.04, 270, 520, 1.06, 270, 520, -.6, ESNAP), (1.14, 270, 520, 1.085, 270, 520, .5), (T, 270, 520, 1.1, 270, 516, .5)])
    out = ['<g class="cm1">'] + s + ['</g>']
    # flesze
    for i, (t0, x, y) in enumerate([(.34, 46, 470), (1.05, 496, 560), (1.6, 60, 700)]):
        c = uid('fl')
        out.append('<g transform="translate(%s,%s)"><g class="%s"><path d="%s" fill="#FFFDF6"/><circle r="10" fill="#fff"/></g></g>' % (f(x), f(y), c, star_path(46, 7, 4, 0)))
        A('.' + c, K([(0, 'opacity:0;transform:scale(.2) rotate(0deg)'), (t0, 'opacity:0;transform:scale(.2) rotate(0deg)', 'cubic-bezier(.2,.8,.3,1)'), (t0 + .06, 'opacity:1;transform:scale(1) rotate(10deg)', ESOFT), (t0 + .32, 'opacity:0;transform:scale(1.2) rotate(25deg)')], T))
        cw = uid('fw')
        out.append('<rect width="540" height="960" fill="#FFFDF6" class="%s" pointer-events="none"/>' % cw)
        A('.' + cw, K([(0, 'opacity:0'), (t0, 'opacity:0', 'linear'), (t0 + .04, 'opacity:.42', 'cubic-bezier(.2,.7,.3,1)'), (t0 + .3, 'opacity:0')], T))
    out.append(vignette2(.3))
    # tytuł (widoczny od klatki 0)
    out.append('<g transform="translate(270,214)"><g class="t1">%s</g></g>' % stext('5 kroków', 0, 0, 96, shadow='#F4F2EF', dxy=(3, 4)))
    A('.t1', K([(0, 'opacity:1;transform:scale(.86)'), (.24, 'opacity:1;transform:scale(1.03)', ESOFT), (.38, 'opacity:1;transform:scale(1)'), (1.05, 'opacity:1;transform:scale(1)', ESNAP), (1.14, 'opacity:1;transform:scale(1.03)', ESOFT), (1.3, 'opacity:1;transform:scale(1)')], T))
    out.append('<text x="252" y="272" font-size="32" text-anchor="middle" class="wsplit w1s" fill="%s" style="font-weight:700">do pełnego relaksu</text>' % INK)
    S('.scene.active .w1s.w{transform-box:fill-box;transform-origin:50% 100%;animation:w1s .4s cubic-bezier(.2,.9,.3,1.04) both;animation-delay:calc(.16s + var(--w) * .12s)}'
      '@keyframes w1s{from{opacity:0;transform:translateY(18px) scale(.7)}to{opacity:1;transform:none}}')
    # ✨ (rysowane gwiazdki)
    c = uid('sp')
    out.append('<g transform="translate(424,256)"><g class="%s"><use href="#star" transform="scale(1.5)" fill="%s"/><use href="#star" transform="translate(16,-14) scale(.8)" fill="%s"/><use href="#star" transform="translate(14,12) scale(.6)" fill="%s"/></g></g>' % (c, MUST, MUST, MUST))
    A('.' + c, K([(0, 'opacity:0;transform:scale(0) rotate(-40deg)'), (.5, 'opacity:0;transform:scale(0) rotate(-40deg)', EBOUNCE), (.75, 'opacity:1;transform:scale(1) rotate(0deg)'), (1.4, 'opacity:1;transform:scale(1) rotate(0deg)', EIO), (1.6, 'opacity:1;transform:scale(1.05) rotate(12deg)'), (1.8, 'opacity:1;transform:scale(1) rotate(0deg)')], T))
    for x, y, sc2, d in [(70, 360, 1.3, .2), (470, 380, 1.1, .7), (96, 610, .9, 1.0), (448, 700, 1.2, .4), (40, 140, .9, .9), (500, 150, 1.0, .3)]:
        out.append(sparkle(x, y, sc2, '#FFFBF1', d))
    out.append(swipe(T, 'in', t0=1.66))
    return ''.join(out), T

# ================= SCENA 2: KROK 1/5 – 5:00 (2–5 s) =================
def alarm_clock():
    return ('<g><circle cx="-30" cy="-50" r="16" fill="%s"/><circle cx="30" cy="-50" r="16" fill="%s"/>' % (BEIGE, BEIGE) +
            '<path d="M-8,-62 H8" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % BROWN +
            '<path d="M-40,40 l-12,14 M40,40 l12,14" stroke="%s" stroke-width="6" stroke-linecap="round"/>' % BROWN +
            '<rect x="-64" y="-44" width="128" height="92" rx="30" fill="%s" stroke="#d9cfc2" stroke-width="2"/>' % CREAM2 +
            '<rect x="-48" y="-26" width="96" height="54" rx="10" fill="#2f3b37"/>'
            '<text x="0" y="14" font-size="34" text-anchor="middle" fill="#F6DDA8" style="font-weight:800;letter-spacing:.02em" class="clkT">5:00</text></g>')

def sc_krok1():
    T = 3.0; s = []
    inst = 'pA2'
    cx, feet, sc = 190, 944, .9
    s.append('<g class="c2">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="%s"/>' % DKG)
    # okno nocą
    wx, wy, ww, wh = 296, 330, 200, 236
    s.append('<rect x="%s" y="%s" width="%s" height="%s" rx="8" fill="#3D544C"/>' % (wx, wy, ww, wh))
    s.append('<circle cx="%s" cy="%s" r="26" fill="#F2EFEB"/><circle cx="%s" cy="%s" r="24" fill="#3D544C"/>' % (wx + 150, wy + 60, wx + 162, wy + 52))
    s.append(''.join('<rect x="%s" y="%s" width="%s" height="%s" fill="#34473F"/>' % (f(wx + 6 + i * 40), f(wy + wh - h), 34, h) for i, h in enumerate([70, 110, 60, 90, 76])))
    s.append(''.join('<rect x="%s" y="%s" width="7" height="9" fill="#F6DDA8" opacity=".75"/>' % (f(wx + 20 + i * 40), f(wy + wh - 50)) for i in (1, 3)))
    for x, y, d in [(wx + 40, wy + 50, .2), (wx + 92, wy + 96, .7), (wx + 60, wy + 140, 1.1)]:
        s.append(sparkle(x, y, .55, '#F2EFEB', d, 1.8))
    s.append('<rect x="%s" y="%s" width="%s" height="%s" rx="8" fill="none" stroke="%s" stroke-width="10"/>' % (wx, wy, ww, wh, BEIGE))
    s.append('<path d="M%s,%s V%s M%s,%s H%s" stroke="%s" stroke-width="7"/>' % (wx + ww / 2, wy, wy + wh, wx, wy + wh * .45, wx + ww, BEIGE))
    s.append('<rect x="%s" y="%s" width="%s" height="12" rx="4" fill="#EADCD2"/>' % (wx - 12, wy + wh, ww + 24))
    # lampa wisząca + ciepły stożek
    s.append('<path d="M190,-20 V300" stroke="#2f3b37" stroke-width="3"/><path d="M150,330 Q190,280 230,330 Z" fill="%s"/><ellipse cx="190" cy="331" rx="40" ry="6" fill="#FFF1D6"/>' % BEIGE)
    s.append('<g class="lamp2"><path d="M152,332 L228,332 L360,820 L20,820 Z" fill="#FFE9C8" opacity=".22"/><ellipse cx="190" cy="520" rx="210" ry="260" fill="url(#warm)" opacity=".9"/></g>')
    A('.lamp2', K([(0, 'opacity:.75'), (.4, 'opacity:.75'), (.5, 'opacity:1'), (T, 'opacity:1')], T))
    s.append(FIG('A', inst, cx, feet, sc, post=ghost('A', inst, '', mug_hand('st2'), arm='R')))
    # blat
    cy = 690
    s.append('<rect x="-100" y="%s" width="740" height="16" rx="3" fill="#EADCD2"/><rect x="-100" y="%s" width="740" height="400" fill="#4A655C"/>' % (cy, cy + 16))
    s.append(''.join('<rect x="%s" y="%s" width="128" height="400" rx="4" fill="none" stroke="#3f5a52" stroke-width="2"/><rect x="%s" y="%s" width="46" height="6" rx="3" fill="%s"/>' % (x + 8, cy + 34, x + 49, cy + 52, BEIGE) for x in range(-100, 640, 140)))
    # budzik
    s.append('<g transform="translate(414,628)"><g class="clk2">%s</g></g>' % alarm_clock())
    S('.clk2{transform-origin:0 40px}')
    shake = [(0, 'transform:rotate(0deg) translateY(0)')]
    for i in range(14):
        t = .32 + i * .055
        shake.append((t, 'transform:rotate(%sdeg) translateY(%spx)' % (f(7 * (-1) ** i), f(-3 if i % 2 else 0))))
    shake.append((.32 + 14 * .055, 'transform:rotate(0deg) translateY(0)'))
    A('.clk2', K(shake, T, 'ease-in-out'))
    rings = ''.join('<path d="M%s,%s q%s,-16 0,-32" fill="none" stroke="%s" stroke-width="3.5" stroke-linecap="round"/>' % (f(sx * 80), -40, f(sx * 12), '#F6DDA8') for sx in (-1, 1))
    rings += ''.join('<path d="M%s,%s q%s,-24 0,-48" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" opacity=".7"/>' % (f(sx * 96), -32, f(sx * 16), '#F6DDA8') for sx in (-1, 1))
    s.append('<g transform="translate(414,618)"><g class="rg2">%s</g></g>' % rings)
    A('.rg2', K([(0, 'opacity:0'), (.3, 'opacity:0', 'steps(1,end)'), (.32, 'opacity:1'), (.4, 'opacity:.3'), (.48, 'opacity:1'), (.56, 'opacity:.3'), (.64, 'opacity:1'), (.72, 'opacity:.3'), (.8, 'opacity:1'), (.9, 'opacity:.3'), (1.0, 'opacity:1'), (1.1, 'opacity:0')], T, 'linear'))
    A('.clkT', K([(0, 'opacity:1'), (1.2, 'opacity:1'), (1.3, 'opacity:.25'), (1.45, 'opacity:1'), (1.6, 'opacity:.25'), (1.75, 'opacity:1')], T, 'linear'))
    s.append('</g>')
    # A: zaspana → budzik → przeciąga się → łyk → uśmiech „prezenterski”
    rig(inst, 'A', T, [(0, {'R': R_HOLD, 'L': (62, 452)}), (.7, {'L': (62, 452)}), (1.0, {'L': (-10, 120), 'eL': 'out'}, ESOFT), (1.25, {'L': (0, 112), 'eL': 'out'}), (1.5, {'L': (62, 452)}, EIO),
                       (1.5, {'R': R_HOLD}), (1.78, {'R': R_SIP}, 'cubic-bezier(.4,0,.2,1)'), (2.0, {'R': R_SIP}), (2.25, {'R': R_HOLD}, ESNAP), (T, {'R': (186, 232)})])
    head(inst, T, [(0, 6, 2, 5), (.36, 6, 2, 5), (.46, -2, 0, -3, ESNAP), (.7, 0, 0, 0), (1.0, -8, -3, 0), (1.3, -8, -3, 0), (1.5, 0, 0, 0), (1.8, -3, 0, 0), (2.2, -3, 0, 0), (2.35, 4, 2, 0, ESNAP), (T, 4, 2, 0)])
    pupils(inst, T, [(0, 0), (.4, 0), (.5, 3.2), (.95, 3.2), (1.1, 0), (2.3, 0), (2.4, 0), (T, 0)])
    A('.fig.%s .eyes' % inst, K([(0, 'transform:scaleY(.32)'), (.38, 'transform:scaleY(.32)', ESNAP), (.46, 'transform:scaleY(1.12)'), (.9, 'transform:scaleY(1)'), (1.0, 'transform:scaleY(.15)'), (1.3, 'transform:scaleY(.15)'), (1.42, 'transform:scaleY(1)'), (T, 'transform:scaleY(1)')], T))
    A('.fig.%s .smile' % inst, K([(0, 'transform:scale(1)'), (2.3, 'transform:scale(1)', ESNAP), (2.45, 'transform:scale(1.14,1.32)'), (T, 'transform:scale(1.14,1.32)')], T))
    A('.st2', K([(0, 'opacity:1'), (T, 'opacity:1')], T))
    FX, FY = L2W(cx, feet, sc, 110, 150)
    cam('cm2', T, [(0, 300, 560, 1.0, 300, 560, 0), (.32, 300, 560, 1.0, 300, 560, 0, ESNAP), (.44, 300, 560, 1.03, 300, 560, .8), (.56, 300, 560, 1.03, 300, 560, -.6), (.7, 300, 560, 1.03, 300, 560, 0),
                   (T, 270, 560, 1.08, 300, 560, 0)])
    out = ['<g class="cm2">'] + s + ['</g>', vignette2(.45)]
    # plansza
    cc = uid('cd2')
    out.append('<g class="%s">%s</g>' % (cc, card(30, 114, 480, 192)))
    card_in(cc, T, .05, 'drop')
    cid, clip = mask_reveal('t2a', T, .3, .4, 30, 140, 480, 80)
    out.append(clip + '<g clip-path="url(#%s)"><g class="t2a">%s</g></g>' % (cid, stext('Wstań o 5:00,', 270, 204, 60)))
    out.append('<g class="t2b">%s</g>' % mtext('żeby mieć czas dla siebie.', 270, 254, 27))
    A('.t2b', K([(0, 'opacity:0;transform:translateY(14px)'), (.62, 'opacity:0;transform:translateY(14px)', ESNAP), (.86, 'opacity:1;transform:translateY(0)'), (1.95, 'opacity:1;transform:translateY(0)', EOUT), (2.1, 'opacity:0;transform:translateY(-12px)')], T))
    out.append('<g class="t2c">%s</g>' % mtext('Zanim wszyscy się obudzą.', 270, 254, 23, col=BROWN, extra='font-style="italic"'))
    A('.t2c', K([(0, 'opacity:0;transform:translateY(14px)'), (2.08, 'opacity:0;transform:translateY(14px)', ESNAP), (2.3, 'opacity:1;transform:translateY(0)')], T))
    out.append(badge(1, 270, 114, T, .12))
    out.append(check(472, 296, T, 2.42))
    # gwiazdkowe przejście (2,68–3,0)
    c = uid('stw')
    out.append('<g transform="translate(270,560)"><g class="%s"><path d="%s" fill="%s"/></g></g>' % (c, star_path(400, 230), SAGE))
    A('.' + c, K([(0, 'transform:scale(0) rotate(-30deg)'), (2.66, 'transform:scale(0) rotate(-30deg)', 'cubic-bezier(.55,0,.8,.5)'), (T, 'transform:scale(3.2) rotate(40deg)')], T))
    # wejście: pasy wyjeżdżają
    out.append(swipe(T, 'out', t1=.36))
    return ''.join(out), T

# ================= SCENA 3: KROK 2/5 – medytacja + kanapki (5–8 s) =================
def bread(col='#EBC99A', crust='#C9955E'):
    return ('<path d="M-22,14 L-22,-6 C-30,-10 -30,-24 -16,-26 C-8,-34 8,-34 16,-26 C30,-24 30,-10 22,-6 L22,14 Z" fill="%s" stroke="%s" stroke-width="3"/>' % (col, crust))

def lunchbox(col, lid, open_cls=''):
    return ('<g><rect x="-40" y="-22" width="80" height="44" rx="10" fill="%s"/><rect x="-40" y="-6" width="80" height="4" fill="#000" opacity=".08"/>' % col +
            '<g class="%s"><rect x="-43" y="-30" width="86" height="14" rx="6" fill="%s"/><rect x="-10" y="-35" width="20" height="7" rx="3" fill="%s"/></g>' % (open_cls, lid, lid) +
            '<use href="#heartShape" transform="translate(0,8) scale(.9)" fill="#FBF9F6" opacity=".8"/></g>')

def sc_krok2():
    T = 3.0; s = []
    inst = 'pA3'
    cx, feet, sc = 270, 624, .72
    s.append('<g class="c3">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="%s"/>' % SAGE)
    s.append('<g transform="translate(270,250)"><g class="ray3">%s</g></g>' % sunburst(20, 900, '#AFC1BA'))
    A('.ray3', K([(0, 'transform:rotate(0deg)'), (T, 'transform:rotate(-16deg)')], T, 'cubic-bezier(.3,0,.6,1)'))
    # aura / „lotos”
    s.append('<g transform="translate(270,262)"><g class="aura3"><circle r="150" fill="%s" opacity=".55"/><circle r="122" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="2 8" stroke-linecap="round"/></g></g>' % (CREAM2, CREAM2))
    S('.aura3{transform-origin:0 0}')
    A('.aura3', K([(0, 'transform:scale(.96)'), (1.5, 'transform:scale(1.04)'), (T, 'transform:scale(.98)')], T))
    petals = ''
    for i in range(7):
        a = -90 + (i - 3) * 26
        petals += '<ellipse cx="0" cy="-62" rx="22" ry="62" fill="%s" transform="rotate(%s)"/>' % ('#E3CCC1' if i % 2 else '#EBD9CF', a + 90 if False else a + 90)
    s.append('<g transform="translate(270,538)">%s</g>' % '')
    # mata / poduszka
    s.append('<ellipse cx="270" cy="556" rx="236" ry="34" fill="#93A99F"/>')
    s.append('<ellipse cx="270" cy="532" rx="150" ry="26" fill="%s"/>' % BEIGE)
    # A siedzi (nogi z fig ukryte – skrzyżowane rysujemy sami)
    S('.fig.%s .legL,.fig.%s .legR,.fig.%s .shadow{display:none}' % (inst, inst, inst))
    knife = '<g class="kn3"><path d="M-4,-4 L4,-4 L3,10 L-3,10 Z" fill="%s"/><path d="M-3,-4 L-3,-34 Q0,-40 4,-34 L3,-4 Z" fill="#d9d4cc" stroke="#b9b2a7" stroke-width="1"/></g>' % BROWN
    brd = '<g class="br3h" transform="translate(4,-14) scale(.9)">%s</g>' % bread()
    s.append(FIG('A', 'sit ' + inst, cx, feet, sc, post=ghost('A', inst, 'sit', knife, arm='R') + ghost('A', inst, 'sit', brd, arm='L')))
    # skrzyżowane nogi
    lx = lambda v: f(v)
    s.append('<path d="M168,520 C170,488 214,472 270,486 C326,472 370,488 372,520 C360,540 320,536 270,524 C220,536 180,540 168,520 Z" fill="%s"/>' % PANTS)
    s.append('<path d="M200,512 C230,500 252,506 270,516 M340,512 C310,500 288,506 270,516" fill="none" stroke="#1d1d20" stroke-width="2"/>')
    s.append('<path d="M222,520 C226,508 252,508 256,518 L254,528 L222,528 Z" fill="#f4f2ee"/><path d="M318,520 C314,508 288,508 284,518 L286,528 L318,528 Z" fill="#f4f2ee"/>')
    # deska na kolanach
    s.append('<g><rect x="190" y="444" width="10" height="70" rx="3" fill="%s"/><rect x="340" y="444" width="10" height="70" rx="3" fill="%s"/>' % (BROWN, BROWN) +
             '<rect x="172" y="430" width="196" height="18" rx="7" fill="#D9B99B" stroke="%s" stroke-width="2"/><rect x="186" y="434" width="168" height="4" rx="2" fill="#fff" opacity=".35"/></g>' % BROWN)
    s.append('<g transform="translate(250,420) scale(.8)"><g class="br3b">%s</g></g>' % bread())
    # pudełka: lecą z prawej, lądują na stosie po lewej
    stack = [(96, 520), (96, 474), (96, 428)]
    boxes = [(SAGE, DKG, 1.0, (-90, 470)), (BEIGE, BROWN, 1.48, (-90, 400)), ('#EBD9CF', SAGE, 1.94, (-80, 340))]
    for i, ((col, lid, t0, (sx, sy)), (ex, ey)) in enumerate(zip(boxes, stack)):
        c1, c2, lid_c = uid('lbx'), uid('lby'), uid('lid')
        s.append('<g transform="translate(%s,%s)"><g class="%s"><g class="%s">%s</g></g></g>' % (f(ex), f(ey), c1, c2, lunchbox(col, lid, lid_c)))
        dx, dy = sx - ex, sy - ey
        A('.' + c1, K([(0, 'transform:translateX(%spx) rotate(-30deg)' % f(dx)), (t0, 'transform:translateX(%spx) rotate(-30deg)' % f(dx), 'cubic-bezier(.3,.1,.6,1)'), (t0 + .42, 'transform:translateX(0) rotate(0deg)')], T))
        A('.' + c2, K([(0, 'transform:translateY(%spx)' % f(dy)), (t0, 'transform:translateY(%spx)' % f(dy), 'cubic-bezier(.2,.6,.4,1)'), (t0 + .2, 'transform:translateY(%spx)' % f(min(dy, 0) - 90), 'cubic-bezier(.6,0,.9,.5)'),
                       (t0 + .42, 'transform:translateY(0)', ESOFT), (t0 + .5, 'transform:translateY(-6px)'), (t0 + .58, 'transform:translateY(0)')], T))
        S('.%s{transform-origin:-43px -22px}' % lid_c)
        A('.' + lid_c, K([(0, 'transform:rotate(-70deg)'), (t0 + .4, 'transform:rotate(-70deg)', EBOUNCE), (t0 + .52, 'transform:rotate(0deg)')], T))
        # kanapka wskakuje do pudełka
        sw = uid('sw3')
        s.append('<g transform="translate(%s,%s) scale(.55)"><g class="%s">%s</g></g>' % (f(ex), f(ey - 20), sw, bread()))
        hx, hy = 250 - ex, 420 - (ey - 20)
        A('.' + sw, K([(0, 'opacity:0;transform:translate(%spx,%spx)' % (f(hx / .55), f(hy / .55))), (t0 + .02, 'opacity:0;transform:translate(%spx,%spx)' % (f(hx / .55), f(hy / .55)), 'steps(1,end)'),
                       (t0 + .04, 'opacity:1;transform:translate(%spx,%spx)' % (f(hx / .55), f(hy / .55)), 'cubic-bezier(.3,0,.5,1)'),
                       (t0 + .22, 'opacity:1;transform:translate(%spx,%spx)' % (f(hx / .55 * .5), f(hy / .55 * .5 - 120))), (t0 + .4, 'opacity:1;transform:translate(0px,0px)', 'steps(1,end)'), (t0 + .42, 'opacity:0;transform:translate(0px,0px)')], T))
    # chleb na desce znika/odnawia się przy każdym wyrzucie
    A('.br3b', K([(0, 'opacity:0'), (.55, 'opacity:0', 'steps(1,end)'), (.56, 'opacity:1'), (1.02, 'opacity:1', 'steps(1,end)'), (1.04, 'opacity:0'), (1.3, 'opacity:0', 'steps(1,end)'), (1.31, 'opacity:1'),
                  (1.5, 'opacity:1', 'steps(1,end)'), (1.52, 'opacity:0'), (1.75, 'opacity:0', 'steps(1,end)'), (1.76, 'opacity:1'), (1.96, 'opacity:1', 'steps(1,end)'), (1.98, 'opacity:0')], T, 'linear'))
    # kromka wlatuje do lewej dłoni z lewej krawędzi
    s.append('<g transform="translate(270,420)"><g class="br3f">%s</g></g>' % bread())
    LH = L2W(cx, feet, sc, 52 + 40, 410)
    A('.br3f', K([(0, 'opacity:1;transform:translate(-360px,-120px) rotate(-200deg)'), (.2, 'opacity:1;transform:translate(-360px,-120px) rotate(-200deg)', 'cubic-bezier(.3,.2,.4,1)'),
                  (.5, 'opacity:1;transform:translate(-40px,30px) rotate(0deg)', 'steps(1,end)'), (.52, 'opacity:0;transform:translate(-40px,30px) rotate(0deg)')], T))
    A('.br3h', K([(0, 'opacity:0'), (.5, 'opacity:0', 'steps(1,end)'), (.52, 'opacity:1'), (.54, 'opacity:1', 'steps(1,end)'), (.56, 'opacity:0')], T, 'linear'))
    s.append('</g>')
    # ręce: lewa łapie kromkę, prawa smaruje (oscylacja)
    fr = [(0, {'L': (70, 430), 'R': (150, 430)}), (.3, {'L': (40, 360)}, ESNAP), (.52, {'L': (40, 362)}), (.62, {'L': (92, 428)}, EIO)]
    t = .62
    for i in range(8):
        t += .12
        fr.append((t, {'R': (122 if i % 2 == 0 else 150, 428 - (i % 2) * 6)}, 'ease-in-out'))
    fr += [(1.7, {'R': (150, 428)}), (2.0, {'R': (132, 410), 'L': (90, 410)}), (2.3, {'R': (124, 330), 'L': (96, 330)}, ESOFT), (T, {'R': (124, 326), 'L': (96, 326)})]
    rig(inst, 'A', T, fr)
    A('.kn3', K([(0, 'opacity:1'), (2.0, 'opacity:1'), (2.1, 'opacity:0')], T, 'linear'))
    A('.fig.%s .eyes' % inst, K([(0, 'transform:scaleY(.1)'), (1.36, 'transform:scaleY(.1)', ESNAP), (1.44, 'transform:scaleY(1)'), (1.66, 'transform:scaleY(1)', ESNAP), (1.74, 'transform:scaleY(.1)'), (T, 'transform:scaleY(.1)')], T))
    pupils(inst, T, [(0, 0), (1.36, 3.4), (1.7, 3.4), (1.75, 0)])
    head(inst, T, [(0, 0, 0, 0), (1.3, 0, 0, 0), (1.4, 6, 2, 0, ESNAP), (1.7, 6, 2, 0), (1.8, 0, 0, 0, ESNAP), (2.3, -3, 0, -2), (T, -3, 0, -2)])
    A('.fig.%s .smile' % inst, K([(0, 'transform:scale(1.1,1.25)'), (T, 'transform:scale(1.1,1.25)')], T))
    A('.fig.%s .body' % inst, K([(0, 'transform:translateY(0)'), (1.5, 'transform:translateY(-3px)'), (T, 'transform:translateY(0)')], T))
    cam('cm3', T, [(0, 270, 420, 1.1, 270, 420, -1.2), (.5, 270, 420, 1.07, 270, 420, -.8), (T, 270, 430, 1.0, 270, 430, .8)], 'cubic-bezier(.3,0,.5,1)')
    out = ['<g class="cm3w"><g class="cm3">'] + s + ['</g></g>', vignette2(.35)]
    # whip-pan na wyjściu
    A('.cm3w', K([(0, 'transform:translateX(0)'), (2.76, 'transform:translateX(0)', 'cubic-bezier(.7,0,1,.6)'), (T, 'transform:translateX(-300px)')], T))
    st = uid('stk')
    out.append('<g class="%s">' % st + ''.join('<rect x="%s" y="%s" width="%s" height="4" rx="2" fill="#FBF9F6" opacity=".7"/>' % (f(R.uniform(0, 420)), f(130 + i * 62), f(R.uniform(120, 260))) for i in range(12)) + '</g>')
    A('.' + st, K([(0, 'opacity:0;transform:translateX(0)'), (2.78, 'opacity:0;transform:translateX(0)', 'linear'), (2.84, 'opacity:.9;transform:translateX(-40px)'), (T, 'opacity:.9;transform:translateX(-160px)')], T))
    # plansza na dole
    cc = uid('cd3')
    out.append('<g class="%s">%s</g>' % (cc, card(36, 588, 468, 160, fill=CREAM2, edge=SAGE)))
    card_in(cc, T, .1, 'rise')
    out.append(stext('Medytuj.', 270, 678, 64, cls='split t3t'))
    S('.scene.active .t3t.ch{transform-box:fill-box;transform-origin:50% 100%;animation:t3d .46s cubic-bezier(.2,.9,.3,1.04) both;animation-delay:calc(.3s + var(--i) * 45ms)}'
      '@keyframes t3d{from{opacity:0;transform:translateY(-46px) rotate(-8deg)}to{opacity:1;transform:none}}')
    out.append('<g class="t3b">%s</g>' % mtext('Najlepiej wielozadaniowo.', 270, 722, 27))
    A('.t3b', K([(0, 'opacity:0;transform:translateY(12px)'), (.95, 'opacity:0;transform:translateY(12px)', ESNAP), (1.18, 'opacity:1;transform:translateY(0)')], T))
    out.append(badge(2, 270, 588, T, .18))
    out.append(check(478, 600, T, 2.36))
    # gwiazdowa „dziura” – wejście sceny
    out.append('<mask id="m3s" maskUnits="userSpaceOnUse" x="-100" y="-100" width="740" height="1160"><rect x="-100" y="-100" width="740" height="1160" fill="#fff"/>'
               '<g transform="translate(270,560)"><g class="st3h"><path d="%s" fill="#000"/></g></g></mask>' % star_path(400, 230))
    out.append('<rect x="-100" y="-100" width="740" height="1160" fill="%s" mask="url(#m3s)" class="st3o"/>' % SAGE)
    A('.st3h', K([(0, 'transform:scale(0) rotate(40deg)'), (.36, 'transform:scale(3.2) rotate(90deg)')], T, 'cubic-bezier(.3,.4,.4,1)'))
    A('.st3o', K([(0, 'opacity:1'), (.36, 'opacity:1', 'steps(1,end)'), (.37, 'opacity:0')], T, 'linear'))
    for x, y, d in [(120, 200, .3), (430, 170, .9), (450, 360, .5)]:
        out.append(sparkle(x, y, 1.0, CREAM2, d))
    return ''.join(out), T

# ================= SCENA 4: KROK 3/5 – joga + klocki (8–11 s) =================
def block(col, mark='#FBF9F6'):
    return ('<g><rect x="-17" y="-17" width="34" height="34" rx="5" fill="%s"/><rect x="-17" y="-17" width="34" height="8" rx="4" fill="#fff" opacity=".22"/>' % col +
            '<use href="#star" transform="scale(.9)" fill="%s" opacity=".85"/></g>' % mark)

def sc_krok3():
    T = 3.0; s = []
    inst = 'pA4'
    cx, feet, sc = 336, 772, .62
    FL = 772
    s.append('<g class="c4">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="%s"/>' % CREAM)
    # girlanda z chorągiewek
    gl = '<path d="M-20,318 Q270,372 560,318" fill="none" stroke="%s" stroke-width="2"/>' % BROWN
    for i in range(12):
        x = -10 + i * 48; y = 318 + 54 * (1 - ((x - 270) / 290) ** 2) * .9
        col = [SAGE, BEIGE, DKG][i % 3]
        gl += '<path d="M%s,%s l16,0 l-8,22 Z" fill="%s"/>' % (f(x - 8), f(y), col)
    s.append('<g class="gl4">%s</g>' % gl)
    A('.gl4', K([(0, 'transform:translateY(0)'), (1.5, 'transform:translateY(3px)'), (T, 'transform:translateY(0)')], T))
    # półka z roślinką (głębia)
    s.append('<rect x="408" y="450" width="120" height="8" rx="3" fill="%s"/><path d="M440,450 q-2,-16 12,-20 q14,-4 16,12 Z" fill="%s"/><rect x="442" y="426" width="30" height="24" rx="4" fill="%s"/>' % (BEIGE, DKG, BEIGE))
    s.append('<use href="#leaf" transform="translate(452,414) rotate(-30) scale(1.3)" fill="%s"/><use href="#leaf" transform="translate(468,412) rotate(25) scale(1.2)" fill="%s"/>' % (DKG, SAGE))
    # podłoga
    s.append('<rect x="-100" y="%s" width="740" height="400" fill="#EADCD2"/><rect x="-100" y="%s" width="740" height="10" fill="#E3CCC1"/>' % (FL - 6, FL - 6))
    s.append('<path d="M240,%s L432,%s L462,%s L210,%s Z" fill="%s"/>' % (FL - 4, FL - 4, FL + 24, FL + 24, SAGE))
    # pudło na zabawki
    s.append('<g transform="translate(112,%s)"><g class="box4"><rect x="-70" y="-84" width="140" height="84" rx="8" fill="%s"/><rect x="-70" y="-84" width="140" height="14" rx="6" fill="#4d675f"/>' % (FL, DKG) +
             '<path d="M-70,-50 H70 M-70,-26 H70" stroke="#4d675f" stroke-width="3"/><circle cx="0" cy="-38" r="16" fill="%s"/><use href="#star" transform="translate(0,-38) scale(1.1)" fill="%s"/></g></g>' % (CREAM2, MUST))
    S('.box4{transform-origin:0 0}')
    A('.box4', K([(0, 'transform:scale(1,1)'), (1.6, 'transform:scale(1,1)', 'ease-out'), (1.66, 'transform:scale(1.06,.92)', ESOFT), (1.82, 'transform:scale(1,1)'), (2.62, 'transform:scale(1,1)', 'ease-out'), (2.68, 'transform:scale(1.06,.92)', ESOFT), (2.84, 'transform:scale(1,1)')], T))
    # A: nogi rysowane ścieżkami (przysiad „malasana”), fig-nogi ukryte
    S('.fig.%s .legL,.fig.%s .legR{display:none}' % (inst, inst))
    D = 232
    def legs(hy, kx_l, ky, kx_r):
        return ("d:path('M86,%s L%s,%s L86,690')" % (f(hy), f(kx_l), f(ky)), "d:path('M134,%s L%s,%s L134,690')" % (f(hy), f(kx_r), f(ky)))
    stand = legs(436, 86, 566, 134)
    squat = legs(436 + D, -22, 606, 242)
    lg = ('<path class="lgL" d="M86,436 L86,566 L86,690" fill="none" stroke="%s" stroke-width="38" stroke-linecap="round" stroke-linejoin="round"/>' % PANTS +
          '<path class="lgR" d="M134,436 L134,566 L134,690" fill="none" stroke="%s" stroke-width="38" stroke-linecap="round" stroke-linejoin="round"/>' % PANTS +
          '<path d="M64,704 C64,690 108,688 102,700 L104,712 L62,712 Z" fill="#f4f2ee"/><rect x="62" y="708" width="48" height="5" rx="2" fill="#d6cfc2"/>'
          '<path d="M112,704 C112,690 156,688 162,700 L164,712 L110,712 Z" fill="#f4f2ee"/><rect x="110" y="708" width="54" height="5" rx="2" fill="#d6cfc2"/>')
    blkL = '<g class="bh4L" transform="translate(0,-8) scale(1.5)">%s</g>' % block(MUST)
    blkR = '<g class="bh4R" transform="translate(0,-8) scale(1.5)">%s</g>' % block(SAGE)
    s.append(FIG('A', inst, cx, feet, sc, pre='<g class="fig figA %s ghost">%s</g>' % (inst, lg), post=ghost('A', inst, '', blkL, arm='L') + ghost('A', inst, '', blkR, arm='R')))
    # klocki na podłodze (w świecie); para 1 i para 2
    pairs = [((70, 690), (150, 690)), ((28, 692), (192, 692))]
    cols = [(MUST, SAGE), (BEIGE, DKG)]
    floor_cls = []
    for (pl, pr), (cl, cr) in zip(pairs, cols):
        row = []
        for (lx_, ly_), col in ((pl, cl), (pr, cr)):
            wx, wy = L2W(cx, feet, sc, lx_, ly_ + 6)
            c = uid('fb')
            s.append('<g transform="translate(%s,%s) rotate(%s) scale(.93)"><g class="%s">%s</g></g>' % (f(wx), f(wy), R.randint(-14, 14), c, block(col)))
            row.append(c)
        floor_cls.append(row)
    # dodatkowe rozrzucone (zostają)
    for x, y, col, r in [(470, FL + 6, BEIGE, 12), (500, FL + 30, SAGE, -20), (214, FL + 34, MUST, 8)]:
        s.append('<g transform="translate(%s,%s) rotate(%s) scale(.93)">%s</g>' % (x, y, r, block(col)))
    s.append('</g>')
    # oś czasu ciała
    downs = [(.55, .86), (1.62, 1.93)]
    ups = [(.96, 1.26), (2.03, 2.33)]
    bfr = [(0, 'transform:translateY(0)')]
    lfr, rfr = [(0, stand[0])], [(0, stand[1])]
    for (d0, d1), (u0, u1) in zip(downs, ups):
        bfr += [(d0, 'transform:translateY(0)', 'cubic-bezier(.45,0,.3,1)'), (d1, 'transform:translateY(%spx)' % D), (u0, 'transform:translateY(%spx)' % D, 'cubic-bezier(.3,0,.25,1)'), (u1, 'transform:translateY(0)')]
        lfr += [(d0, stand[0], 'cubic-bezier(.45,0,.3,1)'), (d1, squat[0]), (u0, squat[0], 'cubic-bezier(.3,0,.25,1)'), (u1, stand[0])]
        rfr += [(d0, stand[1], 'cubic-bezier(.45,0,.3,1)'), (d1, squat[1]), (u0, squat[1], 'cubic-bezier(.3,0,.25,1)'), (u1, stand[1])]
    A('.fig.%s .body' % inst, K(bfr, T))
    A('.%s .lgL' % inst, K(lfr, T))
    A('.%s .lgR' % inst, K(rfr, T))
    UP_L, UP_R = (96, 62), (124, 62)
    TOSS_L, TOSS_R = (-50, 300), (40, 292)
    fr = [(0, {'L': UP_L, 'R': UP_R, 'eL': 'out', 'eR': 'out'}), (.5, {'L': UP_L, 'R': UP_R, 'eL': 'out', 'eR': 'out'})]
    for k, ((d0, d1), (u0, u1)) in enumerate(zip(downs, ups)):
        (pl, pr) = pairs[k]
        fr.append((d1, {'L': (pl[0], pl[1] - 8 - D), 'R': (pr[0], pr[1] - 8 - D), 'eL': 'out', 'eR': 'out'}, 'cubic-bezier(.45,0,.3,1)'))
        fr.append((u0, {'L': (pl[0], pl[1] - 8 - D), 'R': (pr[0], pr[1] - 8 - D), 'eL': 'out', 'eR': 'out'}))
        fr.append((u1, {'L': TOSS_L, 'R': TOSS_R, 'eL': 'out', 'eR': 'out'}, 'cubic-bezier(.3,0,.25,1)'))
        fr.append((u1 + .14, {'L': (-40, 340), 'R': (100, 400), 'eL': 'out', 'eR': 'out'}))
        if k == 0:
            fr.append((d0 + 1.07 - .01 if False else 1.62, {'L': (60, 300), 'R': (160, 300), 'eL': 'out', 'eR': 'out'}))
    fr += [(2.62, {'L': UP_L, 'R': UP_R, 'eL': 'out', 'eR': 'out'}, EIO), (T, {'L': UP_L, 'R': UP_R, 'eL': 'out', 'eR': 'out'})]
    fr.sort(key=lambda x: x[0])
    rig(inst, 'A', T, fr)
    # bloki: podłoga → dłonie → lot do pudła
    for k, ((d0, d1), (u0, u1)) in enumerate(zip(downs, ups)):
        for side, c in zip('LR', floor_cls[k]):
            A('.' + c, K([(0, 'opacity:1'), (d1, 'opacity:1', 'steps(1,end)'), (d1 + .01, 'opacity:0')], T, 'linear'))
        for side, tgt in (('L', TOSS_L), ('R', TOSS_R)):
            pass
    A('.bh4L', K([(0, 'opacity:0'), (downs[0][1], 'opacity:0', 'steps(1,end)'), (downs[0][1] + .01, 'opacity:1'), (ups[0][1], 'opacity:1', 'steps(1,end)'), (ups[0][1] + .01, 'opacity:0'),
                  (downs[1][1], 'opacity:0', 'steps(1,end)'), (downs[1][1] + .01, 'opacity:1'), (ups[1][1], 'opacity:1', 'steps(1,end)'), (ups[1][1] + .01, 'opacity:0')], T, 'linear'))
    A('.bh4R', K([(0, 'opacity:0'), (downs[0][1], 'opacity:0', 'steps(1,end)'), (downs[0][1] + .01, 'opacity:1'), (ups[0][1], 'opacity:1', 'steps(1,end)'), (ups[0][1] + .01, 'opacity:0'),
                  (downs[1][1], 'opacity:0', 'steps(1,end)'), (downs[1][1] + .01, 'opacity:1'), (ups[1][1], 'opacity:1', 'steps(1,end)'), (ups[1][1] + .01, 'opacity:0')], T, 'linear'))
    fly = []
    BOX = (112, FL - 92)
    for k, (u0, u1) in enumerate(ups):
        for j, (tgt, col) in enumerate(((TOSS_L, cols[k][0]), (TOSS_R, cols[k][1]))):
            hx, hy = L2W(cx, feet, sc, tgt[0], tgt[1] - 8)
            cX, cY = uid('fx'), uid('fy')
            t0 = u1 + .01; t1 = t0 + .36 + j * .06
            ex, ey = BOX[0] + (j * 2 - 1) * 22, BOX[1] + 30
            fly.append('<g class="%s"><g class="%s"><g transform="scale(.93)">%s</g></g></g>' % (cX, cY, block(col)))
            A('.' + cX, K([(0, 'opacity:0;transform:translateX(%spx)' % f(hx)), (t0 - .01, 'opacity:0;transform:translateX(%spx)' % f(hx), 'steps(1,end)'), (t0, 'opacity:1;transform:translateX(%spx)' % f(hx), 'cubic-bezier(.35,.1,.6,.9)'),
                           (t1, 'opacity:1;transform:translateX(%spx)' % f(ex), 'steps(1,end)'), (t1 + .01, 'opacity:0;transform:translateX(%spx)' % f(ex))], T))
            apex = min(hy, ey) - 110
            A('.' + cY, K([(0, 'transform:translateY(%spx) rotate(0deg)' % f(hy)), (t0, 'transform:translateY(%spx) rotate(0deg)' % f(hy), 'cubic-bezier(.2,.6,.4,1)'), ((t0 + t1) / 2, 'transform:translateY(%spx) rotate(-200deg)' % f(apex), 'cubic-bezier(.6,0,.8,.4)'),
                           (t1, 'transform:translateY(%spx) rotate(-380deg)' % f(ey))], T))
    s.insert(len(s) - 1, ''.join(fly))
    head(inst, T, [(0, 0, 0, 0), (.6, 0, 0, 0), (.86, 0, 0, 6), (1.26, -6, -3, 0), (1.5, -8, -3, 0), (1.62, -8, -3, 0), (1.93, 0, 0, 6), (2.33, -6, -3, 0), (2.62, 0, 0, 0), (T, 3, 1, 0)])
    pupils(inst, T, [(0, 0), (.6, 0), (.8, 0), (1.26, -3), (1.7, -3), (1.9, 0), (2.33, -3), (2.65, -3), (2.75, 0)])
    A('.fig.%s .smile' % inst, K([(0, 'transform:scale(1.14,1.32)'), (T, 'transform:scale(1.14,1.32)')], T))
    cam('cm4', T, [(0, 300, 560, 1.0, 300, 560, 0), (1.3, 290, 570, 1.03, 300, 560, 0), (2.5, 270, 580, 1.06, 300, 560, 0), (T, 270, 580, 1.08, 300, 560, 0)], 'cubic-bezier(.4,0,.6,1)')
    out = ['<g class="cm4w"><g class="cm4">'] + s + ['</g></g>', vignette2(.3)]
    A('.cm4w', K([(0, 'transform:translateX(300px)'), (.26, 'transform:translateX(0)')], T, 'cubic-bezier(0,.6,.3,1)'))
    st = uid('stk')
    out.append('<g class="%s">' % st + ''.join('<rect x="%s" y="%s" width="%s" height="4" rx="2" fill="#FBF9F6" opacity=".7"/>' % (f(R.uniform(0, 420)), f(140 + i * 60), f(R.uniform(120, 260))) for i in range(12)) + '</g>')
    A('.' + st, K([(0, 'opacity:.9;transform:translateX(160px)'), (.22, 'opacity:0;transform:translateX(-40px)')], T, 'linear'))
    # plansza (lewa, przechylona)
    cc = uid('cd4')
    out.append('<g class="%s">%s</g>' % (cc, card(28, 116, 384, 190, fill='#FBF6F1', edge=BEIGE, rot=-3)))
    card_in(cc, T, .12, 'drop')
    out.append('<g transform="rotate(-3 220 211)">')
    out.append('<g transform="translate(220,214)"><g class="t4">%s</g></g>' % stext('Joga!', 0, 0, 84, shadow=BEIGE, dxy=(3, 4)))
    A('.t4', K([(0, 'opacity:0;transform:scale(2.2) rotate(-10deg)'), (.34, 'opacity:0;transform:scale(2.2) rotate(-10deg)', 'cubic-bezier(.6,0,.9,.4)'), (.5, 'opacity:1;transform:scale(.97) rotate(1deg)', ESOFT), (.62, 'opacity:1;transform:scale(1) rotate(0deg)')], T))
    out.append('<g class="t4b">%s</g>' % mtext('Przy okazji posprzątasz.', 220, 270, 26))
    A('.t4b', K([(0, 'opacity:0;transform:translateX(-16px)'), (1.02, 'opacity:0;transform:translateX(-16px)', ESNAP), (1.26, 'opacity:1;transform:translateX(0)')], T))
    out.append('</g>')
    out.append(badge(3, 220, 122, T, .2))
    out.append(check(52, 134, T, 2.4))
    # flash-zoom wyjście
    out.append('<rect width="540" height="960" fill="#FFFDF6" class="fo4" pointer-events="none"/>')
    A('.fo4', K([(0, 'opacity:0'), (2.76, 'opacity:0', 'cubic-bezier(.5,0,.9,.6)'), (T, 'opacity:.95')], T))
    return ''.join(out), T

# ================= SCENA 5: KROK 4/5 – mikrofalówka (11–14 s) =================
DINGS = [.72, 1.52, 2.3]
PRESS = [.16, .98, 1.76]

def sc_krok4():
    T = 3.0; s = []
    s.append('<g class="c5">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="%s"/>' % BEIGE)
    s.append(''.join('<path d="M-100,%s H640" stroke="#D9C0B4" stroke-width="1.6"/>' % y for y in range(130, 480, 38)))
    s.append(''.join('<path d="M%s,%s v38" stroke="#D9C0B4" stroke-width="1.6"/>' % (x + (19 if (j % 2) else 0), 130 + j * 38) for x in range(-100, 640, 38) for j in range(9)))
    cy = 476
    s.append('<rect x="-100" y="%s" width="740" height="18" rx="3" fill="#EADCD2"/><rect x="-100" y="%s" width="740" height="500" fill="%s"/>' % (cy, cy + 18, DKG))
    # mikrofalówka
    mx0, my0, mw, mh = 46, 196, 448, 280
    s.append('<rect x="%s" y="%s" width="%s" height="%s" rx="22" fill="#3a2a20" opacity=".14" transform="translate(4,8)"/>' % (mx0, my0, mw, mh))
    s.append('<rect x="%s" y="%s" width="%s" height="%s" rx="22" fill="%s" stroke="#d6cdc1" stroke-width="2.5"/>' % (mx0, my0, mw, mh, CREAM2))
    s.append('<rect x="70" y="220" width="278" height="232" rx="14" fill="#E9E1D6"/>')
    s.append('<rect x="88" y="236" width="242" height="200" rx="10" fill="#3F4F49"/>')
    s.append('<rect x="88" y="236" width="242" height="200" rx="10" fill="#F3D7B0" class="ml5"/>')
    on = []
    for p, d in zip(PRESS, DINGS):
        on += [(p + .12, 'opacity:0', 'steps(1,end)'), (p + .13, 'opacity:.85'), (d, 'opacity:.85', 'steps(1,end)'), (d + .01, 'opacity:0')]
    A('.ml5', K([(0, 'opacity:0')] + on, T, 'linear'))
    s.append('<ellipse cx="209" cy="412" rx="92" ry="14" fill="#e9e3da" opacity=".85"/>')
    # kubek na talerzu (obrót = przesuw + odbicie)
    mug = ('<g><path d="M-24,-46 L24,-46 L21,6 Q20,13 12,13 L-12,13 Q-20,13 -21,6 Z" fill="#FBF9F6"/><path d="M23,-32 Q42,-32 39,-15 Q36,-2 21,-3" fill="none" stroke="#FBF9F6" stroke-width="7"/>'
           '<path d="M-23,-22 L23,-22 L22.4,-12 L-22.4,-12 Z" fill="%s"/><ellipse cx="0" cy="-46" rx="24" ry="6" fill="#7a4a30"/></g>' % SAGE)
    s.append('<g transform="translate(209,410)"><g class="mg5x"><g class="mg5f">%s</g></g></g>' % mug)
    mx, mf = [(0, 'transform:translateX(0)')], [(0, 'transform:scaleX(1)')]
    for p, d in zip(PRESS, DINGS):
        a, b = p + .13, d
        n = 4
        for i in range(1, n + 1):
            t = a + (b - a) * i / n
            mx.append((t - (b - a) / n / 2, 'transform:translateX(%spx)' % (26 if i % 2 else -26)))
            mx.append((t, 'transform:translateX(0)'))
            mf.append((t - (b - a) / n / 2 + .01, 'transform:scaleX(%s)' % (-1 if i % 2 else 1)))
    mx.sort(key=lambda x: x[0]); mf.sort(key=lambda x: x[0])
    A('.mg5x', K(mx, T, 'ease-in-out'))
    A('.mg5f', K(mf, T, 'steps(1,end)'))
    # para po DING – i znika (stygnie)
    s.append('<g transform="translate(209,350)"><g class="sm5">%s</g></g>' % steam_paths('stm', 3, 40, 6, 3, '#FBF9F6', 12))
    A('.sm5', K([(0, 'opacity:0')] + sum([[(d, 'opacity:0', 'steps(1,end)'), (d + .01, 'opacity:1'), (d + .5, 'opacity:1', EOUT), (d + .7, 'opacity:0')] for d in DINGS], []), T, 'linear'))
    s.append('<rect x="88" y="236" width="242" height="200" rx="10" fill="url(#shine)" opacity=".25"/>')
    s.append('<rect x="324" y="300" width="12" height="70" rx="6" fill="#d6cdc1"/>')
    # panel
    s.append('<rect x="368" y="226" width="104" height="54" rx="8" fill="#2f3b37"/>')
    disp = []
    for i, (p, d) in enumerate(zip(PRESS, DINGS)):
        seq = ['0:30', '0:22', '0:15', '0:07', '0:00']
        for j, txt in enumerate(seq):
            c = uid('ds')
            t0 = p + .13 + (d - p - .13) * j / len(seq)
            t1 = p + .13 + (d - p - .13) * (j + 1) / len(seq) if j < len(seq) - 1 else d + .01
            disp.append('<text x="420" y="264" font-size="28" text-anchor="middle" fill="#F6DDA8" style="font-weight:800" class="%s">%s</text>' % (c, txt))
            A('.' + c, K([(0, 'opacity:0'), (t0, 'opacity:0', 'steps(1,end)'), (t0 + .005, 'opacity:1'), (t1, 'opacity:1', 'steps(1,end)'), (t1 + .005, 'opacity:0')], T, 'linear'))
    c = uid('ds')
    disp.append('<text x="420" y="264" font-size="22" text-anchor="middle" fill="#F6DDA8" style="font-weight:900;letter-spacing:.06em" class="%s">END</text>' % c)
    endf = [(0, 'opacity:0')]
    for p, d in zip(PRESS, DINGS):
        endf += [(d, 'opacity:0', 'steps(1,end)'), (d + .01, 'opacity:1')]
    for p in PRESS[1:]:
        endf += [(p + .12, 'opacity:1', 'steps(1,end)'), (p + .13, 'opacity:0')]
    endf.sort(key=lambda x: x[0])
    A('.' + c, K(endf, T, 'linear'))
    s.append(''.join(disp))
    for r in range(3):
        for k in range(3):
            s.append('<rect x="%s" y="%s" width="26" height="16" rx="5" fill="#E9E1D6"/>' % (374 + k * 34, 296 + r * 26))
    s.append('<g transform="translate(420,410)"><g class="btn5"><rect x="-44" y="-22" width="88" height="44" rx="12" fill="%s"/><text x="0" y="7" font-size="17" text-anchor="middle" fill="%s" style="font-weight:900;letter-spacing:.1em">START</text></g></g>' % (SAGE, CREAM2))
    S('.btn5{transform-origin:0 0}')
    bf = [(0, 'transform:scale(1)')]
    for p in PRESS:
        bf += [(p + .08, 'transform:scale(1)', 'ease-out'), (p + .12, 'transform:scale(.9)'), (p + .22, 'transform:scale(1)')]
    A('.btn5', K(bf, T))
    # ręka A (pasiasty rękaw) wciska START – wchodzi z prawej
    s.append('<g transform="translate(446,424) scale(-1,1) rotate(-28)"><g class="hd5"><g transform="scale(1.25)">%s</g></g></g>' % side_arm('url(#stripesA)', 'open', '', skin=SKIN, cuff='#ece8df', width=30))
    hf = [(0, 'transform:translate(-300px,0)')]
    for p in PRESS:
        hf += [(p - .14, 'transform:translate(-300px,0)', ESNAP), (p + .06, 'transform:translate(6px,0)', 'ease-out'), (p + .12, 'transform:translate(16px,0)', ESOFT), (p + .3, 'transform:translate(0,0)', EIO), (p + .5, 'transform:translate(-300px,0)')]
    A('.hd5', K(hf, T))
    s.append('</g>')
    zf = [(0, 270, 330, 1.12, 270, 330, 0), (.3, 270, 330, 1.02, 270, 330, 0)]
    for i, d in enumerate(DINGS):
        rot = [-1.2, 1.2, -1.6][i]
        zf += [(d, 270, 330, 1.02 + .02 * i, 270, 330, 0 if i == 0 else zf[-1][6], ESNAP), (d + .1, 270, 330, 1.06 + .02 * i, 270, 330, rot), (min(d + .7, T), 270, 330, 1.05 + .02 * i, 270, 330, rot * .6)]
    zf.sort(key=lambda x: x[0])
    cam('cm5', T, zf, 'cubic-bezier(.3,0,.4,1)')
    out = ['<g class="cm5">'] + s + ['</g>', vignette2(.3)]
    # licznik
    out.append('<g transform="translate(270,150)"><g class="cn5"><rect x="-148" y="-30" width="296" height="60" rx="30" fill="%s" stroke="%s" stroke-width="2"/>' % (CREAM2, DKG) +
               '<text x="-32" y="9" font-size="23" text-anchor="middle" fill="%s" style="font-weight:800;letter-spacing:.1em">PODGRZANA:</text>' % INK)
    for i, d in enumerate(DINGS):
        c = uid('cn')
        out.append('<g transform="translate(96,0)"><g class="%s"><text x="0" y="15" font-size="44" text-anchor="middle" class="serif" fill="%s">%d×</text></g></g>' % (c, DKG, i + 1))
        nx = DINGS[i + 1] if i + 1 < len(DINGS) else 99
        fr2 = [(0, 'opacity:0;transform:translateY(16px)'), (d + .02, 'opacity:0;transform:translateY(16px)', ESNAP), (d + .14, 'opacity:1;transform:translateY(0)')]
        if nx < T:
            fr2 += [(nx, 'opacity:1;transform:translateY(0)', EOUT), (nx + .06, 'opacity:0;transform:translateY(-16px)')]
        A('.' + c, K(fr2, T))
    out.append('</g></g>')
    S('.cn5{transform-origin:0 0}')
    cf = [(0, 'opacity:0;transform:scale(.7)'), (DINGS[0] - .04, 'opacity:0;transform:scale(.7)', EBOUNCE), (DINGS[0] + .12, 'opacity:1;transform:scale(1)')]
    for d in DINGS[1:]:
        cf += [(d, 'opacity:1;transform:scale(1)', ESOFT), (d + .08, 'opacity:1;transform:scale(1.05)'), (d + .2, 'opacity:1;transform:scale(1)')]
    A('.cn5', K(cf, T))
    # DING! ×3
    for i, (d, (x, y, r)) in enumerate(zip(DINGS, [(186, 300, -8), (232, 336, 6), (200, 296, -4)])):
        c = uid('dg')
        rays = ''.join('<path d="M%s,%s L%s,%s" stroke="%s" stroke-width="4" stroke-linecap="round"/>' % (f(math.cos(math.radians(a)) * 92), f(math.sin(math.radians(a)) * 54), f(math.cos(math.radians(a)) * 118), f(math.sin(math.radians(a)) * 70), '#F6DDA8')
                       for a in range(0, 360, 30))
        out.append('<g transform="translate(%s,%s) rotate(%s)"><g class="%s">%s<text x="0" y="17" font-size="%s" text-anchor="middle" fill="%s" stroke="%s" stroke-width="7" paint-order="stroke" stroke-linejoin="round" style="font-weight:900;letter-spacing:.04em">DING!</text></g></g>'
                   % (f(x), f(y), r, c, rays, 50 + i * 4, DKG, CREAM2))
        S('.%s{transform-origin:0 0}' % c)
        A('.' + c, K([(0, 'opacity:0;transform:scale(.3)'), (d, 'opacity:0;transform:scale(.3)', 'cubic-bezier(.2,.8,.3,1)'), (d + .1, 'opacity:1;transform:scale(1.05)', ESOFT), (d + .2, 'opacity:1;transform:scale(1)'),
                     (d + .5, 'opacity:1;transform:scale(1)', EOUT), (d + .62, 'opacity:0;transform:scale(1.1)')], T))
    # plansza na dole
    cc = uid('cd5')
    out.append('<g class="%s">%s</g>' % (cc, card(30, 528, 480, 220, fill=CREAM2, edge=BEIGE)))
    card_in(cc, T, .1, 'rise')
    S('.t5w1,.t5w2{transform-origin:40px 0}')
    out.append('<clipPath id="cp5a"><rect class="t5w1" x="40" y="566" width="460" height="64"/></clipPath><clipPath id="cp5b"><rect class="t5w2" x="40" y="630" width="460" height="58"/></clipPath>')
    out.append('<g clip-path="url(#cp5a)">%s</g>' % stext('Ciesz się', 270, 616, 54))
    out.append('<g clip-path="url(#cp5b)">%s</g>' % stext('ciepłą kawą.', 270, 670, 54))
    A('.t5w1', K([(0, 'transform:scaleX(0)'), (.3, 'transform:scaleX(0)', 'cubic-bezier(.5,0,.3,1)'), (.62, 'transform:scaleX(1)')], T))
    A('.t5w2', K([(0, 'transform:scaleX(0)'), (.55, 'transform:scaleX(0)', 'cubic-bezier(.5,0,.3,1)'), (.9, 'transform:scaleX(1)')], T))
    out.append('<g class="t5b">%s</g>' % mtext('Odgrzaną trzeci raz.', 270, 718, 28, col=BROWN))
    A('.t5b', K([(0, 'opacity:0;transform:translateY(12px)'), (1.1, 'opacity:0;transform:translateY(12px)', ESNAP), (1.32, 'opacity:1;transform:translateY(0)')], T))
    out.append(badge(4, 270, 528, T, .16))
    out.append(check(478, 548, T, 2.5, r=30))
    # wejście: flash
    out.append('<rect width="540" height="960" fill="#FFFDF6" class="fi5" pointer-events="none"/>')
    A('.fi5', K([(0, 'opacity:.95'), (.3, 'opacity:0')], T, 'cubic-bezier(.2,.7,.3,1)'))
    # wyjście: żaluzje
    bl = ''
    for i in range(8):
        c = uid('bl')
        bl += '<rect x="-10" y="%s" width="560" height="122" fill="%s" class="%s"/>' % (i * 120, SAGE, c)
        S('.%s{transform-origin:0 %spx}' % (c, i * 120))
        A('.' + c, K([(0, 'transform:scaleY(0)'), (2.7 + i * .02, 'transform:scaleY(0)', 'cubic-bezier(.6,0,.4,1)'), (min(T, 2.86 + i * .02), 'transform:scaleY(1)')], T))
    out.append(bl)
    return ''.join(out), T

# ================= SCENA 6: KROK 5/5 – łazienka (14–17 s) =================
KNOCKS = [.56, .7, 1.56, 1.7, 2.26, 2.36, 2.46]

def sc_krok5():
    T = 3.0; s = []
    s.append('<g class="c6">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="%s"/>' % SAGE)
    s.append('<rect x="-100" y="560" width="740" height="230" fill="#93A99F"/><rect x="-100" y="556" width="740" height="8" fill="%s"/>' % CREAM2)
    s.append('<rect x="-100" y="786" width="740" height="300" fill="%s"/><rect x="-100" y="786" width="740" height="6" fill="#d6bdb0"/>' % BEIGE)
    # obrazek na ścianie
    s.append('<g transform="translate(456,420) rotate(3)"><rect x="-40" y="-50" width="80" height="100" fill="%s" stroke="%s" stroke-width="5"/><path d="M-28,30 l18,-30 l12,16 l10,-12 l16,26 Z" fill="%s"/><circle cx="16" cy="-22" r="8" fill="%s"/></g>' % (CREAM2, BEIGE, SAGE, MUST))
    # drzwi
    door = ('<rect x="152" y="372" width="236" height="418" fill="#D8BFB3"/>'
            '<rect x="166" y="384" width="208" height="406" fill="%s"/>' % CREAM2 +
            '<rect x="186" y="404" width="168" height="160" rx="6" fill="none" stroke="%s" stroke-width="3"/><rect x="186" y="584" width="168" height="182" rx="6" fill="none" stroke="%s" stroke-width="3"/>' % (BEIGE, BEIGE) +
            '<circle cx="270" cy="432" r="20" fill="%s" stroke="%s" stroke-width="2.5"/>' % (CREAM2, DKG) +
            '<path d="M256,434 h28 q-2,10 -14,10 q-12,0 -14,-10 Z M260,434 v-10 q0,-5 5,-5" fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % DKG +
            '<rect x="166" y="782" width="208" height="8" fill="#FFF1D6"/>')
    s.append('<g class="dr6">%s' % door)
    # klamka
    s.append('<g transform="translate(350,620)"><g class="kn6"><circle r="7" fill="%s"/><rect x="-30" y="-4" width="34" height="8" rx="4" fill="%s"/></g></g>' % (BROWN, BROWN))
    # timer na drzwiach
    s.append('<rect x="200" y="470" width="140" height="70" rx="14" fill="#2f3b37"/><rect x="206" y="476" width="128" height="58" rx="10" fill="none" stroke="#46564f" stroke-width="2"/>')
    vals = ['4:00', '3:41', '3:17', '2:52', '2:26', '1:58', '1:31', '1:03', '0:38', '0:12', '0:00']
    ts = [0] + [.5 + i * .2 for i in range(len(vals) - 1)]
    for i, v in enumerate(vals):
        c = uid('tm')
        t0, t1 = ts[i], (ts[i + 1] if i + 1 < len(vals) else 99)
        s.append('<text x="270" y="522" font-size="44" text-anchor="middle" fill="#F6DDA8" style="font-weight:800" class="%s">%s</text>' % (c, v))
        fr = [(0, 'opacity:%s' % ('1' if i == 0 else '0'))]
        if i > 0: fr += [(t0, 'opacity:0', 'steps(1,end)'), (t0 + .005, 'opacity:1')]
        if t1 < T: fr += [(t1, 'opacity:1', 'steps(1,end)'), (t1 + .005, 'opacity:0')]
        else: fr += [(2.6, 'opacity:1', 'steps(1,end)'), (2.68, 'opacity:.2', 'steps(1,end)'), (2.76, 'opacity:1', 'steps(1,end)'), (2.84, 'opacity:.2', 'steps(1,end)'), (2.92, 'opacity:1')]
        A('.' + c, K(fr, T, 'linear'))
    s.append('</g>')
    # drżenie drzwi przy pukaniu
    dfr = [(0, 'transform:translateX(0)')]
    for k in KNOCKS:
        dfr += [(k, 'transform:translateX(0)', 'ease-out'), (k + .03, 'transform:translateX(2.5px)'), (k + .08, 'transform:translateX(0)')]
    A('.dr6', K(dfr, T))
    S('.kn6{transform-origin:0 0}')
    A('.kn6', K([(0, 'transform:rotate(0deg)'), (1.96, 'transform:rotate(0deg)', ESNAP), (2.04, 'transform:rotate(-22deg)'), (2.12, 'transform:rotate(0deg)'), (2.18, 'transform:rotate(-18deg)'), (2.28, 'transform:rotate(0deg)')], T))
    # cień dziecka na drzwiach
    s.append('<clipPath id="cpd6"><rect x="166" y="384" width="208" height="398"/></clipPath>')
    s.append('<g clip-path="url(#cpd6)"><g class="sh6"><path d="M0,0 C-30,0 -40,26 -36,52 C-80,62 -96,100 -100,160 L100,160 C96,100 80,62 36,52 C40,26 30,0 0,0 Z" fill="#2f3b37" opacity=".16" transform="translate(190,600)"/></g></g>')
    A('.sh6', K([(0, 'transform:translateX(-160px)'), (.2, 'transform:translateX(-160px)', ESOFT), (.6, 'transform:translateX(0)'), (1.4, 'transform:translateX(6px)'), (2.2, 'transform:translateX(30px)'), (T, 'transform:translateX(34px)')], T))
    # stopy pod drzwiami (cień w szczelinie)
    s.append('<g class="ft6"><ellipse cx="236" cy="787" rx="16" ry="4" fill="#2f3b37" opacity=".5"/><ellipse cx="300" cy="787" rx="16" ry="4" fill="#2f3b37" opacity=".5"/></g>')
    A('.ft6', K([(0, 'opacity:0;transform:translateX(-30px)'), (1.1, 'opacity:0;transform:translateX(-30px)', ESOFT), (1.4, 'opacity:1;transform:translateX(0)'), (2.0, 'opacity:1;transform:translateX(8px)'), (T, 'opacity:1;transform:translateX(-4px)')], T))
    # pięść z lewej
    s.append('<g transform="translate(150,600) rotate(-6)"><g class="hk6">%s</g></g>' % side_arm(MUST, 'fist', '', width=26))
    hk = [(0, 'transform:translate(-300px,0)'), (.36, 'transform:translate(-300px,0)', ESNAP), (.5, 'transform:translate(-10px,0)')]
    for k in KNOCKS:
        hk += [(k - .06, 'transform:translate(-14px,0)', 'cubic-bezier(.5,0,1,.6)'), (k, 'transform:translate(0,0)', ESOFT), (k + .05, 'transform:translate(-14px,0)')]
    hk += [(2.62, 'transform:translate(-14px,0)', EIO), (2.9, 'transform:translate(-300px,0)')]
    hk.sort(key=lambda x: x[0])
    A('.hk6', K(hk, T))
    imp = []
    for k in KNOCKS:
        c = uid('im')
        imp.append('<g transform="translate(164,600)"><g class="%s"><path d="M10,-22 l12,-10 M14,0 l16,0 M10,22 l12,10" stroke="%s" stroke-width="3.5" stroke-linecap="round"/></g></g>' % (c, CREAM2))
        A('.' + c, K([(0, 'opacity:0;transform:scale(.6)'), (k, 'opacity:0;transform:scale(.6)', ESOFT), (k + .02, 'opacity:1;transform:scale(1)'), (k + .14, 'opacity:0;transform:scale(1.3)')], T))
    s.append(''.join(imp))
    s.append('</g>')
    zf = [(0, 270, 560, 1.0, 270, 560, 0)]
    for k in KNOCKS:
        zf += [(k, 270, 560, 1.0 + .02 * (k / T), 270, 560, 0, 'ease-out'), (k + .04, 270, 560, 1.0 + .02 * (k / T), 266, 562, .3), (k + .1, 270, 560, 1.0 + .02 * (k / T), 270, 560, 0)]
    zf += [(T, 270, 560, 1.07, 270, 560, 0)]
    zf.sort(key=lambda x: x[0])
    # zoom ciągły zamiast skokowego – nadpisz skale liniową interpolacją
    zz = []
    for x in zf:
        z = 1.0 + .07 * (x[0] / T)
        zz.append((x[0], x[1], x[2], z) + x[4:])
    cam('cm6', T, zz, 'ease-in-out')
    out = ['<g class="cm6">'] + s + ['</g>', vignette2(.32)]
    # dymki
    b1, w1, h1 = bubble(['Mamooo?'], fill=BEIGE, stroke=BROWN, fs=24, tail=(30, 34))
    out.append(place_bubble(b1, 100, 520, T, .76, pop_dur=.3))
    b2, w2, h2 = bubble(['Mamo, gdzie…?'], fill=CREAM2, stroke=BROWN, fs=24, tail=(-40, 34))
    out.append(place_bubble(b2, 400, 676, T, 1.74, pop_dur=.3))
    b3, w3, h3 = bubble(['?!'], fill=BEIGE, stroke=BROWN, fs=26, tail=(26, 30))
    out.append(place_bubble(b3, 92, 690, T, 2.3, pop_dur=.26))
    # plansza
    cc = uid('cd6')
    out.append('<g class="%s">%s</g>' % (cc, card(30, 114, 480, 218, fill=CREAM2, edge=SAGE)))
    card_in(cc, T, .08, 'drop')
    out.append('<g class="t6">%s%s</g>' % (stext('Odpoczywaj', 270, 194, 56), stext('w łazience.', 270, 250, 56)))
    S('.t6{transform-origin:270px 200px}')
    A('.t6', K([(0, 'opacity:0;transform:scaleY(0)'), (.3, 'opacity:1;transform:scaleY(0)', 'cubic-bezier(.3,.6,.4,1)'), (.52, 'opacity:1;transform:scaleY(1.04)', ESOFT), (.62, 'opacity:1;transform:scaleY(1)')], T))
    out.append('<g class="t6b">%s</g>' % mtext('Aż 4 minuty!', 270, 302, 32, col=BROWN, weight=800))
    S('.t6b{transform-origin:270px 292px}')
    A('.t6b', K([(0, 'opacity:0;transform:scale(.6)'), (1.0, 'opacity:0;transform:scale(.6)', EBOUNCE), (1.22, 'opacity:1;transform:scale(1)')], T))
    out.append(badge(5, 270, 114, T, .14))
    out.append(check(474, 326, T, 2.5))
    # wejście: żaluzje się otwierają
    bl = ''
    for i in range(8):
        c = uid('bl')
        bl += '<rect x="-10" y="%s" width="560" height="122" fill="%s" class="%s"/>' % (i * 120, SAGE, c)
        S('.%s{transform-origin:0 %spx}' % (c, i * 120 + 122))
        A('.' + c, K([(0, 'transform:scaleY(1)'), (.02 + i * .02, 'transform:scaleY(1)', 'cubic-bezier(.6,0,.4,1)'), (.22 + i * .02, 'transform:scaleY(0)')], T))
    out.append(bl)
    return ''.join(out), T

# ================= SCENA 7: „…serio?” (17–19 s) =================
def sc_serio():
    T = 2.0; s = []
    inst = 'pA7'
    cx, sc = 270, 2.3
    feet = 452 + (712 - 131) * sc
    s.append('<g class="c7">')
    s.append('<rect x="-400" y="-400" width="1340" height="1760" fill="#EDE7E1"/>')
    s.append('<rect x="-60" y="140" width="190" height="300" rx="8" fill="#F4EFE8"/><path d="M35,140 V440 M-60,280 H130" stroke="#E2D9D0" stroke-width="7"/>')
    s.append('<rect x="400" y="560" width="200" height="12" fill="#E2D9D0"/>')
    # nakładka brwi (lewa brew postaci, prawa na ekranie) – w hierarchii głowy
    brow = ('<g class="fig figA %s ghost"><g class="body"><g class="headWrap"><g class="tilt">' % inst +
            '<path d="M116,106.5 H145.5 V122.4 Q131,115.8 119.4,119.4 L116,119.4 Z" fill="#f1caa9"/>'
            '<g class="brw7"><path d="M142,119 Q131,111.5 119,115.5 L119,118 Q131,115 140.5,121.5 Z" fill="#9c7a52"/></g>'
            '</g></g></g></g>')
    s.append(FIG('A', inst, cx, feet, sc, post=brow))
    s.append('</g>')
    S('.brw7{transform-origin:131px 117px}')
    A('.brw7', K([(0, 'transform:translateY(0) rotate(0deg)'), (1.0, 'transform:translateY(0) rotate(0deg)', 'cubic-bezier(.3,0,.2,1)'), (1.28, 'transform:translateY(-6px) rotate(-7deg)'), (T, 'transform:translateY(-6px) rotate(-7deg)')], T))
    head(inst, T, [(0, -6, -3, 2), (.3, -6, -3, 2), (1.0, 2, 1, 0, 'cubic-bezier(.4,0,.2,1)'), (1.3, 3, 1, -1), (T, 3, 1, -1)])
    pupils(inst, T, [(0, -3.4), (.35, -3.4), (.95, 0), (T, 0)], 'cubic-bezier(.4,0,.2,1)')
    S('.fig.%s .smile{transform-origin:110px 168px}' % inst)
    A('.fig.%s .smile' % inst, K([(0, 'transform:scale(.95) rotate(0deg)'), (1.2, 'transform:scale(.95) rotate(0deg)', EIO), (1.5, 'transform:scale(1.04,1.08) rotate(-5deg) translateY(-1px)'), (T, 'transform:scale(1.04,1.08) rotate(-5deg) translateY(-1px)')], T))
    A('.fig.%s .eyes' % inst, K([(0, 'transform:scaleY(1)'), (1.55, 'transform:scaleY(1)'), (1.62, 'transform:scaleY(.1)'), (1.7, 'transform:scaleY(.86)'), (T, 'transform:scaleY(.86)')], T))
    A('.fig.%s .tilt,.fig.%s .tiltBack' % (inst, inst), K([(0, 'transform:none'), (T, 'transform:none')], T))
    A('.fig.%s .body' % inst, K([(0, 'transform:translateY(0)'), (T, 'transform:translateY(-3px)')], T))
    cam('cm7', T, [(0, 270, 452, 1.0, 270, 452, 0), (T, 280, 440, 1.09, 270, 452, 0)], 'cubic-bezier(.3,0,.5,1)')
    out = ['<g class="cm7">'] + s + ['</g>', vignette2(.5)]
    out.append('<g class="t7"><text x="270" y="172" font-size="68" text-anchor="middle" class="serif" fill="%s">…serio?</text></g>' % INK)
    A('.t7', K([(0, 'opacity:0'), (.5, 'opacity:0', 'ease-out'), (.74, 'opacity:1')], T))
    # wyjście: do kremu
    out.append('<rect width="540" height="960" fill="#F4EFE8" class="fo7" pointer-events="none"/>')
    A('.fo7', K([(0, 'opacity:0'), (1.8, 'opacity:0', 'ease-in'), (T, 'opacity:1')], T))
    return ''.join(out), T

# ================= SCENA 8: Prawdziwy odpoczynek (19–22 s) =================
def sc_prawdziwy():
    T = 3.0; s = []
    iA, iB = 'pA8', 'pB8'
    sc = .98; feet = 992
    cxA, cxB = 160, 386
    s.append('<g class="c8">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="url(#skyB)"/>')
    s.append('<circle cx="420" cy="520" r="260" fill="url(#sunG)" class="sun8"/>')
    S('.sun8{transform-box:fill-box;transform-origin:center}')
    A('.sun8', K([(0, 'opacity:.4;transform:scale(.8)'), (1.4, 'opacity:1;transform:scale(1)'), (T, 'opacity:1;transform:scale(1.04)')], T))
    for i, (y, amp, n, seed, col, t0, px) in enumerate([(560, 40, 7, 31, '#C9D5CF', .05, 8), (620, 34, 8, 32, SAGE, .18, 18), (700, 24, 9, 33, DKG, .32, 30)]):
        c, p = uid('mt'), uid('px')
        extra = ''
        if i == 1:
            extra = ''.join(tree(x, 650 + R.uniform(-8, 10), R.uniform(54, 80), cc) for x, cc in zip(range(-40, 620, 38), itertools.cycle([RUST, MUST, DKG, '#c47a3c', MUST, DKG])))
        s.append('<g class="%s"><g class="%s">%s%s</g></g>' % (p, c, ridge(-100, 660, y, amp, n, seed, 1100, col), extra))
        A('.' + c, K([(0, 'transform:translateY(220px)'), (t0, 'transform:translateY(220px)', 'cubic-bezier(.2,.8,.2,1)'), (t0 + .9, 'transform:translateY(0)')], T))
        A('.' + p, K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(%spx)' % (-px))], T, 'ease-in-out'))
    # mgiełka
    s.append('<g class="mist8"><rect x="-100" y="600" width="760" height="40" rx="20" fill="#F4F2EF" opacity=".5"/></g>')
    A('.mist8', K([(0, 'transform:translateX(-20px)'), (T, 'transform:translateX(30px)')], T, 'ease-in-out'))
    # postacie
    s.append(FIG('B', iB, cxB, feet, sc, post=ghost('B', iB, '', '<g class="mr8">%s</g>' % mic(), arm='R')))
    s.append(FIG('A', iA, cxA, feet, sc))
    # barierka
    rail = 736
    s.append('<rect x="-100" y="%s" width="740" height="18" rx="4" fill="#8a6a56"/><rect x="-100" y="%s" width="740" height="5" fill="#a5826c"/>' % (rail, rail))
    s.append(''.join('<rect x="%s" y="%s" width="16" height="300" fill="#7a5c4a"/>' % (x, rail + 18) for x in range(-20, 600, 70)))
    s.append('<rect x="-100" y="%s" width="740" height="14" fill="#8a6a56"/>' % (rail + 120))
    # mikrofon odłożony na barierkę
    rel = 1.0
    H = (178, 446)
    mw = L2W(cxB, feet, sc, H[0], H[1])
    s.append('<g transform="translate(%s,%s) scale(%s)"><g class="mw8"><g transform="rotate(78)">%s</g></g></g>' % (f(mw[0]), f(mw[1]), f(sc), mic(fingers=False)))
    A('.mw8', K([(0, 'opacity:0'), (rel, 'opacity:0', 'steps(1,end)'), (rel + .01, 'opacity:1')], T, 'linear'))
    A('.mr8', K([(0, 'opacity:1;transform:rotate(0deg)'), (.35, 'opacity:1;transform:rotate(0deg)', EIO), (rel - .04, 'opacity:1;transform:rotate(78deg)'), (rel, 'opacity:1;transform:rotate(78deg)', 'steps(1,end)'), (rel + .01, 'opacity:0;transform:rotate(78deg)')], T))
    # liście (≤ 6)
    for i in range(5):
        c = uid('lf')
        x0 = [22, 512, 36, 500, 18][i]; t0 = .3 + i * .45
        s.append('<g transform="translate(%s,-30)"><g class="%s"><use href="#leaf" transform="scale(1.2)" fill="%s"/></g></g>' % (f(x0), c, [RUST, MUST, '#c47a3c'][i % 3]))
        A('.' + c, K([(0, 'opacity:0;transform:translate(0,0) rotate(0deg)'), (t0, 'opacity:1;transform:translate(0,0) rotate(0deg)', 'cubic-bezier(.4,.1,.6,.9)'), (min(T, t0 + 2.4), 'opacity:1;transform:translate(%spx,%spx) rotate(220deg)' % (R.randint(-12, 12), 1000 if t0 + 2.4 <= T else int(1000 * (T - t0) / 2.4)))], T))
    s.append('</g>')
    rig(iB, 'B', T, [(0, {'R': (150, 300), 'L': (60, 452)}), (.35, {'R': (150, 300)}), (rel - .04, H, EIO) if False else (rel - .04, {'R': H}, EIO), (rel + .12, {'R': H}), (rel + .5, {'R': (166, 452)}, EIO),
                     (1.6, {'L': (60, 452)}), (1.95, {'L': (20, 420)}, ESOFT), (T, {'L': (22, 418)})])
    head(iB, T, [(0, 0, 0, 0), (.4, 4, 2, 2), (rel, 5, 2, 3), (1.5, 0, 0, 0), (1.85, -7, -4, 0), (T, -8, -4, 0)])
    pupils(iB, T, [(0, 0), (.4, 2.5), (1.1, 2.5), (1.4, 0), (1.75, -3.2), (T, -3.2)])
    A('.fig.%s .smile' % iB, K([(0, 'transform:scale(1)'), (1.8, 'transform:scale(1)'), (2.1, 'transform:scale(1.12,1.25)'), (T, 'transform:scale(1.12,1.25)')], T))
    rig(iA, 'A', T, [(0, {'R': (158, 452), 'L': (64, 452)}), (1.7, {'R': (158, 452)}), (2.1, {'R': (196, 420)}, ESOFT), (T, {'R': (198, 418)})])
    head(iA, T, [(0, 0, 0, 0), (1.2, 0, 0, 0), (1.6, 7, 4, 0), (2.2, 9, 5, 2), (T, 9, 5, 2)])
    pupils(iA, T, [(0, 0), (1.2, 0), (1.5, 3.2), (T, 3.2)])
    A('.fig.%s .smile' % iA, K([(0, 'transform:scale(1)'), (1.9, 'transform:scale(1)'), (2.2, 'transform:scale(1.12,1.25)'), (T, 'transform:scale(1.12,1.25)')], T))
    cam('cm8', T, [(0, 270, 560, 1.06, 270, 560, 0), (T, 270, 540, 1.0, 270, 548, 0)], 'cubic-bezier(.3,0,.5,1)')
    out = ['<g class="cm8">'] + s + ['</g>']
    out.append('<rect width="540" height="960" fill="url(#warm)" pointer-events="none"/>')
    out.append(vignette2(.3))
    out.append('<g class="t8a">%s</g>' % mtext('Albo po prostu:', 270, 150, 28, col=BROWN))
    A('.t8a', K([(0, 'opacity:0;transform:translateY(10px)'), (.42, 'opacity:0;transform:translateY(10px)', ESNAP), (.66, 'opacity:1;transform:translateY(0)')], T))
    out.append('<g class="t8b"><text x="270" y="212" font-size="58" text-anchor="middle" class="serif" fill="%s">3 dni tylko</text><text x="270" y="272" font-size="58" text-anchor="middle" class="serif" fill="%s">dla siebie.</text></g>' % (INK, INK))
    A('.t8b', K([(0, 'opacity:0;filter:blur(8px);transform:translateY(8px)'), (.9, 'opacity:0;filter:blur(8px);transform:translateY(8px)', ESOFT), (1.16, 'opacity:1;filter:blur(0px);transform:translateY(0)')], T))
    # wejście: z kremu
    out.append('<rect width="540" height="960" fill="#F4EFE8" class="fi8" pointer-events="none"/>')
    A('.fi8', K([(0, 'opacity:1'), (.45, 'opacity:0')], T, 'cubic-bezier(.3,0,.3,1)'))
    # wyjście: iris
    out.append('<circle cx="270" cy="520" r="640" fill="%s" class="iris8"/>' % CREAM)
    S('.iris8{transform-origin:270px 520px}')
    A('.iris8', K([(0, 'transform:scale(0)'), (2.66, 'transform:scale(0)', 'cubic-bezier(.6,0,.3,1)'), (T, 'transform:scale(1)')], T))
    return ''.join(out), T

# ================= SCENA 9: Logo + CTA (22–25 s) =================
def sc_logo():
    T = 3.0; s = []
    s.append('<g class="c9">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="%s"/>' % CREAM)
    s.append('<g class="lp9"><rect x="-100" y="-100" width="740" height="1160" fill="%s"/><g transform="translate(270,640)"><g class="ray9">%s</g></g></g>' % (BEIGE, sunburst(28, 1200, '#EBD9CF')))
    A('.lp9', K([(0, 'opacity:0'), (2.35, 'opacity:0', EIO), (T, 'opacity:1')], T))
    A('.ray9', K([(0, 'transform:rotate(-10deg)'), (T, 'transform:rotate(0deg)')], T, 'cubic-bezier(.3,0,.6,1)'))
    s.append('<ellipse cx="270" cy="330" rx="380" ry="300" fill="url(#halo6)"/>')
    # góry – linia (Beskidy)
    s.append('<path class="ln9" pathLength="1" d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>' % (smooth([(60, 760), (130, 712), (180, 736), (260, 676), (330, 730), (400, 700), (480, 744)]), SAGE))
    S('.ln9{stroke-dasharray:1}')
    A('.ln9', K([(0, 'stroke-dashoffset:1'), (.2, 'stroke-dashoffset:1', EIO), (1.3, 'stroke-dashoffset:0')], T))
    # logo: napis (odsłaniany) + hasło
    s.append('<clipPath id="cp9"><rect class="w9" x="30" y="250" width="480" height="70"/></clipPath>')
    s.append('<g clip-path="url(#cp9)"><use href="#logoWord" transform="translate(270,286) scale(.68)" style="color:%s"/></g>' % DKG)
    S('.w9{transform-origin:30px 0}')
    A('.w9', K([(0, 'transform:scaleX(.04)', 'cubic-bezier(.4,0,.25,1)'), (.6, 'transform:scaleX(1)')], T))
    s.append('<g class="tg9"><use href="#logoTag" transform="translate(270,342) scale(.45)" style="color:%s"/></g>' % BROWN)
    A('.tg9', K([(0, 'opacity:0;transform:translateY(10px)'), (.45, 'opacity:0;transform:translateY(10px)', ESNAP), (.72, 'opacity:1;transform:translateY(0)')], T))
    s.append('<g class="d9">%s</g>' % mtext('5–7.11 · Beskidy · 20 miejsc', 270, 446, 26, weight=800))
    A('.d9', K([(0, 'opacity:0;transform:translateY(12px)'), (.85, 'opacity:0;transform:translateY(12px)', ESNAP), (1.1, 'opacity:1;transform:translateY(0)')], T))
    s.append('<g transform="translate(270,556)"><g class="bt9"><rect x="-166" y="-46" width="332" height="92" rx="46" fill="#3a2a20" opacity=".15" transform="translate(0,5)"/>'
             '<rect x="-166" y="-46" width="332" height="92" rx="46" fill="%s"/>' % BROWN +
             '<text x="0" y="-4" font-size="32" text-anchor="middle" fill="%s" style="font-weight:800">Zapisz się →</text>' % CREAM2 +
             '<text x="0" y="28" font-size="22" text-anchor="middle" fill="#F1E2D3" style="font-weight:700;letter-spacing:.03em">shebalance.pl</text>'
             '<g clip-path="url(#btnClip)"><rect class="bsh9" x="-60" y="-60" width="40" height="120" fill="url(#shine)" transform="rotate(18)"/></g></g></g>')
    S('.bt9{transform-origin:0 0}')
    A('.bt9', K([(0, 'opacity:0;transform:scale(.6)'), (1.1, 'opacity:0;transform:scale(.6)', EBOUNCE), (1.42, 'opacity:1;transform:scale(1)'), (2.0, 'opacity:1;transform:scale(1)', 'ease-in-out'), (2.2, 'opacity:1;transform:scale(1.04)'), (2.4, 'opacity:1;transform:scale(1)')], T))
    A('.bsh9', K([(0, 'transform:rotate(18deg) translateX(-180px)'), (1.5, 'transform:rotate(18deg) translateX(-180px)', EIO), (2.0, 'transform:rotate(18deg) translateX(260px)')], T))
    for x, y, d in [(78, 236, .2), (466, 214, .8), (452, 380, .5), (90, 420, 1.1)]:
        s.append(sparkle(x, y, .9, MUST, d, 1.8))
    s.append('</g>')
    cam('cm9', T, [(0, 270, 470, 1.05, 270, 470, 0), (T, 270, 470, 1.0, 270, 470, 0)], 'cubic-bezier(.3,0,.4,1)')
    return '<g class="cm9">' + ''.join(s) + '</g>' + vignette2(.25), T

SCENES = [('studio', sc_studio, BEIGE), ('krok1', sc_krok1, DKG), ('krok2', sc_krok2, SAGE), ('krok3', sc_krok3, CREAM), ('krok4', sc_krok4, BEIGE),
          ('krok5', sc_krok5, SAGE), ('serio', sc_serio, CREAM), ('prawdziwy', sc_prawdziwy, CREAM), ('logo', sc_logo, CREAM)]

def build():
    parts, sj = [], []
    t = 0; starts = []
    for sid, fn, bg in SCENES:
        svg, T = fn()
        parts.append('<g class="scene" data-s="%s">%s</g>' % (sid, svg))
        sj.append("{id:'%s',d:%s,bg:'%s'}" % (sid, f(T), bg)); starts.append(t); t += T
    tpl = (HERE / 'szablon.html').read_text(encoding='utf-8')
    defs = DEFS_EXTRA + '<clipPath id="btnClip"><rect x="-166" y="-46" width="332" height="92" rx="46"/></clipPath>'
    html = (tpl.replace('@@CSS@@', '\n'.join(CSS)).replace('@@DEFS@@', defs)
            .replace('@@SCENES@@', '\n'.join(parts)).replace('@@SCJS@@', ','.join(sj)))
    OUT.write_text(html, encoding='utf-8')
    print('ok', OUT, len(html), 'reguł', len(CSS), 'czas', t, 'starty', starts)

if __name__ == '__main__':
    build()
