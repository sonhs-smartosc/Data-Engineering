from flask import Flask, request, jsonify
from flasgger import Swagger
from google.cloud import bigquery
from google.oauth2 import service_account

app = Flask(__name__)
swagger = Swagger(app)

TABLE_NAME='boreal-album-457603-u0.sales_dataset.sales'

project_id = 'boreal-album-457603-u0'
credentials_path = '../credentials/service-account-key.json'
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = bigquery.Client(credentials=credentials, project=project_id )

@app.route('/api/total_revenue_by_segment', methods=['GET'])
def total_revenue_by_segment():
    """
    Total Revenue by Segment
    ---
    responses:
      200:
        description: JSON with segment, total revenue, opportunity count
    """
    query = f"""
        SELECT segment,
               SUM(`weighted_revenue`) as total_revenue,
               COUNT(*) as opportunity_count
        FROM `{TABLE_NAME}`
        GROUP BY segment
        ORDER BY total_revenue DESC
    """
    results = client.query(query).result()
    data = [dict(row) for row in results]
    return jsonify(data)

@app.route('/api/sales_trend_by_date', methods=['GET'])
def sales_trend_by_date():
    """
    Sales Trend by Date
    ---
    responses:
      200:
        description: JSON with date, daily revenue, opportunity count
    """
    query = f"""
        SELECT Date,
               SUM(`weighted_revenue`) as daily_revenue,
               COUNT(*) as opportunity_count
        FROM `{TABLE_NAME}`
        GROUP BY Date
        ORDER BY Date
    """
    results = client.query(query).result()
    data = [dict(row) for row in results]
    return jsonify(data)

@app.route('/api/top_salespeople', methods=['GET'])
def top_salespeople():
    """
    Top Salespeople by Revenue
    ---
    responses:
      200:
        description: JSON with salesperson info
    """
    query = f"""
        SELECT salesperson,
               SUM(`weighted_revenue`) as total_revenue,
               COUNT(*) as opportunity_count,
               AVG(`weighted_revenue`) as avg_opportunity_value
        FROM `{TABLE_NAME}`
        GROUP BY salesperson
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    results = client.query(query).result()
    data = [dict(row) for row in results]
    return jsonify(data)

@app.route('/api/opportunity_stage_analysis', methods=['GET'])
def opportunity_stage_analysis():
    """
    Opportunity Stage Analysis
    ---
    responses:
      200:
        description: JSON with opportunity stage info
    """
    query = f"""
        SELECT `opportunity_stage`,
               SUM(`weighted_revenue`) as total_revenue,
               COUNT(*) as opportunity_count,
               AVG(`weighted_revenue`) as avg_opportunity_value
        FROM `{TABLE_NAME}`
        GROUP BY `opportunity_stage`
        ORDER BY total_revenue DESC
    """
    results = client.query(query).result()
    data = [dict(row) for row in results]
    return jsonify(data)

@app.route('/api/regional_performance', methods=['GET'])
def regional_performance():
    """
    Regional Performance
    ---
    responses:
      200:
        description: JSON with region, metrics
    """
    query = f"""
        SELECT region,
               COUNT(DISTINCT salesperson) as salespeople_count,
               SUM(`weighted_revenue`) as total_revenue,
               COUNT(*) as opportunity_count,
               AVG(`weighted_revenue`) as avg_opportunity_value
        FROM `{TABLE_NAME}`
        GROUP BY region
        ORDER BY total_revenue DESC
    """
    results = client.query(query).result()
    data = [dict(row) for row in results]
    return jsonify(data)

@app.route('/api/active_vs_closed', methods=['GET'])
def active_vs_closed():
    """
    Active vs. Closed Opportunities
    ---
    responses:
      200:
        description: JSON with opportunity status metrics
    """
    query = f"""
        SELECT `active_opportunity`,
               `closed_opportunity`,
               COUNT(*) as opportunity_count,
               SUM(`weighted_revenue`) as total_revenue,
               AVG(`weighted_revenue`) as avg_revenue
        FROM `{TABLE_NAME}`
        GROUP BY `active_opportunity`, `closed_opportunity`
        ORDER BY opportunity_count DESC
    """
    results = client.query(query).result()
    data = [dict(row) for row in results]
    return jsonify(data)

@app.route('/api/segment_performance_by_region', methods=['GET'])
def segment_performance_by_region():
    """
    Segment Performance by Region
    ---
    responses:
      200:
        description: JSON with segment, region, metrics
    """
    query = f"""
        SELECT segment,
               region,
               SUM(`weighted_revenue`) as total_revenue,
               COUNT(*) as opportunity_count
        FROM `{TABLE_NAME}`
        GROUP BY segment, region
        ORDER BY segment, total_revenue DESC
    """
    results = client.query(query).result()
    data = [dict(row) for row in results]
    return jsonify(data)

@app.route('/api/monthly_forecast', methods=['GET'])
def monthly_forecast():
    """
    Monthly Forecasted Revenue Analysis
    ---
    responses:
      200:
        description: JSON with month, year, forecast metrics
    """
    query = f"""
        SELECT EXTRACT(MONTH FROM date) as month,
               EXTRACT(YEAR FROM date) as year,
               AVG(`forecasted_monthly_revenue`) as avg_forecasted_revenue,
               SUM(`forecasted_monthly_revenue`) as total_forecasted_revenue,
               COUNT(*) as opportunity_count
        FROM `{TABLE_NAME}`
        WHERE `forecasted_monthly_revenue` > 0
        GROUP BY year, month
        ORDER BY year, month
    """
    results = client.query(query).result()
    data = [dict(row) for row in results]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
