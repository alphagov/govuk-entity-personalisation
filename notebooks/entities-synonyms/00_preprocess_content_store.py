# run in terminal: python -m spacy download en_core_web_sm
# run in python: import nltk; nltk.download('stopwords')
from src.utils.constants import CONTENT_STORE_HEADERS, CONTENT_STORE_DATES
from src.utils.preprocess import clean_text

import os
from time import time
import pandas as pd
import swifter  # noqa: F401


DIR_RAW = os.getenv('DIR_DATA_RAW')
DIR_INTERIM = os.getenv('DIR_DATA_INTERIM')


# import data
df = pd.read_csv(filepath_or_buffer=DIR_RAW + '/preprocessed_content_store_010221.csv.gz',
                 compression='gzip',
                 encoding='utf-8',
                 sep='\t',
                 header=0,
                 names=list(CONTENT_STORE_HEADERS.keys()),
                 dtype=CONTENT_STORE_HEADERS,
                 parse_dates=CONTENT_STORE_DATES)

# remove NAs
df = df.dropna(subset=['text'], inplace=False)

# use spacy to clean text
start_time = time()
df['text_clean'] = df['text'].swifter.apply(clean_text,
                                            lib_sw='spacy',
                                            lib_l='spacy')
elapsed_time = (time() - start_time) / 60
print(f"Time to clean: {round(elapsed_time, 2)} minutes")

df.to_csv(path_or_buf=DIR_INTERIM + '/content_store_clean.csv',
          columns=['base_path', 'text', 'text_clean'])
