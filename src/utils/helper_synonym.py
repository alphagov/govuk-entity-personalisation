import concurrent.futures
import threading

from PyDictionary import PyDictionary


# use threading for I/O operation of making API calls to synonyms.com
thread_local = threading.local()


def create_pydict():
    """
    Initialises a PyDictionary class object so we can use it to make calls to the synonyms.com API.

    :param :
    :return: An initialised PyDictionary class
    """
    if not hasattr(thread_local, "synonym"):
        thread_local.session = PyDictionary()
    return thread_local.session


def get_synonym(term):
    """
    Gets the synonyms for a single term passed in.

    :param term: A string to get the synonyms for
    :return: The synonyms of the term passed in
    """
    dictionary = create_pydict()
    try:
        return dictionary.synonym(term)
    except TypeError:
        print(f"{term} is not of string type. Please pass in a string!")


def get_synonym_all(terms, threads=1):
    """
    Gets all the synonyms for each term within a list of terms passed in.

    :param terms: A list of terms to get the synonyms for
    :param threads: Maximum number of threads to execute get_synonym function calls asynchronously
    :return: A dictionary where the keys are the terms and the values are the synonyms
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        synonyms = list(executor.map(get_synonym, terms))
        terms_synonyms = dict(zip(terms, synonyms))
        return terms_synonyms
