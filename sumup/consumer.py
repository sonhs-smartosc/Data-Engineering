import os
import json
import time
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, expr, when, lit, array_contains, 
    explode, size, sum as spark_sum, to_timestamp
)
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, 
    ArrayType, BooleanType, TimestampType
)
from google.cloud import bigquery
from google.oauth2 import service_account

# Define schema for parsing match result JSON
team_stats_schema = ArrayType(
    StructType([
        StructField("champion", StringType(), True),
        StructField("kills", IntegerType(), True),
        StructField("deaths", IntegerType(), True),
        StructField("assists", IntegerType(), True),
        StructField("gold", IntegerType(), True),
        StructField("damage_dealt", IntegerType(), True),
        StructField("damage_taken", IntegerType(), True),
        StructField("healing_done", IntegerType(), True)
    ])
)

objectives_schema = StructType([
    StructField("team1_towers", IntegerType(), True),
    StructField("team2_towers", IntegerType(), True),
    StructField("team1_dragons", IntegerType(), True),
    StructField("team2_dragons", IntegerType(), True),
    StructField("team1_barons", IntegerType(), True),
    StructField("team2_barons", IntegerType(), True)
])

match_schema = StructType([
    StructField("match_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("match_type", StringType(), True),
    StructField("map", StringType(), True),
    StructField("duration", IntegerType(), True),
    StructField("winner", StringType(), True),
    StructField("team1", team_stats_schema, True),
    StructField("team2", team_stats_schema, True),
    StructField("objectives", objectives_schema, True)
])

# Google BigQuery configuration
PROJECT_ID = "your-gcp-project-id"
DATASET_ID = "aov_matches"
MATCHES_TABLE = "matches"
TEAMS_TABLE = "teams"
PLAYERS_TABLE = "players"
CREDENTIALS_PATH = "/path/to/your/gcp/credentials.json"

def initialize_spark():
    """Initialize Spark session"""
    return (SparkSession.builder
            .appName("AOVMatchConsumer")
            .config("spark.jars.packages", 
                   "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,com.google.cloud:google-cloud-bigquery:2.13.3")
            .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", CREDENTIALS_PATH)
            .getOrCreate())

def create_kafka_stream(spark):
    """Create streaming DataFrame from Kafka topic"""
    return (spark
            .readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "localhost:9092")
            .option("subscribe", "match-results")
            .option("startingOffsets", "latest")
            .load())

