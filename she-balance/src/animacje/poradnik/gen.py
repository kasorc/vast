# -*- coding: utf-8 -*-
# Generator animacji „Zadbasz o siebie. Tylko najpierw…” (SheBalance, reel 9:16, 25 s, wersja 2)
# → src/animacje/poradnik.html.  Uruchom: python3 src/animacje/poradnik/gen.py && python3 src/zbuduj_animacje.py poradnik
# Sceny (start, s): 0 hak · 2.5 praca · 6.5 dom · 10.5 jeszcze · 13.5 potem · 16.5 pytanie · 18.5 w końcu · 22 logo (koniec 25)
# Całość = jedno zdanie (napis zawsze w tym samym miejscu) + karteczka „DO ZROBIENIA” z punktem „zadbać o siebie”, który spada.
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pomoc import *          # K, A, S, uid, f, rig, head, pupils, FIG, L2W, ghost, cam, bubble, place_bubble, side_arm, kitchen, counter, mug_hand…
from pomoc import CSS

# ---------- TEKST DO PODMIANY (data i miejsce campu na planszy końcowej) ----------
DATA_CAMPU = "5–7.11 · Beskidy · 20 miejsc"

PANTS = '#2a2a2e'
EBOUNCE = 'cubic-bezier(.2,.9,.3,1.04)'
EV = []          # oś zdarzeń (sekundy globalne) – do raportu / muzyki
def ev(t, what): EV.append((round(t, 2), what))

def tree(x, base, h, col, trunk=BROWN):
    return ('<rect x="%s" y="%s" width="4" height="%s" fill="%s"/>' % (f(x - 2), f(base - h * .45), f(h * .45), trunk) +
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (f(x), f(base - h * .62), f(h * .3), f(h * .38), col))

def mtext(txt, x, y, fs, col=INK, weight=700, cls='', anchor='middle', extra=''):
    return '<text x="%s" y="%s" font-size="%s" text-anchor="%s" class="%s" fill="%s" style="font-weight:%s" %s>%s</text>' % (f(x), f(y), fs, anchor, cls, col, weight, extra, txt)

def vignette2(op=.4):
    return '<rect width="540" height="960" fill="url(#vignette)" opacity="%s" pointer-events="none"/>' % f(op)

def sparkle(x, y, sc, col, delay, dur=1.6):
    return ('<g transform="translate(%s,%s) scale(%s)"><g class="twinkle" style="animation-delay:-%ss;animation-duration:%ss"><use href="#star" fill="%s"/></g></g>'
            % (f(x), f(y), f(sc), f(delay), f(dur), col))

def streaks(T, t_in=None, t_out=None):
    c = uid('stk')
    s = '<g class="%s">' % c + ''.join('<rect x="%s" y="%s" width="%s" height="4" rx="2" fill="#FBF9F6" opacity=".7"/>' % (f(R.uniform(0, 420)), f(130 + i * 62), f(R.uniform(120, 260))) for i in range(12)) + '</g>'
    if t_out is not None:
        A('.' + c, K([(0, 'opacity:0;transform:translateX(0)'), (t_out, 'opacity:0;transform:translateX(0)', 'linear'), (t_out + .06, 'opacity:.9;transform:translateX(-40px)'), (T, 'opacity:.9;transform:translateX(-160px)')], T))
    else:
        A('.' + c, K([(0, 'opacity:.9;transform:translateX(160px)'), (.2, 'opacity:0;transform:translateX(-40px)')], T, 'linear'))
    return s

def whip(cls, T, t_in=True, t_out=None):
    fr = []
    if t_in: fr += [(0, 'transform:translateX(300px)'), (.24, 'transform:translateX(0)', 'cubic-bezier(0,.6,.3,1)')]
    else: fr += [(0, 'transform:translateX(0)')]
    if t_out is not None: fr += [(t_out, 'transform:translateX(0)', 'cubic-bezier(.7,0,1,.6)'), (T, 'transform:translateX(-300px)')]
    if fr[0][0] == 0 and t_in: fr[0] = (0, 'transform:translateX(300px)', 'cubic-bezier(0,.6,.3,1)')
    A('.' + cls, K(fr, T))

# ================= NAPIS – jedno zdanie, zawsze w tym samym miejscu =================
CY1, CY2, CFS = 166, 224, 52
S('.scene.active .cw.w{transform-box:fill-box;transform-origin:50% 100%;animation:cpw .34s cubic-bezier(.2,.9,.3,1.04) both;animation-delay:calc(var(--d0) + var(--w) * .11s)}'
  '@keyframes cpw{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}')

def cap_text(txt, y, fs=CFS, x=270, col=INK, serif=True):
    return ('<text x="%s" y="%s" font-size="%s" text-anchor="middle" class="%s" fill="%s"%s>%s</text>'
            % (f(x), f(y), fs, 'serif' if serif else '', col, '' if serif else ' style="font-weight:700"', txt))

def caption(T, lines, prev=None):
    """lines: [(tekst, y, t0, fs, serif, kolor)] – słowa wskakują po kolei (ten sam styl w każdej scenie).
    prev: poprzednia fraza (stan z końca poprzedniej sceny) – gaśnie w 0,18 s, nowa wchodzi w to samo miejsce."""
    out = '<ellipse cx="270" cy="196" rx="300" ry="96" fill="url(#capGlow)" pointer-events="none"/>'
    if prev:
        c = uid('cpp')
        out += '<g class="%s">%s</g>' % (c, ''.join(cap_text(*p) for p in prev))
        A('.' + c, K([(0, 'opacity:1;transform:translateY(0)'), (.18, 'opacity:0;transform:translateY(-10px)')], T, EOUT))
    for (txt, y, t0, fs, serif, col) in lines:
        out += ('<text x="270" y="%s" font-size="%s" text-anchor="middle" class="%s wsplit cw" fill="%s" style="--d0:%ss%s">%s</text>'
                % (f(y), fs, 'serif' if serif else '', col, f(t0), '' if serif else ';font-weight:700', txt))
    return out

def L(txt, y, t0, fs=CFS, serif=True, col=INK): return (txt, y, t0, fs, serif, col)
def P(txt, y, fs=CFS, serif=True, col=INK): return (txt, y, fs, 270, col, serif)

# ================= KARTECZKA „DO ZROBIENIA” =================
NX, NY, NW = 290, 270, 178
RH, ROW0, VIS = 30, NY + 62, 6
# punkty listy: (czas globalny wstawienia, tekst); „zadbać o siebie” jest pierwszy (najstarszy) – każdy nowy wchodzi na górę i spycha go w dół
ITEMS = [(-1, 'SELF')]
def add_item(tg, txt):
    ITEMS.append((tg, txt)); ev(tg, 'lista: +„%s” (punkt „zadbać o siebie” spada)' % txt)

def row_text(txt, kind, grey=False):
    if txt == 'SELF':
        col = '#9a948c' if grey else DKG
        return ('<rect x="-6" y="-19" width="%s" height="26" rx="6" fill="%s" opacity="%s"/>' % (NW - 16, SAGE, '.18' if grey else '.38') +
                '<rect x="4" y="-14" width="15" height="15" rx="3" fill="none" stroke="%s" stroke-width="2"/>' % col +
                '<text x="27" y="0" font-size="18" fill="%s" style="font-weight:800">zadbać o siebie</text>' % col)
    if txt == '~':
        w = R.uniform(70, 120)
        return ('<rect x="4" y="-14" width="15" height="15" rx="3" fill="none" stroke="#8a8278" stroke-width="2"/>'
                '<path d="M27,-6 q8,-6 16,0 t16,0 t16,0 t16,0 t16,0" fill="none" stroke="#8a8278" stroke-width="2.2" stroke-linecap="round" transform="scale(%s,1)"/>' % f(w / 80))
    return ('<rect x="4" y="-14" width="15" height="15" rx="3" fill="none" stroke="%s" stroke-width="2"/>' % INK +
            '<text x="27" y="0" font-size="18" fill="%s" style="font-weight:700">%s</text>' % (INK, txt))

