"""Laduje przygotowane transakcje (data/transactions.csv) do hurtowni PostgreSQL.

Dane pochodza z LAB11 (surowe zdarzenia ze strumienia, skonsolidowane
do jednego pliku CSV) i maja pola: event_time, user_id, category, amount, status.
"""

import sys

import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql+psycopg2://bi:bi@localhost:5432/ntpd"
CSV_PATH = "data/transactions.csv"
TABLE = "transactions"


def main() -> None:
    engine = create_engine(DB_URL)

    df = pd.read_csv(CSV_PATH, parse_dates=["event_time"])
    df["amount"] = df["amount"].astype(float)

    df.to_sql(TABLE, engine, if_exists="replace", index=False)

    with engine.connect() as conn:
        from sqlalchemy import text
        n = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE}")).scalar()

    print(f"Zaladowano wierszy: {len(df)} (w bazie: {n})")
    print("Zakres czasu:", df["event_time"].min(), "->", df["event_time"].max())
    print("Kategorie:", ", ".join(sorted(df["category"].unique())))


if __name__ == "__main__":
    sys.exit(main())
