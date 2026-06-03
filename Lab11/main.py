from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, count, sum, to_timestamp, window
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

# ==========================================
# TASK 1: spark session
# ==========================================

spark = SparkSession.builder \
    .appName("LAB11_StructuredStreaming") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print(f"Spark version: {spark.version}")

# ==========================================
# TASK 2: streaming source (csv files)
# ==========================================

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

# czyszczenie: konwersja czasu, usuniecie brakow i blednych kwot
df = df.withColumn("event_time", to_timestamp(col("event_time"))) \
    .dropna() \
    .filter(col("amount") > 0)

print(f"Is streaming: {df.isStreaming}")
df.printSchema()

# ==========================================
# TASK 3: transformations and aggregation
# ==========================================

# transformacje: filtr statusu + kolumna z kwota brutto
paid = df.filter(col("status") == "paid") \
    .withColumn("amount_gross", col("amount") * 1.23) \
    .select("event_time", "user_id", "category", "amount", "amount_gross")

summary = paid.groupBy("category").agg(
    count("*").alias("events_count"),
    sum("amount").alias("total_amount"),
    avg("amount").alias("avg_amount"),
)

console_query = summary.writeStream \
    .format("console") \
    .outputMode("complete") \
    .option("truncate", False) \
    .queryName("category_summary") \
    .start()

# ==========================================
# TASK 4: time windows + watermarking
# ==========================================

# okno stale (tumbling) 10 min z watermarkiem 10 min
tumbling = paid.withWatermark("event_time", "10 minutes") \
    .groupBy(window(col("event_time"), "10 minutes"), col("category")) \
    .agg(
        count("*").alias("events_count"),
        sum("amount").alias("total_amount"),
    )

# okno przesuwajace (sliding) 10 min co 5 min - do porownania
sliding = paid.withWatermark("event_time", "10 minutes") \
    .groupBy(window(col("event_time"), "10 minutes", "5 minutes"), col("category")) \
    .agg(count("*").alias("events_count"))

sliding_query = sliding.writeStream \
    .format("console") \
    .outputMode("update") \
    .option("truncate", False) \
    .queryName("sliding_window") \
    .start()

# ==========================================
# TASK 5: file sink + checkpointing
# ==========================================

file_query = tumbling.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("path", "data/output_stream") \
    .option("checkpointLocation", "checkpoints/lab11") \
    .queryName("tumbling_to_parquet") \
    .start()

spark.streams.awaitAnyTermination()
