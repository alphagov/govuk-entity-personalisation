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
nlp = spacy.load(name='en_core_web_sm', disable=['parser', 'ner'])


def get_n_word_strings(terms: list, n: int) -> list:
    """
    Extract all n-word strings from a list of varying n-word strings.

    :param terms: List of strings to extract from.
    :param n: Integer of words in a string to extract by.
    :return: List of n-word strings.
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


def scrub_stopwords(txt: str, lib_sw: str = None) -> str:
    """
    Removes stopwords from text using a choice of libraries.
    Reference:
        - https://medium.com/towards-artificial-intelligence/stop-the-stopwords-using-different-python-libraries-ffa6df941653 # noqa: E501

    :param txt: String to pass in to remove stopwords.
    :param lib_sw: String of the library to use to remove stopwords.
    :return: String that has had its stopwords removed.
    """
    if lib_sw is None:
        pass
    elif lib_sw == 'sklearn':
        txt = [word for word in txt.split() if word not in ENGLISH_STOP_WORDS]
        txt = ' '.join(txt)
        return txt
    elif lib_sw == 'nltk':
        txt = [word for word in txt.split() if word not in STOPWORDS_NLTK]
        txt = ' ' .join(txt)
        return txt
    elif lib_sw == 'spacy':
        txt = [word for word in txt.split() if word not in STOPWORDS_SPACY]
        txt = ' '.join(txt)
        return txt
    elif lib_sw == 'gensim':
        txt = remove_stopwords(txt)
        return txt
    else:
        raise Exception(f"Sorry, entered library, {lib_sw}, is not recognised.\n"
                        + "Please enter one from [None, 'sklearn', 'nltk', 'spacy', 'gensim']")


def lemmatise_text(txt: str, lib_l: str = None) -> str:
    """
    Lemmatises the text using a choice of libraries.
    Reference:
        - https://www.machinelearningplus.com/nlp/lemmatization-examples-python/#comparingnltktextblobspacypatternandstanfordcorenlp # noqa: E501

    :param txt: String to lemmatise on.
    :param lib_l: String of the library to use to perform lemmatisation.
    :return: String that has been lemmatised on.
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


def clean_text(txt: str, lib_sw: str, lib_l: str) -> str:
    """
    Cleans text by:
        - Lower-casing
        - Removing punctuation
        - Removing stopwords
        - Lemmatising

    :param txt: String to pass in to clean.
    :param lib_sw: String of the library to use to remove stopwords.
    :param lib_l: String of the library to use to lemmatise.
    :return: String that has been cleaned.
    """

    try:
        txt = txt.lower()
        txt = sub(pattern=r'[^\w\s]', repl='', string=txt)
        txt = scrub_stopwords(txt, lib_sw)
        txt = lemmatise_text(txt, lib_l)
        return txt

    except Exception as error:
        print(f"Cannot clean text. Cause is: {error}")
