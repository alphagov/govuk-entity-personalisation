from src.make_features.extract_synonyms import extract_synonyms
import os
import json
from gensim.models import Word2Vec


DIR_INTERIM = os.getenv('DIR_DATA_INTERIM')
DIR_PROCESSED = os.getenv('DIR_DATA_PROCESSED')

# load svo verbs and objects
# from `src/make_features/extract_subject_verb_object_from_content_titles.py`
with open(DIR_INTERIM + '/objects.json') as fp:
    key_objects = json.load(fp=fp)
with open(DIR_INTERIM + '/verbs.json') as fp:
    key_verbs = json.load(fp=fp)

# load w2v model
model_w2v = Word2Vec.load('model/word2vec_cbow.model')

# transform each verb and object so suitable for comparing
key_objects = [x.replace(' ', '_') for x in key_objects.keys()]
key_verbs = [x.replace(' ', '_') for x in key_verbs.keys()]

# get cbow terms
synonyms_objects = extract_synonyms(model=model_w2v, terms=key_objects)
synonyms_verbs = extract_synonyms(model=model_w2v, terms=key_verbs)

# export to json file
with open(DIR_PROCESSED + '/verbs_synonyms_cbow.json', mode='w') as fp:
    json.dump(obj=synonyms_verbs,
              fp=fp,
              sort_keys=True,
              indent=4)
with open(DIR_PROCESSED + '/objects_synonyms_cbow.json', mode='w') as fp:
    json.dump(obj=synonyms_objects,
              fp=fp,
              sort_keys=True,
              indent=4)
