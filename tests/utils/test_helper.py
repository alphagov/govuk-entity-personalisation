from src.utils.helper import get_n_word_strings, scrub_stopwords, lemmatise_text, clean_text


def test_get_n_word_strings(variable_word_strings, two_word_strings):
    assert get_n_word_strings(terms=variable_word_strings, n=2) == two_word_strings


def test_scrub_stopwords(text, text_stopword):
    assert scrub_stopwords(txt=text,
                           lib_sw='sklearn') == text_stopword['sklearn']
    assert scrub_stopwords(txt=text,
                           lib_sw='nltk') == text_stopword['nltk']
    assert scrub_stopwords(txt=text,
                           lib_sw='spacy') == text_stopword['spacy']
    assert scrub_stopwords(txt=text,
                           lib_sw='gensim') == text_stopword['gensim']


def test_lemmatise_text(text, text_lemmatise):
    assert lemmatise_text(txt=text,
                          lib_l='nltk') == text_lemmatise['nltk']
    assert lemmatise_text(txt=text,
                          lib_l='spacy') == text_lemmatise['spacy']


def test_clean_text(text, text_clean):
    assert clean_text(txt=text,
                      lib_sw='nltk',
                      lib_l='nltk') == text_clean['nltk']
    assert clean_text(txt=text,
                      lib_sw='spacy',
                      lib_l='spacy') == text_clean['spacy']