def process_match_data(kafka_df):
    """Process and transform match data from Kafka into the required tables schema"""
    # Parse JSON from Kafka value
    parsed_df = kafka_df.select(
        from_json(col("value").cast("string"), match_schema).alias("data")
    ).select("data.*")
    
    # Convert timestamp string to actual timestamp
    parsed_df = parsed_df.withColumn("start_timestamp", 
                                    to_timestamp(col("timestamp")))
    
    # Calculate end_time based on start_time and duration
    parsed_df = parsed_df.withColumn("end_timestamp", 
                                    expr("start_timestamp + interval duration second"))
    
    # Extract matches table data
    matches_df = parsed_df.select(
        col("match_id"),
        col("start_timestamp").alias("start_time"),
        col("end_timestamp").alias("end_time"),
        col("duration").alias("duration_seconds")
    )
    
    # Process teams data
    # First, compute team totals and create team1 record
    team1_df = parsed_df.select(
        col("match_id"),
        lit(1).alias("team_id"),  # Using 1 for team1 and 2 for team2
        (col("winner") == "team1").alias("win"),
        col("objectives.team1_dragons").alias("dragons"),
        col("objectives.team1_barons").alias("barons"),
        col("objectives.team1_towers").alias("towers"),
        # Note: inhibitors and heralds are not in the original data, adding as 0
        lit(0).alias("inhibitors"),
        lit(0).alias("heralds"),
        # Calculate aggregates from player data
        expr("array_sum(transform(team1, x -> x.kills))").alias("total_kills"),
        expr("array_sum(transform(team1, x -> x.gold))").alias("total_gold"),
        # These fields aren't in the data, so randomly assign for demonstration
        (expr("rand()") > 0.5).alias("first_blood"),
        (expr("rand()") > 0.5).alias("first_tower"),
        (expr("rand()") > 0.5).alias("first_inhibitor")
    )
    
    # Create team2 record
    team2_df = parsed_df.select(
        col("match_id"),
        lit(2).alias("team_id"),
        (col("winner") == "team2").alias("win"),
        col("objectives.team2_dragons").alias("dragons"),
        col("objectives.team2_barons").alias("barons"),
        col("objectives.team2_towers").alias("towers"),
        lit(0).alias("inhibitors"),
        lit(0).alias("heralds"),
        expr("array_sum(transform(team2, x -> x.kills))").alias("total_kills"),
        expr("array_sum(transform(team2, x -> x.gold))").alias("total_gold"),
        (expr("rand()") > 0.5).alias("first_blood"),
        (expr("rand()") > 0.5).alias("first_tower"),
        (expr("rand()") > 0.5).alias("first_inhibitor")
    )
    
    # Union the two team dataframes
    teams_df = team1_df.union(team2_df)
    
    # Process players data - first explode team1 players
    team1_players = parsed_df.select(
        col("match_id"),
        lit(1).alias("team_id"),
        (col("winner") == "team1").alias("win"),
        explode(col("team1")).alias("player_data")
    ).select(
        col("match_id"),
        col("team_id"),
        # Assign participant IDs 1-5 for team1
        expr("posexplode(team1)").getItem(0).plus(1).alias("participant_id"),
        col("player_data.champion"),
        col("player_data.kills"),
        col("player_data.deaths"),
        col("player_data.assists"),
        col("player_data.damage_dealt").alias("total_damage_dealt"),
        col("player_data.damage_taken").alias("total_damage_taken"),
        col("player_data.gold").alias("gold_earned"),
        col("win")
    )
    
    # Process team2 players
    team2_players = parsed_df.select(
        col("match_id"),
        lit(2).alias("team_id"),
        (col("winner") == "team2").alias("win"),
        explode(col("team2")).alias("player_data")
    ).select(
        col("match_id"),
        col("team_id"),
        # Assign participant IDs 6-10 for team2
        expr("posexplode(team2)").getItem(0).plus(6).alias("participant_id"),
        col("player_data.champion"),
        col("player_data.kills"),
        col("player_data.deaths"),
        col("player_data.assists"),
        col("player_data.damage_dealt").alias("total_damage_dealt"),
        col("player_data.damage_taken").alias("total_damage_taken"),
        col("player_data.gold").alias("gold_earned"),
        col("win")
    )
    
    # Union the two player dataframes
    players_df = team1_players.union(team2_players)
    
    return matches_df, teams_df, players_df

def write_to_bigquery(batch_df, table_name, batch_id):
    """Write a dataframe to BigQuery table"""
    try:
        # Set up BigQuery table path
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        
        # Write mode - append to the table
        write_mode = "append"
        
        # Write to BigQuery
        batch_df.write \
            .format("bigquery") \
            .option("table", table_id) \
            .option("temporaryGcsBucket", "your-temp-bucket") \
            .mode(write_mode) \
            .save()
        
        print(f"Successfully wrote batch {batch_id} to BigQuery table {table_id}")
        return True
    
    except Exception as e:
        print(f"Error writing to BigQuery: {str(e)}")
        return False

