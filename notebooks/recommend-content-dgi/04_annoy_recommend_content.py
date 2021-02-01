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
import src.utils.helper_annoy as a

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

# f is the length of embedding vector to be used
# f is the length of the vectors, aka 'embedding dimension'
f = settings[embedding_type]['embedding_dim']
# load a previously trained Annoy Index (the one you saved two lines up)
u = AnnoyIndex(f=f, metric='angular')
u.load(fn=DIR_PROCESSED + '/' + settings[embedding_type]['ann_index'])

# pass in the settings above for importing the embeddings data and matching text
embeddings_df = pd.read_csv(filepath_or_buffer=DIR_PROCESSED + '/' + settings[embedding_type]['embeddings'])
text_df = pd.read_csv(filepath_or_buffer=DIR_PROCESSED + '/' + settings[embedding_type]['text'])
embeddings = np.asarray(embeddings_df.iloc[:, :settings[embedding_type]['embedding_dim']])
content_id = embeddings_df['content_id'].to_list()

del settings, file_json, embedding_type
# pick a random document, and search the index, printing to screen
a.print_cosine_and_texts(df=text_df, text_idx=np.random.randint(0, 1000))
# this is really how you can compare the ability of different embeddings
a.print_cosine_and_texts(df=text_df, text_idx=3779, max_length_string=10000)

# collect a list of potentially interesting documents, inspecting results
list_interesting_indices = []
n = 1000
while n > 0:
    n -= 1
    n_index_items = u.get_n_items()
    text_idx = np.random.randint(0, n_index_items)
    cosine_angle = a.print_cosine_and_texts(df=text_df, text_idx=text_idx)
    if cosine_angle is not None and 0.9 < cosine_angle < 0.95:
        list_interesting_indices.append(text_idx)

del n, text_idx, cosine_angle, n_index_items
# check count of collected docs which match your criteria above
len(list_interesting_indices)

# set counter
i = 0
# if you highlight the two lines beneath, and hit 'shift + enter' in vs code
# you can manually inspect the results
a.print_cosine_and_texts(df=text_df, text_idx=list_interesting_indices[i])
i += 1


# LOOKING AT GUIDANCE ON VIRUS CONTENT
# this is just an illustration of finding content based on keywords and then looking for similar
# content
# errors out sometime because text_df['doc_text'] has NAs.

# search by date and content type:
doc_types = ['press_release', 'news_story', 'speech', 'world_news_story', 'guidance']
doc_types = ['guidance']
doc_mask = text_df['document_type'].isin(doc_types)
date_mask = text_df['first_published_at'].str[:4].fillna('2000').astype(int) >= 2020
text_mask = text_df['doc_text'].str.lower().str.contains('virus')
content_mask = date_mask & doc_mask & text_mask
cols_keep = ['base_path', 'document_type', 'content_id', 'first_published_at', 'doc_text']
subset_text_df = text_df.loc[content_mask, cols_keep].copy()
subset_text_df.shape

del doc_types, doc_mask, date_mask, text_mask, content_mask, cols_keep

collected_guidance_ids = []
for i in subset_text_df.index.to_list():
    results = np.array(u.get_nns_by_item(i, 2, include_distances=True))
    cosine_angle = a.get_cosine_from_similarity(results[1, 1])
    if cosine_angle > 0.8:
        collected_guidance_ids.append(i)

a.print_cosine_and_texts(df=text_df, text_idx=20800)
i = 0
a.print_cosine_and_texts(df=text_df, text_idx=collected_guidance_ids[i])
i += 1


# search by vector
# this illustrates how you can search for similar documents, based on any text
# being converted into an embedding schema
# requires the loading of the embedding model, which can take time to load, as its 1GB
# flake complains about the import of libraries here, but it will add to the run time of the script
# happy for this to be chopped and moved etc
'''
from universal_sentence_encoder import document_embedding

test_text = ['Britain will roll out COVID-19 vaccinations when they are ready based on clinical advice about who \
    should be prioritised, health minister Matt Hancock said on Monday, after a report that half the population \
    could miss out on the jabs.',
    'Asked about comments by the chair of the government vaccine taskforce to the Financial Times that vaccines \
    would probably only be available to less than half the UK population, Hancock said the taskforce had done \
    good work in procuring vaccines but that deployment was his department responsibility.',
    '“We will take the advice on the deployment of the vaccine, based on clinical advice from the Joint \
    Committee on vaccinations and immunizations,” Hancock told parliament.']

embedding = document_embedding(test_text)
results = np.array(u.get_nns_by_vector(embedding, 4, include_distances=True))

get_cosine_from_similarity(similarity=results[1,0])
text_df['doc_text'][results[0,0]]
'''

# end code
