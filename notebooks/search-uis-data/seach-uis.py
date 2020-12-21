from src.utils.helper_bq import create_bq_client

import os
import pandas as pd

DATA_RAW = os.getenv('DIR_DATA_RAW')
QUERY_SCRIPT = 'src/make_data/search_uis.sql'

client = create_bq_client()
with open(QUERY_SCRIPT, mode='r') as f:
    query = f.read()

# df_search_uis = pd.read_gbq(query=query)
# df_search_uis = df_search_uis.to_csv(path_or_buf=DATA_RAW + '/df_search_uis.csv', index=False)
df_search_uis = pd.read_csv(filepath_or_buffer=DATA_RAW + '/df_search_uis.csv')
