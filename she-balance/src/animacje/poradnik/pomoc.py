# -*- coding: utf-8 -*-
# Pomocnicze funkcje (kopia z kawa/gen.py – IK, keyframes, dymki, kuchnia) dla generatora „Poradnik”.
import math, random, pathlib, itertools, json

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / 'poradnik.html'
ROOT = HERE.parent.parent.parent
R = random.Random(20261107)

SAGE, DKG, BEIGE, CREAM, CREAM2, BROWN = '#A4B8B0', '#58756C', '#E3CCC1', '#F2EFEB', '#F4F2EF', '#6E5446'
RUST, MUST, INK = '#B5582F', '#D4A23A', '#333'
SKIN, SKIN2 = '#f2c9aa', '#e9b996'
EIN = 'cubic-bezier(.2,.9,.25,1.05)'
EOUT = 'cubic-bezier(.6,0,.8,.2)'
EIO = 'cubic-bezier(.45,0,.2,1)'
ESOFT = 'cubic-bezier(.3,0,.2,1)'
ESNAP = 'cubic-bezier(.2,.8,.2,1)'

CSS = []
_ctr = itertools.count()

def f(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')

def K(frames, T, ease=EIO, it='1', fill='both'):
    """frames = [(t, 'props') | (t, 'props', 'easing-od-tej-klatki')], czasy w s od początku sceny."""
    name = 'k%d' % next(_ctr)
    fr = sorted(frames, key=lambda x: x[0])
    if fr[0][0] > 0: fr = [(0,) + tuple(fr[0][1:2])] + fr
    if fr[-1][0] < T - 1e-6: fr = fr + [(T, fr[-1][1])]
    ks = []
    for x in fr:
        body = x[1]
        if len(x) > 2: body += ';animation-timing-function:' + x[2]
        ks.append('%.3f%%{%s}' % (min(100, max(0, x[0] / T * 100)), body))
    CSS.append('@keyframes %s{%s}' % (name, ''.join(ks)))
    return '%s %.3fs %s 0s %s %s' % (name, T, ease, it, fill)

def A(sel, *anims, extra=''):
    sels = ','.join('.active ' + s.strip() for s in sel.split(','))
    # części postaci mają domyślne animacje z fig.css/baza.css (oddech, mruganie, tilt…). Gdyby reguła .active je podmieniała,
    # zapauzowana stara animacja zostaje „osierocona” i wygrywa – więc poza aktywną sceną wyłączamy je całkiem.
    figp = [s.strip() for s in sel.split(',') if '.fig' in s]
    if figp:
        CSS.append('%s{animation:none}' % ','.join(figp))
    CSS.append('%s{animation:%s%s}' % (sels, ','.join(anims), extra))

def S(css): CSS.append(css)
def uid(p='e'): return '%s%d' % (p, next(_ctr))

def smooth(pts, closed=False):
    P = [pts[-1]] + pts + pts[:2] if closed else [pts[0]] + pts + [pts[-1]]
    d = 'M%s,%s' % (f(pts[0][0]), f(pts[0][1]))
    n = len(pts) if closed else len(pts) - 1
    for i in range(1, n + 1):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += ' C%s,%s %s,%s %s,%s' % tuple(map(f, (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])))
    return d + (' Z' if closed else '')

def ridge(x0, x1, y, amp, n, seed, bottom, fill, extra=''):
    r = random.Random(seed)
    pts = [(x0 + (x1 - x0) * i / n, y + r.uniform(-amp, amp)) for i in range(n + 1)]
    d = smooth(pts) + ' L%s,%s L%s,%s Z' % (f(x1), f(bottom), f(x0), f(bottom))
    return '<path d="%s" fill="%s" %s/>' % (d, fill, extra)

def vis(t0, t1, T, fade=.2, dy=0, ease_in=ESNAP):
    """widoczność: pojawia się w t0 (fade), znika w t1 (fade); dy = wjazd z dołu."""
    fr = [(0, 'opacity:0;transform:translateY(%dpx)' % dy), (t0, 'opacity:0;transform:translateY(%dpx)' % dy, ease_in),
          (t0 + fade, 'opacity:1;transform:translateY(0)')]
    if t1 is not None and t1 < T:
        fr += [(t1 - fade, 'opacity:1;transform:translateY(0)', EOUT), (t1, 'opacity:0;transform:translateY(0)')]
    return K(fr, T)

