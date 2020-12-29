from src.utils.helper_intent_uis import get_linguistic_features

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style='ticks', color_codes=True)

DATA_PROCESSED = os.getenv('DIR_DATA_PROCESSED')

# import manually-labelled intent data
df = pd.read_csv(filepath_or_buffer=DATA_PROCESSED + '/test.csv')

intent_text_full = df["intent_text_full"].tolist()
# remove nans
intent_text_full = [x for x in intent_text_full if x == x]
# extract pos, tag and dep, lemma and stop
# note: pos is constant between `Q3` and `intent_text_full`
#       whereas dep changes between `Q3` and `intent_text_full`
#       thus, focus on pos for extracting intent from `Q3` later on
linguistic_features = [get_linguistic_features(txt) for txt in intent_text_full]

# get pos as we want to see most common pos for intent
pos = [txt.get('pos') for txt in linguistic_features]
lemma = [txt.get('lemma') for txt in linguistic_features]
# store together
intent_pos = dict(zip(intent_text_full, pos))
intent_lemma = dict(zip(intent_text_full, lemma))


# check one element of dictionary
intent_pos.get('register as a vulnerable resident for supermarket delivery')

# convert to dataframe so can plot distribution
df_pos = pd.DataFrame.from_dict(data=intent_pos,
                                orient='index').reset_index()
df_pos = df_pos.melt(id_vars="index",
                     var_name="word_position",
                     value_name="pos")
# relabel to get 'Describe why you came to GOV.UK today?'
df_pos = df_pos.rename(columns={"index": "q3"})
df_pos = df_pos.sort_values(by=["q3", "word_position"])
df_pos = df_pos.dropna(subset=["pos"], axis=0)


# see noun, verb, adp, det and propn are most common
sns.catplot(x="pos", kind='count', data=df_pos,
            order=df_pos['pos'].value_counts().index)
plt.show()
plt.close()

# filter for only noun, verb, adp, det and propn
df_pos = df_pos[df_pos["pos"].isin(["NOUN", "VERB", "ADP", "DET", "PROPN"])]
