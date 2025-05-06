from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col
import os
import glob

def main():
    spark = SparkSession.builder.appName("CSVProcessing").getOrCreate()

    file_path = "../SalesData.csv"
    df = spark.read.csv(file_path, header=True, inferSchema=True)

    df.show(5)
    print("Schema DataFrame:")
    df.printSchema()

    df = df.withColumn(
        "RevenueCategory",
        when(col("Forecasted Monthly Revenue") >= 10000, "High")
        .when((col("Forecasted Monthly Revenue") >= 5000) & (col("Forecasted Monthly Revenue") < 10000), "Medium")
        .otherwise("Low")
    )

    try:
        df_filtered = df.filter(col('Salesperson') == "Victor Burk")
        df_filtered.show()
    except Exception as e:
        print(f"error: {e}")


    spark.stop()

if __name__ == "__main__":
    main()