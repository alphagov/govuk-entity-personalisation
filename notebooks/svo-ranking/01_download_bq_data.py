import os
from google.cloud import bigquery
import pandas_gbq as pdg

DIR_RAW = os.getenv('DIR_DATA_RAW', 'data/raw')
DIR_EXTERNAL = os.getenv('DIR_DATA_EXTERNAL', 'data/external')

# store credentials file in environment variable, GOOGLE_APPLICATION_CREDENTIALS
credential_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

# initialise client
client = bigquery.Client()

# get GA data
with open(DIR_EXTERNAL + '/svo_ranking.sql', mode='r') as f:
    query_sql = f.read()
df_ga = pdg.read_gbq(query=query_sql)

# export GA data
df_ga.to_csv(path_or_buf=DIR_RAW + '/bq_results_svo_ranking.csv',
             index=False)
