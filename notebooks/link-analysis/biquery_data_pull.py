from google.cloud import bigquery
import os

# store credentials file in environment variable, GOOGLE_APPLICATION_CREDENTIALS
credential_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

client = bigquery.Client()

sql_string = """
    SELECT
      date,
      hits.page.pagePath
    FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`, unnest(hits) as hits
    WHERE _table_suffix > FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY))
        AND hits.type = "PAGE"
    GROUP BY date, hits.pagePath
    Limit 10
"""

# Perform a query.
# API request
query_job = client.query(sql_string)
# Waits for query to finish
rows = query_job.result()
for row in rows:
    print(row)
