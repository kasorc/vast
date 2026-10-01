# Generator muzyki do animacji SheBalance (bez licencji – syntezowana od zera).
# Użycie: python3 muzyka.py <nazwa> <czas_s> [czasy_przejść_s oddzielone przecinkami]
# Zapisuje ../animacje/<nazwa>.wav (48 kHz, stereo).
import sys, json, pathlib
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
rng = np.random.default_rng(7)
OUT = pathlib.Path(__file__).parent.parent / 'animacje'

def t_arr(d): return np.arange(int(d * SR)) / SR
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, order=2): return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)

class Mix:
    def __init__(self, dur): self.n = int(dur * SR) + SR * 4; self.L = np.zeros(self.n); self.R = np.zeros(self.n); self.dur = dur
    def add(self, sig, at, gain=1.0, pan=0.0):
        i = int(at * SR)
        if i >= self.n: return
        s = sig[: self.n - i] * gain
        self.L[i:i + len(s)] += s * np.cos((pan + 1) * np.pi / 4)
        self.R[i:i + len(s)] += s * np.sin((pan + 1) * np.pi / 4)

# ---------- instrumenty ----------
def piano(note, dur=3.0, vel=0.7):
    f = midi(note); t = t_arr(dur); B = 0.00015
    sig = np.zeros_like(t)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > 16000: break
        decay = 1.2 + 2.2 / k + (note < 55) * 1.5
        sig += (0.9 ** k) / k ** 0.7 * np.sin(2 * np.pi * fk * t + rng.random() * 6) * np.exp(-t * (1.0 / decay) * (1 + k * 0.35))
    atk = np.minimum(1, t / 0.004)
    hammer = hp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 90) * 0.05
    rel = np.clip((dur - t) / 0.25, 0, 1)
    return (sig * atk + hammer) * rel * vel * 0.18

def pad(notes, dur, vol=0.05):
    t = t_arr(dur); sig = np.zeros_like(t)
    for n in notes:
        for det in (-0.08, 0.0, 0.07):
            f = midi(n) * 2 ** (det / 12)
            sig += np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 1.2) * np.clip((dur - t) / 1.5, 0, 1)
    return lp(sig, 2200) * env * vol / len(notes)

def pluck(note, dur=0.8, vel=0.6):  # marimba/kalimba
    f = midi(note); t = t_arr(dur)
    sig = np.sin(2 * np.pi * f * t) * np.exp(-t * 6) + 0.35 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t * 18) + 0.15 * np.sin(2 * np.pi * f * 9.9 * t) * np.exp(-t * 40)
    return sig * np.minimum(1, t / 0.002) * vel * 0.25

def chime(note=88, vel=0.5):
    t = t_arr(3.0); f = midi(note)
    sig = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for a, r, d in ((1, 1, 1.4), (.5, 2.76, 2.5), (.3, 5.4, 4), (.2, 8.9, 6)))
    return sig * np.minimum(1, t / 0.003) * vel * 0.12

def noise_swell(dur, lo, hi, peak=0.5, vol=0.2):  # wiatr / whoosh / szelest
    t = t_arr(dur); x = bp(rng.standard_normal(len(t)), lo, hi)
    env = np.where(t < dur * peak, t / (dur * peak), (dur - t) / (dur * (1 - peak))) ** 1.6
    return x * env * vol

def rustle(dur, vol=0.08):  # szelest liści: impulsy pasmowe
    t = t_arr(dur); x = np.zeros_like(t)
    for _ in range(int(dur * 60)):
        i = rng.integers(0, len(t) - 2000); l = rng.integers(300, 1800)
        x[i:i + l] += rng.standard_normal(l) * np.exp(-np.arange(l) / (l / 4)) * rng.random()
    x = bp(x, 1800, 9000)
    env = np.minimum(1, t / 0.6) * np.clip((dur - t) / 0.8, 0, 1)
    return x * env * vol

