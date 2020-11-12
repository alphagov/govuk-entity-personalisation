from nltk.corpus import wordnet
from PyDictionary import PyDictionary

# use wordnet to get synonyms of finance - really poor!
synonyms = []
for word in wordnet.synsets('finance'):
    for synonym in word.lemma_names():
        synonyms.append(synonym)

# call API to get synonyms - slightly better
dictionary = PyDictionary()
print(dictionary.synonym('finance'))
