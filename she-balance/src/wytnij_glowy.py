# Wycina z popiersi (postacie.svg) włosy z tyłu i głowy obu postaci do budowy figur w całej sylwetce.
import pathlib
src = pathlib.Path(__file__).parent
s = (src / 'postacie.svg').read_text()
A = s[:s.index('  <!-- Dziewczyna 2')]; B = s[s.index('  <!-- Dziewczyna 2'):]
def block(txt, start):
    i = start; depth = 0
    while True:
        o = txt.find('<g', i); c = txt.find('</g>', i)
        if o != -1 and o < c: depth += 1; i = o + 2
        else:
            depth -= 1; i = c + 4
            if depth == 0: return txt[start:i]
for who, T in (('A', A), ('B', B)):
    b1 = T.index('<g class="tilt"><g class="sway">'); back = block(T, b1)
    b2 = T.index('<g class="tilt">', b1 + len(back)); head = block(T, b2)
    (src / f'_back{who}.svg').write_text(back); (src / f'_head{who}.svg').write_text(head)
print('ok')
