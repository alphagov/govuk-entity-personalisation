from src.utils.preprocess import correct_doc_spelling
import src.utils.helper_intent_uis as f
import os
import pandas as pd


DATA_PROCESSED = os.getenv('DIR_DATA_PROCESSED')

# import manually-labelled intent data:
# https://drive.google.com/drive/folders/1mBc3iHys1X44IwPTUeeySTaHrIh9mZiL?usp=sharing
df = pd.read_csv(filepath_or_buffer=DATA_PROCESSED + '/test.csv')

# convert to list and remove nans
q3_text = df["Q3"].tolist()
q3_text = [x for x in q3_text if x == x]

# apply spell-corrector so can correctly identify POS
q3_text_correct = [correct_doc_spelling(doc=txt,
                                        max_edit_distance=2,
                                        ignore_non_words=True,
                                        transfer_casing=True) for txt in q3_text]
# get pos, lemma and stopwords
# due to spell-corrector turning the below, we will not use it:
#   - Corrects "COVID-19" to "OVID 19"
#   - Corrects "lockdown" to "lock own"
# q3_text_pos = f.get_linguistic_dict_to_df(txt=q3_text_correct, linguistic_feature='pos')
q3_text_pos = f.get_linguistic_dict_to_df(txt=q3_text, linguistic_feature='pos')
q3_text_lemma = f.get_linguistic_dict_to_df(txt=q3_text, linguistic_feature='lemma')
q3_text_stop = f.get_linguistic_dict_to_df(txt=q3_text, linguistic_feature='stop')
df_intent = q3_text_lemma.merge(right=q3_text_stop,
                                how='inner',
                                on=["q3", "word_position"],
                                validate='one-to-one')
df_intent = df_intent.merge(right=q3_text_pos,
                            how='inner',
                            on=["q3", "word_position"],
                            validate='one-to-one')

# Option 1: Filter for most common POS with all words
# Common POS are noun, verb, adp, det and propn - from 02_identify_intent_structure.py
df_intent_with_stop = df_intent[df_intent["pos"].isin(["NOUN", "VERB", "ADP", "DET", "PROPN"])]

# Option 2: Filter for most common POS without stopwords
# Common POS are noun, verb, propn and adj
mask_stopword = df_intent["stop"] == False  # noqa: E712
mask_verbs = df_intent["pos"].isin(["NOUN", "VERB", "PROPN", "ADJ"])
mask = mask_verbs & mask_stopword
df_intent_no_stop = df_intent.loc[mask]

# we have a lot of noise to actual intents,
# especially for long comments,
# so explore alternative methods
