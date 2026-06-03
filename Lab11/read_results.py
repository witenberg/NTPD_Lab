from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("LAB11_ReadResults") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# odczyt wynikow strumienia jako zwykly batch DataFrame
df = spark.read.parquet("data/output_stream")

print(f"Is streaming: {df.isStreaming}")
df.printSchema()
df.orderBy("window", "category").show(50, truncate=False)
print(f"Total rows: {df.count()}")

spark.stop()
