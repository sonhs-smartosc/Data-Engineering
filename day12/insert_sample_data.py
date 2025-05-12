# insert_sample_data.py

import os
import psycopg2
import time
from dotenv import load_dotenv

load_dotenv()

print(os.getenv('DBT_USER'))
DBT_USER = os.getenv('DBT_USER')
DBT_PASSWORD = os.getenv('DBT_PASSWORD')
DBT_DEMO_DB = os.getenv('DBT_DEMO_DB')
DB_HOST = 'localhost'
DB_PORT = '5432'

# Thông tin schema và bảng nguồn
SOURCE_SCHEMA = 'raw_data'
ORDERS_TABLE = 'orders'

# Dữ liệu mẫu để chèn (danh sách các tuple)
SAMPLE_ORDERS_DATA = [
    (101, '2023-01-05', 50.00),
    (102, '2023-01-06', 120.50),
    (101, '2023-01-07', 75.25),
    (103, '2023-01-08', 210.00),
    (102, '2023-01-09', 40.00),
    (104, '2023-01-10', 155.75),
    (101, '2023-01-11', 90.00),
    (103, '2023-01-12', 300.00),
]

# SQL để tạo schema và bảng
CREATE_SCHEMA_SQL = f"CREATE SCHEMA IF NOT EXISTS {SOURCE_SCHEMA};"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {SOURCE_SCHEMA}.{ORDERS_TABLE} (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE,
    amount NUMERIC(10, 2)
);
"""

# SQL để chèn dữ liệu
# Sử dụng %s làm placeholder để tránh SQL Injection
INSERT_DATA_SQL = f"""
INSERT INTO {SOURCE_SCHEMA}.{ORDERS_TABLE} (customer_id, order_date, amount)
VALUES (%s, %s, %s);
"""

def wait_for_db(host, port, dbname, user, password, retries=10, delay=5):
    """Chờ database sẵn sàng kết nối."""
    print(f"Waiting for database at {host}:{port} to be ready...")
    for i in range(retries):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=dbname,
                user=user,
                password=password
            )
            conn.close()
            print("Database is ready!")
            return True
        except psycopg2.OperationalError as e:
            print(f"Attempt {i+1}/{retries} failed: {e}")
            time.sleep(delay)
    print("Database did not become ready after multiple retries.")
    return False

def insert_sample_data():
    """Kết nối database và chèn dữ liệu mẫu."""
    conn = None
    cur = None
    try:
        # Kết nối đến database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DBT_DEMO_DB,
            user=DBT_USER,
            password=DBT_PASSWORD
        )
        cur = conn.cursor()

        # Tạo schema
        print(f"Creating schema '{SOURCE_SCHEMA}' if not exists...")
        cur.execute(CREATE_SCHEMA_SQL)
        conn.commit()
        print("Schema created or already exists.")

        # Tạo bảng
        print(f"Creating table '{SOURCE_SCHEMA}.{ORDERS_TABLE}' if not exists...")
        cur.execute(CREATE_TABLE_SQL)
        conn.commit()
        print("Table created or already exists.")

        # Kiểm tra xem bảng đã có dữ liệu chưa trước khi chèn
        cur.execute(f"SELECT COUNT(*) FROM {SOURCE_SCHEMA}.{ORDERS_TABLE};")
        count = cur.fetchone()[0]

        if count == 0:
            # Chèn dữ liệu mẫu
            print(f"Inserting {len(SAMPLE_ORDERS_DATA)} sample rows into {SOURCE_SCHEMA}.{ORDERS_TABLE}...")
            cur.executemany(INSERT_DATA_SQL, SAMPLE_ORDERS_DATA)
            conn.commit()
            print("Sample data inserted successfully.")
        else:
            print(f"Table {SOURCE_SCHEMA}.{ORDERS_TABLE} already contains {count} rows. Skipping sample data insertion.")

    except psycopg2.OperationalError as e:
        print(f"Database connection or operation failed: {e}")
        print("Please ensure the Docker container is running and accessible.")
    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback() # Rollback transaction in case of error
            print("Transaction rolled back.")
    finally:
        # Đóng cursor và kết nối
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    # Kiểm tra xem các biến môi trường cần thiết đã được đặt chưa
    if not all([DBT_USER, DBT_PASSWORD, DBT_DEMO_DB]):
        print("Error: Database connection environment variables (DBT_USER, DBT_PASSWORD, DBT_DEMO_DB) are not set.")
        print("Please ensure you have a .env file or have set these variables in your environment.")
    else:
        # Chờ database sẵn sàng trước khi thử kết nối
        if wait_for_db(DB_HOST, DB_PORT, DBT_DEMO_DB, DBT_USER, DBT_PASSWORD):
             insert_sample_data()