def note(T, t0g, items=None, mode='normal', fall=None, grey_self=False, scroll=None, enter=None):
    """Karteczka; wiersz r ma y = ROW0 + r*RH. mode 'unroll' – papier rozwija się do dołu kadru."""
    items = items if items is not None else [it for it in ITEMS if it[0] <= t0g + T]
    cls_all = uid('nt')
    clip = uid('ncl')
    paper_h = 62 + VIS * RH
    s = '<g transform="rotate(-2 %s %s)"><g class="%s">' % (f(NX + NW / 2), f(NY), cls_all)
    s += '<rect x="%s" y="%s" width="%s" height="%s" rx="4" fill="#3a2a20" opacity=".15" transform="translate(3,6)" class="pp%s"/>' % (NX, NY, NW, paper_h, cls_all)
    s += '<rect x="%s" y="%s" width="%s" height="%s" rx="4" fill="#F7EEDC" class="pp%s"/>' % (NX, NY, NW, paper_h, cls_all)
    s += ''.join('<path d="M%s,%s H%s" stroke="#E6D6BC" stroke-width="1.2"/>' % (NX + 8, ROW0 + 9 + i * RH, NX + NW - 8) for i in range(30) if ROW0 + 9 + i * RH < (1000 if mode == 'unroll' else NY + paper_h - 4))
    s += '<rect x="%s" y="%s" width="%s" height="10" fill="%s" opacity=".55"/>' % (NX + NW / 2 - 30, NY - 5, 60, BEIGE)
    s += '<text x="%s" y="%s" font-size="18" fill="%s" style="font-weight:800;letter-spacing:.08em">DO ZROBIENIA:</text>' % (NX + 14, NY + 30, BROWN)
    s += '<clipPath id="%s"><rect class="cr%s" x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (clip, cls_all, NX, NY + 38, NW, 186)
    if mode == 'unroll':
        S('.pp%s{transform-box:view-box;transform-origin:0 %spx}.cr%s{transform-box:view-box;transform-origin:0 %spx}' % (cls_all, NY, cls_all, NY + 38))
        sc = 1030 / paper_h
        A('.pp%s' % cls_all, K([(0, 'transform:scaleY(1)'), (.05, 'transform:scaleY(1)', 'cubic-bezier(.4,0,.2,1)'), (.45, 'transform:scaleY(%s)' % f(sc))], T))
        A('.cr%s' % cls_all, K([(0, 'transform:scaleY(1)'), (.05, 'transform:scaleY(1)', 'cubic-bezier(.4,0,.2,1)'), (.45, 'transform:scaleY(%s)' % f((1030 - 38) / 186))], T))
    rows = '<g clip-path="url(#%s)"><g class="sc%s">' % (clip, cls_all)
    if scroll:
        A('.sc%s' % cls_all, K([(0, 'transform:translateY(0)')] + [((t, 'transform:translateY(%spx)' % f(y), e) if e else (t, 'transform:translateY(%spx)' % f(y))) for t, y, e in scroll], T))
    times = [it[0] for it in items]
    for idx, (tg, txt) in enumerate(items):
        newer = [x for x in times[idx + 1:]]
        def row_at(g): return sum(1 for x in newer if x <= g)
        r0 = row_at(t0g)
        if r0 > 40: continue
        ins = [x - t0g for x in newer if t0g < x <= t0g + T]
        c = uid('nr')
        y0 = ROW0 + r0 * RH
        appear = tg - t0g if t0g < tg <= t0g + T else None
        fr = []
        if appear is not None:
            fr += [(0, 'opacity:0;transform:translate(0,%spx)' % f(ROW0 - 16)), (appear, 'opacity:0;transform:translate(0,%spx)' % f(ROW0 - 16), ESNAP), (appear + .24, 'opacity:1;transform:translate(0,%spx)' % f(ROW0))]
            r = 0
        else:
            fr += [(0, 'opacity:1;transform:translate(0,%spx)' % f(y0))]
            r = r0
        for t in ins:
            if appear is not None and t <= appear: continue
            fr += [(t, 'opacity:1;transform:translate(0,%spx)' % f(ROW0 + r * RH), 'cubic-bezier(.4,0,.2,1)'), (t + .26, 'opacity:1;transform:translate(0,%spx)' % f(ROW0 + (r + 1) * RH))]
            r += 1
        fr.sort(key=lambda x: x[0])
        # usuń duplikaty czasów
        ded = []
        for x in fr:
            if ded and abs(ded[-1][0] - x[0]) < 1e-4: ded[-1] = x
            else: ded.append(x)
        A('.' + c, K(ded, T))
        rows += '<g transform="translate(%s,0)"><g class="%s">%s</g></g>' % (NX + 8, c, row_text(txt, 'x', grey=grey_self))
    rows += '</g></g>'
    s += rows + '</g></g>'
    fr = []
    if enter is not None:
        fr = [(0, 'opacity:0;transform:translate(60px,-20px) rotate(8deg)'), (enter, 'opacity:0;transform:translate(60px,-20px) rotate(8deg)', ESNAP), (enter + .35, 'opacity:1;transform:translate(0,0) rotate(0deg)')]
    if fall is not None:
        if not fr: fr = [(0, 'opacity:1;transform:translate(0,0) rotate(0deg)')]
        fr += [(fall, 'opacity:1;transform:translate(0,0) rotate(0deg)', 'cubic-bezier(.5,0,.9,.5)'), (fall + .55, 'opacity:0;transform:translate(40px,620px) rotate(28deg)')]
    if fr:
        S('.%s{transform-origin:%spx %spx}' % (cls_all, NX + NW / 2, NY))
        A('.' + cls_all, K(fr, T))
    return s

def bubble_at(T, x, y, t0, lines, fill=CREAM2, tail=(0, 30), fs=20, t_off=None, k=.6):
    b, w, h = bubble(lines, fill=fill, stroke=BROWN, fs=fs, tail=tail, k=k)
    pile = (t_off, 0, 0, .8, 0) if t_off is not None else None
    return place_bubble(b, x, y, T, t0, pile=pile, pop_dur=.3)

# ================= tła / rekwizyty =================
def office(desk_y, wall='#EAE4DC'):
    s = '<rect x="-400" y="-400" width="1340" height="1760" fill="%s"/>' % wall
    # okno z żaluzjami
    s += '<rect x="20" y="300" width="150" height="190" rx="4" fill="#DDE6E1"/>' + ''.join('<rect x="20" y="%s" width="150" height="9" fill="#F4F2EF" opacity=".9"/>' % (306 + i * 15) for i in range(12)) + \
         '<rect x="20" y="300" width="150" height="190" rx="4" fill="none" stroke="%s" stroke-width="6"/>' % BEIGE
    # tablica z karteczkami
    s += '<rect x="-60" y="520" width="70" height="90" rx="4" fill="%s"/>' % BEIGE
    s += '<rect x="-400" y="%s" width="1340" height="16" fill="#D9B99B"/><rect x="-400" y="%s" width="1340" height="4" fill="#E9D3BC"/>' % (desk_y, desk_y)
    s += '<rect x="-400" y="%s" width="1340" height="600" fill="%s"/><rect x="-400" y="%s" width="1340" height="12" fill="#000" opacity=".12"/>' % (desk_y + 16, DKG, desk_y + 16)
    return s

def laptop(x, base_y, lid_cls, cnt_classes):
    """laptop przodem; ekran 150×100, licznik maili (osobne <text> na każdą wartość)."""
    s = '<g>'
    s += '<path d="M%s,%s L%s,%s L%s,%s L%s,%s Z" fill="#cfc8bd"/>' % (f(x - 92), f(base_y), f(x + 92), f(base_y), f(x + 80), f(base_y - 10), f(x - 80), f(base_y - 10))
    s += '<g class="%s"><rect x="%s" y="%s" width="160" height="108" rx="7" fill="#2f3b37"/>' % (lid_cls, f(x - 80), f(base_y - 118))
    s += '<rect x="%s" y="%s" width="148" height="96" rx="3" fill="#F4F2EF"/>' % (f(x - 74), f(base_y - 112))
    s += '<rect x="%s" y="%s" width="148" height="16" fill="%s"/>' % (f(x - 74), f(base_y - 112), SAGE)
    s += '<g transform="translate(%s,%s)"><rect x="-22" y="-15" width="44" height="30" rx="3" fill="none" stroke="%s" stroke-width="3"/><path d="M-22,-15 L0,4 L22,-15" fill="none" stroke="%s" stroke-width="3"/></g>' % (f(x - 40), f(base_y - 56), DKG, DKG)
    s += ''.join('<rect x="%s" y="%s" width="%s" height="4" rx="2" fill="#d6cdc1"/>' % (f(x - 62), f(base_y - 30 + i * 8), w) for i, w in enumerate((90, 60)))
    for c, v in cnt_classes:
        s += '<g class="%s"><circle cx="%s" cy="%s" r="22" fill="%s"/><text x="%s" y="%s" font-size="%s" text-anchor="middle" fill="#FBF9F6" style="font-weight:900">%s</text></g>' % (
            c, f(x + 30), f(base_y - 58), RUST, f(x + 30), f(base_y - 51), 20 if len(v) < 3 else 17, v)
    s += '</g></g>'
    return s

def phone_svg(cls):
    return ('<g class="%s"><path d="M-30,-6 L22,-10 L34,6 L-20,10 Z" fill="#2f3b37"/><path d="M-26,-4 L20,-8 L30,5 L-17,8 Z" fill="#46564f"/>'
            '<path class="gl%s" d="M-26,-4 L20,-8 L30,5 L-17,8 Z" fill="#F6DDA8"/></g>' % (cls, cls))

def vib(cls, T, starts):
    fr = [(0, 'transform:translate(0,0) rotate(0)')]
    for t0 in starts:
        fr += [(t0 - .01, 'transform:translate(0,0) rotate(0)')]
        for i in range(8):
            fr.append((t0 + .04 * (i + 1), 'transform:translate(%spx,0) rotate(%sdeg)' % (f(2.4 * (-1) ** i), f(3 * (-1) ** i))))
        fr.append((t0 + .36, 'transform:translate(0,0) rotate(0)'))
    S('.%s{transform-box:fill-box;transform-origin:center}' % cls)
    A('.' + cls, K(fr, T, 'linear'))
    g = [(0, 'opacity:0')]
    for t0 in starts: g += [(t0 - .01, 'opacity:0'), (t0 + .04, 'opacity:.9'), (t0 + .9, 'opacity:.9'), (t0 + 1.1, 'opacity:0')]
    A('.gl' + cls, K(g, T, 'linear'))