def rain(dur, vol=0.05):
    t = t_arr(dur); x = lp(hp(rng.standard_normal(len(t)), 800), 7000)
    return x * np.minimum(1, t / 1) * np.clip((dur - t) / 1, 0, 1) * vol

def paper(vol=0.25):  # szelest papieru/mapy
    t = t_arr(0.35); x = bp(rng.standard_normal(len(t)), 1200, 7000) * np.exp(-t * 10) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t))
    return x * vol

def click(vol=0.4):  # stuk kamienia
    t = t_arr(0.25); f = 1900 + rng.random() * 400
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 60) + 0.6 * np.sin(2 * np.pi * f * 1.6 * t) * np.exp(-t * 90) + hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 200) * 0.3) * vol

def kick(vol=0.9):
    t = t_arr(0.45); f = 48 + 90 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * vol

def snare(vol=0.35):
    t = t_arr(0.3)
    return (bp(rng.standard_normal(len(t)), 1500, 8000) * np.exp(-t * 22) + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.5) * vol

def hat(vol=0.08, open_=False):
    t = t_arr(0.2); return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * (18 if open_ else 70)) * vol

def bass(note, dur, vol=0.35):
    t = t_arr(dur); f = midi(note)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    return lp(x, 400) * np.minimum(1, t / 0.01) * np.clip((dur - t) / 0.05, 0, 1) * np.exp(-t * 1.5) * vol

# ---------- pogłos i mastering ----------
def reverb(L, R, wet=0.28, secs=2.6):
    n = int(secs * SR); t = np.arange(n) / SR
    irL = rng.standard_normal(n) * np.exp(-t * 3.2 / secs * 3); irR = rng.standard_normal(n) * np.exp(-t * 3.2 / secs * 3)
    irL = lp(irL, 6000); irR = lp(irR, 6000); irL /= np.sqrt((irL ** 2).sum()); irR /= np.sqrt((irR ** 2).sum())
    return L * (1 - wet) + fftconvolve(L, irL)[:len(L)] * wet * 2.2, R * (1 - wet) + fftconvolve(R, irR)[:len(R)] * wet * 2.2

def master(m, dur):
    L, R = reverb(m.L, m.R)
    n = int(dur * SR); L, R = L[:n], R[:n]
    fade = np.clip((dur - np.arange(n) / SR) / 1.2, 0, 1); fi = np.minimum(1, np.arange(n) / (SR * 0.05))
    L *= fade * fi; R *= fade * fi
    for a, b in getattr(m, 'gates', []):  # twarde wyciszenie (np. „…serio?”)
        tt = np.arange(n) / SR; g = np.clip(np.maximum((a - tt) / 0.015, (tt - b) / 0.015), 0, 1); L *= g; R *= g
    rms = np.sqrt(np.mean(np.concatenate([L, R]) ** 2)) + 1e-9
    g = 0.1 / rms; L *= g; R *= g  # ok. -20 dBFS RMS
    pk = max(np.abs(L).max(), np.abs(R).max())
    if pk > 0.89: L *= 0.89 / pk; R *= 0.89 / pk
    return np.stack([L, R], 1)

# ---------- utwory ----------
PROG = [(62, [50, 57, 62, 66, 69, 73]), (59, [47, 54, 59, 62, 66, 69]), (55, [43, 50, 55, 59, 62, 66]), (57, [45, 52, 57, 61, 64, 69])]  # Dmaj7 Bm7 Gmaj7 A
MEL = [78, 76, 74, 76, 73, 74, 71, 69, 71, 73, 74, 76, 78, 81, 78, 76]

