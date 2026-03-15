# Laboratorium 2 - MLflow; Wersjonowanie modelu; Logowanie hiperparametrów i metryk;

## Zadanie 3: Porównanie eksperymentów poprzez zmianę hiperparametrów
W celu znalezienia optymalnych hiperparametrów, skrypt `train.py` został zmodyfikowany o pętlę testującą różne kombinacje `n_estimators`, `max_depth` oraz `learning_rate`. 

**Wnioski z MLflow UI:**
Po porównaniu wyników w interfejsie graficznym MLflow, najwyższą wartość metryki `accuracy` (wynoszącą: 0.9561) osiągnął model o następujących parametrach:
* n_estimators: 128
* max_depth: 7
* learning_rate: 1

## Zadanie 4: Rejestrowanie i wersjonowanie modelu w MLflow
Po przejściu do zakładki *Artifacts* w wybranym Run'ie, MLflow automatycznie wygenerował zestaw plików niezbędnych do odtworzenia modelu:
1. **MLmodel** - plik konfiguracyjny (metadane) opisujący, w jaki sposób model ma zostać załadowany przez narzędzia MLflow.
2. **conda.yaml** i **requirements.txt** - pliki zawierające pełne środowisko i zależności (wersje bibliotek), co gwarantuje, że model zadziała identycznie na innym urządzeniu.


## Zadanie 5: Wykorzystanie modelu zarejestrowanego w MLflow
Do weryfikacji działania zapisanego modelu utworzono skrypt `predict.py`. Model został załadowany po jego unikalnym Run ID.

Do testu wykorzystano 10 pierwszych próbek ze zbioru danych. Wynik działania skryptu:

**Prawdziwe etykiety:** [0 0 0 0 0 0 0 0 0 0]
**Przewidywane etykiety:** [0 0 0 0 0 0 0 0 0 0]
**Prawdopodobieństwa klas:** 
[[9.96345639e-01 3.65434051e-03]
 [9.99331415e-01 6.68606430e-04]
 [9.99892235e-01 1.07775224e-04]
 [9.96394455e-01 3.60552780e-03]
 [9.84435916e-01 1.55640692e-02]
 [9.92507696e-01 7.49228010e-03]
 [9.99939382e-01 6.05964269e-05]
 [9.99913812e-01 8.62045199e-05]
 [9.98497367e-01 1.50265533e-03]
 [9.94571507e-01 5.42846695e-03]]

Z powyższego testu wynika, że model został poprawnie załadowany ze ścieżki i generuje poprawne predykcje wraz z odpowiednimi prawdopodobieństwami przynależności do klas (0 - nowotwór złośliwy, 1 - nowotwór łagodny).