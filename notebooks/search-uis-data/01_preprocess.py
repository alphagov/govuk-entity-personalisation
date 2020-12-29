from src.utils.helper_bq import create_bq_client
from src.utils.helper_intent_uis import get_linguistic_features

import os
import pandas as pd
import swifter  # noqa: F401


DATA_RAW = os.getenv('DIR_DATA_RAW')
DATA_INTERIM = os.getenv('DIR_DATA_INTERIM')
QUERY_SCRIPT = 'src/make_data/search_uis.sql'

client = create_bq_client()

with open(QUERY_SCRIPT, mode='r') as f:
    query = f.read()

client.close()
del client, f, query

# download data from BigQuery
# and save down so do not always query BQ and waste money
# df_search_uis = pd.read_gbq(query=query)
# df_search_uis = df_search_uis.to_csv(path_or_buf=DATA_RAW + '/df_search_uis.csv', index=False)
df_search_uis = pd.read_csv(filepath_or_buffer=DATA_RAW + '/df_search_uis.csv')

# focus on those who could not find what they are looking for
df_search_uis["Q4"].unique()
# filter for failed terms and where they searched
df_not_found = df_search_uis[df_search_uis["Q4"].isin(["Not sure / Not yet", "No"])]
df_not_found = df_not_found.dropna(subset=["cleaned_search_terms_sequence"])
df_not_found = df_not_found[["primary_key",
                             "fullVisitorId",
                             "session_id",
                             "Started", "Ended",
                             "Q3", "Q4", "Q5", "Q6", "Q7",
                             "ga_date",
                             "total_pageviews_in_session_across_days",
                             "events_sequence",
                             "cleaned_search_terms_sequence",
                             "PageSequence"]]
df_not_found = df_not_found.sort_values(by=["session_id", "Started", "Ended"])

# use POS-tagging to obtain intent
# e.g. I want to look for coronavirus content
# e.g. I wish to apply for a passport
# e.g. I need to get help with applying for benefits
df_not_found["linguistic_features"] = df_not_found["Q3"].swifter.apply(get_linguistic_features)

df_not_found[["Q3", "linguistic_features"]].to_csv(path_or_buf=DATA_INTERIM + '/test.csv',
                                                   index=False)
