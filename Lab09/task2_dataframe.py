"""
Zadanie 2: Podstawowe operacje na DataFrame w PySpark
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, avg, count, round as spark_round

# inicjalizacja sesji Spark
spark = SparkSession.builder \
    .appName("DataFrameExample") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# wczytanie danych z CSV
df = spark.read.csv("data/sales.csv", header=True, inferSchema=True)

# --- schemat i podgląd ---
print("=== Schemat danych ===")
df.printSchema()

print("=== Pierwsze 5 wierszy ===")
df.show(5)

# --- selekcja kolumn ---
print("=== Selekcja: produkt, kategoria, cena jednostkowa ===")
df.select("product", "category", "unit_price").show(5)

# --- filtrowanie ---
print("=== Elektronika droższa niż 500 zł ===")
df.filter((col("category") == "Electronics") & (col("unit_price") > 500)).show()

print("=== Zamówienia z regionu North ===")
df.where(col("region") == "North").show()

# --- dodanie kolumny z łączną wartością zamówienia ---
df = df.withColumn("total_value", spark_round(col("quantity") * col("unit_price"), 2))

# --- grupowanie i agregacje ---
print("=== Sprzedaż według kategorii ===")
df.groupBy("category") \
    .agg(
        count("order_id").alias("orders"),
        spark_sum("quantity").alias("total_qty"),
        spark_round(spark_sum("total_value"), 2).alias("total_revenue"),
        spark_round(avg("unit_price"), 2).alias("avg_price")
    ) \
    .show()

print("=== Sprzedaż według regionu ===")
df.groupBy("region") \
    .agg(
        count("order_id").alias("orders"),
        spark_round(spark_sum("total_value"), 2).alias("total_revenue")
    ) \
    .orderBy("total_revenue", ascending=False) \
    .show()

print("=== Top 5 produktów wg łącznej wartości sprzedaży ===")
df.groupBy("product") \
    .agg(spark_round(spark_sum("total_value"), 2).alias("total_revenue")) \
    .orderBy("total_revenue", ascending=False) \
    .show(5)

# --- zapis do CSV i Parquet ---
df.write.mode("overwrite").option("header", True).csv("output/sales_processed_csv")
df.write.mode("overwrite").parquet("output/sales_processed_parquet")
print("=== Dane zapisane do output/sales_processed_csv i output/sales_processed_parquet ===")

spark.stop()