def calm_piano(m, start, end, bpm=72, arp=True, melody=True, vol=1.0):
    beat = 60 / bpm; bar = beat * 4; t0 = start; i = 0
    while t0 < end - 0.2:
        root, ch = PROG[i % 4]
        m.add(piano(ch[0], 4, 0.55 * vol), t0, pan=-0.2)
        m.add(pad(ch[1:4], bar + 1.5, 0.05 * vol), t0)
        if arp:
            for k, n in enumerate([ch[2], ch[3], ch[4], ch[5], ch[4], ch[3], ch[2], ch[3]]):
                if t0 + k * beat / 2 < end: m.add(piano(n, 2.2, 0.32 * vol), t0 + k * beat / 2, pan=0.25 * np.sin(k))
        if melody:
            for k in range(4):
                if (i * 4 + k) % 3 != 2 and t0 + k * beat < end: m.add(piano(MEL[(i * 4 + k) % 16], 3, 0.42 * vol), t0 + k * beat, pan=0.1)
        t0 += bar; i += 1

def song_role(d, cuts):
    m = Mix(d)
    m.add(lp(rain(6.2, 0.022), 3500), 0); m.add(pad([38, 45, 50], 6.5, 0.07), 0)          # szare miasto: deszcz + głuchy dron
    for k in range(6): m.add(piano(62 - (k % 3) * 2, 2, 0.25), 0.6 + k * 0.9, pan=-0.3)  # pojedyncze, zmęczone dźwięki
    calm_piano(m, 6.0, 12.4, bpm=72, melody=False, vol=0.8)                    # bus: pianino rusza
    m.add(noise_swell(4.2, 250, 2500, 0.45, 0.22), 12.3); m.add(rustle(4.2, 0.11), 12.6)  # wiatr i liście
    for k in range(9): m.add(chime(90 + (k % 4) * 2, 0.35), 13.0 + k * 0.1, pan=(k % 3 - 1) * 0.6)  # pękające nitki
    calm_piano(m, 15.2, d - 1.0, bpm=76, vol=1.0)                               # montaż, taras, logo
    m.add(rustle(3.5, 0.05), 21.1)
    m.add(piano(50, 5, 0.6), d - 3.4); m.add(piano(62, 5, 0.5), d - 3.4); m.add(piano(69, 5, 0.45), d - 3.4); m.add(chime(86, 0.5), d - 2.2)
    return m

def song_calm(d, cuts, bpm=72, fx=paper):
    m = Mix(d); calm_piano(m, 0, d - 1.5, bpm=bpm)
    for c in cuts: m.add(fx(), c, pan=float(rng.uniform(-.5, .5)))
    m.add(chime(86, 0.45), d - 2.6); m.add(piano(50, 5, 0.6), d - 2.6); m.add(piano(62, 5, 0.5), d - 2.6)
    return m

