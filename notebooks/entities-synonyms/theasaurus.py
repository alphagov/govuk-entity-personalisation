from src.utils.helper_synonym import get_synonym_all

from os import getenv
from time import time
import csv

from nltk.corpus import wordnet


DATA_DIR = getenv('DATA_DIR')


# load data
with open(DATA_DIR + '/kg_entities.csv', encoding='utf-8') as csv_file:
    # skip first line
    next(csv_file, None)
    file = csv.reader(csv_file, delimiter=',')
    data = list(file)

# un-nest nested list
data = [item for sublist in data for item in sublist]

# use wordnet to get synonyms of finance - really poor!
synonyms = []
for word in wordnet.synsets('finance'):
    for synonym in word.lemma():
        synonyms.append(synonym.name())

# call API to get synonyms - slightly better
# dictionary = PyDictionary()
# print(dictionary.synonym('finance'))

tic = time()
test = get_synonym_all(terms=['finance', 'money', 'state', 'form', 'event', 'person', 'organisation'])
print(time() - tic)
