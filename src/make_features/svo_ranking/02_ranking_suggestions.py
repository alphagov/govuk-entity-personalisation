from src.utils.constants import CONTENT_STORE_HEADERS, CONTENT_STORE_DATES

import os
import pandas as pd

if __name__ == "__main__":
    DIR_RAW = os.getenv('DIR_DATA_RAW', 'data/raw')
    DIR_EXTERNAL = os.getenv('DIR_DATA_EXTERNAL', 'data/external')
    DIR_PROCESSED = os.getenv('DIR_DATA_DIR_PROCESSED', 'data/processed')

    # get GA and content store data
    df_ga = pd.read_csv(filepath_or_buffer=DIR_RAW + '/bq_results_svo_ranking.csv')

    # Remove pages we don't want (search pages or smart answers etc)
    # Reduces numbers a *lot*
    df_ga = df_ga[~df_ga.pageId.str.contains("\\?", na=False)]
    df_ga = df_ga[~df_ga.pageId.str.contains("/y/", na=False)]
    df_ga = df_ga[~df_ga.pageId.str.contains("/n/", na=False)]
    df_ga = df_ga[~df_ga.pageId.str.contains("/[date]/", na=False)]
    df_ga = df_ga[~df_ga.pageId.str.contains("/email/unsubscribe/", na=False)]
    df_ga = df_ga[~df_ga.pageId.str.contains("/email-signup", na=False)]

    df_cs = pd.read_csv(filepath_or_buffer=DIR_RAW + '/preprocessed_content_store.csv.gz',
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
        df_subset[
            [
                'pagePath',
                'averagePageHitsMeanNormalised'
            ]
        ].to_csv(path_or_buf=DIR_PROCESSED + f"/svo_ranking_{index}.csv", index=False)
        index += 1
