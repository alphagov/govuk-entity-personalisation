from typing import Union
import spacy
import pandas as pd


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


def get_dict_to_df(txt: Union[str, list], linguistic_feature: str) -> pd.DataFrame:
    """
    Extracts a linguistic feature from list of strings and transforms to dataframe.


    :param txt: String or list of strings to extract linguistic features from.
    :param linguistic_feature: String of the linguistic feature such as POS, dep or tag that you want to extract.
                               The linguistic features you can extract are:
                                    - pos: parts of speech,
                                    - tag: detailed POS-tag,
                                    - dep: relation between tokens,
                                    - lemma: base form of word, and
                                    - stop: is token part of a stop list

    :return: Dataframe of original strings and their linguistic features in 'long' format.
    """
    try:
        if isinstance(txt, str):
            txt = [txt]
            return get_dict_to_df(txt=txt, linguistic_feature=linguistic_feature)
        else:
            feature_all = [get_linguistic_features(txt) for txt in txt]
            feature = [txt.get(linguistic_feature) for txt in feature_all]

            # store together as dictionary
            intent_feature = dict(zip(txt, feature))

            # convert to dataframe
            df_feature = pd.DataFrame.from_dict(data=intent_feature,
                                                orient='index').reset_index()
            df_feature = df_feature.melt(id_vars="index",
                                         var_name="word_position",
                                         value_name=linguistic_feature)
            df_feature["word_position"] = df_feature["word_position"].astype(int)
            # relabel to get 'Describe why you came to GOV.UK today?'
            df_feature = df_feature.rename(columns={"index": "q3"})
            df_feature = df_feature.sort_values(by=["q3", "word_position"])
            df_feature = df_feature.dropna(subset=[linguistic_feature], axis=0)

            return df_feature

    except Exception:
        raise
