import src.utils.helper_intent_uis as f
import pkg_resources
import os
import pandas as pd
from symspellpy import SymSpell


DATA_PROCESSED = os.getenv('DIR_DATA_PROCESSED')

# set max_dictionary_edit_distance=0 to avoid spelling correction
dictionary_path = pkg_resources.resource_filename("symspellpy",
                                                  "frequency_dictionary_en_82_765.txt")
bigram_path = pkg_resources.resource_filename("symspellpy",
                                              "frequency_bigramdictionary_en_243_342.txt")
sym_spell = SymSpell(max_dictionary_edit_distance=5, prefix_length=7)
# term_index is the column of the term and
# count_index is the column of the term frequency
sym_spell.load_dictionary(corpus=dictionary_path,
                          term_index=0,
                          count_index=1)
sym_spell.load_dictionary(corpus=bigram_path,
                          term_index=0,
                          count_index=1)

# import manually-labelled intent data
df = pd.read_csv(filepath_or_buffer=DATA_PROCESSED + '/test.csv')

# convert to list and remove nans
q3_text = df["Q3"].tolist()
q3_text = [x for x in q3_text if x == x]

# apply spell-corrector so can correctly identify POS
input_term = 'conmdition fotk'
result = sym_spell.lookup_compound(phrase=input_term,
                                   max_edit_distance=4,
                                   ignore_non_words=True,
                                   # keep original casing
                                   transfer_casing=True)
# display suggestion term, term frequency, and edit distance
for suggestion in result:
    print(suggestion.term)
