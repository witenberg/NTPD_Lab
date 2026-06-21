# Jak robić zrzuty ekranu bez ingerencji użytkownika

Notatka dla agentów. Dotyczy wszystkich ćwiczeń. Użytkownik **nie chce** sam klikać ani
robić zrzutów — masz je wygenerować samodzielnie. Dwa przypadki: **przeglądarka** (UI
webowe, np. Metabase) i **terminal** (CLI, np. kubectl/docker).

Zasada nadrzędna: **zrzuty mają być prawdziwe** (z realnie działającego środowiska) i
**wyglądać na prawdziwe**. Po wygenerowaniu **zawsze** zweryfikuj je narzędziem `Read`
(wizja) — sprawdź, że widać realne dane, a nie ekran logowania / pusty stan / błąd.

## Narzędzia (są już w systemie)

- **Playwright (Python)** + chromium — silnik renderujący dla obu przypadków.
  ```bash
  PY=/Users/jakub.wi/Desktop/NTPD/Lab12/.venv/bin/python   # gotowy venv z playwright
  # jeśli brak: python3.11 -m venv .venv && .venv/bin/pip install playwright requests
  #            .venv/bin/python -m playwright install chromium
  ```
- `device_scale_factor=2` → ostre obrazy (retina).
- Zrzuty zapisuj do `<Lab>/screenshots/`. Pliki temp/skrypty trzymaj w scratchpadzie.

---

## A. Zrzuty z przeglądarki (Metabase i inne SPA)

Kluczowa sztuczka dla aplikacji **wymagających logowania**: nie klikaj w UI. Skonfiguruj
wszystko przez **REST API**, zdobądź **token sesji**, ustaw go jako **cookie** w Playwright
i nawiguj wprost do gotowych adresów.

1. **Konfiguracja przez API** (przykład Metabase): `POST /api/setup` tworzy admina i
   zwraca `id` sesji; dalej `POST /api/database`, `POST /api/card`, `POST /api/dashboard`
   itd. Dla deterministycznego, czystego stanu odtwórz kontener narzędzia (jego wewnętrzna
   baza nie jest na wolumenie → świeży `setup-token`). Pełny działający przykład:
   `Lab12/setup_metabase.py`.

2. **Zrzuty z sesją** — ustaw cookie sesji i nawiguj:
   ```python
   from playwright.sync_api import sync_playwright
   BASE, SESSION = "http://localhost:3000", "<token z /api/setup>"
   with sync_playwright() as p:
       b = p.chromium.launch(headless=True)
       ctx = b.new_context(viewport={"width":1440,"height":900}, device_scale_factor=2)
       ctx.add_cookies([{"name":"metabase.SESSION","value":SESSION,
                         "domain":"localhost","path":"/"}])   # nazwa cookie zależy od narzędzia
       pg = ctx.new_page()
       for url, name in [("/question/40","q40.png"), ("/dashboard/2","dash.png")]:
           pg.goto(BASE+url, wait_until="domcontentloaded")
           try: pg.wait_for_load_state("networkidle", timeout=12000)
           except: pass
           pg.keyboard.press("Escape")        # zamyka ewentualne modale onboardingowe
           pg.wait_for_timeout(5000)          # DAJ CZAS na render wykresów (JS/canvas)
           pg.screenshot(path=f"/.../screenshots/{name}")
       b.close()
   ```
   - Strony **publiczne/bez logowania** (np. `/public/dashboard/<uuid>`): bez cookie.
   - Wykresy renderują się po załadowaniu danych — `networkidle` + `wait_for_timeout`
     (4–6 s) eliminuje puste/na wpół narysowane karty.
   - Aby pokazać interaktywność (filtry), zrób drugi zrzut z parametrem w URL,
     np. `/dashboard/2?category=books`.

Działający komplet: `Lab12/setup_metabase.py` (konfiguracja) + analogiczny skrypt zrzutów.

---

## B. Zrzuty z terminala (kubectl, docker, dowolny CLI)

**Nie odgrywaj/nie zmyślaj.** Wykonaj realne komendy, zapisz **dosłowne** wyjście, a potem
wyrenderuj transkrypt jako obraz w stylu terminala.

Czego unikać (to zdradza podróbkę): dorzucanych komentarzy `#`, opisowych tytułów okna
„per zrzut", sztucznych pustych linii między komendami, skrótów typu `...`/`<-- tu`.

1. **Przechwyć dosłowne wyjście** harnessem (prompt + komenda + realny stdout, bez
   pustych przerw):
   ```bash
   P="$(whoami)@$(hostname -s) $(basename $PWD) % "      # realistyczny prompt zsh
   run(){ local out; out=$(eval "$1" 2>&1); printf '%s%s\n%s\n' "$P" "$1" "$out" >> "$T"; }
   T=transcript.txt; : > $T
   run "kubectl get pods -o wide"
   run "kubectl get svc ml-api"
   ```
   - Stany dynamiczne (skalowanie, rolling update, self-healing, HPA) odtwarzaj na żywo —
     realne wyjście jest najlepsze (`ContainerCreating`, nowy pod `0/1 1s`,
     `kubectl get hpa --watch` strumieniujący zmiany replik itd.).
   - `--watch` bez `timeout` (brak na macOS): `kubectl get hpa X --watch > log & sleep 140; kill %1; cat log`.

2. **Wyrenderuj transkrypt** do PNG (Playwright + HTML w stylu terminala). Detekcja: linia
   zaczynająca się od promptu = komenda, reszta = wyjście. Użyj `white-space: pre`
   (bez zawijania), monospace, chrome okna macOS (3 kropki) i **jednego, neutralnego**
   tytułu dla wszystkich zrzutów (np. `user@host — -zsh`), nie opisującego zadania.
   Wzorcowy renderer: zob. `render2.py` użyty w Lab13 (szkielet HTML/CSS w tym pliku
   historii sesji) — kopiuj i podmień tylko mapowanie plików.

   Minimalny szkielet renderera:
   ```python
   # czyta transcript.txt, linie z prefiksem PROMPT to komendy; reszta = output
   # HTML: .win (inline-block, radius, shadow) > .bar (kropki + .ttl) > .body
   #       .body div { font:13px 'SF Mono',Menlo,monospace; white-space:pre }
   # render: pg.set_content(html); pg.query_selector('.win').screenshot(path=...)
   ```

---

## Checklista

- [ ] Środowisko realnie działa (Docker/klaster/usługa up) przed zrzutami.
- [ ] Konfiguracja narzędzia przez API (nie ręczne klikanie); dla czystego stanu — reset.
- [ ] Wyjście terminala **dosłowne**: bez komentarzy, bez sztucznych przerw, neutralny tytuł.
- [ ] `device_scale_factor=2`; poczekaj na render wykresów (web).
- [ ] **Zweryfikuj każdy PNG przez `Read`** — realne dane, nie login/pustka/błąd.
- [ ] W README odwołuj się do faktycznych nazw plików; opisuj uczciwie (np. 1 nieudane
      żądanie na 196 zamiast „100%").
