from src.utils.helper_embedding import get_embedding_synonyms
import pandas as pd
from tqdm import tqdm

df_bow = pd.read_pickle(filepath_or_buffer='data/processed/tf_embeddings.pkl')
df_tfidf = pd.read_pickle(filepath_or_buffer='data/processed/tfidf_embeddings.pkl')

# unforgivably slow...
synonyms = []
for word in tqdm(df_bow['word']):
    synonyms.append(get_embedding_synonyms(df=df_bow,
                                           word=word,
                                           col_embedding='bow_embeddings',
                                           threshold=0.75))
df_bow['embedding_synonyms'] = synonyms

# check out synonyms
df_bow_synoynms = df_bow[df_bow['embedding_synonyms'].map(len) > 0]
df_bow_synonyms = df_bow_synoynms[['word', 'embedding_synonyms']]
