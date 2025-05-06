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

    output_dir = "./output_sales_data"
    df.coalesce(1) \
      .write \
      .option("header", "true") \
      .mode("overwrite") \
      .csv(output_dir)

    import time
    time.sleep(1)


    list_files = glob.glob(f"{output_dir}/part-*.csv")
    if list_files:
        os.rename(list_files[0], "sales_data.csv")
        import shutil
        shutil.rmtree(output_dir)
        print("save success sales_data.csv")
    else:
        print("save error")

    spark.stop()

if __name__ == "__main__":
    main()