# ================= postacie, IK i rekwizyty =================
SH = {('A', 'R'): (168, 238), ('A', 'L'): (52, 238), ('B', 'R'): (170, 238), ('B', 'L'): (50, 238)}
L1, L2 = 104.0, 110.0
REST = {'armL': 7, 'foreL': -6, 'armR': -7, 'foreR': 6}

def ik(who, side, H, elbow='down'):
    Sx, Sy = SH[(who, side)]
    Dx, Dy = H[0] - Sx, H[1] - Sy
    d = max(10, min(math.hypot(Dx, Dy), L1 + L2 - .5))
    phi = math.degrees(math.atan2(-Dx, Dy))
    al = math.degrees(math.acos(max(-1, min(1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)))))
    sols = []
    for a1 in (phi + al, phi - al):
        r = math.radians(a1); E = (Sx - L1 * math.sin(r), Sy + L1 * math.cos(r))
        psi = math.degrees(math.atan2(-(H[0] - E[0]), H[1] - E[1]))
        a2 = (psi - a1 + 180) % 360 - 180
        sols.append((a1, a2, E))
    if elbow == 'down': s = max(sols, key=lambda q: q[2][1])
    elif elbow == 'out': s = max(sols, key=lambda q: q[2][0] * (1 if side == 'R' else -1))
    else: s = max(sols, key=lambda q: -q[2][0] * (1 if side == 'R' else -1))
    a1 = (s[0] + 180) % 360 - 180
    return a1, s[1]

def unwrap(vals):
    out = [vals[0]]
    for v in vals[1:]:
        while v - out[-1] > 180: v -= 360
        while v - out[-1] < -180: v += 360
        out.append(v)
    return out

def rig(inst, who, T, frames, ease=EIO):
    """Wspólna oś czasu dla stawów rąk. frames: [(t, {'R':(x,y)|'L':(x,y)|'armR':deg..., 'eR':'down'}, easing?)].
    Zwraca nazwy klas kontr-rotacji dłoni: .<inst>cR / .<inst>cL (rekwizyty stoją pionowo)."""
    cur = dict(REST); rows = []
    for fr in frames:
        t, d = fr[0], fr[1]; e = fr[2] if len(fr) > 2 else ease
        for side in 'RL':
            if side in d:
                a1, a2 = ik(who, side, d[side], d.get('e' + side, 'down'))
                cur['arm' + side], cur['fore' + side] = a1, a2
        for j in ('armL', 'foreL', 'armR', 'foreR'):
            if j in d: cur[j] = d[j]
        rows.append((t, dict(cur), e))
    out = {}
    for j in ('armL', 'foreL', 'armR', 'foreR'):
        out[j] = unwrap([r[1][j] for r in rows])
    for side in 'RL':
        out['c' + side] = [-(a + b) for a, b in zip(out['arm' + side], out['fore' + side])]
    for j in ('armL', 'foreL', 'armR', 'foreR'):
        A('.fig.%s .%s' % (inst, j), K([(r[0], 'transform:rotate(%sdeg)' % f(v), r[2]) for r, v in zip(rows, out[j])], T))
    for side in 'RL':
        A('.%sc%s' % (inst, side), K([(r[0], 'transform:rotate(%sdeg)' % f(v), r[2]) for r, v in zip(rows, out['c' + side])], T))
    return out

def head(inst, T, frames, ease=EIO):
    """frames: (t, rot, dx, dy[, easing]) – obrót głowy wokół szyi."""
    A('.fig.%s .headWrap' % inst, K([(x[0], 'transform:translate(%spx,%spx) rotate(%sdeg)' % (f(x[2]), f(x[3]), f(x[1]))) + ((x[4],) if len(x) > 4 else ()) for x in frames], T, ease))

def pupils(inst, T, frames, ease=EIO):
    A('.fig.%s .pupils' % inst, K([(x[0], 'transform:translateX(%spx)' % f(x[1])) for x in frames], T, ease))

def FIG(who, cls, cx, feet, s, wrap='', pre='', post=''):
    tx, ty = cx - 110 * s, feet - 712 * s
    return '<g transform="translate(%s,%s) scale(%s)"><g class="%s">%s/*FIG_%s:%s*/%s</g></g>' % (f(tx), f(ty), f(s), wrap, pre, who, cls, post)

def L2W(cx, feet, s, lx, ly):
    return (cx - 110 * s + lx * s, feet - 712 * s + ly * s)

