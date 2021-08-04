from gensim.models import Word2Vec


def extract_synonyms(model: Word2Vec, terms: list) -> dict:
    """
    Extracts the synonyms for terms in relation to a trained Word2Vec model.
    TO-DO: Add tests but not sure how to because need to create Word2Vec class.

    :param model: Word2Vec trained model where word-embeddings are computed.
    :param terms: List of terms you want to get synonyms for from model.
    :return: Dictionary of each term from terms and their associated synonyms.
    """
    words = list(model.wv.vocab.keys())
    terms_words = list(set(terms) & set(words))
    synonyms = [model.wv.most_similar(positive=x) for x in terms_words]
    synonyms = dict(zip(terms_words, synonyms))
    return synonyms
