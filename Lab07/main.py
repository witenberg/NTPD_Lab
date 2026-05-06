import pandas as pd
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from evidently import Report, Dataset, DataDefinition, BinaryClassification
from evidently.metrics import *
from evidently.presets import *

# Zadanie 1 - zbieranie danych z produkcji + przygotowanie modelu

# Zbiór historyczny (treningowy)
X_train, y_train = make_classification(n_samples=700, n_features=5, random_state=42)
df_train = pd.DataFrame(X_train, columns=[f"feature_{i}" for i in range(5)])
df_train["target"] = y_train

# Zbiór "produkcyjny"
X_prod, y_prod = make_classification(n_samples=300, n_features=5, random_state=999)
df_prod = pd.DataFrame(X_prod, columns=[f"feature_{i}" for i in range(5)])
df_prod["target"] = y_prod

# EDA
print("analiza zbioru treningowego:")
print(df_train.head())
df_train.info()

print("\nanaliza zbioru produkcyjnego:")
print(df_prod.head())
df_prod.info()

# Inicjalizacja i trening modelu
model = RandomForestClassifier(random_state=42)
model.fit(df_train.drop("target", axis=1), df_train["target"])

# Predykcje dla obu zbiorów
df_train["prediction"] = model.predict(df_train.drop("target", axis=1))
df_prod["prediction"] = model.predict(df_prod.drop("target", axis=1))


# Zadanie 2 - wykrywanie driftu danych z Evidently AI

# Usunięcie kolumny target i prediction z DataDrift
df_drift_train = df_train.drop(['target', 'prediction'], axis=1)
df_drift_prod = df_prod.drop(['target', 'prediction'], axis=1)

# Tworzenie obiektów Dataset
dataset_drift_train = Dataset.from_pandas(df_drift_train, data_definition=DataDefinition())
dataset_drift_prod = Dataset.from_pandas(df_drift_prod, data_definition=DataDefinition())

# Generowanie raportu
data_drift_report = Report(metrics=[DataDriftPreset()])

# Porównanie zbiorów
snapshot_drift = data_drift_report.run(
    reference_data=dataset_drift_train,
    current_data=dataset_drift_prod
)

# Zapis raportu
snapshot_drift.save_html("data_drift_report.html")
print("zapisano: data_drift_report.html")


# Zadanie 3 - analiza jakości predykcji po wdrożeniu

# Przypisanie zadania BinaryClassification
data_def_classification = DataDefinition(
    classification=[
        BinaryClassification(
            target="target",
            prediction_labels="prediction"
        )
    ]
)

dataset_class_train = Dataset.from_pandas(df_train, data_definition=data_def_classification)
dataset_class_prod = Dataset.from_pandas(df_prod, data_definition=data_def_classification)

# Analiza jakości predykcji dla klasyfikacji
classification_performance_report = Report(metrics=[ClassificationPreset()])

snapshot_classification = classification_performance_report.run(
    reference_data=dataset_class_train,
    current_data=dataset_class_prod
)

# Zapis raportu do HTML
snapshot_classification.save_html("classification_quality_report.html")
print("zapisano: classification_quality_report.html")