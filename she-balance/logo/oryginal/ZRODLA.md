# Źródła — logo SheBalance

Pobrano 2026-09-30 ze strony https://shebalance.pl/ (WordPress + Elementor 4.3.2).

## Pliki

| Plik | Źródło | Uwagi |
|---|---|---|
| `LOGO.svg` | https://shebalance.pl/wp-content/uploads/2026/09/LOGO.svg | Główne logo (sygnet), wektor, viewBox 1500×1500, bez kolorów wypełnienia (domyślnie czarne). Na stronie wstawione inline w sekcji hero (widget ikony Elementora `6bb10a8`), barwione na `#FFFFFF`, 300 px wysokości. Media ID 76 w bibliotece (`/?rest_route=/wp/v2/media`). |
| `header-logo-inline.svg` | https://shebalance.pl/ — inline `<svg>` w `<a class="sb-logo">` w nagłówku | W nagłówku nie ma pliku graficznego: logo to wbudowany SVG (26×28 px, obrys `#FFFFFF`) plus tekst „SHE BALANCE”. Nie ma oryginalnej nazwy pliku, więc nazwę nadano tutaj. Dodano tylko `xmlns`, żeby plik otwierał się samodzielnie. |

### Czego nie znaleziono

- **custom-logo w WordPressie:** brak (`site_logo: 0` w `/?rest_route=/`), a w HTML nie ma klasy `custom-logo`.
- **Favicon / site icon:** brak. W HTML nie ma `link rel="icon"` ani `apple-touch-icon`, a `site_icon: 0`. `/favicon.ico` i `/apple-touch-icon.png` zwracają 404.
- **og:image:** strona nie ma żadnych tagów `og:*`.
- **srcset / warianty `-WxH`:** nie dotyczy, bo oba logo są w SVG. Pozostałe SVG w bibliotece (`Obszar-roboczy-*.svg`) to ikony sekcji, nie logo.

## Kolory marki (z CSS strony)

Paleta globalna Elementora (`post-8.css`, kit):

| Zmienna | Kolor |
|---|---|
| `--e-global-color-primary` | `#A4B8B0` (szałwiowa zieleń) |
| `--e-global-color-secondary` | `#E3CCC1` (pudrowy beż/róż) |
| `--e-global-color-7b1f86c` | `#58756C` (ciemna zieleń) |
| `--e-global-color-d875d25` | `#5F756D` (ciemna zieleń, wariant) |
| `--e-global-color-757b71d` | `#C6B8AA` (ciepły beż) |
| `--e-global-color-430f16d` | `#F2EFEB` (kremowe tło) |
| `--e-global-color-text` | `#7A7A7A` |
| `--e-global-color-accent` | `#3333330A` |

Kolory używane w praktyce (`post-23.css` i style inline strony głównej):

- **Tekst:** `#333333` (główny, najczęstszy), `#6B6B6B` (drugorzędny), `#FFFFFF` i `#F4F2EF` na ciemnym tle.
- **Tła sekcji:** `#F4F2EF` i `#F2EFEB` (krem), `#A4B8B0` (primary), `#58756C` (ciemna zieleń), `#E0CCC0` (beż), `#333333`. Warstwy na zdjęciach: `#8F9894`, `#6E5446`.
- **Akcenty tekstu / linki:** `#58756C`, `#E0CCC0`.
- **Przyciski:**
  - Nagłówek/hero: przezroczyste, ramka i tekst `#FFFFFF`; po najechaniu tło `#FFFFFF`, tekst `#333333`.
  - Formularz: tło `#333333`, tekst `#F4F2EF`; po najechaniu tło przezroczyste, tekst `#333333`.
  - Wszystkie mają `border-radius: 0` i wersaliki.
- **Logo:** białe (`#FFFFFF`) na zdjęciu / ciemnym tle.

## Fonty (Google Fonts)

- **Forum:** nagłówki (szeryfowy, fallback `Georgia, serif`).
- **Mulish:** tekst, menu, przyciski (wagi 300/400; przyciski 12 px, wersaliki, `letter-spacing` 3.4 px).
- W domyślnym kicie Elementora są też `Roboto` i `Roboto Slab`, a w motywie `Manrope` i `Fira Code`. To ustawienia domyślne, na stronie praktycznie nieużywane.
