from src.utils.preprocess import get_n_word_strings
from src.utils.helper_synonym import get_synonym_all

import os
from time import time
from multiprocessing import cpu_count
import json

n_cores = cpu_count() - 1
DIR_INTERIM = os.getenv('DIR_DATA_INTERIM')
DIR_PROCESSED = os.getenv('DIR_DATA_PROCESSED')

# load svo verbs and objects
# from `src/make_features/extract_subject_verb_object_from_content_titles.py`
with open(DIR_INTERIM + '/objects.json') as fp:
    key_objects = json.load(fp=fp)
with open(DIR_INTERIM + '/verbs.json') as fp:
    key_verbs = json.load(fp=fp)

# extract single-words
key_objects = get_n_word_strings(terms=key_objects.keys(), n=1)
key_verbs = get_n_word_strings(terms=key_verbs.keys(), n=1)

# call API to get synonyms
tic = time()
synonyms_objects = get_synonym_all(terms=key_objects, threads=n_cores)
synonyms_verbs = get_synonym_all(terms=key_verbs, threads=n_cores)
elapsed_time = round(number=(time() - tic) / 60, ndigits=2)
print(f'Time taken to get synonyms: {elapsed_time} mins')

# remove None values from dictionary so can easily convert to df
synonyms_objects = {k: v for k, v in synonyms_objects.items() if v is not None}
synonyms_verbs = {k: v for k, v in synonyms_verbs.items() if v is not None}

# write to json
with open(DIR_PROCESSED + '/objects_synonyms_thesaurus.json', mode='w') as fp:
    json.dump(obj=synonyms_objects,
              fp=fp,
              sort_keys=True,
              indent=4)
with open(DIR_PROCESSED + '/verbs_synonyms_thesaurus.json', mode='w') as fp:
    json.dump(obj=synonyms_verbs,
              fp=fp,
              sort_keys=True,
              indent=4)
