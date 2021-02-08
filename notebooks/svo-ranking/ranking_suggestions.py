from src.utils.constants import CONTENT_STORE_HEADERS, CONTENT_STORE_DATES

import os
from google.cloud import bigquery
import pandas as pd


DIR_RAW = os.getenv('DIR_DATA_RAW')
DIR_EXTERNAL = os.getenv('DIR_DATA_EXTERNAL')

# store credentials file in environment variable, GOOGLE_APPLICATION_CREDENTIALS
credential_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

# initialise client
client = bigquery.Client()

# get GA data
with open(DIR_EXTERNAL + '/popularity.sql', mode='r') as f:
    query_sql = f.read()
query_job = client.query(query_sql)
df_ga = query_job.result()
df_ga = pd.DataFrame(data=df_ga)
df_ga = pd.read_csv(filepath_or_buffer=DIR_EXTERNAL + '/bq_results_intra.csv')


# get content store data
df_cs = pd.read_csv(filepath_or_buffer=DIR_RAW + '/preprocessed_content_store_010221.csv.gz',
                    compression='gzip',
                    encoding='utf-8',
                    sep='\t',
                    header=0,
                    names=list(CONTENT_STORE_HEADERS.keys()),
                    dtype=CONTENT_STORE_HEADERS,
                    parse_dates=CONTENT_STORE_DATES)

df_ga = df_ga.merge(right=df_cs[['base_path', 'first_published_at', 'document_type', 'title']],
                    how='left',
                    left_on='pagePath',
                    right_on='base_path',
                    validate='one_to_one')
