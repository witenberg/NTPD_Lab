# Politechnika Bydgoska im. Jana i Jędrzeja Śniadeckich
Wydział Telekomunikacji,  
Informatyki i Elektrotechniki  
Nowoczesne Technologie Przetwarzania Danych  
Laboratorium 11  
Temat: Przetwarzanie strumieniowe danych w Apache Spark Structured Streaming


## Cel ćwiczenia

Celem ćwiczenia jest praktyczne poznanie przetwarzania strumieniowego danych w Apache Spark Structured Streaming; utworzenie strumieniowego DataFrame; wykonanie transformacji i agregacji na danych napływających w czasie; wykorzystanie okien czasowych, watermarkingu i checkpointingu; zapis wyników strumienia do konsoli oraz plików.

## Materiały

https://spark.apache.org/docs/latest/streaming/index.html  
https://spark.apache.org/docs/latest/api/python/index.html  
https://spark.apache.org/docs/latest/sql-programming-guide.html  
https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/index.html

## Zadanie 1: Przygotowanie środowiska

- Skonfiguruj Apache Spark oraz PySpark. Możesz wykorzystać środowisko przygotowane podczas poprzednich laboratoriów.

- Utwórz aplikację PySpark uruchamiającą lokalną sesję Spark i sprawdź, czy działa poprawnie.

- W sprawozdaniu podaj wersję Spark/PySpark oraz sposób uruchomienia aplikacji.

Przykład startowy:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("LAB11_StructuredStreaming") \
    .getOrCreate()

print(spark.version)
```

## Zadanie 2: Strumieniowe wczytywanie danych

- Przygotuj źródło danych strumieniowych oparte na plikach CSV dodawanych do wybranego folderu wejściowego.

- Dane powinny zawierać co najmniej:

  - czas zdarzenia;
  - identyfikator użytkownika lub obiektu;
  - kategorię;
  - wartość liczbową;
  - status zdarzenia.

- Wczytaj dane za pomocą `readStream`, zdefiniuj schemat i wykonaj podstawowe czyszczenie danych.

- Sprawdź, czy utworzony DataFrame jest strumieniowy oraz przedstaw jego schemat w sprawozdaniu.

Przykład startowy:

```python
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.sql.functions import col, to_timestamp

schema = StructType([
    StructField("event_time", StringType()),
    StructField("user_id", StringType()),
    StructField("category", StringType()),
    StructField("amount", DoubleType()),
    StructField("status", StringType()),
])

df = spark.readStream \
    .schema(schema) \
    .option("header", True) \
    .csv("data/input_stream")

df = df.withColumn("event_time", to_timestamp(col("event_time")))
```

Przykładowy format rekordu:

```csv
event_time,user_id,category,amount,status
2026-05-01 10:00:00,u001,books,39.99,paid
```

## Zadanie 3: Transformacje i agregacje strumieniowe

- Na podstawie danych strumieniowych wykonaj minimum dwie transformacje, np. filtrowanie statusu, konwersję typu czasu, wybór kolumn albo obliczenie dodatkowej kolumny.

- Przygotuj agregację według kategorii, np. liczba zdarzeń i suma wartości.

- Zapisz wynik do konsoli z użyciem odpowiedniego trybu wyjścia (`append`, `update` albo `complete`).

- Dodaj kilka kolejnych plików wejściowych podczas działania aplikacji i pokaż, że Spark przetwarza nowe dane bez restartu programu.

Przykład startowy:

```python
from pyspark.sql.functions import count, sum

summary = df.filter(col("status") == "paid") \
    .groupBy("category") \
    .agg(
        count("*").alias("events_count"),
        sum("amount").alias("total_amount")
    )

query = summary.writeStream \
    .format("console") \
    .outputMode("complete") \
    .start()

query.awaitTermination()
```

Na maksymalną ocenę 5 przygotuj prosty generator danych, który automatycznie dodaje nowe pliki do folderu wejściowego.

## Zadanie 4: Okna czasowe i watermarking

- Rozbuduj aplikację o agregacje w oknach czasowych, np. 10-minutowych.

- Zastosuj watermarking dla kolumny czasu zdarzenia.

- Przetestuj działanie aplikacji dla:

  - danych przychodzących w poprawnej kolejności;
  - danych opóźnionych;
  - różnych kategorii i wartości liczbowych.

- W sprawozdaniu wyjaśnij, czym różni się czas zdarzenia od czasu przetwarzania oraz jaki wpływ ma watermarking na dane opóźnione.

Przykład startowy:

```python
from pyspark.sql.functions import col, count, window

window_summary = df.withWatermark("event_time", "10 minutes") \
    .groupBy(window(col("event_time"), "10 minutes"), col("category")) \
    .agg(count("*").alias("events_count"))
```

Na maksymalną ocenę 5 porównaj okna stałe i przesuwające oraz pokaż różnicę w wynikach.

## Zadanie 5: Zapis wyników i checkpointing

- Zapisz wynik przetwarzania strumieniowego do plików, np. w formacie Parquet albo CSV.

- Skonfiguruj checkpointing dla zapytania strumieniowego.

- Zatrzymaj aplikację, uruchom ją ponownie i sprawdź, czy Spark nie przetwarza ponownie tych samych danych wejściowych.

- Wczytaj zapisane wyniki jako zwykły DataFrame batch i porównaj je z wynikami widocznymi w konsoli.

Przykład startowy:

```python
file_query = window_summary.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("path", "data/output_stream") \
    .option("checkpointLocation", "checkpoints/lab11") \
    .start()

file_query.awaitTermination()
```

- W sprawozdaniu opisz różnice między:

  - przetwarzaniem batch a streaming;
  - trybami `append`, `update` i `complete`;
  - checkpointingiem a zwykłym zapisem plików wynikowych.

Wskazówki:  
Nie usuwaj folderu checkpointów podczas testowania odporności na restart. W przypadku problemów sprawdź dokumentację `readStream`, `writeStream`, output modes oraz checkpoint location.

UWAGA: Rozwiązanie zadania należy przesłać w aplikacji Teams. Rozwiązaniem może być link do repozytorium GitHub/GitLab zawierającego kod źródłowy oraz plik `README.md`. Plik `README.md` będzie traktowany jako sprawozdanie: należy w nim opisać sposób uruchomienia projektu, odpowiedzieć na pytania z zadań, a także dodać zrzuty ekranu z wykonania ćwiczeń, jeśli są wymagane.
