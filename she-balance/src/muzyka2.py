# Muzyka v2: pogodny, ciepły pop-akustyk (ukulele + celesta + lekki beat) – zamiast nastrojowych padów.
# Użycie: python3 muzyka2.py <nazwa> <czas_s> ['[[start, "tryb"], ...]']
#   tryby: full (cały zespół), light (bez stopy/klaskania), soft (tylko ukulele + melodia), silent (cisza)
# Zapisuje ../animacje/<nazwa>.wav (48 kHz, stereo).
import sys, json
import numpy as np
from scipy.signal import lfilter
from muzyka import SR, OUT, t_arr, midi, lp, hp, bp, Mix, kick, hat, bass

rng = np.random.default_rng(11)

def uke(note, dur=0.9, vel=0.5):  # szarpana struna (Karplus-Strong)
    n = int(dur * SR); N = int(SR / midi(note))
    b = lp(rng.uniform(-1, 1, N), 5000); x = np.zeros(n); x[:N] = b - b.mean()
    a = 0.996
    den = np.zeros(N + 2); den[0] = 1; den[N] = -a / 2; den[N + 1] = -a / 2
    y = lfilter([1], den, x)
    y = hp(lp(y, 4200), 70) * np.clip((dur - t_arr(dur)) / 0.08, 0, 1)
    return y * vel * 0.5

def celesta(note, dur=1.6, vel=0.5):  # pozytywka / celesta – harmoniczna, ciepła
    t = t_arr(dur); f = midi(note)
    sig = np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t * 5) + 0.1 * np.sin(6 * np.pi * f * t) * np.exp(-t * 9)
    return sig * np.minimum(1, t / 0.002) * vel * 0.22

def clap(vol=0.25):
    t = t_arr(0.25); e = np.zeros_like(t)
    for d in (0, 0.009, 0.018): e += np.exp(-np.clip(t - d, 0, None) * 60) * (t >= d)
    return bp(rng.standard_normal(len(t)), 900, 6000) * e * vol * 0.6

def shaker(vol=0.05):
    t = t_arr(0.09); return hp(rng.standard_normal(len(t)), 5000) * np.sin(np.pi * t / 0.09) * vol

# C – G – Am – F, pogodnie
CHORDS = [(48, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [60, 64, 69, 72]), (41, [60, 65, 69, 72])]
MELODY = [  # (takt-ósemka, nuta, długość w ósemkach) – 2 takty, powtarzane z wariacją
    (0, 76, 2), (2, 79, 1), (3, 76, 1), (4, 74, 2), (6, 72, 2),
    (8, 74, 2), (10, 76, 1), (11, 74, 1), (12, 71, 3), (15, 74, 1),
    (16, 72, 2), (18, 76, 1), (19, 79, 1), (20, 81, 2), (22, 79, 2),
    (24, 77, 2), (26, 76, 1), (27, 74, 1), (28, 72, 4)]

def mode_at(t, plan):
    m = plan[0][1]
    for s, md in plan:
        if t >= s: m = md
    return m

def song(d, plan, bpm=104):
    m = Mix(d); e = 60 / bpm / 2  # ósemka
    end = d - 2.2
    n8 = int(end / e)
    for k in range(n8):
        t = k * e; md = mode_at(t, plan)
        if md == 'silent': continue
        bar = k // 8; root, ch = CHORDS[bar % 4]; pos = k % 8
        # ukulele: rytm D-DU-UDU
        if pos in (0, 2, 3, 5, 6, 7):
            down = pos in (0, 2, 6)
            notes = ch if down else ch[::-1][:3]
            v = 0.32 if pos in (0, 6) else 0.2
            for j, nt in enumerate(notes): m.add(uke(nt, 0.9, v), t + j * 0.011, pan=-0.35 + 0.12 * j)
        if md in ('full', 'light'):
            if pos in (0, 3, 4, 6): m.add(bass(root - 12 + (12 if pos == 6 else 0), e * 1.6, 0.3), t)
            m.add(shaker(0.05 if pos % 2 else 0.035), t, pan=0.4)
        if md == 'full':
            if pos in (0, 4): m.add(kick(0.55), t)
            if pos in (2, 6): m.add(clap(0.3), t, pan=0.1)
        # melodia celesty (od 2. taktu)
        if bar >= 1 and md in ('full', 'light', 'soft'):
            ph = (k - 8) % 32
            for st, nt, ln in MELODY:
                if st == ph: m.add(celesta(nt + (12 if md == 'soft' else 0) * 0, 1.4, 0.55 if md != 'soft' else 0.45), t, pan=0.2)
    # finał: akord C z ukulele + celesta
    for j, nt in enumerate(CHORDS[0][1]): m.add(uke(nt, 2.2, 0.3), end + j * 0.03, pan=-0.3 + 0.2 * j)
    m.add(bass(36, 1.8, 0.3), end); m.add(celesta(84, 2.2, 0.5), end + 0.1)
    return m

def master(m, dur):
    n = int(dur * SR); L, R = m.L[:n].copy(), m.R[:n].copy()
    # krótki, jasny pogłos (bez „ciemnego” ogona)
    dly = int(0.09 * SR); L[dly:] += R[:-dly] * 0.18; R[dly:] += L[:-dly] * 0.18
    fade = np.clip((dur - np.arange(n) / SR) / 0.6, 0, 1); fi = np.minimum(1, np.arange(n) / (SR * 0.03))
    L *= fade * fi; R *= fade * fi
    rms = np.sqrt(np.mean(np.concatenate([L, R]) ** 2)) + 1e-9
    g = 0.11 / rms; L *= g; R *= g
    pk = max(np.abs(L).max(), np.abs(R).max())
    if pk > 0.89: L *= 0.89 / pk; R *= 0.89 / pk
    return np.stack([L, R], 1)

PLANS = {  # przebieg nastroju dopasowany do scen
    'kawa': [[0, 'light'], [3, 'full'], [11, 'silent'], [13, 'soft'], [17, 'full']],
    'poradnik': [[0, 'light'], [2.5, 'full'], [16.5, 'silent'], [18.5, 'soft'], [20, 'full']],
    'beat-balansu': [[0, 'light'], [2.4, 'full'], [7.2, 'soft'], [9.0, 'light'], [11.4, 'full']],
    'role-liscie': [[0, 'soft'], [3.7, 'light'], [8.4, 'full']],
}

if __name__ == '__main__':
    name, dur = sys.argv[1], float(sys.argv[2])
    plan = json.loads(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else PLANS.get(name, [[0, 'soft'], [2.3, 'light'], [4.6, 'full']])
    from scipy.io import wavfile
    data = master(song(dur, plan), dur)
    wavfile.write(OUT / f'{name}.wav', SR, (data * 32767).astype(np.int16))
    print('zapisano', OUT / f'{name}.wav')
