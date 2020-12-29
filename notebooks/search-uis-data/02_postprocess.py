from src.utils.helper_intent_uis import get_linguistic_features

import os
import pandas as pd


DATA_PROCESSED = os.getenv('DIR_DATA_PROCESSED')

df = pd.read_csv(filepath_or_buffer=DATA_PROCESSED + '/test.csv')

intent_text_full = df["intent_text_full"].tolist()
# remove nans
intent_text_full = [x for x in intent_text_full if x == x]
# extract pos, tag and dep, lemma and stop
# note: pos is constant between `Q3` and `intent_text_full`
#       whereas dep changes between `Q3` and `intent_text_full`
#       thus, focus on pos for extracting intent from `Q3` later on
linguistic_features = [get_linguistic_features(txt) for txt in intent_text_full]
# store together
intent_text_full = dict(zip(intent_text_full, linguistic_features))

# check one element of dictionary
intent_text_full.get('register as a vulnerable resident for supermarket delivery')
