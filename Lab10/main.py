from pyspark.sql import SparkSession

# inicjalizacja sesji spark
spark = SparkSession.builder \
    .appName("SparkSQL_Lab10") \
    .getOrCreate()

# ==========================================
# TASK 1: parquet file handling
# ==========================================

# wczytanie pliku parquet
df_parquet = spark.read.parquet("sales.parquet")

df_parquet.show(5)
df_parquet.printSchema()

# ==========================================
# TASK 2: csv file handling & temp view
# ==========================================

# wczytanie csv z klientami
df_csv = spark.read.csv(
    "customers.csv",
    header=True,
    inferSchema=True 
)

df_csv.createOrReplaceTempView("customers_view")

spark.sql("SELECT * FROM customers_view LIMIT 10").show()

# ==========================================
# TASK 3: advanced spark sql queries
# ==========================================

# rejestracja widoku dla pliku parquet
df_parquet.createOrReplaceTempView("sales_view")

# agregacje, grupowanie i warunkowe filtrowanie (kwota > 1000)
query_agg = """
SELECT region, SUM(amount) AS total_amount, COUNT(*) AS transaction_count
FROM sales_view
WHERE amount > 1000
GROUP BY region
"""

df_agg_result = spark.sql(query_agg)
print("--- aggregation results ---")
df_agg_result.show()

# join dwoch widokow na podstawie id klienta
query_join = """
SELECT s.transaction_id, s.product, s.amount, c.customer_name, c.customer_segment
FROM sales_view s
JOIN customers_view c ON s.customer_id = c.id
"""

df_join_result = spark.sql(query_join)
print("--- join results ---")
df_join_result.show()

# zapis wyników do nowych plikow
df_agg_result.write.mode("overwrite").csv("output_agg.csv", header=True)
df_join_result.write.mode("overwrite").parquet("output_join.parquet")

spark.stop()