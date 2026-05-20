"""
Skrypt generujący syntetyczne zbiory danych do ćwiczeń z re-trenowania modelu.
Tworzy dwa pliki CSV:
  - initial_data.csv  : dane bazowe do pierwszego treningu (symuluje dane historyczne)
  - new_data.csv      : "nowe" dane symulujące świeże dane produkcyjne
"""

import os
import pandas as pd
from sklearn.datasets import make_classification

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
FEATURE_NAMES = [f"feature_{i}" for i in range(6)]


def generate_dataset(n_samples: int, random_state: int) -> pd.DataFrame:
    X, y = make_classification(
        n_samples=n_samples,
        n_features=6,
        n_informative=4,
        n_redundant=1,
        random_state=random_state,
    )
    df = pd.DataFrame(X, columns=FEATURE_NAMES)
    df["target"] = y
    return df


def main():
    # Dane bazowe – symulacja danych historycznych / produkcyjnych (pierwszy model)
    initial_df = generate_dataset(n_samples=800, random_state=42)
    initial_path = os.path.join(OUTPUT_DIR, "initial_data.csv")
    initial_df.to_csv(initial_path, index=False)
    print(f"Zapisano dane bazowe: {initial_path} ({len(initial_df)} rekordów)")

    # Nowe dane – symulacja świeżych danych do re-trenowania
    new_df = generate_dataset(n_samples=800, random_state=99)
    new_path = os.path.join(OUTPUT_DIR, "new_data.csv")
    new_df.to_csv(new_path, index=False)
    print(f"Zapisano nowe dane: {new_path} ({len(new_df)} rekordów)")


if __name__ == "__main__":
    main()
