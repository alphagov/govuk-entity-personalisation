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
cbow_terms = list(model_w2v.wv.vocab.keys())
cbow_objects = list(set(key_objects) & set(cbow_terms))
cbow_verbs = list(set(key_verbs) & set(cbow_terms))
synonyms_objects = [model_w2v.wv.most_similar(positive=x) for x in cbow_objects]
synonyms_verbs = [model_w2v.wv.most_similar(positive=x) for x in cbow_verbs]
synonyms_objects = dict(zip(cbow_objects, synonyms_objects))
synonyms_verbs = dict(zip(cbow_verbs, synonyms_verbs))