def paper_sheet(txt, w=176, h=74, fs=24):
    return ('<g><rect x="%s" y="%s" width="%s" height="%s" fill="#3a2a20" opacity=".14" transform="translate(3,4)"/>' % (f(-w / 2), f(-h / 2), w, h) +
            '<rect x="%s" y="%s" width="%s" height="%s" fill="#FBF9F6" stroke="#d9cfc2"/>' % (f(-w / 2), f(-h / 2), w, h) +
            '<path d="M%s,%s H%s M%s,%s H%s" stroke="#d6cdc1" stroke-width="3"/>' % (f(-w / 2 + 14), f(h / 2 - 16), f(w / 2 - 50), f(-w / 2 + 14), f(h / 2 - 8), f(w / 2 - 70)) +
            '<text x="0" y="4" font-size="%s" text-anchor="middle" fill="%s" style="font-weight:900;letter-spacing:.02em">%s</text></g>' % (fs, RUST, txt))

def hoodie():
    return ('<g transform="translate(6,6)"><path d="M-14,-6 C-10,-20 22,-22 30,-8 C40,10 34,38 20,44 C6,48 -12,40 -14,26 Z" fill="%s"/>' % MUST +
            '<path d="M-6,4 Q8,10 24,2 M0,22 Q12,28 26,20" stroke="#b9862a" stroke-width="2" fill="none"/></g>')

def notebook():
    return ('<g transform="rotate(-8)"><rect x="-4" y="-34" width="64" height="48" rx="3" fill="%s" stroke="#c9ad9f" stroke-width="1.4"/>' % BEIGE +
            '<rect x="-4" y="-34" width="8" height="48" fill="%s"/>' % BROWN +
            '<rect x="12" y="-24" width="40" height="13" rx="2" fill="#F7F4EE"/><path d="M16,-18 H46" stroke="#9a8a7e" stroke-width="1.4"/></g>')

def plate():
    return '<g><ellipse cx="14" cy="0" rx="30" ry="9" fill="#FBF9F6" stroke="#d6cdc1" stroke-width="1.6"/><ellipse cx="14" cy="-1" rx="16" ry="4" fill="none" stroke="#e6ded3" stroke-width="1.4"/></g>'

def laundry():
    return ('<g><path d="M-62,0 L-52,-44 L52,-44 L62,0 Z" fill="%s"/>' % BEIGE +
            '<path d="M-52,-44 C-40,-70 -10,-62 0,-52 C14,-76 46,-64 52,-44 Z" fill="#F7F4EE"/><path d="M-30,-56 C-20,-66 0,-60 6,-52" stroke="%s" stroke-width="6" fill="none"/>' % SAGE +
            '<path d="M14,-60 c10,-8 26,-6 30,8" stroke="%s" stroke-width="6" fill="none"/>' % MUST +
            ''.join('<path d="M%s,-40 L%s,-4" stroke="#cdb5a8" stroke-width="2"/>' % (x, x * 1.12) for x in range(-40, 50, 14)) + '</g>')

# ================= SCENA 1: Hak (0–2,5 s) =================
def sc_hak():
    T = 2.5; s = []
    inst = 'qA1'
    cx, feet, sc = 172, 900, .82
    s.append('<g class="w1"><g class="c1">')
    s.append('<rect x="-400" y="-400" width="1340" height="1760" fill="%s"/>' % CREAM)
    s.append('<rect x="-400" y="%s" width="1340" height="400" fill="#E9DCD2"/><rect x="-400" y="%s" width="1340" height="6" fill="#DCC9BD"/>' % (feet - 8, feet - 8))
    # okno w ciepłym świetle + roślina
    s.append('<rect x="24" y="300" width="130" height="200" rx="6" fill="url(#kDawn)"/><rect x="24" y="300" width="130" height="200" rx="6" fill="none" stroke="%s" stroke-width="8"/><path d="M89,300 V500" stroke="%s" stroke-width="6"/>' % (SAGE, SAGE))
    s.append('<path d="M154,300 L330,%s L210,%s L24,500 Z" fill="#FFF6E2" opacity=".35"/>' % (feet, feet))
    # fotel z książką i matą
    s.append('<g transform="translate(400,%s)">' % (feet - 4) +
             '<rect x="-96" y="-210" width="192" height="150" rx="40" fill="%s"/>' % SAGE +
             '<rect x="-118" y="-120" width="50" height="110" rx="22" fill="#93A99F"/><rect x="68" y="-120" width="50" height="110" rx="22" fill="#93A99F"/>' +
             '<rect x="-80" y="-96" width="160" height="56" rx="18" fill="#B3C4BD"/><rect x="-86" y="-44" width="172" height="40" rx="10" fill="#93A99F"/>' +
             '<rect x="-76" y="-4" width="10" height="4" fill="%s"/><rect x="66" y="-4" width="10" height="4" fill="%s"/>' % (BROWN, BROWN) +
             '<g transform="translate(-10,-102) rotate(-6)"><rect x="-30" y="-8" width="60" height="12" rx="2" fill="%s"/><rect x="-28" y="-6" width="56" height="3" fill="#F7F4EE"/></g>' % RUST +
             '<g transform="translate(-130,-30)"><rect x="-14" y="-104" width="28" height="104" rx="14" fill="%s"/><ellipse cx="0" cy="-104" rx="14" ry="6" fill="#C9B1A5"/></g>' % BEIGE +
             '</g>')
    ph = uid('ph')
    s.append('<g transform="translate(%s,%s) scale(.8)">%s</g>' % (460, feet - 112, phone_svg(ph)))
    vib(ph, T, [1.35])
    ev(1.35, 'telefon wibruje (scena 1)')
    s.append(FIG('A', inst, cx, feet, sc, wrap='st1w', post=ghost('A', inst, '', mug_hand('st1'), arm='R') + ghost('A', inst, '', '<g transform="translate(-4,-6) rotate(-12)"><rect x="-10" y="-34" width="20" height="62" rx="3" fill="%s"/><rect x="-7" y="-31" width="3" height="56" fill="#F7F4EE"/><ellipse cx="4" cy="6" rx="9" ry="10" fill="%s"/></g>' % (RUST, SKIN), arm='L')))
    s.append('</g></g>')
    S('.st1w{transform-origin:%spx %spx}' % (cx, feet))
    A('.st1w', K([(0, 'transform:translateX(0)'), (.5, 'transform:translateX(0)', EIO), (1.2, 'transform:translateX(26px)'), (T, 'transform:translateX(26px)')], T))
    rig(inst, 'A', T, [(0, {'R': R_HOLD, 'L': (62, 452)}), (.5, {'R': R_HOLD, 'L': (62, 452)}), (.95, {'R': R_SIP}, 'cubic-bezier(.4,0,.2,1)'), (1.2, {'R': R_SIP}),
                       (1.45, {'R': R_HOLD}, ESNAP), (2.0, {'L': (62, 452)}), (2.3, {'L': (40, 420)}), (T, {'R': (186, 232)})])
    head(inst, T, [(0, -3, -1, 0), (.6, 3, 1, 0), (1.2, 2, 0, 1), (1.45, 2, 0, 1), (1.6, 9, 5, 0, ESNAP), (2.1, 8, 5, 0), (T, 8, 5, 2)])
    pupils(inst, T, [(0, 0), (1.45, 0), (1.55, 3.4), (T, 3.4)])
    A('.fig.%s .eyes' % inst, K([(0, 'transform:scaleY(1)'), (.95, 'transform:scaleY(1)'), (1.1, 'transform:scaleY(.15)'), (1.4, 'transform:scaleY(.15)'), (1.52, 'transform:scaleY(1.1)', ESNAP), (T, 'transform:scaleY(1)')], T))
    A('.fig.%s .smile' % inst, K([(0, 'transform:scale(1.1,1.2)'), (1.5, 'transform:scale(1.1,1.2)', ESNAP), (1.7, 'transform:scale(.92,.9)'), (T, 'transform:scale(.92,.9)')], T))
    A('.st1', K([(0, 'opacity:1'), (T, 'opacity:1')], T))
    cam('c1', T, [(0, 270, 560, 1.0, 270, 560, 0), (1.5, 280, 560, 1.04, 270, 560, 0), (1.6, 280, 560, 1.05, 270, 560, -.4, ESNAP), (T, 290, 560, 1.07, 270, 560, -.4)], 'cubic-bezier(.3,0,.5,1)')
    whip('w1', T, t_in=False, t_out=2.3)
    out = s + [vignette2(.3), streaks(T, t_out=2.3)]
    out.append(caption(T, [L('Tylko najpierw…', CY2, 1.0)]))
    out.append('<g class="h1t">%s</g>' % cap_text('Zadbasz o siebie.', CY1))
    S('.h1t{transform-origin:270px %spx}' % CY1)
    A('.h1t', K([(0, 'opacity:1;transform:scale(.94)'), (.45, 'opacity:1;transform:scale(1)')], T, 'cubic-bezier(.2,.8,.3,1)'))
    out.append(note(T, 0, enter=.3))
    return ''.join(out), T

