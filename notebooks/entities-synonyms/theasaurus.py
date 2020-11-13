from os import getenv
from time import time
import csv
import concurrent.futures
import threading

from nltk.corpus import wordnet
from PyDictionary import PyDictionary

DATA_DIR = getenv('DATA_DIR')

# use threading to I/O operation
thread_local = threading.local()


def create_pydict():
    if not hasattr(thread_local, "synonym"):
        thread_local.session = PyDictionary()
    return thread_local.session


def get_synonym(term):
    dictionary = create_pydict()
    return dictionary.synonym(term)


def get_synonym_all(terms):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(get_synonym, terms)


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
get_synonym_all(terms=['finance', 'money', 'state', 'form', 'event', 'person', 'organisation'])
print(time() - tic)
