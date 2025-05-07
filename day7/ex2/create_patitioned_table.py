from google.cloud import bigquery
from google.oauth2 import service_account
import random
from datetime import datetime, timedelta


# Khởi tạo client
SERVICE_ACCOUNT_PATH = '../credentials/service-account-key.json'
PROJECT_ID = 'boreal-album-457603-u0'
DATASET_REF = f'{PROJECT_ID}.sales_dataset'

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH)
client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

def create_date_partitioned_table():
    """
    Tạo bảng phân chia theo ngày (DATE)
    """
    table_id = f"{DATASET_REF}.sales_by_date_extended"

    schema = [
        bigquery.SchemaField("transaction_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("transaction_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("product_id", "STRING"),
        bigquery.SchemaField("amount", "FLOAT"),
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("region", "STRING"),
        bigquery.SchemaField("sales_channel", "STRING"),
    ]

    table = bigquery.Table(table_id, schema=schema)

    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="transaction_date"
    )

    # add clustering
    table.clustering_fields = ["region", "sales_channel"]

    try:
        client.create_table(table)
        print(f"Created table {table_id}, partitioned by transaction_date.")
    except Exception as e:
        print(f"Error when create table {table_id}: {e}")

def create_range_partitioned_table():
    """
    Tạo bảng phân chia theo phạm vi số với nhiều trường hơn.
    """
    table_id = f"{DATASET_REF}.user_by_age"

    schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("age", "INT64"),
    ]

    table = bigquery.Table(table_id, schema=schema)

    table.range_partitioning = bigquery.RangePartitioning(
        field="age",
        range_=bigquery.PartitionRange(start=0, end=100, interval = 10)
    )

    try:
        client.create_table(table)
        print(f"Created table {table_id}, user_by_age success")
    except Exception as e:
        print(f"create error {table_id}: {e}")



def insert_data_sales_by_date():
    """
    Chèn dữ liệu ngẫu nhiên vào bảng `sales_by_date_extended`.
    """
    table_id = f"{DATASET_REF}.sales_by_date_extended"
    rows = []

    for _ in range(200):
        transaction_date = datetime.now() - timedelta(days=random.randint(0, 60))
        row = {
            "transaction_id": f"tx_{random.randint(10000,99999)}",
            "transaction_date": transaction_date.date().isoformat(),
            "product_id": f"prod_{random.randint(1,50)}",
            "amount": round(random.uniform(10, 1000), 2),
            "customer_id": f"cust_{random.randint(100,200)}",
            "region": random.choice(["North", "South", "East", "West"]),
            "sales_channel": random.choice(["Online", "Retail", "Partner"])
        }
        rows.append(row)

    errors = client.insert_rows_json(table_id, rows)
    if errors:
        print(f" error  when insert{table_id}: {errors}")
    else:
        print(f" insert data success {table_id}.")

def insert_data_user_by_age():
    """
    Chèn dữ liệu ngẫu nhiên vào bảng `user_by_age`.
    """
    table_id = f"{DATASET_REF}.user_by_age"
    rows = []

    for _ in range(200):
        age = random.randint(0, 100)
        row = {
            "user_id": f"user_{random.randint(1000,9999)}",
            "name": f"User {random.randint(1, 100)}",
            "age": age
        }
        rows.append(row)

    errors = client.insert_rows_json(table_id, rows)
    if errors:
        print(f" error  when insert {table_id}: {errors}")
    else:
        print(f" insert data success {table_id}.")

if __name__ == "__main__":
    create_date_partitioned_table()
    create_range_partitioned_table()
    insert_data_sales_by_date()
    insert_data_user_by_age()