def ghost(who, inst, extra, content, arm=None):
    """„Duch” postaci: ta sama hierarchia klas → rekwizyt rusza się razem z ciałem/dłonią."""
    cls = 'fig fig%s %s %s ghost' % (who, inst, extra)
    if arm is None:
        return '<g class="%s"><g class="body">%s</g></g>' % (cls, content)
    hx = SH[(who, arm)][0]
    return ('<g class="%s"><g class="body"><g class="arm%s"><g class="fore%s"><g transform="translate(%s,452)"><g class="%sc%s">%s</g></g></g></g></g></g>'
            % (cls, arm, arm, hx, inst, arm, content))

def steam_paths(cls, n=3, h=44, w=7, sw=3.2, col='#fff', spread=11, halo='#9fb3aa'):
    s = ''
    for i in range(n):
        x = (i - (n - 1) / 2) * spread
        d = 'M%s,0 q-%s,-%s 0,-%s q%s,-%s 0,-%s' % (f(x), f(w), f(h / 4), f(h / 2), f(w), f(h / 4), f(h / 2))
        s += ('<g class="%s" style="animation-delay:-%ss"><path d="%s" fill="none" stroke="%s" stroke-opacity=".45" stroke-width="%s" stroke-linecap="round"/>'
              '<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/></g>' % (cls, f(i * .55), d, halo, f(sw + 2.6), d, col, f(sw)))
    return s

S('.stm{animation:stm 1.6s ease-in-out infinite;opacity:0}'
  '@keyframes stm{0%{opacity:0;transform:translateY(4px) scaleY(.8)}35%{opacity:.95}100%{opacity:0;transform:translateY(-26px) scaleY(1.1)}}')

R_HOLD, R_SIP = (184, 230), (158, 236)   # kubek przy barku / przy ustach – łokieć w dół, po prawej

def mug_hand(steam_cls='', skin=SKIN, col='#F4F2EF', band=SAGE):
    """Kubek trzymany w dłoni; (0,0) = środek dłoni (układ lokalny postaci)."""
    return ('<g transform="scale(1.22)"><g transform="translate(-4,-6)">'
            '<path d="M-19,-34 L19,-34 L17,4 Q16,10 10,10 L-10,10 Q-16,10 -17,4 Z" fill="%s" stroke="#d9cfc2" stroke-width="1.2"/>'
            '<path d="M18,-24 Q32,-24 30,-11 Q28,-1 16,-2" fill="none" stroke="%s" stroke-width="5.5"/>'
            '<path d="M-18.2,-14 L18.2,-14 L17.6,-6 L-17.6,-6 Z" fill="%s"/>'
            '<ellipse cx="0" cy="-34" rx="19" ry="4.6" fill="#7a4a30"/>'
            '<ellipse cx="0" cy="-34" rx="19" ry="4.6" fill="none" stroke="#efe6da" stroke-width="1.4"/>'
            '<g transform="translate(0,-40)" class="%s">%s</g></g>'
            '<ellipse cx="-2" cy="2" rx="9" ry="10" fill="%s"/><ellipse cx="-12" cy="-6" rx="4.5" ry="7" fill="%s"/></g>'
            % (col, col, band, steam_cls, steam_paths('stm'), skin, skin))

# ================= dymki =================
def tw(text, fs, k=.6):
    return len(text) * fs * k

def bubble(lines, fill=CREAM2, stroke=BROWN, fs=20, tail=None, col=INK, weight=800, k=.6, padx=16, pady=11, upper=False, font='Mulish', lh=1.16, rx=None):
    w = max(tw(l, fs, k) for l in lines) + 2 * padx
    h = len(lines) * fs * lh + 2 * pady
    rx = rx if rx is not None else min(h / 2, 22)
    s = '<g>'
    tailp = ''
    if tail:
        tx, ty = tail
        bx = max(-w / 2 + rx, min(w / 2 - rx, tx * .35))
        if abs(ty) >= abs(tx) * .5 or True:
            by = h / 2 if ty > 0 else -h / 2
            tailp = 'M%s,%s L%s,%s L%s,%s Z' % (f(bx - 9), f(by * .8), f(tx), f(ty), f(bx + 9), f(by * .8))
    s += '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="#3a2a20" opacity=".13" transform="translate(3,4)"/>' % (f(-w / 2), f(-h / 2), f(w), f(h), f(rx))
    if tailp: s += '<path d="%s" fill="%s" stroke="%s" stroke-width="1.6" stroke-linejoin="round"/>' % (tailp, fill, stroke)
    s += '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (f(-w / 2), f(-h / 2), f(w), f(h), f(rx), fill, stroke)
    if tailp: s += '<path d="M%s,%s L%s,%s" stroke="%s" stroke-width="3"/>' % (f(max(-w / 2 + rx, min(w / 2 - rx, tail[0] * .35)) - 7.5), f((h / 2 if tail[1] > 0 else -h / 2) * .99), f(max(-w / 2 + rx, min(w / 2 - rx, tail[0] * .35)) + 7.5), f((h / 2 if tail[1] > 0 else -h / 2) * .99), fill)
    for i, l in enumerate(lines):
        y = -h / 2 + pady + fs * lh * i + fs * .82
        s += '<text x="0" y="%s" font-size="%s" text-anchor="middle" style="font-family:%s;font-weight:%s" fill="%s">%s</text>' % (f(y), fs, font, weight, col, l)
    return s + '</g>', w, h

