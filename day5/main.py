from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from google.cloud import bigquery
from google.oauth2 import service_account
from fastapi import Query
from datetime import date

# Tạo app FastAPI
app = FastAPI(title="BigQuery CRUD API", description="API để thao tác CRUD dữ liệu trên BigQuery", version="1.0.0")

KEY_PATH = './credentials/service-account-key.json'
PROJECT_ID = 'boreal-album-457603-u0'
DATASET_NAME = 'my_sales_dataset'
TABLE_NAME = 'my_sales_table'

credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

class Record(BaseModel):
    Date: Optional[date]
    Salesperson: Optional[str]
    Lead_Name: Optional[str]
    Segment: Optional[str]
    Region: Optional[str]
    Target_Close: Optional[date]
    Forecasted_Monthly_Revenue: Optional[int]
    Opportunity_Stage: Optional[str]
    Weighted_Revenue: Optional[int]
    Closed_Opportunity: Optional[bool]
    Active_Opportunity: Optional[bool]
    Latest_Status_Entry: Optional[bool]

def run_query(query):
    query_job = client.query(query)
    return query_job.result()

# API CRUD

@app.get("/records/")
def get_list_records(
    skip: int = Query(0, ge=0, description=""),
    limit: int = Query(10, gt=0, le=100, description="Số bản ghi lấy ra")
):
    query = f"""
        SELECT * FROM `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}`
        ORDER BY Date
        LIMIT {limit} OFFSET {skip}
    """
    results = run_query(query)
    records = [dict(row) for row in results]
    return records

@app.get("/records/{lead_name}")
def get_record(lead_name: str):
    query = f"""
        SELECT * FROM `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}`
        WHERE `Lead Name` = '{lead_name}'
        LIMIT 1
    """
    results = run_query(query)
    row = next(results, None)
    if row:
        return dict(row)
    else:
        raise HTTPException(status_code=404, detail="Record not found")

@app.post("/records/")
def create_record(record: Record):
    columns = ', '.join(record.dict().keys())
    values = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in record.dict().values()])
    query = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}` ({columns})
        VALUES ({values})
    """
    try:
        client.query(query).result()
        return {"message": "Record inserted"}
    except Exception as e:
        # Optional: xử lý lỗi, ví dụ thêm log
        raise HTTPException(status_code=500, detail=str(e))

# @app.put("/records/{lead_name}")
# def update_record(lead_name: str, record: Record):
#     fields = ', '.join([f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}" for k, v in record.dict().it ems()])
#     query = f"""
#         UPDATE `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}`
#         SET {fields}
#         WHERE Lead_Name = '{lead_name}'
#     """
#     client.query(query).result()
#     return {"message": "Record updated"}
#
# @app.delete("/records/{lead_name}")
# def delete_record(lead_name: str):
#     query = f"""
#         DELETE FROM `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}`
#         WHERE Lead_Name = '{lead_name}'
#     """
#     client.query(query).result()
#     return {"message": "Record deleted"}
