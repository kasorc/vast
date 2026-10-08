# SheBalance – stałe zasady projektu

Animacje i grafiki dla SheBalance (shebalance.pl, IG @shebalance_camp) – kobiecy camp „Healthy · Networking · Self-development”.
Pliki: `she-balance/` (animacje, postacie, muzyka), `logo/`, `logo-animacje/`. Komunikacja z klientką po polsku.

## Postacie (ZAWSZE, bez wyjątków)
- **Postać A – blondynka:** BEZ CZAPKI – nigdy nie dodawaj czapki ani nakrycia głowy. Proste, długie blond włosy z przedziałkiem na środku i pasmami okalającymi twarz, szaro-zielone oczy, delikatny uśmiech, biała koszulka w czarne paski, czarne spodnie. Jest mamą i żoną.
- **Postać B – brunetka:** brązowe fale z karmelowymi końcówkami, curtain bangs, piegi, niebieskie oczy, biała muślinowa bluzka z bufkami, brązowe spodnie.
- Obie są równego wzrostu.
- Jedyne źródło wyglądu: `she-balance/src/postacie.svg` (popiersia) → `wytnij_glowy.py` → `zbuduj_figury.py` → `figura-A.svg` / `figura-B.svg`. W animacjach używaj wyłącznie znaczników `/*FIG_A:...*/`, `/*FIG_B:...*/`, `/*BUST_A*/`, `/*BUST_B*/` – nie rysuj postaci od nowa i nie zmieniaj twarzy.
- Tylne włosy muszą poruszać się razem z głową (`.headWrap.hairBack > .tiltBack`).

## Marka
- Aktualne logo i font: wektory z `logo/oryginal/logo-wektor.json` → symbole `#logoWord`, `#logoTag`, `#logoLockup`, `#logoSign` (kolor przez `style="color:…"`).
- Paleta: szałwia #A4B8B0, ciemna zieleń #58756C, beż #E3CCC1, krem #F2EFEB/#F4F2EF, brąz #6E5446, tekst #333; akcenty rdza #B5582F, musztarda #D4A23A.
- Camp: **5–7.11 · Karolowy Dwór, Wisła · 20 miejsc**. CTA: „Zapisz się → shebalance.pl”.
- Camp to odpoczynek, relacje i rozwój – nigdy nie przedstawiamy go jako leczenia (bez „terapia”, „depresja”, „leczenie”).

## Produkcja
- Filmy: MP4 H.264 1080×1920, 30 fps, yuv420p, faststart (odtwarza się na telefonie). Render: `she-balance/src/finalizuj.sh <nazwa>`; wersja premium: `node renderuj.mjs <nazwa> --premium` (motion blur + korekcja + ziarno).
- Muzyka: `she-balance/src/muzyka2.py` (pogodna: ukulele + celesta). Stara `muzyka.py` była odebrana jako „creepy” – nie wracać do niej.
- Pliki w repo < 100 MB. Po każdej zmianie commit + push na `master`.