# ================= SCENA 2: Praca (2,5–6,5 s) =================
def sc_praca():
    T = 4.0; s = []; t0g = 2.5
    inst = 'qA2'
    cx, feet, sc = 168, 921, .8
    desk = 640
    MAIL = [(0, '3'), (.85, '47'), (2.4, '128')]
    cc = [(uid('ml'), v) for _, v in MAIL]
    s.append('<g class="w2"><g class="c2">')
    s.append(office(desk))
    s.append(FIG('A', inst, cx, feet, sc))
    s.append('<rect x="-400" y="%s" width="1340" height="16" fill="#D9B99B"/><rect x="-400" y="%s" width="1340" height="4" fill="#E9D3BC"/>' % (desk, desk))
    s.append('<rect x="-400" y="%s" width="1340" height="600" fill="%s"/><rect x="-400" y="%s" width="1340" height="12" fill="#000" opacity=".12"/>' % (desk + 16, DKG, desk + 16))
    lid = uid('lid')
    s.append(laptop(372, desk, lid, cc))
    for i, (c, v) in enumerate(cc):
        a = MAIL[i][0]; b = MAIL[i + 1][0] if i + 1 < len(MAIL) else 99
        fr = [(0, 'opacity:%s;transform:scale(%s)' % ('1' if a == 0 else '0', '1' if a == 0 else '.4'))]
        if a > 0: fr += [(a, 'opacity:0;transform:scale(.4)', EBOUNCE), (a + .2, 'opacity:1;transform:scale(1)')]
        if b < T: fr += [(b, 'opacity:1;transform:scale(1)', 'steps(1,end)'), (b + .01, 'opacity:0;transform:scale(1)')]
        S('.%s{transform-box:fill-box;transform-origin:center}' % c)
        A('.' + c, K(fr, T))
        if a > 0: ev(t0g + a, 'maile: %s (ping)' % v)
    ph = uid('ph')
    s.append('<g transform="translate(70,%s)">%s</g>' % (desk + 2, phone_svg(ph)))
    vib(ph, T, [1.2, 1.7])
    ev(t0g + 1.2, 'telefon dzwoni (ping)')
    # ręka szefa z kartką „NA WCZORAJ!”
    s.append('<g transform="translate(470,%s) scale(-1,1) rotate(8)"><g class="bs2">%s</g></g>' % (desk - 26, side_arm('#4d5a56', 'open', '<g transform="translate(70,-10) scale(-1,1) rotate(-6)">%s</g>' % paper_sheet('NA WCZORAJ!'), skin=SKIN2, cuff='#F4F2EF', width=34)))
    A('.bs2', K([(0, 'transform:translate(-320px,-30px)'), (2.0, 'transform:translate(-320px,-30px)', ESNAP), (2.3, 'transform:translate(0,0)'), (2.36, 'transform:translate(4px,4px)'), (2.44, 'transform:translate(0,0)'), (3.0, 'transform:translate(0,0)', EIO), (3.4, 'transform:translate(-340px,10px)')], T))
    ev(t0g + 2.3, 'ręka szefa: kartka „NA WCZORAJ!” trzaśnięta o biurko')
    s.append('</g></g>')
    # A: pisze, odwraca się do dymków, do szefa, opada
    fr = [(0, {'R': (250, 330), 'L': (60, 372)})]
    t = 0
    for i in range(6):
        t += .13
        fr.append((t, {'R': (244 + 8 * (i % 2), 326 + 6 * (i % 2))}, 'ease-in-out'))
    fr += [(1.1, {'R': (250, 330)}), (1.25, {'L': (40, 330)}, ESNAP), (1.5, {'L': (60, 372)}), (2.2, {'R': (250, 330)}), (2.45, {'R': (210, 300)}, ESNAP), (2.9, {'R': (220, 320)}), (3.4, {'R': (180, 340), 'L': (60, 380)}), (T, {'R': (180, 344)})]
    rig(inst, 'A', T, fr)
    head(inst, T, [(0, 2, 1, 4), (.55, 2, 1, 4), (.7, -8, -4, 0, ESNAP), (1.2, -7, -4, 0), (1.3, -9, -5, 2, ESNAP), (1.62, -7, -3, 0), (2.1, -6, -3, 0), (2.3, 9, 5, 0, ESNAP), (2.7, 8, 5, 0), (2.85, -8, -4, 0, ESNAP), (3.3, -6, -3, 4), (T, 3, 1, 8)])
    pupils(inst, T, [(0, 2.4), (.6, 2.4), (.7, -3.2), (2.25, -3.2), (2.32, 3.4), (2.8, 3.4), (2.85, -3.2), (3.3, -3), (3.5, 0)])
    A('.fig.%s .smile' % inst, K([(0, 'transform:scale(1)'), (T, 'transform:scale(.9,.85)')], T))
    A('.fig.%s .body' % inst, K([(0, 'transform:translateY(0)'), (3.2, 'transform:translateY(0)', EIO), (3.6, 'transform:translateY(8px) scaleY(.99)')], T))
    zf = [(0, 270, 560, 1.0, 270, 560, 0)]
    for i, tt in enumerate([.6, 1.2, 1.6, 2.3, 2.75]):
        zf += [(tt, 270, 560, 1.0 + .018 * i, 270, 560, zf[-1][6], ESNAP), (tt + .2, 270, 560, 1.018 + .018 * i, 270, 560, [.5, -.5, .6, -.8, .9][i])]
    zf += [(T, 270, 560, 1.12, 270, 560, .9)]
    cam('c2', T, zf, 'cubic-bezier(.4,0,.6,1)')
    whip('w2', T, t_in=True, t_out=3.78)
    out = s + [vignette2(.32), streaks(T), streaks(T, t_out=3.78)]
    # dymki – pas między napisem a twarzą
    out.append(bubble_at(T, 132, 306, .6, ['Masz chwilę?'], fill=BEIGE, tail=(-30, 30), t_off=1.55))
    out.append(bubble_at(T, 150, 306, 1.6, ['Raport do 16!'], fill=SAGE, tail=(-30, 30), t_off=2.7))
    out.append(bubble_at(T, 150, 314, 2.75, ['Tylko szybkie', 'spotkanie'], fill=CREAM2, tail=(-40, 40)))
    for tt, txt in [(.6, 'Masz chwilę?'), (1.6, 'Raport do 16!'), (2.75, 'Tylko szybkie spotkanie')]:
        ev(t0g + tt, 'dymek „%s” (ping)' % txt)
    out.append(caption(T, [L('…skończysz w pracy.', CY1, .22)], prev=[P('Zadbasz o siebie.', CY1), P('Tylko najpierw…', CY2)]))
    add_item(t0g + .95, 'maile')
    add_item(t0g + 1.75, 'raport do 16')
    add_item(t0g + 2.9, 'spotkanie')
    out.append(note(T, t0g))
    return ''.join(out), T

