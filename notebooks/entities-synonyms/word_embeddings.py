from src.utils.constants import CONTENT_STORE_HEADERS, CONTENT_STORE_DATES
from src.utils.preprocess import clean_text
from src.utils.helper_embedding import reshape_df

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

# use spacy to clean text
start_time = time()
df['text_clean'] = df['text'].parallel_apply(clean_text,
                                             lib_sw='spacy',
                                             lib_l='spacy')
elapsed_time = (time() - start_time) / 60
print(f"Time to clean: {round(elapsed_time, 2)} minutes")

df.to_csv(path_or_buf='data/processed/df.csv',
          columns=['base_path', 'text', 'text_clean'])
df = pd.read_csv(filepath_or_buffer='data/processed/df.csv')

# convert dtype object to unicode string
df['text_clean'] = df['text_clean'].astype('U').values

df = df.sample(n=10000, random_state=42)

# use term-frequency/normalised bag of words
tf_vec = TfidfVectorizer(use_idf=False,
                         norm='l2',
                         max_features=512)
tf_content = tf_vec.fit_transform(raw_documents=df['text_clean'])
tf_word_embeddings = pd.DataFrame(data=tf_content.toarray(),
                                  columns=tf_vec.get_feature_names())
tf_word_embeddings = reshape_df(df=tf_word_embeddings,
                                col_name='bow_embeddings')
tf_word_embeddings.to_pickle(path='data/processed/tf_embeddings.pkl')

# use tf-idf
tfidf_vec = TfidfVectorizer(use_idf=True,
                            lowercase=True,
                            max_features=512)
tfidf_content = tfidf_vec.fit_transform(raw_documents=df['text_clean'])
tfidf_word_embeddings = pd.DataFrame(data=tfidf_content.toarray(),
                                     columns=tfidf_vec.get_feature_names())
tfidf_word_embeddings = reshape_df(df=tfidf_word_embeddings,
                                   col_name='tfidf_embeddings')
tf_word_embeddings.to_pickle(path='data/processed/tfidf_embeddings.pkl')
