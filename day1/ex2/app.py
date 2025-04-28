from flask import Flask, render_template, jsonify
# from error_handlers import error_handler, BigQueryError
from google.oauth2 import service_account
from google.cloud import bigquery
import os
import dotenv as dotenv

app = Flask(__name__)

dotenv.load_dotenv()
# client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
def get_bigquery_client():
    """
    Creates and returns a BigQuery client using credentials from environment variables
    """
    try:
        # Check if using service account key file
        key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        project_id = os.getenv("GCP_PROJECT_ID")

        if not project_id:
            print("GCP_PROJECT_ID environment variable is not set")

        if key_path and os.path.exists(key_path):
            # Using service account key file
            credentials = service_account.Credentials.from_service_account_file(
                key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            client = bigquery.Client(credentials=credentials, project=project_id)
        else:
            # Using application default credentials or metadata server on GCP
            client = bigquery.Client(project=project_id)

        # logger.info(f"BigQuery client created successfully for project: {project_id}")
        return client
    except Exception as e:
        print(f"Failed to create BigQuery client: {str(e)}")
        print(f"Failed to create BigQuery client: {str(e)}", 500)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query')
def query_data():
    try:
        client = get_bigquery_client()
        table_id = os.getenv('TABLE_ID')
        query = f"""
        SELECT *
        FROM `{table_id}`
        LIMIT 100
        """

        query_job = client.query(query)
        results = query_job.result()

        data = []
        for row in results:
            data.append(dict(row))

        return jsonify({"status": "success", "data": data})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)