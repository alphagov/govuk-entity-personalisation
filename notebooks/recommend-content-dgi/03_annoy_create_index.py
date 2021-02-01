'''
use Approximate Nearest Neighbours to see whether the doc vectors work
requires the Spotify Annoy package
depends on previous creation of two data frames from 02_dgi_embeddings.py:
- embeddings_use_large_2000_df.csv
- text_use_large_2000_df.csv
or whatever you have chosen to call them in the previous step of creating embedding vectors
it makes sense to create various differently named flavours of embedding vectors and adding
them to the settings json beneath, so that you can easily compare different vectors
'''

import os
import json
import pandas as pd
import numpy as np
from annoy import AnnoyIndex


DIR_PROCESSED = os.getenv('DIR_DATA_PROCESSED')
with open('src/utils/config_annoy.json') as file_json:
    settings = json.load(fp=file_json)

# select which embeddings you are going to analyse
embedding_type = 'dgi_use_128'

# pass in the settings above for importing the embeddings data and matching text
embeddings_df = pd.read_csv(filepath_or_buffer=DIR_PROCESSED + '/' + settings[embedding_type]['embeddings'])
embeddings = np.asarray(embeddings_df.iloc[:, :settings[embedding_type]['embedding_dim']])

# build the Annoy Index, f is the length of embedding vector to be used
# f is the length of the vectors, aka 'embedding dimension'
f = settings[embedding_type]['embedding_dim']
# declare an empty index which is going to be based on cosine similarity, aka 'angular'
t = AnnoyIndex(f=f, metric='angular')
# add embedding vectors into the index, converting the values into a list before hand
for i in range(embeddings_df.shape[0]):
    v = [x for x in embeddings[i, :]]
    t.add_item(i, v)

# number of trees determines how refined the groupings are, in practice, it makes little
# difference to performance, in theory, it increases performance with greater number of trees
# you can specify thousands of trees -  no advantage seen in doing this though
t.build(10)
t.save(fn=DIR_PROCESSED + '/' + settings[embedding_type]['ann_index'])
