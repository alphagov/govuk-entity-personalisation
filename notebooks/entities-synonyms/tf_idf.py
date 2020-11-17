from src.utils.constants import CONTENT_STORE_HEADERS, CONTENT_STORE_DATES
from src.utils.helper import clean_text

from time import time
from os import getenv
from multiprocessing import cpu_count

import pandas as pd
from pandarallel import pandarallel
from sklearn.feature_extraction.text import TfidfVectorizer

n_cores = cpu_count()
pandarallel.initialize(nb_workers=n_cores,
                       progress_bar=True,
                       use_memory_fs=False)

DATA_DIR = getenv('DATA_DIR')
FILE_NAME = 'preprocessed_content_store_141020.csv.gz'

# import data
df = pd.read_csv(filepath_or_buffer=DATA_DIR + '/' + FILE_NAME,
                 compression='gzip',
                 encoding='utf-8',
                 sep='\t',
                 header=0,
                 names=list(CONTENT_STORE_HEADERS.keys()),
                 dtype=CONTENT_STORE_HEADERS,
                 parse_dates=CONTENT_STORE_DATES)

# remove NAs
df = df.dropna(subset=['text'], inplace=False)

df_test = df.iloc[:1000]
# use spacy to clean text
start_time = time()
df_test['text_clean'] = df_test['text'].parallel_apply(clean_text,
                                                       lib_sw='spacy',
                                                       lib_l='spacy')
elapsed_time = (time() - start_time) / 60
print(f"Time to clean: {round(number=elapsed_time, digit=2)} minutes")

df.to_csv(path_or_buf='data/processed/df.csv',
          columns=['base_path', 'text', 'text_clean'])
df = pd.read_csv(filepath_or_buffer='data/processed/df.csv')

# convert dtype object to unicode string
df['text_clean'] = df['text_clean'].astype('U').values

# use term-frequency/normalised bag of words
tf_vec = TfidfVectorizer(use_idf=False, norm='l2')
tf_content = tf_vec.fit_transform(raw_documents=df['text_clean'])

# use tf-idf
tfidf_vec = TfidfVectorizer(use_idf=True, lowercase=True, stop_words='english')
tfidf_content = tfidf_vec.fit_transform(raw_documents=df['text_clean'])