def process_batch(batch_df, batch_id):
    """Process a batch of data and write to BigQuery"""
    if batch_df.isEmpty():
        print(f"Batch {batch_id} is empty, skipping.")
        return

    try:
        # Parse and transform the data
        matches_df, teams_df, players_df = process_match_data(batch_df)
        
        # Write each table to BigQuery
        write_to_bigquery(matches_df, MATCHES_TABLE, batch_id)
        write_to_bigquery(teams_df, TEAMS_TABLE, batch_id) 
        write_to_bigquery(players_df, PLAYERS_TABLE, batch_id)
        
        print(f"Successfully processed batch {batch_id}")
    except Exception as e:
        print(f"Error processing batch {batch_id}: {str(e)}")
        import traceback
        traceback.print_exc()

def ensure_bigquery_resources():
    """Ensure that BigQuery dataset and tables exist"""
    try:
        # Create BigQuery client
        credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
        client = bigquery.Client(credentials=credentials, project=PROJECT_ID)
        
        # Create dataset if it doesn't exist
        dataset_id = f"{PROJECT_ID}.{DATASET_ID}"
        try:
            client.get_dataset(dataset_id)
            print(f"Dataset {dataset_id} already exists")
        except Exception:
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = "US"  # Set your preferred location
            client.create_dataset(dataset, exists_ok=True)
            print(f"Created dataset {dataset_id}")
        
        # Define table schemas
        matches_schema = [
            bigquery.SchemaField("match_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("start_time", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("end_time", "TIMESTAMP", mode="REQUIRED"), 
            bigquery.SchemaField("duration_seconds", "INTEGER", mode="REQUIRED")
        ]
        
        teams_schema = [
            bigquery.SchemaField("match_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("team_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("win", "BOOLEAN", mode="REQUIRED"),
            bigquery.SchemaField("dragons", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("barons", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("towers", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("inhibitors", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("heralds", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("total_kills", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("total_gold", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("first_blood", "BOOLEAN", mode="REQUIRED"),
            bigquery.SchemaField("first_tower", "BOOLEAN", mode="REQUIRED"),
            bigquery.SchemaField("first_inhibitor", "BOOLEAN", mode="REQUIRED")
        ]
        
        players_schema = [
            bigquery.SchemaField("match_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("team_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("participant_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("champion", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("kills", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("deaths", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("assists", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("total_damage_dealt", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("total_damage_taken", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("gold_earned", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("win", "BOOLEAN", mode="REQUIRED")
        ]
        
        # Create tables if they don't exist
        tables = {
            MATCHES_TABLE: matches_schema,
            TEAMS_TABLE: teams_schema,
            PLAYERS_TABLE: players_schema
        }
        
        for table_name, schema in tables.items():
            table_id = f"{dataset_id}.{table_name}"
            try:
                client.get_table(table_id)
                print(f"Table {table_id} already exists")
            except Exception:
                table = bigquery.Table(table_id, schema=schema)
                client.create_table(table, exists_ok=True)
                print(f"Created table {table_id}")
        
        return True
    
    except Exception as e:
        print(f"Error ensuring BigQuery resources: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_streaming_job():
    """Main function to run the Spark streaming job"""
    # Make sure BigQuery resources exist
    if not ensure_bigquery_resources():
        print("Failed to ensure BigQuery resources. Exiting.")
        return
    
    spark = initialize_spark()
    
    # Create streaming DataFrame from Kafka
    kafka_df = create_kafka_stream(spark)
    
    # Define the streaming query with foreachBatch to handle microbatches
    query = (kafka_df
             .writeStream
             .outputMode("append")
             .foreachBatch(process_batch)
             .option("checkpointLocation", "/tmp/checkpoint")
             .trigger(processingTime="30 seconds")  # Process every 30 seconds
             .start())
    
    # Wait for the streaming query to terminate
    query.awaitTermination()

if __name__ == "__main__":
    try:
        print("Starting Spark Streaming job to consume match results from Kafka and write to BigQuery...")
        run_streaming_job()
    except KeyboardInterrupt:
        print("Consumer interrupted by user")
    except Exception as e:
        print(f"Error in consumer: {e}")
        import traceback
        traceback.print_exc()
