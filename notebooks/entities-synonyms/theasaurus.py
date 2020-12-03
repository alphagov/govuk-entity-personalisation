from src.utils.preprocess import get_n_word_strings
from src.utils.helper_synonym import get_synonym_all

from os import getenv
from time import time
import pandas as pd
import re
import csv
import json


DATA_DIR = getenv('DATA_DIR')

# load data
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

# remove number strings as API won't pick these up
entities_single = [s for s in entities_single if not re.search(r'\d', s)]

# call API to get synonyms
tic = time()
entities_single_synonyms = get_synonym_all(terms=entities_single, threads=3)
elapsed_time = round(number=(time() - tic) / 60, ndigits=2)
print(f'Time taken to get synonyms: {elapsed_time} mins')

# remove None values from dictionary so can easily convert to df
entities_single_synonyms = {k: v for k, v in entities_single_synonyms.items() if v is not None}

# write to csv
with open('data/processed/api_synonyms.json', mode='w') as fp:
    json.dump(obj=entities_single_synonyms,
              fp=fp,
              sort_keys=True,
              indent=4)

del csv_file, entities_single, file, tic

# format to dataframe for knowledge graph
df_synonyms = pd.DataFrame.from_dict(data=entities_single_synonyms, orient='index')
df_synonyms = df_synonyms.reset_index()
df_synonyms = df_synonyms.melt(id_vars='index', value_name='synonym')
df_synonyms = df_synonyms.dropna(subset=['synonym'])
df_synonyms = df_synonyms.rename(columns={'index': 'entity'})
df_synonyms[['entity', 'synonym']].to_csv(path_or_buf='data/processed/api_synonyms.csv',
                                          index=False)
