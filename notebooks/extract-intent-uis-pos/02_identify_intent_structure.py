import src.make_features.helper_intent_uis as f

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
# extract pos and lemma
# note: pos is constant between `Q3` and `intent_text_full`
#       whereas dep changes between `Q3` and `intent_text_full`
#       thus, focus on pos for extracting intent from `Q3` later on
df_pos = f.get_linguistic_dict_to_df(txt=intent_text_full, linguistic_feature='pos')
df_lemma = f.get_linguistic_dict_to_df(txt=intent_text_full, linguistic_feature='lemma')
df_stop = f.get_linguistic_dict_to_df(txt=intent_text_full, linguistic_feature='stop')

# join
df_ling_feature = df_lemma.merge(right=df_stop,
                                 how='inner',
                                 on=["q3", "word_position"],
                                 validate='one_to_one')
df_ling_feature = df_ling_feature.merge(right=df_pos,
                                        how='inner',
                                        on=["q3", "word_position"],
                                        validate='one_to_one')


# Option 1: See most common POS with all words
# noun, verb, adp, det and propn are most common
sns.catplot(x="pos", kind='count', data=df_ling_feature,
            order=df_ling_feature['pos'].value_counts().index)
plt.show()
plt.close()

# Option 2: See most common POS with non-stopwords
# noun, verb, propn, adj are most common
df_no_stop = df_ling_feature[df_ling_feature["stop"] == False]  # noqa: E712
sns.catplot(x="pos", kind='count', data=df_no_stop,
            order=df_no_stop['pos'].value_counts().index)
plt.show()
plt.close()
