import spacy


nlp = spacy.load('en_core_web_sm')


def get_linguistic_features(txt: str) -> dict:
    """
    Gets the parts of speech of a text.
    References:
        - https://spacy.io/usage/linguistic-features

    :param txt: String to extract parts of speech from.
    :return: Dictionary of the:
        - pos: parts of speech,
        - tag: detailed POS-tag,
        - dep: relation between tokens,
        - lemma: base form of word, and
        - stop: is token part of a stop list
    """
    txt = nlp(txt)

    list_pos = []
    for token in txt:
        list_pos.append([token.pos_, token.tag_, token.dep_, token.lemma_, token.is_stop])

    # transpose nested list
    list_linguistic_value = [list(x) for x in zip(*list_pos)]

    # create dictionary of each list to their linguistic feature
    list_linguistic_key = ['pos', 'tag', 'dep', 'lemma', 'stop']
    dict_linguistic = dict(zip(list_linguistic_key, list_linguistic_value))

    return dict_linguistic