def place_bubble(svg, x, y, T, t0, pile=None, pop_dur=.32, cls='', push=None):
    """dymek w (x,y): pop-in w t0 (t0<0 → widoczny od początku); pile=(t1,dx,dy,scale,op) – odsunięcie na stos."""
    c = uid('bb')
    if t0 < 0:
        fr = [(0, 'opacity:1;transform:translate(0,0) scale(1) rotate(0deg)')]
    else:
        fr = [(0, 'opacity:0;transform:translate(0,0) scale(.2) rotate(-6deg)'),
              (t0, 'opacity:0;transform:translate(0,0) scale(.2) rotate(-6deg)', 'cubic-bezier(.2,.8,.3,1)'),
              (t0 + pop_dur * .65, 'opacity:1;transform:translate(0,0) scale(1.05) rotate(1deg)', ESOFT),
              (t0 + pop_dur, 'opacity:1;transform:translate(0,0) scale(1) rotate(0deg)')]
    if pile:
        t1, dx, dy, sc, op = pile
        fr += [(t1, 'opacity:1;transform:translate(0,0) scale(1) rotate(0deg)', EIO), (t1 + .35, 'opacity:%s;transform:translate(%spx,%spx) scale(%s) rotate(0deg)' % (f(op), f(dx), f(dy), f(sc)))]
    if push:
        p0, p1, dx, dy = push
        fr += [(p0, 'opacity:1;transform:translate(0,0) scale(1) rotate(0deg)', 'cubic-bezier(.6,0,.4,1)'), (p1, 'opacity:1;transform:translate(%spx,%spx) scale(1.1) rotate(0deg)' % (f(dx), f(dy)))]
    A('.' + c, K(fr, T))
    return '<g transform="translate(%s,%s)"><g class="%s %s">%s</g></g>' % (f(x), f(y), c, cls, svg)