# ================= SCENA 3: Dom (6,5–10,5 s) =================
def sc_dom():
    T = 4.0; t0g = 6.5; s = []
    inst = 'qA3'
    cy = 700; cx, feet, sc = 176, 922, .8
    s.append('<g class="w3"><g class="zp3"><g class="c3">')
    s.append(kitchen(cy, window=(20, 300, 120, 220), shelf=None))
    s.append(FIG('A', inst, cx, feet, sc, post=ghost('A', inst, '', mug_hand('st3'), arm='R') + ghost('A', inst, '', '<g class="pen3"><path d="M6,-2 L22,26" stroke="%s" stroke-width="4" stroke-linecap="round"/></g>' % RUST, arm='L')))
    s.append(counter(cy))
    # pranie (ląduje na blacie)
    s.append('<g transform="translate(410,%s)"><g class="ld3">%s</g></g>' % (cy + 2, laundry()))
    S('.ld3{transform-origin:0 0}')
    A('.ld3', K([(0, 'opacity:0;transform:translate(160px,-260px) rotate(30deg)'), (1.9, 'opacity:1;transform:translate(160px,-260px) rotate(30deg)', 'cubic-bezier(.5,0,.9,.5)'), (2.18, 'opacity:1;transform:translate(0,0) rotate(0deg)', ESOFT),
                 (2.24, 'opacity:1;transform:translate(0,0) scale(1.06,.9)'), (2.36, 'opacity:1;transform:translate(0,0) scale(1,1)')], T))
    ev(t0g + 2.18, 'kosz z praniem ląduje na blacie')
    # zeszyt na blacie (podsuwa dziecko)
    s.append('<g transform="translate(250,%s) rotate(-90)"><g class="hc3b">%s</g></g>' % (cy + 6, side_arm('#7F978E', 'open', '<g transform="translate(6,-10) rotate(90)">%s</g>' % notebook(), width=24)))
    A('.hc3b', K([(0, 'transform:translate(-300px,0)'), (2.5, 'transform:translate(-300px,0)', ESNAP), (2.8, 'transform:translate(0,0)'), (3.4, 'transform:translate(0,0)', EIO), (3.7, 'transform:translate(-300px,0)')], T))
    # ręka dziecka z lewej
    s.append('<g transform="translate(120,610)"><g class="hc3">%s</g></g>' % side_arm(MUST, 'open', '', width=24))
    A('.hc3', K([(0, 'transform:translate(-260px,20px)'), (.4, 'transform:translate(-260px,20px)', ESNAP), (.72, 'transform:translate(0,0)'), (.86, 'transform:translate(6px,-4px)'), (1.0, 'transform:translate(0,0)'), (1.4, 'transform:translate(-280px,20px)')], T))
    # ręka męża z prawej z pustym talerzem
    s.append('<g transform="translate(420,610) scale(-1,1)"><g class="hh3">%s</g></g>' % side_arm('#7d6a5c', 'open', '<g transform="translate(4,-8)">%s</g>' % plate(), width=34))
    A('.hh3', K([(0, 'transform:translate(-300px,10px)'), (1.2, 'transform:translate(-300px,10px)', ESNAP), (1.55, 'transform:translate(0,0)'), (1.7, 'transform:translate(0,-6px)'), (1.85, 'transform:translate(0,0)'), (2.3, 'transform:translate(-320px,10px)')], T))
    s.append('</g></g></g>')
    rig(inst, 'A', T, [(0, {'R': R_HOLD, 'L': (62, 452)}), (2.6, {'L': (62, 452)}), (2.85, {'L': (130, 450)}, ESNAP), (2.95, {'L': (120, 456)}), (3.03, {'L': (134, 452)}), (3.11, {'L': (118, 458)}), (3.19, {'L': (134, 452)}), (3.4, {'L': (62, 452)})])
    A('.pen3', K([(0, 'opacity:0'), (2.8, 'opacity:0'), (2.86, 'opacity:1'), (3.3, 'opacity:1'), (3.36, 'opacity:0')], T, 'linear'))
    head(inst, T, [(0, 3, 1, 4), (.5, 3, 1, 4), (.62, -9, -5, 0, ESNAP), (1.25, -8, -5, 0), (1.38, 9, 5, 0, ESNAP), (1.9, 8, 5, 0), (2.0, 10, 6, -2, ESNAP), (2.4, 8, 5, 0), (2.6, -4, -2, 6, ESNAP), (3.3, -4, -2, 6), (T, 0, 0, 6)])
    pupils(inst, T, [(0, 0), (.6, -3.2), (1.3, -3.2), (1.38, 3.2), (2.4, 3.2), (2.55, -1), (T, -1)])
    A('.fig.%s .smile' % inst, K([(0, 'transform:scale(.95,.9)'), (T, 'transform:scale(.9,.85)')], T))
    A('.st3', K([(0, 'opacity:.25'), (T, 'opacity:0')], T))
    zf = [(0, 270, 560, 1.0, 270, 560, 0)]
    for i, tt in enumerate([.55, 1.35, 2.18, 2.6]):
        zf += [(tt, 270, 560, 1.0 + .02 * i, 270, 560, zf[-1][6], ESNAP), (tt + .2, 270, 560, 1.02 + .02 * i, 270, 560, [-.6, .7, -.8, .9][i])]
    zf += [(T, 270, 560, 1.1, 270, 560, .9)]
    cam('c3', T, zf, 'cubic-bezier(.4,0,.6,1)')
    whip('w3', T, t_in=True)
    A('.zp3', K([(0, 'transform:scale(1)'), (3.72, 'transform:scale(1)', 'cubic-bezier(.6,0,.9,.4)'), (T, 'transform:scale(1.35)')], T))
    S('.zp3{transform-origin:200px 520px}')
    out = s + [vignette2(.35), streaks(T)]
    out.append(bubble_at(T, 150, 306, .62, ['Mamo, gdzie moje…?!'], fill=BEIGE, tail=(-50, 34), t_off=1.35))
    out.append(bubble_at(T, 164, 306, 1.45, ['Co na obiad?'], fill=SAGE, tail=(60, 34), t_off=2.55))
    out.append(bubble_at(T, 120, 306, 2.62, ['Podpisz zeszyt!'], fill=CREAM2, tail=(-40, 34)))
    for tt, txt in [(.62, 'Mamo, gdzie moje…?!'), (1.45, 'Co na obiad?'), (2.62, 'Podpisz zeszyt!')]:
        ev(t0g + tt, 'dymek „%s” (ping)' % txt)
    flash = '<rect width="540" height="960" fill="#FFFDF6" class="fo3" pointer-events="none"/>'
    A('.fo3', K([(0, 'opacity:0'), (3.78, 'opacity:0', 'ease-in'), (T, 'opacity:.7')], T))
    out.append(flash)
    out.append(caption(T, [L('…ogarniesz dom.', CY1, .22)], prev=[P('…skończysz w pracy.', CY1)]))
    add_item(t0g + .8, 'skarpetki')
    add_item(t0g + 1.62, 'obiad')
    add_item(t0g + 2.3, 'pranie')
    add_item(t0g + 2.95, 'zeszyt')
    out.append(note(T, t0g))
    return ''.join(out), T

# ================= SCENA 4: Jeszcze tylko… (10,5–13,5 s) =================
def sc_jeszcze():
    T = 3.0; t0g = 10.5; s = []
    inst = 'qA4'
    cx, feet, sc = 138, 1004, .6
    s.append('<g class="c4"><g class="zi4">')
    s.append(kitchen(820, window=(20, 300, 120, 200), shelf=None))
    s.append(FIG('A', inst, cx, feet, sc))
    s.append('</g></g>')
    S('.zi4{transform-origin:200px 520px}')
    A('.zi4', K([(0, 'transform:scale(1.3)'), (.3, 'transform:scale(1)')], T, 'cubic-bezier(.2,.8,.3,1)'))
    BUB = [(.12, ['Mama', 'dzwoni!'], 'L'), (.52, ['Upieczesz', 'ciasto?'], 'R'), (.88, ['Odbierzesz', 'paczkę?'], 'L'), (1.18, ['Zebranie', 'w szkole!'], 'R'), (1.44, ['Pomożesz', 'mi?'], 'L'),
           (1.66, ['Szybciutko!'], 'R'), (1.85, ['Tylko', 'chwilka!'], 'L'), (2.02, ['A to?'], 'R'), (2.17, ['I to!'], 'L'), (2.3, ['Jeszcze!'], 'R'), (2.42, ['Mamo!'], 'L')]
    SLOTS = [(98, 300), (224, 350), (96, 410), (226, 460), (98, 520), (232, 570), (240, 670), (238, 760), (100, 300), (226, 350), (96, 410)]
    cols = [BEIGE, SAGE, CREAM2]
    ov = []
    head_fr = [(0, 0, 0, 0)]
    for i, ((t, lines, side), (x, y)) in enumerate(zip(BUB, SLOTS)):
        nxt = [BUB[j][0] for j in range(i + 1, len(BUB)) if SLOTS[j] == (x, y)]
        b, w, h = bubble(lines, fill=cols[i % 3], stroke=BROWN, fs=19, tail=((-30 if x < 160 else 30), 30), padx=10)
        c = uid('jb')
        if x < 160:
            fr = [(0, 'opacity:1;transform:translate(-360px,0) scale(1)'), (t, 'opacity:1;transform:translate(-360px,0) scale(1)', 'cubic-bezier(.2,.8,.3,1)'), (t + .2, 'opacity:1;transform:translate(0px,0) scale(1)')]
        else:
            fr = [(0, 'opacity:0;transform:translate(0px,0) scale(.2)'), (t, 'opacity:0;transform:translate(0px,0) scale(.2)', 'cubic-bezier(.2,.8,.3,1)'), (t + .14, 'opacity:1;transform:translate(0px,0) scale(1.05)', ESOFT), (t + .22, 'opacity:1;transform:translate(0px,0) scale(1)')]
        t_end = nxt[0] if nxt else None
        if t_end: fr += [(t_end - .06, 'opacity:1;transform:translate(0px,0) scale(1)', EOUT), (t_end, 'opacity:0;transform:translate(0px,0) scale(.8)')]
        A('.' + c, K(fr, T))
        ov.append('<g transform="translate(%s,%s)"><g class="%s">%s</g></g>' % (f(x), f(y), c, b))
        ev(t0g + t, 'dymek „%s” (ping)' % ' '.join(lines))
        head_fr += [(t, head_fr[-1][1], head_fr[-1][2], 0, ESNAP), (t + .12, (-9 if x < 160 else 9), (-5 if x < 160 else 5), 0)]
    head(inst, T, head_fr + [(T, head_fr[-1][1], head_fr[-1][2], 0)])
    pupils(inst, T, [(0, 0)] + [(b[0] + .1, -3.2 if SLOTS[i][0] < 160 else 3.2) for i, b in enumerate(BUB)])
    rig(inst, 'A', T, [(0, {'R': (158, 452), 'L': (62, 452)}), (1.3, {'R': (150, 380), 'L': (70, 380)}), (2.4, {'R': (120, 250), 'L': (100, 250), 'eR': 'out', 'eL': 'out'}), (T, {'R': (118, 246), 'L': (102, 246), 'eR': 'out', 'eL': 'out'})])
    A('.fig.%s .eyes' % inst, K([(0, 'transform:scaleY(1)'), (2.3, 'transform:scaleY(1.12)'), (T, 'transform:scaleY(1.12)')], T))
    zf = [(0, 270, 560, 1.0, 270, 560, 0)]
    for i, (t, _, _) in enumerate(BUB):
        zf += [(t, 270, 560, 1.0 + .012 * i, 270 + (2 if i % 2 else -2), 560, (-1) ** i * .3 * (i / 4), ESNAP), (t + .1, 270, 560, 1.012 + .012 * i, 270, 560, (-1) ** i * .3 * (i / 4))]
    zf += [(T, 270, 560, 1.16, 270, 560, 0)]
    cam('c4', T, zf, 'linear')
    out = s + [vignette2(.4)] + ov
    out.append(caption(T, [L('…i jeszcze tylko to.', CY1, .2), L('I to.', CY2, 1.2, x=None) if False else L('I to.', CY2, 1.2)], prev=[P('…ogarniesz dom.', CY1)]))
    # „I to. I to.” – dwa osobne słowa w drugiej linii
    out[-1] = out[-1].replace('<text x="270" y="%s" font-size="%s" text-anchor="middle" class="serif wsplit cw" fill="%s" style="--d0:1.2s">I to.</text>' % (f(CY2), CFS, INK),
                              '<text x="214" y="%s" font-size="%s" text-anchor="middle" class="serif wsplit cw" fill="%s" style="--d0:1.2s">I to.</text>' % (f(CY2), CFS, INK) +
                              '<text x="326" y="%s" font-size="%s" text-anchor="middle" class="serif wsplit cw" fill="%s" style="--d0:1.85s">I to.</text>' % (f(CY2), CFS, INK))
    ev(t0g + 1.2, 'napis „I to.”'); ev(t0g + 1.85, 'napis „I to.” (2)')
    labels = ['mama', 'ciasto', 'paczka', 'zebranie', 'pomóc', '~', '~', '~', '~', '~', '~', '~', '~']
    for i, (t, _, _) in enumerate(BUB):
        add_item(t0g + t + .08, labels[i])
    extra = [2.52, 2.6, 2.68, 2.76]
    for t in extra: ITEMS.append((t0g + t, '~'))
    out.append(note(T, t0g, mode='unroll'))
    return ''.join(out), T

