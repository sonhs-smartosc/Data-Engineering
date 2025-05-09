import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window
from pyspark.sql.types import StructType, StructField, StringType, LongType, TimestampType

APP_NAME = 'PageViewAggregatorPerPage'
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'page_views'

OUTPUT_PATH = "./spark_output/page_view_counts_per_page"
CHECKPOINT_LOCATION = "./spark_checkpoint/page_view_counts_per_page"

json_schema = StructType([
    StructField("user_id", StringType(), True),
    StructField("page_url", StringType(), True),
    StructField("timestamp", LongType(), True) # Timestamp từ producer (ms)
])

def run_spark_consumer():
    """Configures and runs the Spark Structured Streaming consumer."""
    print(f"Starting Spark Structured Streaming application: {APP_NAME}")
    print(f"Connecting to Kafka broker at {KAFKA_BROKER}, topic '{TOPIC_NAME}'")
    print(f"Writing results to: {OUTPUT_PATH}")
    print(f"Using checkpoint location: {CHECKPOINT_LOCATION}")


    # 💡 Tạo SparkSession
    spark = SparkSession.builder \
        .appName(APP_NAME) \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1").getOrCreate()

    # Set log level to avoid excessive logging from Spark/Kafka
    spark.sparkContext.setLogLevel("WARN")
    print("SparkSession created.")

    kafka_stream_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", TOPIC_NAME) \
        .option("startingOffsets", "latest").load()

    print("Reading stream from Kafka.")

    processed_stream_df = kafka_stream_df \
        .selectExpr("CAST(value AS STRING)", "timestamp") \
        .select(
            from_json(col("value"), json_schema).alias("data"),
            col("timestamp").cast(TimestampType()).alias("kafka_timestamp_casted")
        ) \
        .select(
             "data.*",
             "kafka_timestamp_casted"
        )

    window_duration = "1 minute"
    slide_duration = "1 minute"

    windowed_counts_per_page = processed_stream_df \
        .groupBy(
        window(col("kafka_timestamp_casted"), window_duration, slide_duration),
        col("page_url")
    ) \
        .count()

    # 💡 Chọn lại các cột: Bỏ cột window (theo yêu cầu của bạn)
    # Bước này loại bỏ cột window khỏi DataFrame TRƯỚC KHI ghi ra sink
    final_output_df = windowed_counts_per_page.select("page_url", "count")

    query = windowed_counts_per_page \
        .writeStream \
        .outputMode("complete") \
        .format("console") \
        .start()

    print(f"Streaming query started, writing per-page counts to {OUTPUT_PATH}. Listening for results...")

    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print("\nStopping streaming query.")
        query.stop()
        print("Spark Structured Streaming query stopped.")
    finally:
        spark.stop()
        print("SparkSession stopped.")

# --- Điểm thực thi chính ---
if __name__ == "__main__":
    run_spark_consumer()
