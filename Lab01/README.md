# Laboratorium 1: Tworzenie modelu ML w Pythonie. Zapisywanie i wersjonowanie modelu.


## 1. Instrukcja uruchomienia

Wszystkie polecenia należy wykonyważ z poziomu folderu `Lab01`.

1. Przygotowanie środowiska:
    ```bash
    cd Lab01
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2. Trening, analiza i zapis:
    ```bash
    python src/main.py
    ```

3. Weryfikacja zapisu i wczytywania modelu:
    ```bash
    python src/load_model.py
    ```

## 2. Polityka wersjonowania modelu

Stosowane jest nazewnictwo plików: `model_[lab01]v[MAJOR].[MINOR].joblib`.

### Podniesienie wersji MINOR:
* Zmiana hiperparametrów
* Trening na nowszych danych, bez zmiany formatu
* Poprawa jakości danych podczas preprocessingu

### Podniesienie wersji MAJOR:
* Zmiana algorytmu uczenia
* Zmiana struktury danych wejściowych
* Zmiana zmiennej docelowej

### Oznaczanie wersji w Git:
```bash
git tag -a Lab01-v1.0 -m "Opis zmian"
```

## 3. Wdrażanie na produkcje vs development

### Zarządzanie danymi i ich jakością

**Problem:**

W środowisku deweloperskim operujemy na statycznych wycinkach danych (np. pliki CSV). Na produkcji dane są dynamiczne, płyną z różnych źródeł (API, bazy SQL), a ich struktura może się różnić oraz mogą zawierać błędy, których nie przewidziano w fazie testów.

**Rozwiązanie:** 

W pipelinach danych należy walidować schematy, służą do tego narzędzia takie jak np. Great Expectations - pozwalają one automatycznie odrzucać rekordy niezgodne z oczekiwanym formatem.


### Monitoring modelu

**Problem:**

Modele mogą sobie dobrze radzić na historycznych danych, ale tracić skuteczność w tych aktualnych. Zjawiska takie jak "Data Drift" (zmiana rozkładu cech wejściowych) oraz "Concept Drift" (zmiana zależności w danych) wymagają stałego nadzoru.

**Rozwiązanie:** 

Implementacja systemów monitorujących (np. Prometheus, Grafana), które śledzić będą (oprócz metryk biznesowych) statystyki zmiennych wejściowych, aby wykryć moment, w którym model przestaje pasować do rzeczywistości.

### Retraining

**Problem:**

W fazie developmentu model trenowany jest raz, a jego wyniki oceniane. Na produkcji trzeba zachować powtarzalność, a ręczne trenowanie nowej wersji przy każdym spadku jakości jest nieefektywne.

**Rozwiązanie:** 

Zautomatyzowany retraining, uruchamiany po wykryciu spadku metryk poniżej określonego produ. W takim wypadku retraining powinien odbywać się na najświeższych danych. Na koniec, dla pewności, należy również porównać wyniki z aktualnym modelem.

### Zarządzanie zależnościami

**Problem:**

Różnice w wersjach bibliotek, narzędzi i systemu mogą prowadzić do błędnych predykcji, a w najgorszym wypadku do awarii.

**Rozwiązanie:** 

Konteneryzacja przy użyciu Dockera. Pozwala to na zamknięcie modelu wraz z całym jego środowiskiem uruchomieniowym w obrazie, gwarantując identyczne zachowanie na każdej maszynie.

### Automatyzacja wdrożeń

**Problem:**

Kod modelu na produkcji wymaga testów jednostkowych, integracyjnych i bezpiecznego deploymentu.

**Rozwiązanie:** 

Wykorzystanie CI/CD (np. GitHub Actions, Jenkins). Każda zmiana w kodzie lub modelu powinna przechodzić automatyczne testy jakości kodu i testy obciążeniowe, zanim trafi na serwer produkcyjny.