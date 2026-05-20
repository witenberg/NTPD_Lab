"""
DAG do automatycznego re-trenowania modelu ML.

Zadanie 2: Prosty DAG trenujący model i zapisujący go z wersjonowaniem (timestamp).
Zadanie 3: Rozszerzenie o walidację i warunkową wymianę modelu produkcyjnego.

Przepływ danych:
  load_data → retrain_model → validate_model → compare_and_promote
"""

import os
import datetime as dt
import shutil

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from airflow.decorators import dag, task
from datetime import datetime, timedelta

# Ścieżki bazowe – wyznaczane względem lokalizacji pliku DAG
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "new_data.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
PRODUCTION_DIR = os.path.join(MODELS_DIR, "production")
ARCHIVED_DIR = os.path.join(MODELS_DIR, "archived")
PRODUCTION_MODEL_PATH = os.path.join(PRODUCTION_DIR, "model.pkl")

# Domyślne parametry DAG-a
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="retrain_model_dag",
    default_args=default_args,
    description="Automatyczne re-trenowanie modelu ML z walidacją i warunkową podmianą",
    schedule="@weekly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ml", "retraining", "lab08"],
)
def retrain_model_dag():

    @task
    def load_data() -> dict:
        """Wczytuje nowy zbiór danych z pliku CSV."""
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(
                f"Brak pliku z danymi: {DATA_PATH}. "
                "Uruchom najpierw: python data/generate_data.py"
            )
        df = pd.read_csv(DATA_PATH)
        print(f"Wczytano {len(df)} rekordów z: {DATA_PATH}")
        # Zwracamy słownik (XCom wymaga serializowalnych typów)
        return df.to_dict(orient="list")

    @task
    def retrain_model(data: dict) -> dict:
        """Trenuje nowy model RandomForest i zapisuje go z wersjonowaniem (timestamp)."""
        df = pd.DataFrame(data)
        X = df.drop("target", axis=1)
        y = df["target"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        os.makedirs(MODELS_DIR, exist_ok=True)
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = os.path.join(MODELS_DIR, f"rf_model_{timestamp}.pkl")
        joblib.dump(clf, model_path)

        # Obliczenie accuracy na zbiorze testowym
        y_pred = clf.predict(X_test)
        accuracy = float(accuracy_score(y_test, y_pred))

        print(f"Nowy model zapisano: {model_path}")
        print(f"Accuracy nowego modelu: {accuracy:.4f}")

        return {"model_path": model_path, "accuracy": accuracy}

    @task
    def validate_model(train_result: dict) -> dict:
        """Wyświetla raport walidacyjny nowo wytrenowanego modelu."""
        accuracy = train_result["accuracy"]
        model_path = train_result["model_path"]

        print("=" * 50)
        print("RAPORT WALIDACYJNY")
        print("=" * 50)
        print(f"Ścieżka modelu : {model_path}")
        print(f"Accuracy       : {accuracy:.4f} ({accuracy * 100:.2f}%)")

        if accuracy >= 0.80:
            print("Ocena          : dobra (>= 80%)")
        elif accuracy >= 0.70:
            print("Ocena          : akceptowalna (>= 70%)")
        else:
            print("Ocena          : niska (< 70%) – rozważ zmianę hiperparametrów")

        print("=" * 50)

        return train_result

    @task
    def compare_and_promote(train_result: dict) -> str:
        """
        Zadanie 3: Porównuje nowy model z modelem produkcyjnym.

        Jeśli nowy model jest lepszy  → kopiuje go do folderu production/.
        Jeśli nie jest lepszy         → przenosi do folderu archived/.
        Jeśli brak modelu produkcyjnego → pierwsze wdrożenie, model zostaje promowany.
        """
        os.makedirs(PRODUCTION_DIR, exist_ok=True)
        os.makedirs(ARCHIVED_DIR, exist_ok=True)

        new_model_path = train_result["model_path"]
        new_accuracy = train_result["accuracy"]

        if os.path.exists(PRODUCTION_MODEL_PATH):
            # Wczytanie aktualnego modelu produkcyjnego
            prod_model = joblib.load(PRODUCTION_MODEL_PATH)
            df = pd.read_csv(DATA_PATH)
            X = df.drop("target", axis=1)
            y = df["target"]

            # Ocena modelu produkcyjnego na tym samym zbiorze testowym
            _, X_test, _, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            prod_accuracy = float(accuracy_score(y_test, prod_model.predict(X_test)))

            print(f"Accuracy nowego modelu      : {new_accuracy:.4f}")
            print(f"Accuracy modelu produkcyjnego: {prod_accuracy:.4f}")

            if new_accuracy > prod_accuracy:
                # Nowy model jest lepszy – promujemy go do produkcji
                shutil.copy(new_model_path, PRODUCTION_MODEL_PATH)
                result = (
                    f"PROMOWANY: nowy ({new_accuracy:.4f}) > produkcyjny ({prod_accuracy:.4f})"
                )
            else:
                # Nowy model nie jest lepszy – archiwizujemy go
                archive_name = os.path.basename(new_model_path)
                shutil.move(new_model_path, os.path.join(ARCHIVED_DIR, archive_name))
                result = (
                    f"ZARCHIWIZOWANY: nowy ({new_accuracy:.4f}) <= produkcyjny ({prod_accuracy:.4f})"
                )
        else:
            # Brak istniejącego modelu produkcyjnego – pierwsze wdrożenie
            shutil.copy(new_model_path, PRODUCTION_MODEL_PATH)
            result = f"PIERWSZE WDROŻENIE: model promowany (accuracy={new_accuracy:.4f})"

        print(result)
        return result

    # Definicja kolejności zadań w DAG-u
    raw_data = load_data()
    train_result = retrain_model(raw_data)
    validated_result = validate_model(train_result)
    compare_and_promote(validated_result)


# Rejestracja DAG-a w Airflow
retrain_model_dag()
