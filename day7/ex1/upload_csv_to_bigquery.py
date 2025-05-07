from google.cloud import bigquery
from google.oauth2 import service_account
import csv
import datetime


def convert_date_columns(input_path, output_path, columns):
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            for col in columns:
                try:
                    date_obj = datetime.datetime.strptime(row[col], '%m/%d/%Y')
                    row[col] = date_obj.strftime('%Y-%m-%d')
                except Exception as e:
                    print(f"Lỗi chuyển đổi {col}: {row[col]}, lỗi: {e}")
            writer.writerow(row)


def upload_csv_to_bigquery():
    project_id = 'boreal-album-457603-u0'
    dataset_name = 'sales_dataset'
    table_name = 'sales'
    csv_file_path = '../SalesData.csv'
    credentials = service_account.Credentials.from_service_account_file('../credentials/service-account-key.json')
    client = bigquery.Client(credentials=credentials, project=project_id )


    dataset_id = f"{project_id}.{dataset_name}"
    table_id = f"{dataset_id}.{table_name}"

    schema = [
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("salesperson", "STRING"),
        bigquery.SchemaField("lead_name", "STRING"),
        bigquery.SchemaField("segment", "STRING"),
        bigquery.SchemaField("region", "STRING"),
        bigquery.SchemaField("target_close", "DATE"),
        bigquery.SchemaField("forecasted_monthly_revenue", "NUMERIC"),
        bigquery.SchemaField("opportunity_stage", "STRING"),
        bigquery.SchemaField("weighted_revenue", "NUMERIC"),
        bigquery.SchemaField("closed_opportunity", "BOOLEAN"),
        bigquery.SchemaField("active_opportunity", "BOOLEAN"),
        bigquery.SchemaField("latest_status_entry", "BOOLEAN"),
    ]

    # try:
    #     table = bigquery.Table(table_id, schema=schema)
    #     table = client.create_table(table)
    #     print(f"create table success {table_id}")
    # except Exception as e:
    #     print(f"error: {e}")

    raw_csv_path = '../SalesData.csv'
    processed_csv_path = '../SalesData_processed.csv'
    convert_date_columns(raw_csv_path, processed_csv_path, ['date', 'target_close'])


    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=schema,
        autodetect=False,
    )

    try:
        with open(processed_csv_path, "rb") as source_file:
            load_job = client.load_table_from_file(
                source_file,
                table_id,
                job_config=job_config,
            )
        load_job.result()
        print(f"upload success {table_id}")
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    upload_csv_to_bigquery()