# ================= kuchnia =================
def kitchen(counter_y, door=None, window=(40, 250, 190, 290), shelf=(370, 330), extra_counter='', micro=None, wall_top=0):
    s = []
    s.append('<rect x="-400" y="-400" width="1340" height="1760" fill="%s"/>' % CREAM)
    s.append('<rect x="-400" y="%s" width="1340" height="%s" fill="url(#kWall)"/>' % (counter_y - 520, 520))
    # okno z porannym światłem
    wx, wy, ww, wh = window
    s.append('<g>'
             '<rect x="%s" y="%s" width="%s" height="%s" rx="6" fill="url(#kDawn)"/>' % (f(wx), f(wy), f(ww), f(wh)) +
             ridge(wx, wx + ww, wy + wh * .62, 8, 5, 3, wy + wh, '#E3CCC1', 'opacity=".9"') +
             ''.join('<rect x="%s" y="%s" width="%s" height="%s" fill="#d9c2b5"/>' % (f(wx + 10 + i * ww / 5), f(wy + wh * (.55 + .12 * (i % 2))), f(ww / 7), f(wh)) for i in range(5)) +
             '<rect x="%s" y="%s" width="%s" height="%s" rx="6" fill="none" stroke="%s" stroke-width="9"/>' % (f(wx), f(wy), f(ww), f(wh), SAGE) +
             '<path d="M%s,%s V%s M%s,%s H%s" stroke="%s" stroke-width="6"/>' % (f(wx + ww / 2), f(wy), f(wy + wh), f(wx), f(wy + wh * .45), f(wx + ww), SAGE) +
             '<rect x="%s" y="%s" width="%s" height="10" rx="3" fill="#cfdbd5"/>' % (f(wx - 10), f(wy + wh), f(ww + 20)) +
             '</g>')
    # promień światła
    s.append('<path d="M%s,%s L%s,%s L%s,%s L%s,%s Z" fill="#FFF6E2" opacity=".35"/>' % (f(wx + ww), f(wy), f(wx + ww + 260), f(counter_y), f(wx + ww + 120), f(counter_y), f(wx), f(wy + wh)))
    # półka
    if shelf:
        sx, sy = shelf
        s.append('<g><rect x="%s" y="%s" width="190" height="9" rx="2" fill="%s"/>' % (f(sx), f(sy), BEIGE) +
                 '<rect x="%s" y="%s" width="26" height="40" rx="6" fill="#f7f3ec" stroke="#d9cfc2"/><rect x="%s" y="%s" width="26" height="14" fill="%s" opacity=".7"/>' % (f(sx + 12), f(sy - 40), f(sx + 12), f(sy - 22), MUST) +
                 '<rect x="%s" y="%s" width="30" height="52" rx="7" fill="#f7f3ec" stroke="#d9cfc2"/><rect x="%s" y="%s" width="30" height="20" fill="%s" opacity=".55"/>' % (f(sx + 46), f(sy - 52), f(sx + 46), f(sy - 30), BROWN) +
                 '<path d="M%s,%s q-2,-14 10,-18 q12,-4 14,10 Z" fill="%s"/>' % (f(sx + 92), f(sy), DKG) +
                 '<rect x="%s" y="%s" width="30" height="24" rx="4" fill="%s"/>' % (f(sx + 92), f(sy - 24), BEIGE) +
                 '<use href="#leaf" transform="translate(%s,%s) rotate(-30) scale(1.3)" fill="%s"/><use href="#leaf" transform="translate(%s,%s) rotate(25) scale(1.2)" fill="%s"/>' % (f(sx + 100), f(sy - 36), DKG, f(sx + 116), f(sy - 38), SAGE) +
                 '<circle cx="%s" cy="%s" r="16" fill="#f7f3ec" stroke="#d9cfc2"/><circle cx="%s" cy="%s" r="9" fill="none" stroke="%s" stroke-width="2"/>' % (f(sx + 150), f(sy - 17), f(sx + 150), f(sy - 17), SAGE) +
                 '</g>')
    # drzwi
    if door:
        s.append(door)
    # fartuch kuchenny (kafle)
    s.append('<rect x="-400" y="%s" width="1340" height="120" fill="#dfe6e1"/>' % f(counter_y - 118))
    tiles = ''.join('<path d="M-400,%s H940" stroke="#cdd8d2" stroke-width="1.4"/>' % f(counter_y - 118 + 30 * i) for i in range(1, 4))
    tiles += ''.join('<path d="M%s,%s v30" stroke="#cdd8d2" stroke-width="1.4"/>' % (f(-400 + 40 * i + (20 if (j % 2) else 0)), f(counter_y - 118 + 30 * j)) for i in range(34) for j in range(4))
    s.append(tiles)
    if micro: s.append(micro)
    return ''.join(s)

def counter(counter_y, x0=-400, x1=940):
    return ('<g><rect x="%s" y="%s" width="%s" height="16" rx="3" fill="#EADCD2"/>' % (f(x0), f(counter_y), f(x1 - x0)) +
            '<rect x="%s" y="%s" width="%s" height="5" fill="#f6eee8"/>' % (f(x0), f(counter_y), f(x1 - x0)) +
            '<rect x="%s" y="%s" width="%s" height="600" fill="%s"/>' % (f(x0), f(counter_y + 16), f(x1 - x0), DKG) +
            '<rect x="%s" y="%s" width="%s" height="14" fill="#000" opacity=".12"/>' % (f(x0), f(counter_y + 16), f(x1 - x0)) +
            ''.join('<rect x="%s" y="%s" width="128" height="400" rx="4" fill="none" stroke="#4d675f" stroke-width="2"/><rect x="%s" y="%s" width="46" height="6" rx="3" fill="%s"/>'
                    % (f(x + 8), f(counter_y + 34), f(x + 49), f(counter_y + 52), BEIGE) for x in range(int(x0), int(x1), 140)) +
            '</g>')