# ================= SCENA 5: Potem może (13,5–16,5 s) =================
TEARS = [.55, 1.05, 1.5, 1.92]
PAGES = ['jutro', 'w weekend', 'po świętach', 'w przyszłym roku', 'kiedyś']

def sc_potem():
    T = 3.0; t0g = 13.5; s = []
    inst = 'qA5'
    cx, feet, sc = 214, 1100, .95
    s.append('<g class="c5">')
    s.append('<rect x="-400" y="-400" width="1340" height="1760" fill="#E6D7CE"/>')
    s.append('<rect x="-400" y="-400" width="1340" height="1760" fill="url(#dusk)"/>')
    # stół
    table = 836
    # kalendarz zrywany
    CX, CYc = 152, 382
    s.append('<g transform="translate(%s,%s)">' % (CX, CYc) +
             '<circle cx="0" cy="-118" r="5" fill="%s"/><path d="M0,-118 L-40,-96 M0,-118 L40,-96" stroke="%s" stroke-width="2"/>' % (BROWN, BROWN) +
             '<rect x="-104" y="-98" width="208" height="186" rx="6" fill="#3a2a20" opacity=".14" transform="translate(3,5)"/>' +
             '<rect x="-104" y="-98" width="208" height="38" rx="6" fill="%s"/><rect x="-104" y="-70" width="208" height="10" fill="%s"/>' % (DKG, DKG) +
             ''.join('<circle cx="%s" cy="-79" r="4" fill="#F4F2EF"/>' % x for x in (-60, -20, 20, 60)) + '</g>')
    for i, txt in enumerate(reversed(PAGES)):
        k = len(PAGES) - 1 - i      # k=0 → „jutro” (na wierzchu)
        fs = min(40, 172 / (len(txt) * .44))
        c = uid('pg')
        pg = ('<g transform="translate(%s,%s)"><g class="%s">' % (CX - 104, CYc - 60, c) +
              '<rect x="0" y="0" width="208" height="148" fill="#FBF9F6" stroke="#e2d9ce"/>'
              '<text x="104" y="%s" font-size="%s" text-anchor="middle" class="serif" fill="%s">%s</text>' % (f(86 + fs * .3), f(fs), INK, txt) +
              '<path d="M14,128 H194" stroke="#e8e0d6" stroke-width="2"/></g></g>')
        s.append(pg)
        if k < len(TEARS):
            t = TEARS[k]
            S('.%s{transform-origin:0 0}' % c)
            A('.' + c, K([(0, 'transform:translate(0,0) rotate(0deg);opacity:1'), (t, 'transform:translate(0,0) rotate(0deg);opacity:1', 'cubic-bezier(.4,0,.8,.6)'), (t + .1, 'transform:translate(-6px,8px) rotate(-14deg);opacity:1', 'cubic-bezier(.3,0,.6,1)'),
                         (t + .5, 'transform:translate(-260px,-180px) rotate(-70deg);opacity:0')], T))
            ev(t0g + t, 'zerwana kartka kalendarza: „%s” → „%s”' % (PAGES[k], PAGES[k + 1]))
    # A – coraz bardziej zmęczona, kubek zimny
    s.append(FIG('A', inst, cx, feet, sc, post=ghost('A', inst, '', mug_hand('st5'), arm='R')))
    s.append('<rect x="-400" y="%s" width="1340" height="20" rx="4" fill="#D9B99B"/><rect x="-400" y="%s" width="1340" height="400" fill="#7d6a5c"/>' % (table, table + 20))
    s.append('</g>')
    A('.st5', K([(0, 'opacity:0'), (T, 'opacity:0')], T))
    rig(inst, 'A', T, [(0, {'R': R_HOLD, 'L': (62, 452)}), (.9, {'R': (182, 290)}), (1.8, {'R': (176, 360)}), (T, {'R': (170, 420)})], 'cubic-bezier(.4,0,.6,1)')
    head(inst, T, [(0, -2, 0, 0), (.6, -6, -3, 2), (1.1, -8, -4, 3), (1.6, -2, 0, 6), (2.0, -6, -2, 8), (T, -4, -1, 12)])
    pupils(inst, T, [(0, -3), (.55, -3.4), (2.2, -3.4), (2.6, 0)])
    A('.fig.%s .eyes' % inst, K([(0, 'transform:scaleY(.95)'), (1.2, 'transform:scaleY(.7)'), (2.0, 'transform:scaleY(.55)'), (2.2, 'transform:scaleY(.1)'), (2.35, 'transform:scaleY(.5)'), (T, 'transform:scaleY(.48)')], T))
    A('.fig.%s .smile' % inst, K([(0, 'transform:scale(.9,.8)'), (T, 'transform:scale(.82,.6)')], T))
    A('.fig.%s .body' % inst, K([(0, 'transform:translateY(0) scaleY(1)'), (T, 'transform:translateY(14px) scaleY(.985)')], T, 'cubic-bezier(.4,0,.6,1)'))
    cam('c5', T, [(0, 270, 520, 1.0, 270, 520, 0), (T, 250, 560, 1.07, 270, 540, 0)], 'cubic-bezier(.3,0,.5,1)')
    out = s + [vignette2(.55)]
    out.append(caption(T, [L('Potem może.', CY1, .22)], prev=[P('…i jeszcze tylko to.', CY1)] + [('I to.', CY2, CFS, 214, INK, True), ('I to.', CY2, CFS, 326, INK, True)]))
    # lista: gęsta, „zadbać o siebie” wyblakły, spada z każdą kartką
    items = [(-9, 'SELF'), (-8, '~'), (-7, '~')] + [(t0g + t + .05, '~') for t in TEARS]
    out.append(note(T, t0g, items=items, grey_self=True))
    for t in TEARS: ev(t0g + t + .05, 'lista: „zadbać o siebie” spada (scena 5)')
    return ''.join(out), T

