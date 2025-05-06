import pandas as pd
from sqlalchemy import create_engine

DB_USER = 'your_username'
DB_PASSWORD = 'your_password'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'mydatabase'
TABLE_NAME = 'sales_data'

CSV_FILE_PATH = 'sales_data.csv'

def main():
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    df = pd.read_csv(CSV_FILE_PATH)

    df.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)


if __name__ == "__main__":
    main()