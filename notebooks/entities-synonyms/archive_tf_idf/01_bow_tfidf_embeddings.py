from src.utils.helper_embedding import reshape_df

import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


DIR_INTERIM = os.getenv('DIR_DATA_INTERIM')
DIR_PROCESSED = os.getenv('DIR_DATA_PROCESSED')


df = pd.read_csv(filepath_or_buffer=DIR_INTERIM + '/content_store_clean.csv')

# convert dtype object to unicode string
df['text_clean'] = df['text_clean'].astype('U').values

df = df.sample(n=10000, random_state=42)

# compute term-frequency/normalised bag of word word vectors
tf_vec = TfidfVectorizer(use_idf=False,
                         norm='l2',
                         max_features=512)
tf_content = tf_vec.fit_transform(raw_documents=df['text_clean'])
tf_word_embeddings = pd.DataFrame(data=tf_content.toarray(),
                                  columns=tf_vec.get_feature_names())
tf_word_embeddings = reshape_df(df=tf_word_embeddings,
                                col_name='bow_embeddings')
tf_word_embeddings.to_pickle(path=DIR_PROCESSED + '/tf_embeddings.pkl')

# compute tf-idf word vectors
tfidf_vec = TfidfVectorizer(use_idf=True,
                            lowercase=True,
                            max_features=512)
tfidf_content = tfidf_vec.fit_transform(raw_documents=df['text_clean'])
tfidf_word_embeddings = pd.DataFrame(data=tfidf_content.toarray(),
                                     columns=tfidf_vec.get_feature_names())
tfidf_word_embeddings = reshape_df(df=tfidf_word_embeddings,
                                   col_name='tfidf_embeddings')
tf_word_embeddings.to_pickle(path=DIR_PROCESSED + '/tfidf_embeddings.pkl')