# ================= SCENA 6: Pytanie (16,5–18,5 s) =================
def sc_pytanie():
    T = 2.0; s = []
    inst = 'qA6'
    cx, sc = 270, 2.3
    feet = 470 + (712 - 131) * sc
    s.append('<g class="c6">')
    s.append('<rect x="-400" y="-400" width="1340" height="1760" fill="#EDE7E1"/>')
    s.append('<rect x="-60" y="160" width="190" height="300" rx="8" fill="#F4EFE8"/><path d="M35,160 V460 M-60,300 H130" stroke="#E2D9D0" stroke-width="7"/>')
    s.append(FIG('A', inst, cx, feet, sc))
    s.append('</g>')
    head(inst, T, [(0, -5, -2, 4), (.4, -5, -2, 4), (1.1, 1, 0, 0, 'cubic-bezier(.4,0,.2,1)'), (T, 2, 1, 0)])
    pupils(inst, T, [(0, -3.2), (.45, -3.2), (1.05, 0), (T, 0)], 'cubic-bezier(.4,0,.2,1)')
    A('.fig.%s .eyes' % inst, K([(0, 'transform:scaleY(.6)'), (.9, 'transform:scaleY(.6)'), (1.15, 'transform:scaleY(1)'), (T, 'transform:scaleY(1)')], T))
    A('.fig.%s .smile' % inst, K([(0, 'transform:scale(.85,.7)'), (1.2, 'transform:scale(.85,.7)'), (1.6, 'transform:scale(.95,.9)'), (T, 'transform:scale(.95,.9)')], T))
    A('.fig.%s .tilt,.fig.%s .tiltBack' % (inst, inst), K([(0, 'transform:none'), (T, 'transform:none')], T))
    A('.fig.%s .body' % inst, K([(0, 'transform:translateY(6px)'), (1.2, 'transform:translateY(6px)'), (T, 'transform:translateY(0)')], T))
    cam('c6', T, [(0, 270, 470, 1.0, 270, 470, 0), (T, 270, 460, 1.08, 270, 470, 0)], 'cubic-bezier(.3,0,.5,1)')
    out = s + [vignette2(.5)]
    out.append(caption(T, [L('A kiedy w końcu Ty?', CY1, .45)]))
    ev(16.5, 'TWARDE CIĘCIE – cisza')
    return ''.join(out), T

# ================= SCENA 7: W końcu (18,5–22 s) =================
def sc_wkoncu():
    T = 3.5; t0g = 18.5; s = []
    iA, iB = 'qA7', 'qB7'
    cx, feet, sc = 168, 921, .8
    desk = 640
    CUT = 1.5
    # --- ujęcie 1: biurko, B zamyka laptop, lista spada ---
    s.append('<g class="u7a"><g class="c7a">')
    s.append(office(desk, wall='#E9E2DA'))
    s.append(FIG('A', iA, cx, feet, sc))
    s.append('<g class="bin7">' + FIG('B', iB, 430, feet, .8, wrap='bob7') + '</g>')
    s.append('<rect x="-400" y="%s" width="1340" height="16" fill="#D9B99B"/><rect x="-400" y="%s" width="1340" height="600" fill="%s"/>' % (desk, desk + 16, DKG))
    lid = uid('lid')
    cc = [(uid('ml'), '128')]
    s.append(laptop(332, desk, lid, cc))
    S('.%s{transform-box:view-box;transform-origin:332px %spx}' % (lid, desk - 10))
    A('.' + lid, K([(0, 'transform:scaleY(1)'), (1.0, 'transform:scaleY(1)', 'cubic-bezier(.5,0,.3,1)'), (1.22, 'transform:scaleY(.05)')], T))
    ev(t0g + 1.22, 'B zamyka laptop')
    s.append('</g></g>')
    S('.bin7{transform-origin:430px %spx}' % feet)
    A('.bin7', K([(0, 'transform:translateX(200px)'), (.4, 'transform:translateX(200px)', 'cubic-bezier(.2,.7,.3,1)'), (.8, 'transform:translateX(0)')], T))
    A('.bob7', K([(0, 'transform:translateY(0)'), (.42, 'transform:translateY(0)'), (.54, 'transform:translateY(-6px)'), (.66, 'transform:translateY(0)'), (.76, 'transform:translateY(-5px)'), (.86, 'transform:translateY(0)')], T, 'ease-in-out'))
    lidtop = ((332 - 430) / .8 + 110, 712 - (feet - (desk - 112)) / .8)
    rig(iB, 'B', T, [(0, {'L': (56, 452), 'R': (166, 452)}), (.8, {'L': (56, 452)}), (1.0, {'L': lidtop}, ESNAP), (1.22, {'L': (lidtop[0], lidtop[1] + 100)}, 'cubic-bezier(.5,0,.3,1)'), (1.45, {'L': (40, 420)})])
    head(iB, T, [(0, 0, 0, 0), (.5, -5, -2, 2), (1.1, -6, -3, 2), (T, -6, -3, 2)])
    pupils(iB, T, [(0, 0), (.5, -3), (T, -3)])
    A('.fig.%s .smile' % iB, K([(0, 'transform:scale(1.05,1.1)'), (T, 'transform:scale(1.05,1.1)')], T))
    rig(iA, 'A', T, [(0, {'R': (220, 320), 'L': (60, 380)}), (.9, {'R': (220, 320)}), (1.2, {'R': (190, 380)})])
    head(iA, T, [(0, 3, 1, 8), (.2, 3, 1, 8), (.45, -2, 0, 4, ESNAP), (.8, -2, 0, 4), (1.0, 8, 4, 0, ESNAP), (T, 8, 4, 0)])
    pupils(iA, T, [(0, 0), (.2, 2), (.5, 1), (.9, 3.2), (T, 3.2)])
    A('.fig.%s .smile' % iA, K([(0, 'transform:scale(.88,.8)'), (1.0, 'transform:scale(.88,.8)'), (1.3, 'transform:scale(1.08,1.15)')], T))
    cam('c7a', T, [(0, 290, 560, 1.0, 270, 560, 0), (CUT, 290, 560, 1.06, 270, 560, 0)], 'cubic-bezier(.3,0,.5,1)')
    A('.u7a', K([(0, 'opacity:1'), (CUT, 'opacity:1', 'steps(1,end)'), (CUT + .01, 'opacity:0')], T, 'linear'))
    # --- ujęcie 2: taras w Beskidach ---
    rail = 700; sF = .74; cA, cB = 196, 384; tf = rail + (712 - 470) * sF
    a2, b2 = 'qA7t', 'qB7t'
    t2 = ['<g class="u7b"><g class="c7b">',
          '<rect x="-100" y="-100" width="740" height="1160" fill="url(#skyB)"/>', '<circle cx="430" cy="380" r="220" fill="url(#sunG)"/>',
          '<g class="px7a">' + ridge(-80, 700, 470, 30, 6, 21, 900, '#CFDAD4') + '</g>',
          '<g class="px7b">' + ridge(-80, 700, 540, 34, 7, 22, 900, SAGE) + ''.join(tree(x, 590 + R.uniform(-8, 10), R.uniform(50, 80), c) for x, c in zip(range(-60, 700, 34), itertools.cycle([RUST, MUST, DKG, '#c47a3c', MUST, DKG]))) + '</g>',
          '<g class="px7c">' + ridge(-80, 700, 630, 20, 8, 23, 900, DKG) + '</g>',
          FIG('B', 'hold has-mug ' + b2, cB, tf, sF),
          FIG('A', a2, cA, tf, sF, post=ghost('A', a2, '', mug_hand('st7'), arm='R')),
          '<rect x="-100" y="%s" width="740" height="18" rx="4" fill="#8a6a56"/><rect x="-100" y="%s" width="740" height="5" fill="#a5826c"/>' % (rail, rail),
          ''.join('<rect x="%s" y="%s" width="16" height="300" fill="#7a5c4a"/>' % (x, rail + 18) for x in range(-20, 600, 70)),
          '<rect x="-100" y="%s" width="740" height="14" fill="#8a6a56"/>' % (rail + 110), '</g></g>']
    s += t2
    A('.u7b', K([(0, 'opacity:0'), (CUT, 'opacity:0', 'steps(1,end)'), (CUT + .01, 'opacity:1')], T, 'linear'))
    A('.px7b', K([(0, 'transform:translateX(0)'), (CUT, 'transform:translateX(0)'), (T, 'transform:translateX(-20px)')], T))
    A('.px7c', K([(0, 'transform:translateX(0)'), (CUT, 'transform:translateX(0)'), (T, 'transform:translateX(-36px)')], T))
    rig(a2, 'A', T, [(0, {'R': R_HOLD, 'L': (62, 452)}), (CUT + .3, {'R': R_HOLD}), (CUT + .8, {'R': R_SIP}, 'cubic-bezier(.4,0,.2,1)'), (CUT + 1.3, {'R': (157, 235)}), (CUT + 1.6, {'R': R_HOLD})])
    head(a2, T, [(0, 0, 0, 0), (CUT + .5, -3, 0, -2), (CUT + 1.3, -3, 0, -2), (CUT + 1.6, 5, 2, 1), (T, 6, 2, 1)])
    A('.fig.%s .eyes' % a2, K([(0, 'transform:scaleY(1)'), (CUT + .8, 'transform:scaleY(1)'), (CUT + .92, 'transform:scaleY(.1)'), (CUT + 1.4, 'transform:scaleY(.1)'), (CUT + 1.55, 'transform:scaleY(1)')], T))
    A('.fig.%s .smile' % a2, K([(0, 'transform:scale(1.1,1.2)'), (T, 'transform:scale(1.1,1.2)')], T))
    head(b2, T, [(0, -4, -2, 1), (T, -6, -2, 1)])
    pupils(b2, T, [(0, -3), (T, -3)])
    A('.st7', K([(0, 'opacity:1;transform:scale(1.15)'), (T, 'opacity:1;transform:scale(1.15)')], T))
    cam('c7b', T, [(0, 270, 520, 1.08, 270, 520, 0), (CUT, 270, 520, 1.08, 270, 520, 0), (T, 270, 530, 1.0, 270, 530, 0)], 'cubic-bezier(.3,0,.5,1)')
    out = s + ['<rect width="540" height="960" fill="url(#warm)" pointer-events="none" class="wm7"/>', vignette2(.3)]
    A('.wm7', K([(0, 'opacity:0'), (CUT, 'opacity:0', 'steps(1,end)'), (CUT + .01, 'opacity:1')], T, 'linear'))
    # błysk ciepłego światła na przejściu
    out.append('<rect width="540" height="960" fill="#FFF3DC" class="fl7" pointer-events="none"/>')
    A('.fl7', K([(0, 'opacity:0'), (CUT - .25, 'opacity:0', 'ease-in'), (CUT, 'opacity:1', 'steps(1,end)'), (CUT + .01, 'opacity:1', 'cubic-bezier(.2,.6,.3,1)'), (CUT + .45, 'opacity:0')], T))
    ev(t0g + CUT, 'przejście do Beskidów (ciepłe światło)')
    # napis: najpierw poprzedni gaśnie
    out.append(caption(T, [L('W końcu', CY1, CUT + .2), L('zadbaj o siebie.', CY2, CUT + .42), L('3 dni tylko dla Ciebie.', CY2 + 54, CUT + 1.05, fs=26, serif=False, col=BROWN)],
                       prev=[P('A kiedy w końcu Ty?', CY1)]))
    # lista: B ją… lista spada i znika
    items = [(-9, 'SELF')] + [(-8 + i * .1, '~') for i in range(6)]
    out.append(note(T, t0g, items=items, fall=.15))
    ev(t0g + .15, 'lista spada i znika')
    out.append('<circle cx="270" cy="520" r="640" fill="%s" class="iris7"/>' % CREAM)
    S('.iris7{transform-origin:270px 520px}')
    A('.iris7', K([(0, 'transform:scale(0)'), (3.16, 'transform:scale(0)', 'cubic-bezier(.6,0,.3,1)'), (T, 'transform:scale(1)')], T))
    return ''.join(out), T

