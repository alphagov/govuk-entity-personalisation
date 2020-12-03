from gensim.models import Word2Vec
import csv
import json
import pandas as pd


# load model and entities
model_w2v = Word2Vec.load('model/word2vec_cbow.model')
# generated from data/interim/kg_entities.cypher
with open('data/interim/kg_entities.csv', encoding='utf-8') as csv_file:
    # skip first line
    next(csv_file, None)
    file = csv.reader(csv_file, delimiter=',')
    entities = list(file)

# transform each entity so suitable for comparing
entities = [item for sublist in entities for item in sublist]
entities = [item.lower() for item in entities]
entities = [x.replace(' ', '_') for x in entities]

# get cbow terms and those that are entities
cbow_terms = list(model_w2v.wv.vocab.keys())
cbow_entities = list(set(entities) & set(cbow_terms))
synonyms = [model_w2v.wv.most_similar(positive=x) for x in cbow_entities]
cbow_synonyms = dict(zip(cbow_entities, synonyms))

# save as json file - human-readable
with open('data/processed/cbow_synonyms.json', mode='w') as fp:
    json.dump(obj=cbow_synonyms,
              fp=fp,
              sort_keys=True,
              indent=4)

# transform to df for knowledge graph
# extract synonyms with cosine-similarity greater than 0.5 from tuples within nested list
synonyms = [[y[0] for y in x if y[1] > 0.5] for x in synonyms]
cbow_synonyms = pd.DataFrame(data={'entity': cbow_entities,
                                   'synonym': synonyms})
cbow_synonyms = cbow_synonyms.explode(column='synonym')
cbow_synonyms = cbow_synonyms.dropna(subset=['synonym'])
cbow_synonyms.to_csv(path_or_buf='data/processed/cbow_synonyms.csv',
                     index=False)