def song_game(d, cuts):
    m = Mix(d); beat = 60 / 110
    scale = [62, 64, 66, 69, 71, 74, 76, 78]
    t = 0.0; k = 0
    while t < d - 1.5:
        m.add(pluck(scale[(k * 3) % 8], 0.7, 0.5), t, pan=0.3 * np.sin(k));
        if k % 2 == 0: m.add(pluck(scale[(k * 5 + 2) % 8] - 12, 0.9, 0.35), t, pan=-0.3)
        if k % 4 == 0: m.add(kick(0.35), t);
        if k % 4 == 2: m.add(hat(0.06, True), t)
        m.add(hat(0.03), t + beat / 2)
        if k % 8 == 0: m.add(pad([PROG[(k // 8) % 4][1][1], PROG[(k // 8) % 4][1][2], PROG[(k // 8) % 4][1][3]], beat * 8, 0.05), t)
        t += beat / 2; k += 1
    for c in cuts: m.add(chime(84 + int(rng.integers(0, 3)) * 2, 0.4), c)
    for i, n in enumerate([74, 78, 81, 86]): m.add(pluck(n, 1.2, 0.6), d - 4.5 + i * 0.12)
    return m

def song_beat(d, sections):
    # sections: dict z czasami: brk_start, brk_end, drop, end_ (sekundy); tempo 100 BPM
    m = Mix(d); beat = 0.6
    nb = int(round(d / beat))
    for b in range(nb):
        t = b * beat; bar = b // 4; pos = b % 4
        in_break = sections['brk_start'] <= t < sections['brk_end']
        build = sections['brk_end'] <= t < sections['drop']
        root, ch = PROG[bar % 4]
        if in_break:
            if pos == 0: m.add(pad(ch[1:5], beat * 4 + 1, 0.07), t)
            continue
        m.add(kick(0.85 if t >= sections['drop'] else 0.6), t)
        if pos in (1, 3): m.add(snare(0.3 if not build else 0.2), t)
        for h in range(2): m.add(hat(0.05), t + h * beat / 2 + beat / 4)
        m.add(bass(root - 24, beat * 0.9, 0.3), t)
        if pos == 0: m.add(pad(ch[1:5], beat * 4 + 0.5, 0.045), t)
        if pos in (0, 2):
            for n in ch[2:5]: m.add(piano(n, 1.2, 0.28), t + beat / 2)
        if build:
            for s in range(4): m.add(snare(0.08 + 0.12 * (t - sections['brk_end']) / (sections['drop'] - sections['brk_end'])), t + s * beat / 4)
    m.add(noise_swell(sections['drop'] - sections['brk_end'], 400, 6000, 0.97, 0.12), sections['brk_end'])
    m.add(chime(86, 0.6), sections['drop'])
    for i in range(4): m.add(click(0.5), d - 2.4 + i * beat)
    return m


def tick(vol=0.25):
    t = t_arr(0.06); return hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 120) * vol

def ping(note=88, vol=0.3):  # powiadomienie
    t = t_arr(0.5); f = midi(note)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2 * t)) * np.exp(-t * 9) * np.minimum(1, t / 0.003) * vol

def buzz(dur=0.45, vol=0.18):  # wibracja telefonu
    t = t_arr(dur); x = np.sign(np.sin(2 * np.pi * 150 * t)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * t)))
    return lp(x, 900) * vol

def song_kawa(d, cuts):
    m = Mix(d)
    # 0–11 s: zegar + narastający chaos próśb
    for k in range(int(11.85 / 0.5)): m.add(tick(0.22 + 0.1 * (k % 2)), k * 0.5, pan=0.4 * (-1) ** k)
    asks = [1.42, 3.15, 4.25, 5.25, 6.15, 6.95, 7.65, 8.3, 8.9, 9.35, 9.7, 10.0, 10.3]  # zgodne z animacją
    for i, a in enumerate(asks): m.add(ping(84 + (i * 5) % 12, 0.18 + 0.012 * i), a, pan=float(rng.uniform(-.7, .7)))
    m.add(buzz(0.6, 0.24), 5.25); m.add(buzz(0.45, 0.22), 8.3)
    for b in range(int(3 / 0.4), int(11.85 / 0.4)):  # puls basu przyspiesza napięcie
        m.add(bass(38, 0.3, 0.12 + 0.02 * (b * 0.4 - 3)), b * 0.4)
    m.add(noise_swell(2.5, 300, 5000, 0.95, 0.06), 8.5)
    # 11–13 s: cisza (tylko delikatny ton)
    m.add(pad([62, 69], 1.3, 0.03), 11.9)
    m.add(click(0.3), 13.15)  # klamka
    # 13 s →: ulga – pianino
    for k in range(5): m.add(chime(88 + k * 2, 0.25), 14.3 + k * 0.07)  # pękające dymki
    m.add(chime(93, 0.4), 15.75)  # błysk biletu
    calm_piano(m, 13.3, d - 1.2, bpm=74, vol=0.95)
    m.add(noise_swell(0.4, 600, 6000, 0.5, 0.12), 18.35)  # whip-pan
    m.add(piano(50, 5, 0.6), d - 3.6); m.add(piano(62, 5, 0.5), d - 3.6); m.add(piano(69, 5, 0.45), d - 3.6); m.add(chime(86, 0.45), d - 2.4)
    return m

