from src.utils.epoch_logger import EpochLogger
import multiprocessing as mp
from time import time

import os
import pandas as pd
from gensim.models.phrases import Phrases, Phraser
from gensim.models import Word2Vec


DIR_INTERIM = os.getenv('DIR_DATA_INTERIM')


# Reference: https://colab.research.google.com/drive/1A4x2yNS3V1nDZFYoQavpoX7AEQ9Rqtve#scrollTo=m1An-k0q9PMr

n_cores = mp.cpu_count() - 1
epoch_logger = EpochLogger()

df = pd.read_csv(filepath_or_buffer=DIR_INTERIM + '/content_store_clean.csv',
                 index_col=0)


# remove empty values
df = df.dropna(subset=['text_clean'])
# get list of words
sentences = [row.split() for row in df['text_clean']]
# create relevant phrases from words list
bigram_model = Phrases(sentences=sentences,
                       min_count=30,
                       progress_per=10000)
# user Phraser for faster access and efficient memory usage
bigram_model = Phraser(bigram_model)
sentences = bigram_model[sentences]
# get trigrams here: https://stackoverflow.com/a/46130945/13416265

# build vocab
model_w2v = Word2Vec(min_count=30,
                     window=4,
                     size=300,
                     sg=0,
                     sample=6e-5,
                     alpha=0.03,
                     min_alpha=0.0007,
                     negative=20,
                     workers=n_cores)
start_time = time()
model_w2v.build_vocab(sentences=sentences, progress_per=10000)
elapsed_time = round(number=(time() - start_time) / 60, ndigits=2)
print(f"Time taken to build Word2Vec vocabulary: {elapsed_time} minutes")

# train model
start_time = time()
model_w2v.train(sentences=sentences,
                total_examples=model_w2v.corpus_count,
                epochs=10,
                callbacks=[epoch_logger])
elapsed_time = round(number=(time() - start_time) / 60, ndigits=2)
print(f"Time taken to train Word2Vec model: {elapsed_time} minutes")

# make model more memory efficient - okay to do as don't plan to train further
model_w2v.init_sims(replace=True)
model_w2v.save('model/word2vec_cbow.model')
