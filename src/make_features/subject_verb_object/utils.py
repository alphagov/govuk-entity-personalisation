import spacy


#  The different models do impact performance, so it's important
#  to consistently use the same model throughout (ie code and tests)
def spacy_model():
    return spacy.load("en_core_web_sm")
