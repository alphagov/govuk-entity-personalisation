from src.utils.preprocess import get_n_word_strings
from src.utils.helper_synonym import get_synonym_all

from time import time
import pandas as pd
import re
import json


# generated from data/interim/kg_entities.cypher
df_entities = pd.read_csv(filepath_or_buffer='data/interim/kg_entities.csv')

# transform each entity so suitable for comparing
entities = [item.lower() for item in df_entities['e.name']]

# extract single-word entities
entities_single = get_n_word_strings(terms=entities, n=1)

# remove number strings as API won't pick these up
entities_single = [s for s in entities_single if not re.search(r'\d', s)]

# call API to get synonyms
tic = time()
entities_single_synonyms = get_synonym_all(terms=entities_single, threads=3)
elapsed_time = round(number=(time() - tic) / 60, ndigits=2)
print(f'Time taken to get synonyms: {elapsed_time} mins')

# remove None values from dictionary so can easily convert to df
entities_single_synonyms = {k: v for k, v in entities_single_synonyms.items() if v is not None}

# write to json
with open('data/processed/thesaurus_synonyms.json', mode='w') as fp:
    json.dump(obj=entities_single_synonyms,
              fp=fp,
              sort_keys=True,
              indent=4)

# format to dataframe for knowledge graph
df_synonyms = pd.DataFrame.from_dict(data=entities_single_synonyms, orient='index')
df_synonyms = df_synonyms.reset_index()
df_synonyms = df_synonyms.melt(id_vars='index', value_name='synonym')
df_synonyms = df_synonyms.dropna(subset=['synonym'])
df_synonyms = df_synonyms.merge(right=df_entities,
                                how='left',
                                left_on='index',
                                right_on='e.name')
df_synonyms = df_synonyms.rename(columns={'index': 'entity',
                                          'e.entity_type': 'entity_type'})
# remove duplicates to ensure can use Cypher CREATE instead of MERGE for efficiency
df_synonyms = df_synonyms.drop_duplicates(subset=['entity', 'entity_type', 'synonym'])
df_synonyms[['entity',
             'entity_type',
             'synonym']].to_csv(path_or_buf='data/processed/thesaurus_synonyms.csv',
                                index=False)
