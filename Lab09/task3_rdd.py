"""
Zadanie 3: Praca z RDD w PySpark
"""

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("RDDExample") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
sc = spark.sparkContext

# wczytanie CSV jako RDD (surowe linie tekstowe)
raw_rdd = sc.textFile("data/sales.csv")

# oddzielenie nagłówka od danych
header = raw_rdd.first()
data_rdd = raw_rdd.filter(lambda line: line != header)

# parsowanie każdego wiersza na słownik
def parse_row(line):
    fields = line.split(",")
    return {
        "order_id": int(fields[0]),
        "product":   fields[1],
        "category":  fields[2],
        "quantity":  int(fields[3]),
        "unit_price": float(fields[4]),
        "region":    fields[5],
        "date":      fields[6],
    }

parsed_rdd = data_rdd.map(parse_row)

# --- liczba wierszy ---
total_rows = parsed_rdd.count()
print(f"Liczba zamówień: {total_rows}")

# --- filtrowanie: tylko elektronika ---
electronics_rdd = parsed_rdd.filter(lambda r: r["category"] == "Electronics")
print(f"Zamówień z kategorii Electronics: {electronics_rdd.count()}")

# --- map: obliczenie wartości każdego zamówienia ---
values_rdd = parsed_rdd.map(lambda r: r["quantity"] * r["unit_price"])

total_revenue = values_rdd.reduce(lambda a, b: a + b)
print(f"Łączny przychód: {total_revenue:.2f} zł")

max_value = values_rdd.max()
min_value = values_rdd.min()
print(f"Najdroższe zamówienie: {max_value:.2f} zł")
print(f"Najtańsze zamówienie:  {min_value:.2f} zł")

# --- suma ilości per kategoria (reduceByKey) ---
qty_by_category = parsed_rdd \
    .map(lambda r: (r["category"], r["quantity"])) \
    .reduceByKey(lambda a, b: a + b)

print("\nŁączna ilość sztuk per kategoria:")
for category, qty in sorted(qty_by_category.collect()):
    print(f"  {category}: {qty}")

# --- przychód per region ---
revenue_by_region = parsed_rdd \
    .map(lambda r: (r["region"], r["quantity"] * r["unit_price"])) \
    .reduceByKey(lambda a, b: a + b) \
    .sortBy(lambda x: x[1], ascending=False)

print("\nPrzychód per region:")
for region, revenue in revenue_by_region.collect():
    print(f"  {region}: {revenue:.2f} zł")

# --- collect: wszystkie produkty (unikalne) ---
products = parsed_rdd.map(lambda r: r["product"]).distinct().collect()
print(f"\nUnikalne produkty ({len(products)}): {sorted(products)}")

spark.stop()
