
def get_n_word_strings(terms, n):
    """
    Extract all n-word strings from a list of varying n-word strings

    :param terms: List of strings to extract from
    :param n: Number of words in a string to extract by
    :return: A list of n-word strings
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
