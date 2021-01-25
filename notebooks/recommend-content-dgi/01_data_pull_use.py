# create USE embeddings for content from content store

'''
demo of the Universal Sentence Encoder (USE) on some gov docs
to run this, you must first download:
- preprocessed_content_store_210920.csv from Google Drive
- USE models, which come in two flavours, if you do not have a graphics card, go for DAN
https://www.tensorflow.org/hub/tutorials/semantic_similarity_with_tf_hub_universal_encoder
https://tfhub.dev/google/universal-sentence-encoder-large/5

'''
import src.utils.constants as c
from src.utils.helper_embedding import get_paragraphs_and_embeddings
import os
import pickle
import pandas as pd
import swifter  # noqa: F401
import tensorflow as tf


DATA_DIR = os.getenv('DIR_DATA')
PROCESSED_DIR = os.getenv('DIR_DATA_PROCESSED')

# tests presence of GPUs, to run the Transformer, GPU is necessary
# otherwise looking at a run time of order of days for scoring the whole corpus
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

# data from `notebooks/initial_connection.py`
pickle_file = open('data/relationship_weights.bin', 'rb')
relationship_weights = pickle.load(pickle_file)

# find out whether the weights are directional
relationship_weights[1]
relationship_weights_dict = {}
cid_count = {}
for i, r in enumerate(relationship_weights):
    relationship_weights_dict[(r['m.contentID'], r['n.contentID'])] = r['r.weight']
    cid_count[r['m.contentID']] = cid_count.get(r['m.contentID'], 0) + 1
    cid_count[r['n.contentID']] = cid_count.get(r['n.contentID'], 0) + 1

# only 22.3k cids with a relationship to other cids
len(cid_count)

# looking at the counts for various pairs its clear that the counts are directional
# note: the cids will change each time you pull in new data from graph,
#       so if generating own relationship_weights.bin file, change the
#       cids here
count_1 = relationship_weights_dict[('fff88e3b-ae66-43e4-afd0-6fc1f227b452', 'dc57162b-59f4-4d0f-9b83-a67f74ffccf5')]
count_2 = relationship_weights_dict[('dc57162b-59f4-4d0f-9b83-a67f74ffccf5', 'fff88e3b-ae66-43e4-afd0-6fc1f227b452')]
assert count_1 == count_2, "not the same count"

del count_1, count_2, i, r, relationship_weights_dict, relationship_weights, pickle_file

# import data from the content store, an improvement here would be to download the same from neo4j
content_store_df = pd.read_csv(DATA_DIR + "/preprocessed_content_store_180121.csv.gz",
                               compression='gzip',
                               delimiter="\t",
                               dtype=c.CONTENT_STORE_HEADERS,
                               parse_dates=c.CONTENT_STORE_DATES)
cid_df = pd.DataFrame({'content_id': list(cid_count.keys()), 'relationship_flag': 1})
cols_keep = ['document_type', 'content_id', 'first_published_at', 'details', 'description']
subset_content_df = content_store_df.merge(cid_df, on='content_id', how='inner')[cols_keep].copy()

del cid_count, cols_keep

# get paragraph embeddings
df_para_embed = subset_content_df.swifter.apply(lambda x: get_paragraphs_and_embeddings(id=x['content_id'],
                                                                                        txt=x['details']),
                                                axis=1)
df_para_embed = pd.DataFrame(data=df_para_embed.to_list())

df_para = df_para_embed[[0, 1]]
df_para = df_para.rename(columns={0: 'content_id', 1: 'doc_text'})
df_para = df_para.merge(right=content_store_df[['content_id', 'document_type', 'first_published_at']],
                        how='left',
                        on='content_id')
df_para = df_para.dropna(subset=['doc_text'])

df_embed = pd.DataFrame(data=df_para_embed[2].to_list())
df_embed['content_id'] = df_para_embed[0]
df_embed = df_embed.dropna()

# output dataframes
df_para.to_csv(PROCESSED_DIR + '/text_use_large_2000_df.csv',
               index=False,
               header=True,
               mode='w')
df_embed.to_csv(PROCESSED_DIR + '/embeddings_use_large_2000_df.csv',
                index=False,
                header=True,
                mode='w')
