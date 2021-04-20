import os
from gensim.models import Word2Vec
import json
import pandas as pd


DIR_INTERIM = os.getenv('DIR_DATA_INTERIM')
DIR_PROCESSED = os.getenv('DIR_DATA_PROCESSED')

# load model and entities
model_w2v = Word2Vec.load('model/word2vec_cbow.model')
# generated from data/interim/kg_entities.cypher
df_entities = pd.read_csv(filepath_or_buffer=DIR_INTERIM + '/kg_entities.csv')

# transform each entity so suitable for comparing
entities = [item.lower() for item in df_entities['e.name']]
entities = [x.replace(' ', '_') for x in entities]

# get cbow terms and those that are entities
cbow_terms = list(model_w2v.wv.vocab.keys())
cbow_entities = list(set(entities) & set(cbow_terms))
synonyms = [model_w2v.wv.most_similar(positive=x) for x in cbow_entities]
cbow_synonyms = dict(zip(cbow_entities, synonyms))

# save as json file - human-readable
with open(DIR_PROCESSED + '/cbow_synonyms.json', mode='w') as fp:
    json.dump(obj=cbow_synonyms,
              fp=fp,
              sort_keys=True,
              indent=4)

# format to df for knowledge graph
# extract synonyms with cosine-similarity greater than 0.5 from tuples within nested list
synonyms = [[y[0] for y in x if y[1] > 0.5] for x in synonyms]
df_cbow_entities = pd.DataFrame(data={'entity': cbow_entities,
                                      'synonym': synonyms})
df_cbow_entities = df_cbow_entities.merge(right=df_entities,
                                          how='left',
                                          left_on='entity',
                                          right_on='e.name')
df_cbow_entities = df_cbow_entities[['entity',
                                     'e.entity_type',
                                     'synonym']].rename(columns={'e.entity_type': 'entity_type'})
# remove duplicates to ensure can use Cypher CREATE instead of MERGE for efficiency
df_cbow_entities = df_cbow_entities.drop_duplicates(subset=['entity', 'entity_type'])

df_cbow_entities = df_cbow_entities.explode(column='synonym')
df_cbow_entities = df_cbow_entities.dropna(subset=['synonym'])
df_cbow_entities.to_csv(path_or_buf=DIR_PROCESSED + '/cbow_synonyms.csv',
                        index=False)
