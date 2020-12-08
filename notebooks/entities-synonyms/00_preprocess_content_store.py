from src.utils.constants import CONTENT_STORE_HEADERS, CONTENT_STORE_DATES
from src.utils.preprocess import clean_text

from time import time
from multiprocessing import cpu_count

import pandas as pd
from pandarallel import pandarallel


n_cores = cpu_count()
pandarallel.initialize(nb_workers=n_cores,
                       progress_bar=True,
                       use_memory_fs=False)

# import data
df = pd.read_csv(filepath_or_buffer='data/raw/preprocessed_content_store_141020.csv.gz',
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
df['text_clean'] = df['text'].parallel_apply(clean_text,
                                             lib_sw='spacy',
                                             lib_l='spacy')
elapsed_time = (time() - start_time) / 60
print(f"Time to clean: {round(elapsed_time, 2)} minutes")

df.to_csv(path_or_buf='data/processed/content_store_clean.csv',
          columns=['base_path', 'text', 'text_clean'])