def knock(vol=0.5):  # pukanie w drzwi
    t = t_arr(0.18)
    x = lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 45) + np.sin(2 * np.pi * 120 * t) * np.exp(-t * 30) * 0.8
    return x * vol

def song_poradnik(d, ev):
    m = Mix(d)
    cut = ev.get('cut', 17.0)
    # 0–17 s: kiczowata, skoczna melodia „telezakupy” (C-dur, 128 bpm)
    bpm = 128; b = 60 / bpm
    chords = [(48, [60, 64, 67]), (53, [60, 65, 69]), (55, [59, 62, 67]), (48, [60, 64, 67])]
    mel = [72, 76, 79, 76, 77, 74, 71, 74, 72, 76, 79, 84, 83, 79, 74, 72]
    n = int(cut / b)
    for k in range(n):
        tt = k * b
        root, ch = chords[(k // 8) % 4]
        if k % 2 == 0: m.add(kick(0.45), tt)
        if k % 4 == 2: m.add(snare(0.18), tt)
        m.add(hat(0.05), tt + b / 2)
        if k % 2 == 0: m.add(bass(root - 12 + (7 if k % 4 == 2 else 0), b * 0.9, 0.22), tt)
        if k % 2 == 1:
            for j, c in enumerate(ch): m.add(pluck(c, 0.3, 0.16), tt + j * 0.008, pan=-0.3 + 0.3 * j)
        if k % 2 == 0 and k >= 4: m.add(pluck(mel[(k // 2) % len(mel)], 0.45, 0.32), tt, pan=0.15)
    for st in ev.get('steps', [2, 5, 8, 11, 14]):  # „ding” + ✔ na każdy krok
        m.add(chime(91, 0.42), st + 0.05); m.add(chime(96, 0.3), st + 0.17)
    m.add(noise_swell(0.5, 800, 7000, 0.6, 0.1), 0.0)  # flesz studia
    for t0 in ev.get('dings', [11.6, 12.5, 13.4]):  # mikrofalówka
        m.add(chime(93, 0.55), t0); m.add(chime(100, 0.25), t0 + 0.02)
    for t0 in ev.get('knocks', [14.9, 15.15, 15.4, 16.2, 16.45]): m.add(knock(0.55), t0, pan=-0.2)
    # 17 s: twarde ucięcie → cisza; jeden suchy akcent przy uniesieniu brwi
    m.gates = [(cut, ev.get('brow', 18.0) - 0.01)]
    m.add(pluck(79, 0.6, 0.18), ev.get('brow', 18.0))
    # 19 s →: spokojne pianino, ciepło
    calm_piano(m, ev.get('calm', 19.0), d - 1.0, bpm=72, vol=0.95)
    m.add(noise_swell(1.2, 200, 3000, 0.7, 0.05), 19.0)
    m.add(piano(48, 4, 0.55), d - 3.0); m.add(piano(60, 4, 0.45), d - 3.0); m.add(piano(67, 4, 0.4), d - 3.0); m.add(chime(84, 0.4), d - 2.2)
    return m

if __name__ == '__main__':
    name, dur = sys.argv[1], float(sys.argv[2])
    cuts = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 and sys.argv[3] else []
    if name == 'role-liscie': m = song_role(dur, cuts)
    elif name == 'gra-odpoczynek': m = song_game(dur, cuts)
    elif name == 'kamienie-sloik': m = song_calm(dur, cuts, 70, click)
    elif name == 'mapa-popup': m = song_calm(dur, cuts, 76, paper)
    elif name == 'kawa': m = song_kawa(dur, cuts)
    elif name == 'poradnik': m = song_poradnik(dur, json.loads(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] else {})
    elif name == 'beat-balansu': m = song_beat(dur, json.loads(sys.argv[4]))
    else: m = song_calm(dur, cuts)
    from scipy.io import wavfile
    data = master(m, dur)
    wavfile.write(OUT / f'{name}.wav', SR, (data * 32767).astype(np.int16))
    print('zapisano', OUT / f'{name}.wav')
