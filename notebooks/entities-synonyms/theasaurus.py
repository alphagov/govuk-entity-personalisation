from src.utils.preprocess import get_n_word_strings
from src.utils.helper_synonym import get_synonym_all

from os import getenv
from time import time
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

# call API to get synonyms
tic = time()
entities_single_synonyms = get_synonym_all(terms=entities_single, thread=3)
print(time() - tic)

# write to csv
with open('data/processed/api_synonyms.json', mode='w') as fp:
    json.dump(obj=entities_single_synonyms,
              fp=fp,
              sort_keys=True,
              indent=4)

del csv_file, entities_single, file, tic
