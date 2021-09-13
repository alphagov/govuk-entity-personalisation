from src.make_features.extract_synonyms import extract_synonyms
import os
import json
from gensim.models import Word2Vec

if __name__ == "__main__":
    DIR_INTERIM = os.getenv('DIR_DATA_INTERIM', 'data/interim')
    DIR_PROCESSED = os.getenv('DIR_DATA_PROCESSED', 'data/processed')

    # load svo verbs and objects
    # from `src/make_features/extract_subject_verb_object_from_content_titles.py`
    with open(DIR_PROCESSED + '/objects.json') as fp:
        key_objects = json.load(fp=fp)
    with open(DIR_PROCESSED + '/verbs.json') as fp:
        key_entities = json.load(fp=fp)

    # load w2v model
    # from: `notebooks/entities_synonyms/02_train_word2vec_for_cbow_embeddings.py`
    model_w2v = Word2Vec.load('model/word2vec_cbow.model')

    # transform each verb and object so suitable for comparing
    key_objects = [x.replace(' ', '_') for x in key_objects.keys()]
    key_entities = [x.replace(' ', '_') for x in key_entities.keys()]

    # get cbow terms
    synonyms_objects = extract_synonyms(model=model_w2v, terms=key_objects)
    synonyms_entities = extract_synonyms(model=model_w2v, terms=key_entities)

    # export to json file
    with open(DIR_PROCESSED + '/entities_synonyms_cbow.json', mode='w') as fp:
        json.dump(obj=synonyms_entities,
                  fp=fp,
                  sort_keys=True,
                  indent=4)
    with open(DIR_PROCESSED + '/objects_synonyms_cbow.json', mode='w') as fp:
        json.dump(obj=synonyms_objects,
                  fp=fp,
                  sort_keys=True,
                  indent=4)
