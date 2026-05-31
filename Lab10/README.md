## Analiza wyników

Na podstawie zrealizowanych zapytań SQL można wyciągnąć następujące wnioski:

1. **Poprawność ładowania danych i schematów:** Plik Parquet z danymi sprzedażowymi został wczytany poprawnie, a Spark automatycznie i bezbłędnie rozpoznał typy danych (np. `amount` jako `double`, `transaction_id` jako `long`). Podobnie poprawnie zinterpretowano plik CSV wraz z jego nagłówkami.

2. **Wyniki agregacji i filtrowania (`--- aggregation results ---`):**
   Zapytanie grupujące (`GROUP BY region`) miało na celu zsumowanie przychodów (`SUM(amount)`) oraz zliczenie transakcji (`COUNT(*)`) dla poszczególnych regionów, ale **tylko dla transakcji o wartości powyżej 1000** (`WHERE amount > 1000`). 
   * Zgodnie z oczekiwaniami, w wyniku widzimy tylko regiony `North` (suma 6000.0) oraz `West` (suma 3400.0). 
   * Region `South` został całkowicie odfiltrowany, ponieważ wszystkie zarejestrowane tam transakcje (np. Myszka za 50.0, Klawiatura za 150.0) nie spełniały warunku brzegowego `amount > 1000`.

3. **Wyniki łączenia tabel (`--- join results ---`):**
   Operacja `JOIN` poprawnie zintegrowała tabelę transakcji z tabelą demograficzną na podstawie klucza obcego (`sales.customer_id = customers.id`). Z uzyskanej tabeli wynikowej widać wyraźną korelację: najdroższe sprzęty (np. Desktop za 3500.0, Laptop za 2500.0) zostały zakupione przez klientów należących do segmentu **VIP** (Jan Kowalski, Piotr Wiśniewski). Klienci z segmentu **Regular** kupowali z reguły tańsze przedmioty lub sprzęt ze średniej półki.

Operacje Spark SQL zostały wykonane poprawnie, a wygenerowane wyniki zapisano do nowych plików wyjściowych (zgodnie z wymaganiami instrukcji).