from src.utils.constants import CONTENT_STORE_HEADERS, CONTENT_STORE_DATES

import os
import pandas as pd

DIR_RAW = os.getenv('DIR_DATA_RAW', 'data/raw')
DIR_PROCESSED = os.getenv('DIR_DATA_PROCESSED', 'data/processed')

# get GA data
df_ga = pd.read_csv(filepath_or_buffer=DIR_RAW + '/bq_results_svo_ranking.csv')
# Remove pages we don't want (search pages or smart answers etc)
# Reduces numbers from ~90m rows to ~14m rows
df_ga = df_ga[~df_ga.pageId.str.contains("\?", na=False)]
df_ga = df_ga[~df_ga.pageId.str.contains("/y/", na=False)]
df_ga = df_ga[~df_ga.pageId.str.contains("/n/", na=False)]
df_ga = df_ga[~df_ga.pageId.str.contains("/[date]/", na=False)]
df_ga = df_ga[~df_ga.pageId.str.contains("/email/unsubscribe/", na=False)]
df_ga = df_ga[~df_ga.pageId.str.contains("/email-signup", na=False)]

# Add path
df_ga['pagePath'] = df_ga['pageId'].str.split('- ').str[-1]

# group and find the mean normalised hits across all the weeks for the time period
df_ga['averagePageHitsMeanNormalised'] = df_ga.groupby('pagePath')['pageHitsMeanNormalised'].transform('mean')
# Drop duplicates
df_ga = df_ga.drop_duplicates(subset=['pagePath'])

# The resultant file would be too big to check into git
# Thus, split it into four chunks that will be
chunk_size = int(df_ga.shape[0] / 4)
index = 1
for start in range(0, df_ga.shape[0], chunk_size):
    df_subset = df_ga.iloc[start:start + chunk_size]
    df_subset[[
           'pagePath',
           'averagePageHitsMeanNormalised']].to_csv(path_or_buf=DIR_PROCESSED + f"/svo_ranking_{index}.csv", index=False)
    index += 1

