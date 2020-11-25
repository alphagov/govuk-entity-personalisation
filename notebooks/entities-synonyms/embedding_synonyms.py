from src.utils.preprocess import get_n_word_strings
from src.utils.helper_embedding import get_embedding_synonyms

from os import getenv
import pandas as pd
import csv
from tqdm import tqdm


DATA_DIR = getenv('DATA_DIR')

df_bow = pd.read_pickle(filepath_or_buffer='data/processed/tf_embeddings.pkl')
df_tfidf = pd.read_pickle(filepath_or_buffer='data/processed/tfidf_embeddings.pkl')
with open(DATA_DIR + '/kg_entities.csv', encoding='utf-8') as csv_file:
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

# restrict to entities
df_bow_entities = df_bow[df_bow['word'].isin(entities_single)].copy()
df_tfidf_entities = df_tfidf[df_tfidf['word'].isin(entities_single)].copy()

# compute synonyms
df_synonyms = [df_bow_entities, df_tfidf]
for df in (df_bow_entities, df_tfidf_entities):
    synonyms = []
    for word in tqdm(df['word']):
        synonyms.append(get_embedding_synonyms(df=df_bow,
                                               word=word,
                                               col_embedding='bow_embeddings',
                                               threshold=0.75,
                                               enable=False))
    df['embedding_synonyms'] = synonyms
    # filter for non-0-returned synonym results
    df = df[df['embedding_synonyms'].map(len) > 0]
    df = df[['word', 'embedding_synonyms']]
    df_synonyms.append(df)
