from src.utils.constants import CONTENT_STORE_HEADERS, CONTENT_STORE_DATES

import os
import pandas as pd


DIR_RAW = os.getenv('DIR_DATA_RAW')
DIR_PROCESSED = os.getenv('DIR_DATA_PROCESSED')

# get GA and content store data
df_ga = pd.read_csv(filepath_or_buffer=DIR_RAW + '/bq_results_svo_ranking.csv')
df_cs = pd.read_csv(filepath_or_buffer=DIR_RAW + '/preprocessed_content_store_010221.csv.gz',
                    compression='gzip',
                    encoding='utf-8',
                    sep='\t',
                    header=0,
                    names=list(CONTENT_STORE_HEADERS.keys()),
                    dtype=CONTENT_STORE_HEADERS,
                    parse_dates=CONTENT_STORE_DATES)

# join first_published_at
df_ga['pagePath'] = df_ga['pageId'].str.split('- ').str[-1]
df_ga = df_ga.merge(right=df_cs[['base_path', 'first_published_at', 'title']],
                    how='left',
                    left_on='pagePath',
                    right_on='base_path',
                    validate='many_to_one')

df_ga = df_ga.rename(columns={'first_published_at': 'pageFirstPublishedAt',
                              'title': 'pageTitle'})
df_ga[['visitStartDateWeek',
       'pageId',
       'pagePath',
       'pageTitle',
       'pageFirstPublishedAt',
       'pageHits',
       'pageHitsMean',
       'allPageHitsMin',
       'allPageHitsMax',
       'pageHitsNormalised']].to_csv(path_or_buf=DIR_PROCESSED + '/svo_ranking.csv',
                                     index=False)