S('#stage text{font-family:"Mulish",sans-serif}')
DEFS_EXTRA = ('<linearGradient id="kWall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s" stop-opacity="0"/><stop offset="1" stop-color="#E9E0D8"/></linearGradient>' % CREAM +
              '<linearGradient id="kDawn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7E6CF"/><stop offset=".6" stop-color="#F3D9C2"/><stop offset="1" stop-color="#EBCDB9"/></linearGradient>' +
              '<radialGradient id="warm" cx=".25" cy=".3" r=".8"><stop offset="0" stop-color="#FFE9C8" stop-opacity=".55"/><stop offset=".55" stop-color="#FFE9C8" stop-opacity=".12"/><stop offset="1" stop-color="#FFE9C8" stop-opacity="0"/></radialGradient>' +
              '<radialGradient id="sunG" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#F6DDA8" stop-opacity=".9"/><stop offset=".4" stop-color="#F3D7B0" stop-opacity=".45"/><stop offset="1" stop-color="#F3D7B0" stop-opacity="0"/></radialGradient>' +
              '<linearGradient id="skyB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4F2EF"/><stop offset=".55" stop-color="#F1E2D3"/><stop offset="1" stop-color="#E9CDB8"/></linearGradient>' +
              '<linearGradient id="fridgeG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9DB2A9"/><stop offset=".5" stop-color="#AEC1B9"/><stop offset="1" stop-color="#A0B4AC"/></linearGradient>' +
              '<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".7"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>' +
              '<radialGradient id="halo6"><stop offset="0" stop-color="#DDE6E1"/><stop offset=".6" stop-color="#E7EBE7" stop-opacity=".6"/><stop offset="1" stop-color="#F2EFEB" stop-opacity="0"/></radialGradient>' +
              '<clipPath id="tixClip"><rect x="-96" y="-58" width="192" height="116" rx="10"/></clipPath>')

def cam(cls, T, frames, ease=EIO):
    """frames: (t, fx, fy, z, sx, sy, rot[, easing]) – punkt świata (fx,fy) w punkcie ekranu (sx,sy) z zoomem z."""
    S('.%s{transform-origin:0 0}' % cls)
    A('.' + cls, K([(x[0], 'transform:translate(%spx,%spx) scale(%s) rotate(%sdeg) translate(%spx,%spx)' % (f(x[4]), f(x[5]), f(x[3]), f(x[6]), f(-x[1]), f(-x[2]))) + ((x[7],) if len(x) > 7 else ()) for x in frames], T, ease))

def vignette(op=.55):
    return '<rect width="540" height="960" fill="url(#vignette)" opacity="%s" pointer-events="none"/>' % f(op)

def side_arm(sleeve, hand_kind='open', prop='', skin=SKIN2, cuff='#f4f2ef', length=520, width=30):
    """Ręka wchodząca z lewej krawędzi; dłoń w (0,0), rękaw ciągnie się w lewo poza kadr."""
    s = '<g>'
    s += '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s"/>' % (f(-length), f(-width / 2), f(length - 16), f(width), f(width / 2), sleeve)
    s += '<path d="M%s,%s H-22" stroke="#000" stroke-opacity=".12" stroke-width="3"/>' % (f(-length), f(width / 2 - 4))
    s += '<rect x="-30" y="%s" width="12" height="%s" rx="4" fill="%s"/>' % (f(-width / 2 + 2), f(width - 4), cuff)
    if hand_kind == 'open':
        s += '<path d="M-20,-11 C-8,-15 8,-13 16,-7 C22,-3 22,3 16,6 C10,9 0,12 -20,11 Z" fill="%s"/>' % skin
        s += '<path d="M-6,-12 C0,-22 10,-22 9,-14" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round"/>' % skin
        s += '<path d="M2,-2 H16 M2,4 H14" stroke="#c98f72" stroke-width="1" opacity=".6"/>'
    elif hand_kind == 'thumb':
        s += '<rect x="-20" y="-14" width="30" height="28" rx="11" fill="%s"/>' % skin
        s += '<rect x="-6" y="-40" width="12" height="32" rx="6" fill="%s"/>' % skin
        s += '<path d="M-16,-2 H8 M-16,5 H8" stroke="#c98f72" stroke-width="1.2" opacity=".6"/>'
    elif hand_kind == 'fist':
        s += '<rect x="-20" y="-13" width="30" height="26" rx="11" fill="%s"/>' % skin
        s += '<path d="M-6,-12 C-2,-20 8,-18 8,-10" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round"/>' % skin
    s += prop + '</g>'
    return s

def slide_x(c, T, frames, ease=EIO):
    A('.' + c, K([(x[0], 'transform:translate(%spx,%spx) rotate(%sdeg)' % (f(x[1]), f(x[2]), f(x[3] if len(x) > 3 else 0))) for x in frames], T, ease))

