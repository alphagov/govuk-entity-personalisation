from src.utils.constants import CONTENT_STORE_HEADERS, CONTENT_STORE_DATES
from os import getenv
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

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
df_content = df[['base_path', 'text']]

# use term-frequency/normalised bag of words
tf_vec = TfidfVectorizer(use_idf=False, norm='l2')
tf_content = tf_vec.fit_transform(raw_documents=df['text'])

# use tf-idf
tfidf_vec = TfidfVectorizer(use_idf=True, lowercase=True, stop_words='english')
tfidf_content = tfidf_vec.fit_transform(raw_documents=df['text'])
