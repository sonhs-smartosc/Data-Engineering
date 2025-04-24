from flask import Flask, render_template, jsonify
from google.cloud import bigquery
import os
import dotenv as dotenv

app = Flask(__name__)

dotenv.load_dotenv()

client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query')
def query_data():
    try:
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