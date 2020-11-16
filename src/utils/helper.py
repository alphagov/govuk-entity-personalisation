from re import sub
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
from gensim.parsing.preprocessing import remove_stopwords


sp = spacy.load('en_core_web_sm')
STOPWORDS_NLTK = set(stopwords.words('english'))
STOPWORDS_SPACY = sp.Defaults.stop_words

lemmatiser_nltk = WordNetLemmatizer()
nlp = spacy.load(name='en', disable=['parser', 'ner'])


def get_n_word_strings(terms, n):
    """
    Extract all n-word strings from a list of varying n-word strings.

    :param terms: List of strings to extract from.
    :param n: Number of words in a string to extract by.
    :return: A list of n-word strings.
    """
    try:
        if isinstance(terms, str):
            terms = list(terms)
            return get_n_word_strings(terms, n)
        else:
            # count number of terms in each element of list
            counts = [len(x.split()) for x in terms]
            # zip it into a dictionary, where number of terms are the values
            terms_count = dict(zip(terms, counts))
            # 'filter' dictionary for values that are n
            terms_n = [key for key, value in terms_count.items() if value == n]

            return terms_n
    except TypeError:
        print(f"{terms} is not a string or a list of strings. Please enter one!")


def scrub_stopwords(txt, lib_sw=None):
    """
    Removes stopwords from text using a choice of libraries.

    :param txt: The text to pass in to remove stopwords.
    :param lib_sw: The library to use to remove stopwords.
    :return: Text that has had its stopwords removed.
    """
    if lib_sw is None:
        pass
    elif lib_sw == 'sklearn':
        return [word for word in txt.split() if word not in ENGLISH_STOP_WORDS]
    elif lib_sw == 'nltk':
        return [word for word in txt.split() if word not in STOPWORDS_NLTK]
    elif lib_sw == 'spacy':
        return [word for word in txt.split() if word not in STOPWORDS_SPACY]
    elif lib_sw == 'gensim':
        return remove_stopwords(txt)
    else:
        raise Exception(f"Sorry, entered library, {lib_sw}, is not recognised.\n"
                        + "Please enter one from [None, 'sklearn', 'nltk', 'spacy', 'gensim']")


def lemmatise_text(txt, lib_l=None):
    """
    Lemmatises the text using a choice of libaries.

    :param txt: The text to lemmatise on.
    :param lib_l: The library to use to perform lemmatisation.
    :return: Text that has been lemmatised on.
    """
    if lib_l is None:
        pass
    elif lib_l == 'nltk':
        txt_list = word_tokenize(txt)
        return " ".join([lemmatiser_nltk.lemmatize(word=w) for w in txt_list])
    elif lib_l == 'spacy':
        txt = nlp(txt)
        return " ".join(token.lemma_ for token in txt)
    else:
        raise Exception(f"Sorry, entered library, {lib_l}, is not recognised.\n"
                        + "Please enter one from [None, 'nltk', 'spacy']")


def clean_text(txt, **kwargs):
    """
    Cleans text by:
        - Lower-casing
        - Removing punctuation
        - Removing stopwords
        - Lemmatising
    Note: Uses sklearn to remove stopwords to be consistent with sklearn usage elsewhere \n
    Reference:
        - https://medium.com/towards-artificial-intelligence/stop-the-stopwords-using-different-python-libraries-ffa6df941653 # noqa: E501
        - https://www.machinelearningplus.com/nlp/lemmatization-examples-python/#comparingnltktextblobspacypatternandstanfordcorenlp # noqa: E501

    :param txt: The text to pass in to clean.
    :param stopword: The library to use to remove stopwords.
    :param lemma: The library to use to lemma-tise.
    :return: Text that has been cleaned.
    """

    try:
        txt = txt.lower()
        txt = sub(pattern=r'[^\w\s]', repl='', string=txt)
        txt = scrub_stopwords(txt, **kwargs)
        txt = lemmatise_text(txt, **kwargs)
        return txt

    except Exception as error:
        print(f"Cannot clean text. Cause is: {error}")