# ================= SCENA 8: Logo + CTA (22–25 s) =================
def sc_logo():
    T = 3.0; s = []
    s.append('<g class="c8">')
    s.append('<rect x="-100" y="-100" width="740" height="1160" fill="%s"/>' % CREAM)
    s.append('<ellipse cx="270" cy="330" rx="380" ry="300" fill="url(#halo6)"/>')
    s.append('<path class="ln8" pathLength="1" d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>' % (smooth([(60, 760), (130, 712), (180, 736), (260, 676), (330, 730), (400, 700), (480, 744)]), SAGE))
    S('.ln8{stroke-dasharray:1}')
    A('.ln8', K([(0, 'stroke-dashoffset:1'), (.2, 'stroke-dashoffset:1', EIO), (1.3, 'stroke-dashoffset:0')], T))
    s.append('<clipPath id="cp8"><rect class="w8" x="30" y="250" width="480" height="70"/></clipPath>')
    s.append('<g clip-path="url(#cp8)"><use href="#logoWord" transform="translate(270,286) scale(.68)" style="color:%s"/></g>' % DKG)
    S('.w8{transform-origin:30px 0}')
    A('.w8', K([(0, 'transform:scaleX(.04)', 'cubic-bezier(.4,0,.25,1)'), (.6, 'transform:scaleX(1)')], T))
    s.append('<g class="tg8"><use href="#logoTag" transform="translate(270,342) scale(.45)" style="color:%s"/></g>' % BROWN)
    A('.tg8', K([(0, 'opacity:0;transform:translateY(10px)'), (.45, 'opacity:0;transform:translateY(10px)', ESNAP), (.72, 'opacity:1;transform:translateY(0)')], T))
    s.append('<g class="d8">%s</g>' % mtext(DATA_CAMPU, 270, 446, 26, weight=800))
    A('.d8', K([(0, 'opacity:0;transform:translateY(12px)'), (.85, 'opacity:0;transform:translateY(12px)', ESNAP), (1.1, 'opacity:1;transform:translateY(0)')], T))
    s.append('<g transform="translate(270,556)"><g class="bt8"><rect x="-166" y="-46" width="332" height="92" rx="46" fill="#3a2a20" opacity=".15" transform="translate(0,5)"/>'
             '<rect x="-166" y="-46" width="332" height="92" rx="46" fill="%s"/>' % BROWN +
             '<text x="0" y="-4" font-size="32" text-anchor="middle" fill="%s" style="font-weight:800">Zapisz się →</text>' % CREAM2 +
             '<text x="0" y="28" font-size="22" text-anchor="middle" fill="#F1E2D3" style="font-weight:700;letter-spacing:.03em">shebalance.pl</text>'
             '<g clip-path="url(#btnClip)"><rect class="bsh8" x="-60" y="-60" width="40" height="120" fill="url(#shine)" transform="rotate(18)"/></g></g></g>')
    S('.bt8{transform-origin:0 0}')
    A('.bt8', K([(0, 'opacity:0;transform:scale(.6)'), (1.1, 'opacity:0;transform:scale(.6)', EBOUNCE), (1.42, 'opacity:1;transform:scale(1)'), (2.0, 'opacity:1;transform:scale(1)', 'ease-in-out'), (2.2, 'opacity:1;transform:scale(1.04)'), (2.4, 'opacity:1;transform:scale(1)')], T))
    A('.bsh8', K([(0, 'transform:rotate(18deg) translateX(-180px)'), (1.5, 'transform:rotate(18deg) translateX(-180px)', EIO), (2.0, 'transform:rotate(18deg) translateX(260px)')], T))
    # kubek z parą – klamra z początkiem
    mug = ('<g transform="scale(1.1)"><path d="M-19,-34 L19,-34 L17,4 Q16,10 10,10 L-10,10 Q-16,10 -17,4 Z" fill="#FBF9F6" stroke="%s" stroke-width="1.8"/>' % DKG +
           '<path d="M18,-24 Q32,-24 30,-11 Q28,-1 16,-2" fill="none" stroke="%s" stroke-width="1.8"/>' % DKG +
           '<path d="M-18.2,-14 L18.2,-14 L17.6,-6 L-17.6,-6 Z" fill="%s"/><ellipse cx="0" cy="-34" rx="19" ry="4.6" fill="#7a4a30" stroke="%s" stroke-width="1.4"/>' % (SAGE, DKG) +
           '<g transform="translate(0,-40)">%s</g></g>' % steam_paths('stm', 3, 26, 5, 2.4, '#FBF9F6', 9, DKG))
    s.append('<g transform="translate(270,680)"><g class="mg8">%s</g></g>' % mug)
    A('.mg8', K([(0, 'opacity:0;transform:translateY(20px)'), (1.6, 'opacity:0;transform:translateY(20px)', ESNAP), (1.9, 'opacity:1;transform:translateY(0)')], T))
    s.append('</g>')
    cam('cm8', T, [(0, 270, 470, 1.05, 270, 470, 0), (T, 270, 470, 1.0, 270, 470, 0)], 'cubic-bezier(.3,0,.4,1)')
    return '<g class="cm8">' + ''.join(s) + '</g>' + vignette2(.25), T

SCENES = [('hak', sc_hak, CREAM), ('praca', sc_praca, CREAM), ('dom', sc_dom, CREAM), ('jeszcze', sc_jeszcze, CREAM),
          ('potem', sc_potem, BEIGE), ('pytanie', sc_pytanie, CREAM), ('wkoncu', sc_wkoncu, CREAM), ('logo', sc_logo, CREAM)]

def build():
    parts, sj = [], []
    t = 0; starts = []
    for sid, fn, bg in SCENES:
        svg, T = fn()
        parts.append('<g class="scene" data-s="%s">%s</g>' % (sid, svg))
        sj.append("{id:'%s',d:%s,bg:'%s'}" % (sid, f(T), bg)); starts.append(t); t += T
    tpl = (HERE / 'szablon.html').read_text(encoding='utf-8')
    defs = (DEFS_EXTRA + '<clipPath id="btnClip"><rect x="-166" y="-46" width="332" height="92" rx="46"/></clipPath>'
            '<radialGradient id="capGlow"><stop offset="0" stop-color="#F7F4EF" stop-opacity=".85"/><stop offset=".6" stop-color="#F7F4EF" stop-opacity=".5"/><stop offset="1" stop-color="#F7F4EF" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C9B6AA" stop-opacity=".35"/><stop offset="1" stop-color="#8a7a70" stop-opacity=".25"/></linearGradient>')
    html = (tpl.replace('@@CSS@@', '\n'.join(CSS)).replace('@@DEFS@@', defs)
            .replace('@@SCENES@@', '\n'.join(parts)).replace('@@SCJS@@', ','.join(sj)))
    OUT.write_text(html, encoding='utf-8')
    print('ok', OUT, len(html), 'reguł', len(CSS), 'czas', t, 'starty', starts)
    for tt, w in sorted(EV): print('  %6.2f  %s' % (tt, w))

if __name__ == '__main__':
    build()
