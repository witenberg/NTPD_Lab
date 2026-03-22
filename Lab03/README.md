# Laboratorium 03 - API do serwowania modelu ML

## Instalacja środowiska
Aby uruchomić projekt, przygotuj środowisko:
```bash
cd Lab03
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Uruchomienie serwera deweloperskiego (Zadanie 1)
Serwer uruchamiamy komendą:
`uvicorn app:app --reload`

Dokumentacja Swagger jest dostępna pod adresem: http://127.0.0.1:8000/docs

---

## Testowanie API za pomocą cURL (Zadanie 2)

**1. Test endpointu głównego (`/`):**

`curl -X GET http://127.0.0.1:8000/`

*Oczekiwany wynik:* `{"message":"Hello world!"}`

**2. Test predykcji (`/predict`) - Poprawne dane:**

Endpoint przyjmuje parametry wina w formacie JSON i dokonuje predykcji.

`curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"alcohol\": 13.5, \"malic_acid\": 2.0, \"ash\": 2.4, \"alcalinity_of_ash\": 15.0}"`

*Oczekiwany wynik:* `{"prediction":0,"predicted_class":"class_0","message":"Predykcja zakończona sukcesem","input_data":{"alcohol":13.5,"malic_acid":2.0,"ash":2.4,"alcalinity_of_ash":15.0}}`

**3. Test informacji o modelu (`/info`):**

`curl -X GET http://127.0.0.1:8000/info`

*Oczekiwany wynik:* `{"model_type":"RandomForestClassifier","features_count":4,"feature_names":["alcohol","malic_acid","ash","alcalinity_of_ash"],"dataset":"Wine Dataset (scikit-learn)","description":"Model klasyfikujący odmianę wina (0, 1 lub 2) na podstawie 4 parametrów chemicznych."}`

**4. Test statusu (`/health`):**

`curl -X GET http://127.0.0.1:8000/health`

*Oczekiwany wynik:* `{"status":"ok"}`


---

## Obsługa błędów i walidacja danych (Zadanie 3)
Aplikacja weryfikuje poprawność danych dzięki bibliotece Pydantic. Jeśli prześlemy niekompletny JSON, API zwróci błąd i opisze co poszło nie tak.

**Test błędu walidacji (brakuje 3 z 4 wymaganych parametrów):**
`curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"alcohol\": 13.5}"`
*Oczekiwany wynik:* API zwróci kod 422 (Unprocessable Entity) wraz z czytelnym komunikatem JSON informującym o brakujących polach (`Field required`) dla zmiennych `malic_acid`, `ash` oraz `alcalinity_of_ash`.


---

## Uruchomienie aplikacji w trybie produkcyjnym (Zadanie 5)
Aby uruchomić aplikację w trybie produkcyjnym za pomocą serwera Uvicorn należy użyć poniższej komendy (wymaga usunięcia flagi `--reload`):

`uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4`
*Opis:* Parametr `--workers 4` uruchamia 4 procesy robocze, a `--host 0.0.0.0` pozwala na nasłuchiwanie na wszystkich interfejsach sieciowych.

## Uwagi końcowe
W prawdziwych projektach dobrą praktyką jest grupowanie i wersjonowanie endpointów, na przykład poprzez dodanie prefiksów do ścieżek (np. `/api/v1/predict`). Dodatkowo, ze względów bezpieczeństwa, w środowisku produkcyjnym należy wyłączyć publiczny dostęp do automatycznej dokumentacji (Swagger), ustawiając w konfiguracji FastAPI parametry `docs_url=None` oraz `redoc_url=None`.