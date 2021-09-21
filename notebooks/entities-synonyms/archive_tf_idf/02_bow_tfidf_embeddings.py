from src.utils.preprocess import get_n_word_strings
from src.utils.helper_embedding import get_embedding_synonyms

import os
import pandas as pd
import csv
import json
from tqdm import tqdm


DIR_PROCESSED = os.getenv('DIR_DATA_PROCESSED')


df_bow = pd.read_pickle(filepath_or_buffer=DIR_PROCESSED + '/tf_embeddings.pkl')
df_tfidf = pd.read_pickle(filepath_or_buffer=DIR_PROCESSED + '/tfidf_embeddings.pkl')
# generated from data/interim/kg_entities.cypher
with open('data/interim/kg_entities.csv', encoding='utf-8') as csv_file:
    # skip first line
    next(csv_file, None)
    file = csv.reader(csv_file, delimiter=',')
    entities = list(file)

# un-nest nested list
entities = [item for sublist in entities for item in sublist]

# lower case so synonyms can be found via API on synonym.com
entities = [item.lower() for item in entities]

# extract single-word entities
entities_single = get_n_word_strings(terms=entities, n=1)


# get synonyms
file_names = ['tf_synonyms', 'tfidf_synonyms']
for counter, df in enumerate((df_bow, df_tfidf)):
    # restrict to entities
    df_entities = df[df['word'].isin(entities_single)].copy()
    synonyms = []
    for word in tqdm(df_entities['word']):
        synonyms.append(get_embedding_synonyms(df=df,
                                               word=word,
                                               col_embedding='bow_embeddings',
                                               threshold=0.75,
                                               enable=False))
    df_entities['embedding_synonyms'] = synonyms
    # filter for non-0-returned synonym results
    df_entities = df_entities[df_entities['embedding_synonyms'].map(len) > 0]
    df_entities = df_entities[['word', 'embedding_synonyms']]

    # save as json files
    file_name = DIR_PROCESSED + '/' + file_names[counter] + '.json'
    synonyms_save = dict(zip(df_entities['word'], df_entities['embedding_synonyms']))
    with open(file_name, mode='w') as fp:
        json.dump(obj=synonyms_save,
                  fp=fp,
                  sort_keys=True,
                  indent=4)
