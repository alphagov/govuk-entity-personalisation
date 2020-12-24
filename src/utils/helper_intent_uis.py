import spacy

nlp = spacy.load('en_core_web_sm')


def get_pos(txt: str) -> str:
    """
    Gets the parts of speech of a text.
    References:
        - https://spacy.io/usage/linguistic-features

    :param txt: String to extract parts of speech from.
    :return: List of the POS, detailed POS-tag and syntactic dependency/relation between tokens.
    """
    txt = nlp(txt)

    list_pos = []
    for token in txt:
        list_pos.append([token.pos_, token.tag_, token.dep_])

    # transpose nested list
    list_linguisitc_value = [list(x) for x in zip(*list_pos)]

    # create dictionary of each list to their linguistic feature
    list_linguistic_key = ['pos', 'tag', 'dep']
    dict_linguistic = dict(zip(list_linguistic_key, list_linguisitc_value))

    return dict_linguistic
