import src.make_features.helper_bert as f
from src.make_visualisations.helper_bert import plot_distances

import json
from time import time
import pandas as pd
from transformers import BertTokenizer, BertModel


# reference: https://towardsdatascience.com/beyond-classification-with-transformers-and-hugging-face-d38c75f574fb

PRETRAINED_MODEL = 'bert-base-uncased'

df = pd.read_csv(filepath_or_buffer='data/interim/content_store_clean.csv',
                 index_col=0)

text = df['text_clean'].tolist()[:100]
# initialise tokeniser
tokeniser = BertTokenizer.from_pretrained(PRETRAINED_MODEL)

# initialise model, and show hidden states for all layers
model = BertModel.from_pretrained(pretrained_model_name_or_path=PRETRAINED_MODEL,
                                  output_hidden_states=True)
# set to eval mode as don't plan on backprop nor special handling like dropout
model.eval()

# run sentences through tokeniser
input_ids, attention_masks, attention_masks_without_special_tokens = f.preprocess_bert(data=text,
                                                                                       tokeniser_obj=tokeniser,
                                                                                       max_length=50)

# call model on sentences
time_start = time()
outputs = model(input_ids, attention_masks)
hidden_states = outputs[2]
time_elapsed = round((time() - time_start) / 60, 2)
print(f"Time elapsed: {time_elapsed}")
del time_start, time_elapsed

print(f"Total hidden layers: {len(hidden_states)}")
print(f"First layer of batch_size, seq_length, vector_dim: {hidden_states[0].shape}")

# get tokenised version of each sentence
tokenised_sentence = [tokeniser.convert_ids_to_tokens(i) for i in input_ids]
tokenised_sentence[0]

# get word vectors and cosine similarity
word_vectors, word = f.evaluate_vectors(input_hidden_states=hidden_states,
                                        input_tokenised_sentences=tokenised_sentence,
                                        attention_mask=attention_masks,
                                        max_length=30,
                                        mode='average',
                                        top_n_layers=4)
dict_embeddings = dict(zip(word, word_vectors.tolist()))
word_embeddings = pd.DataFrame.from_dict(data=dict_embeddings, orient='index')
word_embeddings = word_embeddings.reset_index()

# export
word_embeddings.to_csv(path_or_buf='data/interim/df_word_embeddings.csv',
                       index=False)

# reload
word_embeddings = pd.read_csv('data/interim/df_word_embeddings.csv')
words_similar = f.get_similar_words(df=word_embeddings,
                                    col_word='index',
                                    similarity_score=0.7)


# remove underscore and number from words
words_similar['word'] = words_similar['word'].str.replace(pat=r'_\d+', repl='')
words_similar['word_compare'] = words_similar['word_compare'].str.replace(pat=r'_\d+', repl='')
# remove duplicates on word and word_compare
words_similar = words_similar[words_similar['word'] != words_similar['word_compare']]
words_similar = words_similar.sort_values(by=['word', 'word_compare', 'cosine_similarity'],
                                          ascending=[True, True, False])
words_similar = words_similar.drop_duplicates(subset=['word', 'word_compare'],
                                              keep='first')
# remove tokens
words_similar = words_similar[~words_similar['word'].str.contains("#")]
words_similar = words_similar[~words_similar['word_compare'].str.contains("#")]
# remove numbers
words_similar = words_similar[~words_similar['word'].str.contains('[0-9]')]
words_similar = words_similar[~words_similar['word_compare'].str.contains('[0-9]')]

# reformat for json output
word_synonyms = words_similar.groupby(by=['word'])[['word_compare',
                                                    'cosine_similarity']].apply(lambda g: g.values.tolist()).to_dict()

with open('data/processed/bert_contentstore_synonyms.json', mode='w') as fp:
    json.dump(obj=word_synonyms,
              fp=fp,
              sort_keys=True,
              indent=4)

# plot
plot_distances(word_vectors=word_vectors,
               labels=word,
               dims=2,
               title="Method: Average")
