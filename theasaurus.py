from nltk.corpus import wordnet

# use wordnet to get synonyms of finance - really poor!
synonyms = []
for word in wordnet.synsets('finance'):
    for synonym in word.lemma_names():
        synonyms.append(synonym)
