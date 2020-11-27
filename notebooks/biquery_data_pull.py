from google.cloud import bigquery
import os

credential_path = "/home/james/Downloads/govuk-bigquery-analytics-89867a035cbf.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

client = bigquery.Client()


sql_string = """SELECT
  date,
  hits.page.pagePath
FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`, unnest(hits) as hits
WHERE _table_suffix > FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY))
AND hits.type = "PAGE"
GROUP BY 1,2
Limit 10"""
# Perform a query.
query_job = client.query(sql_string)  # API request
rows = query_job.result()  # Waits for query to finish
for row in rows:
    print(row)
