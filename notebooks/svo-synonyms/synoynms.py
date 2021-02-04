import os
import json
import pandas as pd


DIR_INTERIM = os.getenv('DIR_DATA_INTERIM')
DIR_PROCESSED = os.getenv('DIR_DATA_PROCESSED')

# load svo verbs and objects
# from `src/make_features/extract_subject_verb_object_from_content_titles.py`
with open(DIR_INTERIM + 'objects.json') as fp:
    key_objects = json.load(fp=fp)
with open(DIR_INTERIM + 'verbs.json') as fp:
    key_verbs = json.load(fp=fp)

# load content store
# from `notebooks/entities-synonyms/00_preprocess_content_store.py`
df = pd.read_csv(filepath_or_buffer='data/processed/content_store_clean.csv',
                 index_col=0)
