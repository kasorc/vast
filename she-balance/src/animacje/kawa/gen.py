# -*- coding: utf-8 -*-
# Generator animacji „Ciągle ktoś czegoś chce” (SheBalance, reel 9:16, 27 s) → src/animacje/kawa.html
# Uruchom: python3 src/animacje/kawa/gen.py && python3 src/zbuduj_animacje.py kawa
# Cała choreografia = statyczne SVG + keyframes CSS liczone od początku sceny (tak działa silnik).
import math, random, pathlib, itertools, json

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / 'kawa.html'
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

TSCALE = 1.0  # skala czasu sceny (np. skrócenie lawiny próśb)

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
    return '%s %.3fs %s 0s %s %s' % (name, T * TSCALE, ease, it, fill)

def A(sel, *anims, extra=''):
    sels = ','.join('.active ' + s.strip() for s in sel.split(','))
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

# ================= SCENA 1: Poranek, który już trwa (0–3 s) =================
def sc_poranek():
    T = 3.0; s = []
    cy = 742; s1 = .7; cx = 300; feet = cy + (712 - 470) * s1
    micro = ('<g><rect x="34" y="%s" width="120" height="74" rx="8" fill="#f7f3ec" stroke="#d6cdc1" stroke-width="2"/>' % (cy - 74) +
             '<rect x="44" y="%s" width="70" height="54" rx="4" fill="#6d7f78"/><rect x="122" y="%s" width="24" height="54" rx="3" fill="#ede6dd"/>' % (cy - 64, cy - 64) +
             '<rect x="124" y="%s" width="20" height="13" rx="2" fill="#2f3b37"/>' % (cy - 62) +
             '<g class="clk"><text x="134" y="%s" font-size="10" text-anchor="middle" fill="#F6DDA8" style="font-weight:800">6:47</text></g>' % (cy - 52) +
             '</g>')
    s.append('<g class="c1">')
    s.append(kitchen(cy, micro=micro, window=(36, 330, 180, 290), shelf=(380, 500)))
    # A z kubkiem (prawa ręka) – podnosi do ust, nie zdąża
    inst = 'kA1'
    s.append(FIG('A', inst, cx, feet, s1, post=ghost('A', inst, '', mug_hand('st1'), arm='R')))
    s.append(counter(cy))
    # zegar 6:47 na mikrofalówce (duży odpowiednik w rogu kadru)
    s.append('</g>')
    rig(inst, 'A', T, [(0, {'R': R_HOLD, 'L': (62, 452)}), (.35, {'R': R_HOLD}), (1.3, {'R': R_SIP}, 'cubic-bezier(.4,0,.2,1)'),
                       (1.42, {'R': R_SIP}), (1.62, {'R': R_HOLD}, ESNAP), (2.4, {'R': R_HOLD}), (2.75, {'R': (186, 232)})])
    head(inst, T, [(0, 0, 0, 0), (.9, 2, 0, 1), (1.45, 2, 0, 1), (1.62, -9, -5, 0, ESNAP), (2.4, -8, -5, 0), (2.9, -4, -2, 0)])
    pupils(inst, T, [(0, 0), (1.45, 0), (1.55, -3.2), (2.6, -3.2), (2.9, -1.5)])
    A('.fig.%s .eyes' % inst, K([(0, 'transform:scaleY(1)'), (.95, 'transform:scaleY(1)'), (1.15, 'transform:scaleY(.15)'), (1.42, 'transform:scaleY(.15)'), (1.52, 'transform:scaleY(1.12)', ESNAP), (2.3, 'transform:scaleY(1.05)'), (2.6, 'transform:scaleY(1)')], T))
    A('.st1', K([(0, 'opacity:1'), (T, 'opacity:.85')], T))
    cam('c1', T, [(0, 300, 509, 1.0, 300, 509, 0), (1.4, 300, 509, 1.05, 296, 509, 0, 'cubic-bezier(.2,.8,.2,1)'), (1.6, 300, 509, 1.075, 300, 509, 0), (T, 300, 509, 1.09, 302, 507, 0)], 'cubic-bezier(.4,0,.6,1)')
    A('.clk', 'clk .5s steps(1) infinite')
    S('@keyframes clk{0%{opacity:1}50%{opacity:.15}}')
    s.append('<rect width="540" height="960" fill="url(#warm)" pointer-events="none"/>')
    s.append(vignette(.45))
    # nakładka: tytuł, zegar, MAMO!
    s.append('<g class="t1a"><text x="270" y="176" font-size="54" text-anchor="middle" class="serif" fill="%s">Jedna kawa.</text></g>' % INK)
    A('.t1a', K([(0, 'transform:translateY(0);opacity:1'), (T, 'transform:translateY(-4px);opacity:1')], T, 'linear'))
    s.append('<text x="270" y="236" font-size="54" text-anchor="middle" class="serif split" fill="%s" style="--d0:.55s">Tylko jedna.</text>' % INK)
    # duży zegar w rogu (miga)
    s.append('<g transform="translate(414,330)"><g class="clkBig">'
             '<rect x="-46" y="-22" width="92" height="44" rx="10" fill="#2f3b37"/>'
             '<text x="0" y="10" font-size="26" text-anchor="middle" fill="#F6DDA8" style="font-weight:800;letter-spacing:.04em">6<tspan class="clk">:</tspan>47</text></g></g>')
    A('.clkBig', K([(0, 'opacity:0;transform:scale(.6)'), (.35, 'opacity:0;transform:scale(.6)', ESNAP), (.6, 'opacity:1;transform:scale(1)'), (2.2, 'opacity:1;transform:scale(1)'), (2.32, 'opacity:.35;transform:scale(1)'), (2.44, 'opacity:1;transform:scale(1.04)'), (2.56, 'opacity:.35;transform:scale(1)'), (2.68, 'opacity:1;transform:scale(1)')], T))
    b, w, h = bubble(['MAMO!'], fill=BEIGE, stroke=BROWN, fs=40, col=RUST, weight=900, k=.72, padx=20, pady=12, tail=(-70, 40))
    lines = ''.join('<path d="M%s,%s l%s,%s" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % (f(dx), f(dy), f(ex), f(ey), BROWN) for dx, dy, ex, ey in [(-w / 2 - 8, -18, -14, -10), (-w / 2 - 10, 2, -18, 0), (-w / 2 - 6, 20, -14, 10)])
    s.append(place_bubble(b + lines, 132, 352, T, 1.42, pop_dur=.3))
    s.append('<g class="sh1">%s</g>' % '')
    return ''.join(s), T

# ================= SCENA 2: Lawina próśb (3–8,6 s; skrócona ×0,7) =================
def child_hoodie():
    return ('<g transform="translate(6,6)"><path d="M-14,-6 C-10,-20 22,-22 30,-8 C40,10 34,38 20,44 C6,48 -12,40 -14,26 Z" fill="%s"/>' % MUST +
            '<path d="M-6,4 Q8,10 24,2 M0,22 Q12,28 26,20" stroke="#b9862a" stroke-width="2" fill="none"/>'
            '<path d="M2,-14 q8,8 18,0" stroke="#b9862a" stroke-width="2.4" fill="none"/></g>')

def shirt_hanger():
    return ('<g><path d="M0,-4 q0,-12 9,-10 q7,2 3,9 L0,8" fill="none" stroke="#8a7a6c" stroke-width="2.6"/>'
            '<path d="M0,8 L-34,22 L34,22 Z" fill="none" stroke="#8a7a6c" stroke-width="2.6"/>'
            '<path d="M-34,20 L-48,40 L-38,52 L-30,44 L-30,104 L30,104 L30,44 L38,52 L48,40 L34,20 L10,18 L0,30 L-10,18 Z" fill="#F7F4EE" stroke="#cfc6b9" stroke-width="1.4"/>'
            '<path d="M0,30 V102" stroke="#cfc6b9" stroke-width="1.2"/>' +
            ''.join('<circle cx="4" cy="%s" r="1.6" fill="#a9b8b1"/>' % y for y in (42, 60, 78, 96)) +
            ''.join('<path d="M%s,24 V104" stroke="%s" stroke-width="2" opacity=".55"/>' % (x, SAGE) for x in (-24, -14, 14, 24)) +
            '</g>')

def notebook():
    return ('<g transform="rotate(-8)"><rect x="-4" y="-34" width="64" height="48" rx="3" fill="%s" stroke="#c9ad9f" stroke-width="1.4"/>' % BEIGE +
            '<rect x="-4" y="-34" width="8" height="48" fill="%s"/>' % BROWN +
            '<rect x="12" y="-24" width="40" height="13" rx="2" fill="#F7F4EE"/><path d="M16,-18 H46" stroke="#9a8a7e" stroke-width="1.4"/></g>')

def sc_lawina():
    global TSCALE
    TSCALE = .7  # skrócona lawina próśb: 8 s → 5,6 s
    T = 8.0; s = []
    cy = 790; s1 = .88; cx = 270; feet = cy + (712 - 470) * s1
    FX, FY = L2W(cx, feet, s1, 110, 140)
    inst = 'kA2'
    mugR = '<g class="mugR">%s</g>' % mug_hand('st2')
    mugL = '<g class="mugL">%s</g>' % mug_hand('st2')
    pen = '<g class="penR"><path d="M6,-2 L22,26" stroke="%s" stroke-width="4" stroke-linecap="round"/><path d="M22,26 L24,31" stroke="#333" stroke-width="2.4"/></g>' % RUST
    hoodA = '<g class="hoodA" transform="translate(-6,-8)">%s</g>' % child_hoodie()
    shirtA = '<g class="shirtA" transform="translate(0,-14) scale(.9)">%s</g>' % shirt_hanger()
    post = ghost('A', inst, '', mugR, arm='R') + ghost('A', inst, '', hoodA + pen, arm='L')
    s.append('<g class="c2">')
    phone = ('<g transform="translate(470,806)"><g class="ph2"><path d="M-30,-6 L22,-10 L34,6 L-20,10 Z" fill="#2f3b37"/><path d="M-26,-4 L20,-8 L30,5 L-17,8 Z" fill="#46564f"/>'
             '<path class="phGlow" d="M-26,-4 L20,-8 L30,5 L-17,8 Z" fill="#F6DDA8"/></g></g>')
    s.append(kitchen(cy, window=(24, 340, 160, 300), shelf=(372, 560)))
    s.append(FIG('A', inst, cx, feet, s1, post=post))
    s.append(counter(cy))
    # stos rzeczy na blacie (rośnie)
    hood_pile = ('<g transform="translate(118,792)"><g class="pl1"><path d="M-46,0 C-44,-22 -10,-30 10,-26 C34,-22 48,-12 46,0 Z" fill="%s"/>' % MUST +
                 '<path d="M-30,-10 Q-6,-20 20,-12 M-10,-2 Q10,-8 30,-2" stroke="#b9862a" stroke-width="2.4" fill="none"/></g></g>')
    shirt_pile = ('<g transform="translate(398,794)"><g class="pl2"><path d="M-40,0 L-36,-18 L36,-20 L42,0 Z" fill="#F7F4EE" stroke="#cfc6b9" stroke-width="1.4"/>' +
                  ''.join('<path d="M%s,-18 V0" stroke="%s" stroke-width="2" opacity=".55"/>' % (x, SAGE) for x in (-24, -12, 12, 24)) +
                  '<path d="M-10,-19 L0,-10 L10,-19" fill="none" stroke="#cfc6b9" stroke-width="1.4"/></g></g>')
    s.append(hood_pile + shirt_pile)
    s.append('<g transform="translate(196,796)"><path d="M-30,0 Q0,16 30,0 Z" fill="%s"/><circle cx="-10" cy="-5" r="9" fill="%s"/><circle cx="8" cy="-6" r="8" fill="%s"/></g>' % (BEIGE, MUST, RUST))
    s.append(phone)
    # ręce z krawędzi (świat)
    s.append('<g transform="translate(150,664)"><g class="hc1">%s</g></g>' % side_arm(DKG, 'open', '<g class="hood1">%s</g>' % child_hoodie(), width=28))
    s.append('<g transform="translate(404,690) scale(-1,1)"><g class="hh1">%s</g></g>' % side_arm('#7d6a5c', 'fist', '<g transform="translate(0,-6) scale(-1,1)"><g class="shirt1">%s</g></g>' % shirt_hanger(), width=36))
    s.append('<g transform="translate(206,742) rotate(-14)"><g class="hc2">%s</g></g>' % side_arm(DKG, 'open', '<g transform="translate(4,-8)">%s</g>' % notebook(), width=28))
    s.append('</g>')
    L_REST = (62, 452)
    fr = [
        (0, {'R': R_HOLD, 'L': L_REST}),
        (.5, {'L': L_REST}),
        (.85, {'L': (-24, 352)}, ESNAP),                 # wolna lewa sięga po bluzę
        (1.0, {'L': (-20, 356)}),
        (1.28, {'L': (20, 470)}, EIO),                   # rzuca bluzę na blat
        (1.5, {'L': L_REST}),
        (2.65, {'R': R_HOLD}),
        (3.0, {'R': R_SIP}, 'cubic-bezier(.4,0,.2,1)'),  # próba 1
        (3.15, {'R': R_SIP}),
        (3.35, {'R': R_HOLD}, ESNAP),
        (4.3, {'R': R_HOLD, 'L': L_REST}),
        (4.55, {'R': R_SIP}),                            # próba 2
        (4.65, {'R': R_SIP}),
        (4.85, {'R': R_HOLD, 'L': (36, 412)}, ESNAP),    # podpis lewą ręką
        (5.0, {'L': (28, 418)}), (5.08, {'L': (42, 414)}), (5.16, {'L': (26, 422)}), (5.24, {'L': (44, 418)}),
        (5.45, {'L': L_REST}),
        (5.9, {'L': (-6, 250)}, ESNAP),                  # „chwila!”
        (6.3, {'L': (-4, 254)}),
        (6.6, {'L': L_REST}),
        (6.9, {'R': R_HOLD}),
        (7.25, {'R': R_SIP}, ESNAP),                     # próba 3 – zimna
        (8.0, {'R': R_SIP}),
    ]
    rig(inst, 'A', T, fr)
    head(inst, T, [(0, 0, 0, 0), (.35, 0, 0, 0), (.55, -9, -5, 0, ESNAP), (1.3, -8, -5, 0), (1.45, 8, 5, 0, ESNAP), (2.2, 7, 4, 0),
                   (2.3, 5, 3, 5, ESNAP), (3.1, 4, 2, 4), (3.2, -9, -5, 0, ESNAP), (3.9, -8, -5, 0), (4.0, 7, 4, -2, ESNAP), (4.6, 7, 4, -2),
                   (4.72, -8, -4, 4, ESNAP), (5.3, -7, -4, 4), (5.38, 9, 5, 2, ESNAP), (5.85, 8, 5, 2), (5.95, 10, 6, 0, ESNAP),
                   (6.35, -10, -6, 0, ESNAP), (6.65, -10, -6, 0), (6.72, 10, 6, 0, ESNAP), (6.98, 10, 6, 0), (7.04, -11, -6, 0, ESNAP), (7.28, -11, -6, 0),
                   (7.34, 11, 6, 0, ESNAP), (7.6, 2, 0, 3, ESNAP), (8.0, 0, 0, 3)])
    pupils(inst, T, [(0, 0), (.5, 0), (.55, -3.2), (1.4, -3.2), (1.45, 3.2), (2.25, 3.2), (2.3, 2), (3.15, 2), (3.2, -3.2), (3.95, -3.2), (4.0, 3), (4.65, 3),
                     (4.72, -3), (5.3, -3), (5.38, 3.2), (6.3, 3.2), (6.35, -3.2), (6.68, -3.2), (6.72, 3.2), (7.0, 3.2), (7.04, -3.2), (7.3, -3.2), (7.34, 3.2), (7.6, 0)])
    A('.fig.%s .eyes' % inst, K([(0, 'transform:scaleY(1)'), (7.55, 'transform:scaleY(1)'), (7.7, 'transform:scaleY(1.15)')], T))
    A('.fig.%s .body' % inst, K([(0, 'transform:translateY(0)'), (7.5, 'transform:translateY(0)'), (7.7, 'transform:translateY(4px) scaleY(.99)'), (8, 'transform:translateY(4px) scaleY(.99)')], T))
    A('.penR', K([(0, 'opacity:0'), (4.7, 'opacity:0'), (4.8, 'opacity:1'), (5.35, 'opacity:1'), (5.45, 'opacity:0')], T, 'linear'))
    A('.st2', K([(0, 'opacity:1;transform:scale(1)'), (2.5, 'opacity:.7;transform:scale(.85)'), (4.5, 'opacity:.3;transform:scale(.7)'), (5.9, 'opacity:0;transform:scale(.6)')], T, 'ease-in-out'))
    # bluza: dłoń dziecka → dłoń A → blat; koszula: dłoń męża → dłoń A → blat
    A('.hood1', K([(0, 'opacity:1'), (.95, 'opacity:1', 'steps(1,end)'), (.96, 'opacity:0')], T, 'linear'))
    A('.hoodA', K([(0, 'opacity:0'), (.95, 'opacity:0', 'steps(1,end)'), (.96, 'opacity:1'), (1.24, 'opacity:1', 'steps(1,end)'), (1.25, 'opacity:0')], T, 'linear'))
    A('.shirt1', K([(0, 'opacity:1'), (1.95, 'opacity:1', 'steps(1,end)'), (1.96, 'opacity:0')], T, 'linear'))
    S('.pl1,.pl2{transform-box:fill-box;transform-origin:50% 100%}')
    A('.pl1', K([(0, 'opacity:0;transform:translateY(-30px) scale(1,1)'), (1.22, 'opacity:0;transform:translateY(-30px) scale(1,1)', 'cubic-bezier(.5,0,.9,.5)'), (1.25, 'opacity:1;transform:translateY(-24px) scale(1,1)'), (1.36, 'opacity:1;transform:translateY(0) scale(1.08,.86)', ESOFT), (1.5, 'opacity:1;transform:translateY(0) scale(1,1)')], T))
    A('.pl2', K([(0, 'opacity:0;transform:translateY(-60px) scale(1,1)'), (1.93, 'opacity:0;transform:translateY(-60px) scale(1,1)', 'cubic-bezier(.5,0,.9,.5)'), (1.96, 'opacity:1;transform:translateY(-54px) scale(1,1)'), (2.1, 'opacity:1;transform:translateY(0) scale(1.08,.86)', ESOFT), (2.25, 'opacity:1;transform:translateY(0) scale(1,1)')], T))
    slide_x('hc1', T, [(0, -260, 30), (.15, -260, 30), (.55, 0, 0), (.95, 6, 0), (1.1, 0, 0), (1.5, -280, 30)], ESOFT)
    slide_x('hh1', T, [(0, -280, 20), (1.25, -280, 20), (1.62, 0, 0), (2.05, 4, 0), (2.2, 0, 0), (2.6, -300, 20)], ESOFT)
    slide_x('hc2', T, [(0, -300, 40), (4.6, -300, 40), (4.92, 0, 0), (5.3, 3, 0, 2), (5.5, 0, 0), (5.9, -320, 40)], ESOFT)
    S('.ph2{transform-box:fill-box;transform-origin:center}')
    vib = []
    for t0 in (2.25, 5.3):
        vib += [(t0 - .01, 'transform:translate(0,0) rotate(0)')]
        for i in range(8):
            vib.append((t0 + .04 * (i + 1), 'transform:translate(%spx,0) rotate(%sdeg)' % (f(2.4 * (-1) ** i), f(3 * (-1) ** i))))
        vib.append((t0 + .36, 'transform:translate(0,0) rotate(0)'))
    A('.ph2', K([(0, 'transform:translate(0,0) rotate(0)')] + vib, T, 'linear'))
    A('.phGlow', K([(0, 'opacity:0'), (2.24, 'opacity:0'), (2.3, 'opacity:.9'), (3.4, 'opacity:.9'), (3.8, 'opacity:0'), (5.29, 'opacity:0'), (5.35, 'opacity:.9'), (6.4, 'opacity:.9'), (6.8, 'opacity:0')], T, 'linear'))
    # kamera: każda prośba = krok bliżej (+ narastający przechył)
    steps = [(0, 1.0, 0), (.15, 1.015, 0), (1.25, 1.03, .2), (2.25, 1.045, -.3), (3.15, 1.06, .4), (3.95, 1.075, -.5), (4.65, 1.09, .6), (5.3, 1.105, -.8),
             (5.9, 1.12, .9), (6.35, 1.135, -1.1), (6.7, 1.15, 1.2), (7.0, 1.165, -1.4), (7.3, 1.18, 1.6)]
    cf = [(0, FX, FY, 1.0, FX, FY, 0)]
    for t, z, r in steps[1:]:
        cf.append((t, FX, FY, cf[-1][3], FX, FY, cf[-1][6], ESNAP))
        cf.append((t + .28, FX, FY, z, FX, FY, r))
    for t, dx, dy in [(7.6, 0, 0), (7.66, 5, -3), (7.72, -6, 2), (7.78, 4, 3), (7.84, -3, -2), (7.9, 2, 1), (8.0, 0, 0)]:
        cf.append((t, FX, FY, 1.19, FX + dx, FY + dy, 1.6))
    cam('c2', T, cf, 'linear')
    s.append('<rect width="540" height="960" fill="url(#warm)" pointer-events="none"/>')
    s.append(vignette(.5))
    # ---- nakładka: prośby wsuwają się z boków kadru (ekran), środek zostaje czysty ----
    REQ = [  # (t, strona, slot_y, linie, kolor)
        (.15, 'L', 262, ['Gdzie moje', 'skarpetki?!'], BEIGE),
        (1.25, 'R', 262, ['Kochanie,', 'wyprasujesz?'], SAGE),
        (2.25, 'R', 664, None, None),                      # SMS
        (3.15, 'L', 462, ['Co na', 'obiad?'], BEIGE),
        (3.95, 'L', 262, ['Zebranie', 'o 9!'], SAGE),
        (4.65, 'L', 664, ['Podpisz', 'zeszyt!'], BEIGE),
        (5.3, 'R', 462, ['Mama,', 'zadzwoń'], CREAM2),
        (5.9, 'R', 262, ['Odbierzesz', 'paczkę?'], SAGE),
        (6.35, 'L', 462, ['Mamo!'], BEIGE),
        (6.7, 'R', 664, ['Kochanie!'], SAGE),
        (7.0, 'L', 262, ['Szybko!'], BEIGE),
        (7.3, 'R', 462, ['Gdzie', 'klucze?'], CREAM2),
    ]
    fs = 21
    ov = []
    for i, (t0, side, y, lines, col) in enumerate(REQ):
        nxt = [r[0] for r in REQ[i + 1:] if r[1] == side and r[2] == y]
        if lines is None:
            b = ('<g><rect x="-80" y="-40" width="160" height="80" rx="14" fill="#3a2a20" opacity=".14" transform="translate(3,4)"/>'
                 '<rect x="-80" y="-40" width="160" height="80" rx="14" fill="#FBF9F6" stroke="%s" stroke-width="1.6"/>' % DKG +
                 '<circle cx="-60" cy="-20" r="8" fill="%s"/><path d="M-64,-21 h8 M-64,-18 h5" stroke="#fff" stroke-width="1.6"/>' % DKG +
                 '<text x="-46" y="-14" font-size="15" fill="%s" style="font-weight:800;letter-spacing:.08em">SMS</text>' % DKG +
                 '<text x="-66" y="10" font-size="20" fill="%s" style="font-weight:700">Hej, raport</text><text x="-66" y="31" font-size="20" fill="%s" style="font-weight:700">na dziś?</text></g>' % (INK, INK))
            w = 160
        else:
            narrow = (y == 462)
            b, w, h = bubble(lines, fill=col, fs=fs if not narrow else 19, padx=10 if narrow else 16,
                             tail=((-1 if side == 'L' else 1) * 40, 34))
        x = (34 + w / 2) if side == 'L' else ((474 if y == 462 else 466) - w / 2)
        sgn = -1 if side == 'L' else 1
        c = uid('sb')
        off = sgn * (w + 130)
        fr = [(0, 'opacity:1;transform:translate(%spx,0) scale(1)' % f(off)),
              (t0, 'opacity:1;transform:translate(%spx,0) scale(1)' % f(off), 'cubic-bezier(.2,.8,.3,1)'),
              (t0 + .22, 'opacity:1;transform:translate(%spx,0) scale(1)' % f(-sgn * 6), ESOFT),
              (t0 + .34, 'opacity:1;transform:translate(0px,0) scale(1)')]
        if nxt:
            t1 = nxt[0]
            fr += [(t1 - .02, 'opacity:1;transform:translate(0px,0) scale(1)', EIO),
                   (t1 + .25, 'opacity:.5;transform:translate(%spx,%spx) scale(.62)' % (f(sgn * w * .55), f(-46 if y < 400 else 46)))]
        S('.%s{transform-origin:%spx 0}' % (c, f(sgn * w / 2)))
        A('.' + c, K(fr, T))
        ov.append('<g transform="translate(%s,%s)"><g class="%s">%s</g></g>' % (f(x), f(y), c, b))
    # licznik: +1 z każdą prośbą
    times = [r[0] for r in REQ]
    hud = ['<g transform="translate(270,142)"><g class="hud2">'
           '<rect x="-122" y="-30" width="244" height="58" rx="29" fill="#FBF9F6" stroke="%s" stroke-width="1.6"/>' % DKG +
           '<text x="-26" y="9" font-size="22" text-anchor="middle" fill="%s" style="font-weight:800;letter-spacing:.12em">PROŚBY:</text>' % INK]
    for i, t0 in enumerate(times):
        t1 = times[i + 1] if i + 1 < len(times) else 99
        c = uid('n')
        hud.append('<g transform="translate(72,0)"><g class="%s"><text x="0" y="14" font-size="40" text-anchor="middle" class="serif" fill="%s">%d</text></g></g>' % (c, RUST, i + 1))
        fr2 = [(0, 'opacity:0;transform:translateY(14px)'), (t0 + .06, 'opacity:0;transform:translateY(14px)', ESNAP), (t0 + .16, 'opacity:1;transform:translateY(0)')]
        if t1 < T: fr2 += [(t1, 'opacity:1;transform:translateY(0)', EOUT), (t1 + .06, 'opacity:0;transform:translateY(-14px)')]
        A('.' + c, K(fr2, T))
    hud.append('</g></g>')
    hf = [(0, 'opacity:0;transform:translateY(-20px) scale(1)'), (.1, 'opacity:0;transform:translateY(-20px) scale(1)', ESNAP), (.3, 'opacity:1;transform:translateY(0) scale(1)')]
    for i, t0 in enumerate(times[1:], 1):
        big = 1.1 + .012 * i
        hf += [(t0, 'opacity:1;transform:translateY(0) scale(1)', 'cubic-bezier(.2,.8,.3,1)'), (t0 + .08, 'opacity:1;transform:translateY(0) scale(%s)' % f(big), ESOFT), (min(t0 + .24, T), 'opacity:1;transform:translateY(0) scale(1)')]
    S('.hud2{transform-origin:0 0}')
    A('.hud2', K(hf, T))
    s.append('<g class="ov2">' + ''.join(ov) + ''.join(hud) + '</g>')
    TSCALE = 1.0
    return ''.join(s), T * .7

# ================= SCENA 3: Przeciążenie (11–13 s) =================
def sc_przeciazenie():
    T = 2.0; s = []
    cy = 700; s1 = .46; cx = 270; feet = cy + (712 - 470) * s1
    face = L2W(cx, feet, s1, 110, 140)
    inst = 'kA3'
    s.append('<g class="c3"><g class="frz">')
    s.append(kitchen(cy, window=(30, 380, 150, 220), shelf=(370, 470)))
    s.append('</g>')
    rr = random.Random(5)
    spots = [(104, 168, 26, 'Mamo!'), (282, 150, 28, 'Kochanie!'), (446, 182, 24, '?!'), (168, 246, 24, 'Szybko!'), (392, 256, 26, 'Obiad?'),
             (72, 326, 22, 'Hej!'), (262, 332, 26, 'Masz chwilę?'), (452, 344, 22, '!!!'), (126, 410, 24, 'Mamo!!'), (410, 424, 24, 'Zebranie!'),
             (70, 488, 20, '…?'), (468, 506, 20, '??'), (112, 566, 22, 'Klucze?'), (428, 588, 22, 'Paczka!'), (76, 646, 20, 'Teraz!'), (462, 660, 20, 'Hej!')]
    fx, fy = face
    ov = []
    for i, (x, y, fs, wd) in enumerate(spots):
        col = [BEIGE, SAGE, CREAM2][i % 3]
        b, w, h = bubble([wd], fill=col, tail=((fx - x) * .2, 30 if y < fy else -30), fs=fs)
        t0 = -1 if i % 3 else .05 + (i // 3) * .07
        ov.append(place_bubble('<g transform="rotate(%s)">%s</g>' % (f(rr.uniform(-8, 8)), b), x, y, T, t0, pop_dur=.18, push=(.45, .85, (x - fx) * 1.6, (y - fy) * 1.6)))
    s.append(FIG('A', inst, cx, feet, s1, post=ghost('A', inst, '', mug_hand('st3'), arm='R')))
    s.append(counter(cy))
    s.append(''.join(ov))
    s.append('</g>')
    A('.st3', K([(0, 'opacity:0'), (T, 'opacity:0')], T))
    head(inst, T, [(0, 6, 3, 0), (.1, -7, -3, 0, ESNAP), (.2, 7, 3, 0, ESNAP), (.3, -6, -3, 0, ESNAP), (.42, 2, 0, 0, ESNAP), (.85, 0, 0, 0)])
    pupils(inst, T, [(0, 3), (.1, -3), (.2, 3), (.3, -3), (.42, 0), (2, 0)])
    rig(inst, 'A', T, [(0, {'R': R_HOLD, 'L': (62, 452)}), (.4, {'R': (186, 232)}), (.85, {'R': (186, 234)}), (2, {'R': (186, 234)})])
    for part in ('body', 'tilt', 'smile'):
        A('.fig.%s .%s' % (inst, part), K([(0, 'transform:none'), (T, 'transform:none')], T))
    A('.fig.%s .eyes' % inst, K([(0, 'transform:scaleY(1)'), (.75, 'transform:scaleY(1)'), (.85, 'transform:scaleY(1.14)'), (T, 'transform:scaleY(1.14)')], T))
    # mocny zoom na twarz i freeze w 0,85 s
    cam('c3', T, [(0, 270, 470, 1.0, 270, 470, 0), (.42, 270, 475, 1.03, 270, 474, 0, 'cubic-bezier(.7,0,.2,1)'), (.85, fx, fy, 2.6, 270, 600, 0), (T, fx, fy, 2.62, 270, 600, 0)])
    # freeze: odbarwienie + błysk
    A('.frz', K([(0, 'filter:saturate(1)'), (.84, 'filter:saturate(1)', 'steps(1,end)'), (.86, 'filter:saturate(.6)')], T, 'linear'))
    s.append(vignette(.6))
    s.append('<rect width="540" height="960" fill="#fff" class="flash3" pointer-events="none"/>')
    A('.flash3', K([(0, 'opacity:0'), (.84, 'opacity:0', 'steps(1,end)'), (.86, 'opacity:.75', 'cubic-bezier(.2,.7,.3,1)'), (1.1, 'opacity:0')], T, 'linear'))
    # ramka „stop-klatki”
    s.append('<g class="frm3"><rect x="14" y="14" width="512" height="932" fill="none" stroke="%s" stroke-width="3"/></g>' % CREAM2)
    A('.frm3', K([(0, 'opacity:0'), (.85, 'opacity:0', 'steps(1,end)'), (.87, 'opacity:.9')], T, 'linear'))
    # napis
    s.append('<g class="t3"><rect x="40" y="128" width="460" height="232" rx="18" fill="%s" opacity=".94"/>' % CREAM2 +
             '<text x="270" y="198" font-size="50" text-anchor="middle" class="serif" fill="%s">A kto zapyta,</text>' % INK +
             '<text x="270" y="262" font-size="50" text-anchor="middle" class="serif" fill="%s">czego <tspan fill="%s">TY</tspan></text>' % (INK, RUST) +
             '<text x="270" y="326" font-size="50" text-anchor="middle" class="serif" fill="%s">potrzebujesz?</text>' % INK +
             '<path class="ul3" d="M300,276 Q328,282 356,274" stroke="%s" stroke-width="4" fill="none" stroke-linecap="round" pathLength="1"/></g>' % RUST)
    A('.t3', K([(0, 'opacity:0;transform:scale(1.04)'), (.74, 'opacity:0;transform:scale(1.04)', ESNAP), (.94, 'opacity:1;transform:scale(1)')], T))
    S('.t3{transform-origin:270px 240px}.ul3{stroke-dasharray:1}')
    A('.ul3', K([(0, 'stroke-dashoffset:1'), (1.3, 'stroke-dashoffset:1', EIO), (1.6, 'stroke-dashoffset:0')], T))
    return ''.join(s), T

# ================= SCENA 4: Wchodzi brunetka (13–17 s) =================
def ticket(big=True):
    """Bilet SheBalance; środek (0,0), szer. 192 × 116 (jednostki lokalne postaci)."""
    s = ('<g><rect x="-96" y="-58" width="192" height="116" rx="10" fill="#3a2a20" opacity=".14" transform="translate(3,5)"/>'
         '<rect x="-96" y="-58" width="192" height="116" rx="10" fill="#FBF9F6" stroke="%s" stroke-width="1.6"/>' % DKG +
         '<rect x="-96" y="-58" width="192" height="30" rx="10" fill="%s"/><rect x="-96" y="-38" width="192" height="10" fill="%s"/>' % (SAGE, SAGE) +
         '<use href="#logoWord" transform="translate(0,-43) scale(.2)" style="color:#FBF9F6"/>' +
         '<path d="M-96,10 a7,7 0 0 1 0,14 M96,10 a7,7 0 0 0 0,14" fill="%s"/>' % CREAM +
         '<path d="M-80,17 H80" stroke="%s" stroke-width="1.4" stroke-dasharray="4 4"/>' % SAGE +
         '<text x="0" y="1" font-size="23" text-anchor="middle" class="serif" fill="%s">3 dni · Beskidy</text>' % INK +
         '<text x="0" y="45" font-size="14.5" text-anchor="middle" fill="%s" style="font-weight:800;letter-spacing:.06em">TYLKO DLA CIEBIE</text>' % BROWN +
         '<g clip-path="url(#tixClip)"><rect class="tixShine" x="-60" y="-70" width="40" height="140" fill="url(#shine)" transform="rotate(18)"/></g>'
         '</g>')
    return s

def sc_brunetka():
    T = 4.0; s = []
    cy = 720; sA = .72; cxA = 150; feetA = cy + (712 - 470) * sA
    sB = .72; cxB = 405; feetB = feetA
    instA, instB = 'kA4', 'kB4'
    door = ('<g><rect x="322" y="362" width="160" height="400" fill="#5f4a3e"/>'
            '<rect x="326" y="366" width="152" height="396" fill="url(#doorLight)"/>'
            '<g class="doorP"><rect x="326" y="366" width="152" height="396" fill="%s" stroke="#cfa996" stroke-width="2"/>' % BEIGE +
            '<rect x="340" y="382" width="124" height="140" rx="4" fill="none" stroke="#cfa996" stroke-width="2"/><rect x="340" y="538" width="124" height="190" rx="4" fill="none" stroke="#cfa996" stroke-width="2"/>'
            '<g transform="translate(350,560)"><g class="knob"><rect x="-4" y="-3" width="20" height="6" rx="3" fill="%s"/></g></g></g>' % BROWN +
            '<rect x="314" y="354" width="176" height="10" fill="%s"/><rect x="314" y="354" width="8" height="408" fill="%s"/><rect x="482" y="354" width="8" height="408" fill="%s"/></g>' % (SAGE, SAGE, SAGE))
    S('.doorP{transform-origin:326px 0}.knob{transform-origin:0 0}')
    s.append('<g class="c4">')
    s.append(kitchen(cy, door=door, window=(20, 330, 120, 240), shelf=None))
    # światło z drzwi
    s.append('<path class="beam4" d="M326,366 L478,366 L590,%s L220,%s Z" fill="#FFF1D6" opacity="0"/>' % (cy, cy))
    # B: wejście przez drzwi
    tixB = '<g class="tixB" transform="translate(0,-14) scale(.38)">%s</g>' % ticket()
    tixA = '<g class="tixA"><g class="tixGrow">%s</g></g>' % ticket()
    s.append('<g class="bIn">' + FIG('B', 'has-pack ' + instB, cxB, feetB, sB, wrap='bBob', post=ghost('B', instB, 'has-pack', tixB, arm='L')) + '</g>')
    s.append(FIG('A', instA, cxA, feetA, sA, wrap='aSlump', post=ghost('A', instA, '', tixA, arm='R')))
    s.append(counter(cy))
    # zimny kubek odstawiony na blat
    s.append('<g transform="translate(92,%s) scale(.62)"><path d="M-19,-34 L19,-34 L17,4 Q16,10 10,10 L-10,10 Q-16,10 -17,4 Z" fill="#F4F2EF" stroke="#d9cfc2" stroke-width="1.2"/><path d="M18,-24 Q32,-24 30,-11 Q28,-1 16,-2" fill="none" stroke="#F4F2EF" stroke-width="5.5"/><path d="M-18.2,-14 L18.2,-14 L17.6,-6 L-17.6,-6 Z" fill="%s"/><ellipse cx="0" cy="-34" rx="19" ry="4.6" fill="#7a4a30"/></g>' % (cy - 4, SAGE))
    # resztki dymków (zamrożone, wyblakłe) – pękają po geście B
    rr = random.Random(9)
    left = [('Mamo!', 78, 300, BEIGE), ('Kochanie!', 222, 290, SAGE), ('?!', 300, 380, CREAM2), ('Szybko!', 64, 392, BEIGE), ('Obiad?', 118, 470 - 128, CREAM2)]
    left = [('Mamo!', 70, 296, BEIGE), ('Kochanie!', 222, 282, SAGE), ('?!', 282, 356, CREAM2), ('Szybko!', 96, 344, BEIGE)]
    for i, (wd, x, y, col) in enumerate(left):
        b, w, h = bubble([wd], fill=col, fs=20, tail=(0, 26))
        c = uid('pp'); t0 = 1.28 + .09 * (len(left) - 1 - i)
        drops = ''.join('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="2"/>' % (f(math.cos(a) * 20), f(math.sin(a) * 20), f(rr.uniform(3, 6)), DKG) for a in [k * math.pi / 3 + .3 for k in range(6)])
        cd = uid('pd')
        s.append('<g transform="translate(%s,%s) rotate(%s)"><g class="%s" style="opacity:.75">%s</g><g class="%s">%s</g></g>' % (f(x), f(y), f(rr.uniform(-6, 6)), c, b, cd, drops))
        A('.' + c, K([(0, 'opacity:.8;transform:scale(1)'), (t0, 'opacity:.8;transform:scale(1)', 'cubic-bezier(.3,0,.5,1)'), (t0 + .08, 'opacity:.9;transform:scale(1.1)'), (t0 + .16, 'opacity:0;transform:scale(1.35)')], T))
        A('.' + cd, K([(0, 'opacity:0;transform:scale(.4)'), (t0 + .1, 'opacity:0;transform:scale(.4)', ESOFT), (t0 + .16, 'opacity:1;transform:scale(1)'), (t0 + .5, 'opacity:0;transform:scale(2.2)')], T))
    # smuga „zdmuchnięcia”
    s.append('<path class="swoosh" d="M340,430 C290,350 180,300 50,330" fill="none" stroke="#FBF9F6" stroke-width="6" stroke-linecap="round" pathLength="1" opacity=".9"/>')
    S('.swoosh{stroke-dasharray:.35 1}')
    A('.swoosh', K([(0, 'stroke-dashoffset:.35;opacity:0'), (1.1, 'stroke-dashoffset:.35;opacity:0', ESOFT), (1.15, 'stroke-dashoffset:.35;opacity:.9'), (1.5, 'stroke-dashoffset:-1;opacity:.9'), (1.52, 'opacity:0')], T))
    s.append('</g>')
    # drzwi i światło
    A('.knob', K([(0, 'transform:rotate(0)'), (.12, 'transform:rotate(0)'), (.26, 'transform:rotate(35deg)'), (.4, 'transform:rotate(35deg)'), (.5, 'transform:rotate(0)')], T))
    A('.doorP', K([(0, 'transform:scaleX(1)'), (.3, 'transform:scaleX(1)', 'cubic-bezier(.5,0,.2,1)'), (.75, 'transform:scaleX(.12)')], T))
    A('.beam4', K([(0, 'opacity:0'), (.32, 'opacity:0'), (.75, 'opacity:.5'), (T, 'opacity:.35')], T))
    # B: chód przez drzwi do przodu
    S('.bIn{transform-origin:%spx %spx}' % (cxB, feetB))
    A('.bIn', K([(0, 'opacity:0;transform:translate(26px,-10px) scale(.86)'), (.42, 'opacity:0;transform:translate(26px,-10px) scale(.86)', 'linear'), (.5, 'opacity:1;transform:translate(24px,-9px) scale(.87)', 'cubic-bezier(.3,0,.3,1)'),
                 (1.0, 'opacity:1;transform:translate(0,0) scale(1)')], T))
    A('.bBob', K([(0, 'transform:translateY(0)'), (.45, 'transform:translateY(0)'), (.6, 'transform:translateY(-5px)'), (.75, 'transform:translateY(0)'), (.9, 'transform:translateY(-5px)'), (1.02, 'transform:translateY(0)')], T, 'ease-in-out'))
    meet = (280, 636)
    bl = ((meet[0] - cxB) / sB + 110, 712 - (feetB - meet[1]) / sB)
    ar = ((meet[0] - cxA) / sA + 110, 712 - (feetA - meet[1]) / sA)
    rig(instB, 'B', T, [(0, {'L': (56, 452), 'R': (166, 452)}), (.95, {'L': (56, 452)}), (1.08, {'L': (-40, 200), 'eL': 'down'}, ESNAP), (1.22, {'L': (-70, 230)}),
                        (1.45, {'L': (-20, 330)}, EIO), (1.62, {'L': bl}), (1.98, {'L': bl}), (2.3, {'L': (56, 452)})])
    head(instB, T, [(0, 0, 0, 0), (1.0, -4, -2, 0), (1.6, -6, -3, 2), (2.6, -5, -2, 1), (T, -3, -1, 0)])
    pupils(instB, T, [(0, 0), (1.0, -3), (T, -3)])
    rig(instA, 'A', T, [(0, {'R': (158, 452), 'L': (64, 452)}), (1.55, {'R': (158, 452)}), (1.8, {'R': ar, 'eR': 'down'}), (1.98, {'R': ar}), (2.35, {'R': (134, 372)}, EIO), (T, {'R': (134, 374)})])
    head(instA, T, [(0, 4, 0, 6), (.7, 4, 0, 6), (.95, 8, 3, 0, ESNAP), (1.7, 7, 3, 0), (2.4, 2, 0, 0), (T, 0, 0, 0)])
    pupils(instA, T, [(0, 0), (.7, 0), (.9, 3), (2.2, 3), (2.5, 0), (T, 0)])
    S('.aSlump{transform-origin:%spx %spx}' % (cxA, feetA))
    A('.aSlump', K([(0, 'transform:translateY(6px)'), (.75, 'transform:translateY(6px)'), (1.05, 'transform:translateY(0)')], T))
    A('.tixB', K([(0, 'opacity:1'), (1.97, 'opacity:1', 'steps(1,end)'), (1.98, 'opacity:0')], T, 'linear'))
    A('.tixA', K([(0, 'opacity:0'), (1.97, 'opacity:0', 'steps(1,end)'), (1.98, 'opacity:1')], T, 'linear'))
    A('.tixGrow', K([(0, 'transform:translate(0,-14px) scale(.38)'), (1.98, 'transform:translate(0,-14px) scale(.38)', EIO), (2.35, 'transform:translate(0,-60px) scale(1)')], T))
    A('.tixShine', K([(0, 'transform:rotate(18deg) translateX(-120px)'), (2.75, 'transform:rotate(18deg) translateX(-120px)', EIO), (3.3, 'transform:rotate(18deg) translateX(200px)')], T))
    A('.st4', K([(0, 'opacity:0'), (T, 'opacity:0')], T))
    # kamera: szeroko → wjazd w bilet
    tix_w = L2W(cxA, feetA, sA, 134, 374 - 60)
    cam('c4', T, [(0, 300, 560, 1.06, 300, 560, 0), (1.9, 270, 560, 1.0, 270, 560, 0), (2.0, 270, 560, 1.0, 270, 560, 0, 'cubic-bezier(.6,0,.2,1)'),
                  (2.5, tix_w[0], tix_w[1], 2.95, 270, 610, -2), (T, tix_w[0], tix_w[1], 3.02, 270, 610, -2)])
    s.append('<rect width="540" height="960" fill="url(#warm)" pointer-events="none"/>')
    s.append(vignette(.45))
    # napis „Mam pomysł.” – wjazd z maski
    s.append('<clipPath id="cp4"><rect x="0" y="120" width="540" height="110"/></clipPath>'
             '<g clip-path="url(#cp4)"><g class="t4"><text x="270" y="196" font-size="60" text-anchor="middle" class="serif" fill="%s">Mam pomysł.</text></g></g>' % INK)
    A('.t4', K([(0, 'transform:translateY(90px)'), (.85, 'transform:translateY(90px)', 'cubic-bezier(.2,.9,.3,1)'), (1.2, 'transform:translateY(0)'), (1.95, 'transform:translateY(0)', EOUT), (2.15, 'transform:translateY(-90px)')], T))
    # iris do lodówki
    s.append('<circle cx="270" cy="610" r="760" fill="%s" class="iris4"/>' % SAGE)
    S('.iris4{transform-origin:270px 610px}')
    A('.iris4', K([(0, 'transform:scale(0)'), (3.72, 'transform:scale(0)', 'cubic-bezier(.6,0,.3,1)'), (T, 'transform:scale(1)')], T))
    return ''.join(s), T

# ================= SCENA 5a: Karteczka na lodówce (17–18,5 s) =================
def sc_lodowka():
    T = 1.5; s = []
    s.append('<g class="c5a"><g class="wh5a">')
    s.append('<rect x="-200" y="-200" width="1300" height="1360" fill="url(#fridgeG)"/>')
    s.append('<rect x="-200" y="196" width="1300" height="8" fill="#8fa49b"/>')
    s.append('<rect x="32" y="250" width="16" height="420" rx="8" fill="%s"/>' % DKG)
    # magnesy i rysunek dziecka
    s.append('<g transform="translate(390,300) rotate(5)"><rect x="-70" y="-60" width="140" height="120" fill="#FBF9F6"/><circle cx="-34" cy="-26" r="16" fill="none" stroke="%s" stroke-width="4"/>' % MUST +
             '<path d="M-52,40 L-10,0 L30,40 Z M10,40 v-26 h14 v26" fill="none" stroke="%s" stroke-width="4" stroke-linejoin="round"/><path d="M-60,44 H60" stroke="%s" stroke-width="4"/>' % (RUST, DKG) +
             '<circle cx="0" cy="-58" r="8" fill="%s"/></g>' % BROWN)
    s.append('<g transform="translate(120,190)"><use href="#leaf" transform="scale(1.6) rotate(20)" fill="%s"/></g>' % RUST)
    s.append('<g transform="translate(440,640)"><ellipse rx="20" ry="13" fill="%s"/><ellipse rx="20" ry="13" fill="none" stroke="#fff" stroke-width="2" opacity=".6"/></g>' % BEIGE)
    s.append('<g transform="translate(110,700) rotate(-4)"><rect x="-60" y="-20" width="120" height="40" fill="#FBF9F6"/><path d="M-48,-6 H40 M-48,6 H20" stroke="#b9aea3" stroke-width="3"/><circle cx="0" cy="-20" r="7" fill="%s"/></g>' % DKG)
    # karteczka
    note = ('<g><rect x="-108" y="-92" width="216" height="184" fill="#3a2a20" opacity=".14" transform="translate(4,6)"/>'
            '<rect x="-108" y="-92" width="216" height="184" fill="#F7E7C9"/>'
            '<rect x="-108" y="-92" width="216" height="22" fill="#000" opacity=".04"/>'
            '<text x="0" y="-18" font-size="40" text-anchor="middle" class="serif" fill="%s">Wracam</text>' % INK +
            '<text x="0" y="34" font-size="40" text-anchor="middle" class="serif" fill="%s">w niedzielę</text>' % INK +
            '<g class="nh"><use href="#heartShape" transform="translate(0,70) scale(1.7)" fill="%s"/></g>' % RUST +
            '<circle cx="0" cy="-86" r="10" fill="%s"/><circle cx="-3" cy="-89" r="3" fill="#fff" opacity=".5"/></g>' % DKG)
    s.append('<g transform="translate(262,452)"><g class="note5">%s</g></g>' % note)
    S('.nh{transform-box:fill-box;transform-origin:center}')
    A('.nh', K([(0, 'transform:scale(0)'), (.48, 'transform:scale(0)', 'cubic-bezier(.3,1.4,.5,1)'), (.7, 'transform:scale(1)'), (1.0, 'transform:scale(1)'), (1.1, 'transform:scale(1.15)'), (1.2, 'transform:scale(1)')], T))
    # ręka A (pasiasty rękaw) przykleja karteczkę
    s.append('<g transform="translate(236,560) rotate(-62)"><g class="ha5"><g transform="scale(1.5)">%s</g></g></g>' % side_arm('url(#stripesA)', 'open', '', skin=SKIN, cuff='#ece8df', width=30))
    s.append('<g transform="translate(400,690) scale(-1,1) rotate(-24)"><g class="hm5"><g transform="scale(1.6)">%s</g></g></g>' % side_arm('#7d6a5c', 'thumb', '', width=34))
    s.append('</g></g>')
    A('.note5', K([(0, 'transform:translate(-40px,150px) rotate(-14deg) scale(.9)'), (.05, 'transform:translate(-40px,150px) rotate(-14deg) scale(.9)', 'cubic-bezier(.3,0,.2,1)'),
                   (.35, 'transform:translate(0,0) rotate(-2deg) scale(1.03)'), (.42, 'transform:translate(0,0) rotate(-4deg) scale(1)', ESOFT), (.55, 'transform:translate(0,0) rotate(-3deg) scale(1)')], T))
    slide_x('ha5', T, [(0, -150, 0), (.05, -150, 0), (.35, 18, 0), (.5, 18, 0), (.85, -400, 0)], 'cubic-bezier(.3,0,.2,1)')
    slide_x('hm5', T, [(0, -320, 0), (.65, -320, 0), (.95, 0, 0), (1.05, 0, 0, -10), (1.15, 0, 0, 6), (1.25, 0, 0, -6), (1.35, 0, 0, 0)], 'cubic-bezier(.2,.9,.3,1.04)')
    cam('c5a', T, [(0, 270, 470, 1.0, 270, 470, 0), (T, 262, 460, 1.09, 262, 468, 1)], 'cubic-bezier(.3,0,.4,1)')
    # whip-pan na wyjściu
    A('.wh5a', K([(0, 'transform:translateX(0)'), (1.32, 'transform:translateX(0)', 'cubic-bezier(.7,0,1,.6)'), (T, 'transform:translateX(-260px)')], T))
    s.append(vignette(.4))
    s.append('<g class="streak5a" opacity="0">' + ''.join('<rect x="%s" y="%s" width="%s" height="3" rx="1.5" fill="#FBF9F6" opacity=".7"/>' % (f(R.uniform(0, 400)), f(120 + i * 60), f(R.uniform(120, 260))) for i in range(13)) + '</g>')
    A('.streak5a', K([(0, 'opacity:0;transform:translateX(0)'), (1.34, 'opacity:0;transform:translateX(0)', 'linear'), (1.4, 'opacity:.9;transform:translateX(-40px)'), (T, 'opacity:.9;transform:translateX(-160px)')], T))
    return ''.join(s), T

# ================= SCENA 5b: Wyjazd – z miasta w Beskidy (18,5–20,5 s) =================
def tree(x, base, h, col, trunk=BROWN, kind='round'):
    if kind == 'spruce':
        return '<path d="M%s,%s l%s,%s h%s Z" fill="%s"/>' % (f(x), f(base - h), f(h * .32), f(h), f(-h * .64), col)
    return ('<rect x="%s" y="%s" width="4" height="%s" fill="%s"/>' % (f(x - 2), f(base - h * .45), f(h * .45), trunk) +
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (f(x), f(base - h * .62), f(h * .3), f(h * .38), col))

def sc_droga():
    T = 2.0; s = []
    ground = 800
    s.append('<g class="c5b"><g class="wi5b">')
    # niebo
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="url(#skyB)"/>')
    s.append('<circle cx="400" cy="300" r="140" fill="url(#sunG)"/>')
    # MIASTO (warstwy) i GÓRY (warstwy), góry odsłaniane maską jadącą od prawej
    city_far = ''.join('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x), f(ground - h), f(w), f(h + 10), c) for x, w, h, c in
                       [(-40, 90, 300, '#E3CCC1'), (60, 70, 360, '#d9c3b8'), (140, 110, 260, '#E3CCC1'), (260, 80, 340, '#d9c3b8'), (350, 120, 290, '#E3CCC1'), (480, 90, 330, '#d9c3b8'), (580, 100, 280, '#E3CCC1'), (690, 90, 350, '#d9c3b8')])
    win = ''
    for x, w, h in [(70, 70, 360), (270, 80, 340), (490, 90, 330), (700, 90, 350)]:
        for i in range(3):
            for j in range(6):
                win += '<rect x="%s" y="%s" width="12" height="16" fill="#f4ece4"/>' % (f(x + 10 + i * 22), f(ground - h + 20 + j * 40))
    city_near = ''.join('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x), f(ground - h), f(w), f(h + 10), c) for x, w, h, c in
                        [(-60, 140, 200, '#cdb5a8'), (200, 150, 170, '#c9b1a3'), (450, 160, 210, '#cdb5a8'), (720, 150, 180, '#c9b1a3'), (980, 140, 200, '#cdb5a8')])
    s.append('<g class="cityL">')
    s.append('<g class="px1">%s%s</g>' % (city_far, win))
    s.append('<g class="px2">%s<rect x="600" y="%s" width="6" height="150" fill="%s"/><circle cx="603" cy="%s" r="12" fill="%s"/></g>' % (city_near, ground - 150, BROWN, ground - 158, '#F6DDA8'))
    s.append('</g>')
    mts = ('<g class="mtL"><rect x="-100" y="-100" width="740" height="1160" fill="url(#skyB)"/><circle cx="400" cy="300" r="140" fill="url(#sunG)"/>' +
           '<g class="px1">' + ridge(-60, 900, 470, 50, 7, 11, ground + 10, '#C9D5CF') + ridge(-60, 900, 540, 40, 8, 12, ground + 10, SAGE) + '</g>' +
           '<g class="px2">' + ridge(-60, 1100, 610, 26, 10, 13, ground + 10, DKG) +
           ''.join(tree(x, 640 + R.uniform(-10, 14), R.uniform(70, 110), c) for x, c in zip(range(-40, 1100, 46), itertools.cycle([RUST, MUST, '#c47a3c', DKG, MUST]))) +
           ''.join(tree(x, ground + 6, R.uniform(100, 150), '#3f5a52', kind='spruce') for x in range(-20, 1100, 130)) + '</g></g>')
    s.append('<clipPath id="mclip"><rect class="mwipe" x="0" y="-200" width="1400" height="1400"/></clipPath>')
    s.append('<g clip-path="url(#mclip)">%s</g>' % mts)
    A('.mwipe', K([(0, 'transform:translateX(700px)'), (.45, 'transform:translateX(700px)', 'cubic-bezier(.5,0,.4,1)'), (1.25, 'transform:translateX(-120px)')], T))
    A('.px1', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(-50px)')], T, 'linear'))
    A('.px2', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(-170px)')], T, 'linear'))
    # liście na krawędzi maski
    for i in range(8):
        c = uid('lf'); y = 200 + i * 70; t0 = .45 + i * .05
        s.append('<g transform="translate(0,%s)"><g class="%s"><use href="#leaf" transform="rotate(%s) scale(1.3)" fill="%s"/></g></g>' % (f(y), c, R.randint(0, 360), [RUST, MUST][i % 2]))
        A('.' + c, K([(0, 'opacity:0;transform:translate(560px,0) rotate(0)'), (t0, 'opacity:0;transform:translate(560px,0) rotate(0)', 'cubic-bezier(.5,0,.4,1)'), (t0 + .1, 'opacity:1;transform:translate(470px,-6px) rotate(40deg)'),
                     (t0 + .8, 'opacity:1;transform:translate(-40px,30px) rotate(260deg)'), (t0 + 1.0, 'opacity:0;transform:translate(-90px,40px) rotate(300deg)')], T))
    # droga
    s.append('<rect x="-100" y="%s" width="740" height="300" fill="#d8c3b5"/>' % ground)
    s.append('<rect x="-100" y="%s" width="740" height="8" fill="#cbb3a4"/>' % ground)
    s.append('<g class="road">' + ''.join('<rect x="%s" y="%s" width="40" height="5" rx="2.5" fill="#efe4da"/>' % (x, ground + 60) for x in range(-100, 1300, 90)) + '</g>')
    A('.road', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(-300px)')], T, 'linear'))
    # drogowskaz „Beskidy”
    s.append('<g class="sign5"><rect x="-3" y="-470" width="6" height="470" fill="%s"/>' % BROWN +
             '<path d="M-66,-500 H52 L70,-478 L52,-456 H-66 Z" fill="%s"/>' % DKG +
             '<text x="-4" y="-470" font-size="21" text-anchor="middle" fill="%s" style="font-weight:800;letter-spacing:.08em">BESKIDY</text></g>' % CREAM2)
    A('.sign5', K([(0, 'transform:translate(660px,%spx)' % (ground + 4)), (.6, 'transform:translate(660px,%spx)' % (ground + 4), 'linear'), (T, 'transform:translate(250px,%spx)' % (ground + 4))], T, 'linear'))
    # postacie idą (chód w miejscu), oba plecaki
    sF = .6
    packA_back = '<rect x="40" y="250" width="140" height="170" rx="26" fill="%s"/><rect x="58" y="230" width="104" height="40" rx="18" fill="#4d675f"/>' % DKG
    packA_front = '<path d="M74,214 C68,280 66,340 68,410 M146,214 C152,280 154,340 152,410" stroke="#3f5a52" stroke-width="10" fill="none" stroke-linecap="round"/>'
    instA, instB = 'kA5', 'kB5'
    s.append(FIG('A', 'walk ' + instA, 190, ground + 4, sF, pre=ghost('A', instA, 'walk', packA_back), post=ghost('A', instA, 'walk', packA_front)))
    s.append(FIG('B', 'walk has-pack ' + instB, 352, ground + 4, sF))
    head(instA, T, [(0, 0, 0, 0), (.45, 0, 0, 0), (.7, 8, 4, 0, ESNAP), (1.4, 8, 4, 0), (1.7, 2, 0, 0)])
    pupils(instA, T, [(0, 0), (.45, 0), (.6, 3.2), (1.5, 3.2), (1.7, 0)])
    A('.fig.%s .armR' % instB, K([(0, 'transform:rotate(-7deg)'), (1.0, 'transform:rotate(-7deg)', ESNAP), (1.25, 'transform:rotate(-100deg)'), (1.8, 'transform:rotate(-98deg)'), (T, 'transform:rotate(-60deg)')], T))
    A('.fig.%s .foreR' % instB, K([(0, 'transform:rotate(6deg)'), (1.0, 'transform:rotate(6deg)', ESNAP), (1.25, 'transform:rotate(-12deg)'), (T, 'transform:rotate(-8deg)')], T))
    head(instB, T, [(0, 0, 0, 0), (.6, 0, 0, 0), (.85, -6, -3, 0), (1.3, -6, -3, 0), (1.5, 4, 2, 0), (T, 4, 2, 0)])
    s.append('</g></g>')
    # whip-in z poprzedniego ujęcia
    A('.wi5b', K([(0, 'transform:translateX(220px)'), (.2, 'transform:translateX(0)', 'linear')], T, 'cubic-bezier(0,.6,.3,1)'))
    s.append('<g class="streak5b">' + ''.join('<rect x="%s" y="%s" width="%s" height="3" rx="1.5" fill="#FBF9F6" opacity=".7"/>' % (f(R.uniform(0, 400)), f(140 + i * 58), f(R.uniform(120, 260))) for i in range(12)) + '</g>')
    A('.streak5b', K([(0, 'opacity:.9;transform:translateX(160px)'), (.18, 'opacity:0;transform:translateX(-40px)')], T, 'linear'))
    cam('c5b', T, [(0, 270, 560, 1.0, 270, 560, 0), (T, 290, 560, 1.06, 270, 556, 0)], 'cubic-bezier(.3,0,.5,1)')
    s.append(vignette(.4))
    return ''.join(s), T

# ================= SCENA 5c: Taras – w końcu gorąca kawa (20,5–23 s) =================
def sc_taras():
    T = 2.5; s = []
    rail = 700; sF = .74
    instA, instB = 'kA6', 'kB6'
    cxA, cxB = 196, 384
    feet = rail + (712 - 470) * sF
    s.append('<g class="c5c">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="url(#skyB)"/>')
    s.append('<circle cx="430" cy="380" r="200" fill="url(#sunG)"/>')
    s.append('<g class="px3">' + ridge(-80, 700, 470, 30, 6, 21, 900, '#CFDAD4') + '</g>')
    s.append('<g class="mist"><rect x="-100" y="500" width="760" height="40" rx="20" fill="#F4F2EF" opacity=".55"/></g>')
    s.append('<g class="px4">' + ridge(-80, 700, 540, 34, 7, 22, 900, SAGE) +
             ''.join(tree(x, 590 + R.uniform(-8, 10), R.uniform(50, 80), c) for x, c in zip(range(-60, 700, 34), itertools.cycle([RUST, MUST, DKG, '#c47a3c', MUST, DKG]))) + '</g>')
    s.append('<g class="px5">' + ridge(-80, 700, 630, 20, 8, 23, 900, DKG) + '</g>')
    A('.px3', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(-8px)')], T, 'ease-in-out'))
    A('.px4', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(-20px)')], T, 'ease-in-out'))
    A('.px5', K([(0, 'transform:translateX(0)'), (T, 'transform:translateX(-36px)')], T, 'ease-in-out'))
    A('.mist', K([(0, 'transform:translateX(-20px)'), (T, 'transform:translateX(30px)')], T, 'ease-in-out'))
    # postacie za balustradą
    s.append(FIG('B', 'has-pack hold has-mug ' + instB, cxB, feet, sF))
    s.append(FIG('A', instA, cxA, feet, sF, wrap='sigh', post=ghost('A', instA, '', mug_hand('st6'), arm='R')))
    # balustrada
    s.append('<rect x="-100" y="%s" width="740" height="18" rx="4" fill="#8a6a56"/><rect x="-100" y="%s" width="740" height="5" fill="#a5826c"/>' % (rail, rail))
    s.append(''.join('<rect x="%s" y="%s" width="16" height="300" fill="#7a5c4a"/>' % (x, rail + 18) for x in range(-20, 600, 70)))
    s.append('<rect x="-100" y="%s" width="740" height="14" fill="#8a6a56"/>' % (rail + 110))
    s.append('</g>')
    MOUTH = (128, 214)
    rig(instA, 'A', T, [(0, {'R': R_HOLD, 'L': (62, 452)}), (.2, {'R': R_HOLD}), (.75, {'R': R_SIP}, 'cubic-bezier(.4,0,.2,1)'), (1.35, {'R': (157, 235)}),
                        (1.7, {'R': R_HOLD}), (T, {'R': (186, 232)})])
    head(instA, T, [(0, 0, 0, 0), (.6, -2, 0, 0), (.8, -4, 0, -2), (1.35, -4, 0, -2), (1.7, 3, 1, 3), (2.1, 6, 2, 1), (T, 6, 2, 1)])
    A('.fig.%s .eyes' % instA, K([(0, 'transform:scaleY(1)'), (.75, 'transform:scaleY(1)'), (.9, 'transform:scaleY(.1)'), (1.55, 'transform:scaleY(.1)'), (1.72, 'transform:scaleY(1)')], T))
    S('.sigh{transform-origin:%spx %spx}' % (cxA, feet))
    A('.sigh', K([(0, 'transform:translateY(0) scaleY(1)'), (.75, 'transform:translateY(0) scaleY(1)'), (1.25, 'transform:translateY(-5px) scaleY(1.012)'), (1.7, 'transform:translateY(5px) scaleY(.99)', ESOFT), (T, 'transform:translateY(3px) scaleY(.995)')], T))
    head(instB, T, [(0, 0, 0, 0), (.5, -5, -2, 1), (T, -6, -2, 1)])
    pupils(instB, T, [(0, 0), (.5, -3), (T, -3)])
    A('.st6', K([(0, 'opacity:1;transform:scale(1.15)'), (T, 'opacity:1;transform:scale(1.15)')], T))
    # westchnienie: łuki obok twarzy (poza strefą twarzy)
    face = L2W(cxA, feet, sF, 110, 150)
    sighs = ''.join('<path d="M%s,%s q12,-8 24,0" fill="none" stroke="#FBF9F6" stroke-width="3.2" stroke-linecap="round"/>' % (f(face[0] - 120 - i * 6), f(face[1] - 10 + i * 16)) for i in range(3))
    s.append('<g class="sg">%s</g>' % sighs)
    A('.sg', K([(0, 'opacity:0;transform:translateX(0)'), (1.65, 'opacity:0;transform:translateX(0)', ESOFT), (1.8, 'opacity:1;transform:translateX(-8px)'), (2.3, 'opacity:0;transform:translateX(-26px)')], T))
    mug_w = L2W(cxA, feet, sF, 184, 200)
    cam('c5c', T, [(0, 270, 520, 1.0, 270, 520, 0), (1.9, 262, 520, 1.07, 270, 524, 0), (2.05, 262, 520, 1.07, 270, 524, 0, 'cubic-bezier(.6,0,.3,1)'), (T, mug_w[0], mug_w[1], 1.7, 270, 540, 0)])
    s.append(vignette(.4))
    s.append('<g class="t5"><text x="270" y="182" font-size="54" text-anchor="middle" class="serif" fill="%s">W końcu…</text>' % INK +
             '<text x="270" y="246" font-size="54" text-anchor="middle" class="serif" fill="%s">gorąca kawa.</text></g>' % INK)
    A('.t5', K([(0, 'opacity:0;filter:blur(6px);transform:translateY(10px)'), (.2, 'opacity:0;filter:blur(6px);transform:translateY(10px)', ESOFT), (.48, 'opacity:1;filter:blur(0);transform:translateY(0)'),
                (2.06, 'opacity:1;filter:blur(0);transform:translateY(0)', EOUT), (2.25, 'opacity:0;filter:blur(0);transform:translateY(-10px)')], T))
    s.append('<circle cx="270" cy="520" r="620" fill="%s" class="iris5"/>' % CREAM)
    S('.iris5{transform-origin:270px 520px}')
    A('.iris5', K([(0, 'transform:scale(0)'), (2.22, 'transform:scale(0)', 'cubic-bezier(.6,0,.3,1)'), (T, 'transform:scale(1)')], T))
    return ''.join(s), T

# ================= SCENA 6: Logo z kamieni + CTA (23–27 s) =================
LOGO = json.loads((ROOT / 'logo/oryginal/logo-wektor.json').read_text())
OX, OY = -806.12, -829.13   # przesunięcie lockupu (środek w 0,0)

def sc_logo():
    T = 4.0; s = []
    LS = .44; LX, LY = 270, 292
    s.append('<g class="c6">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="%s"/>' % CREAM)
    s.append('<ellipse cx="270" cy="330" rx="400" ry="380" fill="url(#halo6)"/>')
    # kamienie (wypełnione) spadają i układają się w sygnet
    stones = [((0, 62), 236, 126, DKG, 0), ((0, -132), 121, 112, SAGE, .28), ((0, -318), 55, 56, BEIGE, .52)]
    for (sx, sy), rx, ry, col, t0 in stones:
        c, q = uid('st'), uid('sq')
        wx, wy = LX + sx * LS, LY + sy * LS
        s.append('<g transform="translate(%s,%s)"><g class="%s"><g class="%s"><ellipse cx="0" cy="0" rx="%s" ry="%s" fill="%s"/>'
                 '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#fff" opacity=".18"/></g></g></g>' % (f(wx), f(wy), c, q, f(rx * LS), f(ry * LS), col, f(-rx * LS * .3), f(-ry * LS * .35), f(rx * LS * .35), f(ry * LS * .22)))
        A('.' + c, K([(0, 'transform:translateY(-300px) rotate(-10deg);opacity:1'), (t0, 'transform:translateY(-300px) rotate(-10deg);opacity:1', 'cubic-bezier(.55,0,.9,.6)'), (t0 + .3, 'transform:translateY(0) rotate(0deg);opacity:1'),
                     (1.1, 'transform:translateY(0) rotate(0);opacity:1', EIO), (1.45, 'transform:translateY(0) rotate(0);opacity:.26')], T))
        S('.%s{transform-origin:0 %spx}' % (q, f(ry * LS)))
        A('.' + q, K([(0, 'transform:scale(1,1)'), (t0 + .3, 'transform:scale(1,1)', 'ease-out'), (t0 + .36, 'transform:scale(1.06,.9)', ESOFT), (t0 + .5, 'transform:scale(1,1)')], T))
    # aktualne logo: sygnet (kontur) → napis litera po literze → hasło
    g = '<g transform="translate(%s,%s) scale(%s)"><g style="color:%s" fill="currentColor" fill-rule="evenodd"><g transform="translate(%s,%s)">' % (f(LX), f(LY), f(LS), DKG, f(OX), f(OY))
    g += '<g class="sg6"><path d="%s"/></g>' % LOGO['sign']
    for i, L in enumerate(LOGO['letters']):
        c = uid('lt')
        g += '<g class="%s lt6"><path d="%s"/></g>' % (c, L['d'])
        t0 = 1.3 + i * .055
        A('.' + c, K([(0, 'opacity:0;transform:translateY(40px) scale(.6)'), (t0, 'opacity:0;transform:translateY(40px) scale(.6)', 'cubic-bezier(.2,.9,.3,1.05)'), (t0 + .3, 'opacity:1;transform:translateY(0) scale(1)')], T))
    g += '<g class="tg6"><path d="%s"/></g>' % LOGO['tag']
    g += '</g></g></g>'
    s.append(g)
    S('.lt6{transform-box:fill-box;transform-origin:50% 100%}')
    A('.sg6', K([(0, 'opacity:0'), (1.05, 'opacity:0', EIO), (1.4, 'opacity:1')], T))
    A('.tg6', K([(0, 'opacity:0;transform:translateY(12px)'), (1.85, 'opacity:0;transform:translateY(12px)', ESNAP), (2.1, 'opacity:1;transform:translateY(0)')], T))
    # data
    s.append('<g class="d6"><text x="270" y="520" font-size="23" text-anchor="middle" fill="%s" style="font-weight:800;letter-spacing:.04em">5–7.11 · Karolowy Dwór, Wisła</text></g>' % INK)
    A('.d6', vis(2.05, None, T, .22, 14))
    # przycisk
    s.append('<g transform="translate(270,590)"><g class="btn6"><rect x="-162" y="-44" width="324" height="88" rx="44" fill="#3a2a20" opacity=".15" transform="translate(0,5)"/>'
             '<rect x="-162" y="-44" width="324" height="88" rx="44" fill="%s"/>' % BROWN +
             '<text x="0" y="-4" font-size="31" text-anchor="middle" fill="%s" style="font-weight:800">Zapisz się →</text>' % CREAM2 +
             '<text x="0" y="27" font-size="22" text-anchor="middle" fill="%s" style="font-weight:700;letter-spacing:.03em">shebalance.pl</text></g></g>' % '#F1E2D3')
    A('.btn6', K([(0, 'opacity:0;transform:scale(.6)'), (2.4, 'opacity:0;transform:scale(.6)', 'cubic-bezier(.2,.9,.3,1.04)'), (2.75, 'opacity:1;transform:scale(1)'), (3.25, 'opacity:1;transform:scale(1)', 'ease-in-out'), (3.5, 'opacity:1;transform:scale(1.04)'), (3.75, 'opacity:1;transform:scale(1)')], T))
    # kubek z parą – klamra z początkiem
    mug = ('<g transform="scale(1.25)"><ellipse cx="0" cy="11" rx="26" ry="4" fill="#000" opacity=".08"/>'
           '<path d="M-19,-34 L19,-34 L17,4 Q16,10 10,10 L-10,10 Q-16,10 -17,4 Z" fill="#FBF9F6" stroke="%s" stroke-width="1.8"/>' % DKG +
           '<path d="M18,-24 Q32,-24 30,-11 Q28,-1 16,-2" fill="none" stroke="%s" stroke-width="1.8"/>' % DKG +
           '<path d="M-18.2,-14 L18.2,-14 L17.6,-6 L-17.6,-6 Z" fill="%s"/>' % SAGE +
           '<ellipse cx="0" cy="-34" rx="19" ry="4.6" fill="#7a4a30" stroke="%s" stroke-width="1.4"/>' % DKG +
           '<g transform="translate(0,-40)">%s</g></g>' % steam_paths('stm', 3, 28, 5, 2.4, '#FBF9F6', 9, DKG))
    s.append('<g transform="translate(270,748)"><g class="mug6">%s</g></g>' % mug)
    A('.mug6', K([(0, 'opacity:0;transform:translateY(24px)'), (2.95, 'opacity:0;transform:translateY(24px)', ESNAP), (3.25, 'opacity:1;transform:translateY(0)')], T))
    s.append('</g>')
    cam('c6', T, [(0, 270, 480, 1.05, 270, 480, 0), (T, 270, 470, 1.0, 270, 470, 0)], 'cubic-bezier(.3,0,.4,1)')
    s.append(vignette(.3))
    return ''.join(s), T

SCENES = [('s1', sc_poranek, CREAM), ('s2', sc_lawina, CREAM), ('s3', sc_przeciazenie, CREAM), ('s4', sc_brunetka, CREAM),
          ('s5a', sc_lodowka, SAGE), ('s5b', sc_droga, CREAM), ('s5c', sc_taras, CREAM), ('s6', sc_logo, CREAM)]

def build():
    parts, sj = [], []
    t = 0
    for sid, fn, bg in SCENES:
        svg, T = fn()
        parts.append('<g class="scene" data-s="%s">%s</g>' % (sid, svg))
        sj.append("{id:'%s',d:%s,bg:'%s'}" % (sid, f(T), bg)); t += T
    tpl = (HERE / 'szablon.html').read_text(encoding='utf-8')
    html = (tpl.replace('@@CSS@@', '\n'.join(CSS)).replace('@@DEFS@@', DEFS_EXTRA + '<linearGradient id="doorLight" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBE9C6"/><stop offset="1" stop-color="#F3D7B0"/></linearGradient>')
            .replace('@@SCENES@@', '\n'.join(parts)).replace('@@SCJS@@', ','.join(sj)))
    OUT.write_text(html, encoding='utf-8')
    print('ok', OUT, len(html), 'reguł', len(CSS), 'czas', t)

if __name__ == '__main__':
    build()
