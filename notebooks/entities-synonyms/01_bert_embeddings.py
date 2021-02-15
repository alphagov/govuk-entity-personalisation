from src.make_features.helper_bert import preprocess_bert, get_vector, evaluate_vectors

import pandas as pd
from transformers import BertTokenizer, BertModel


PRETRAINED_MODEL = 'bert-base-uncased'

df = pd.read_csv(filepath_or_buffer='data/interim/content_store_clean.csv',
                 index_col=0)

text = df['text_clean'].tolist()[:500]
# initialise tokeniser
tokeniser = BertTokenizer.from_pretrained(PRETRAINED_MODEL)

# initialise model, and show hidden states for all layers
model = BertModel.from_pretrained(pretrained_model_name_or_path=PRETRAINED_MODEL,
                                  output_hidden_states=True)
# set to eval mode as don't plan on backprop nor special handling like dropout
model.eval()

# run sentences through tokeniser
input_ids, attention_masks, attention_masks_without_special_tokens = preprocess_bert(data=text,
                                                                                     tokeniser_obj=tokeniser,
                                                                                     max_length=50,
                                                                                     padding='max_length',
                                                                                     truncate=True)

# call model on sentences
outputs = model(input_ids, attention_masks)
hidden_states = outputs[2]

print(f"Total hidden layers: {len(hidden_states)}")
print(f"First layer of batch_size, seq_length, vector_dim: {hidden_states[0].shape}")

# get tokenised version of each sentence
tokenised_sentence = [tokeniser.convert_ids_to_tokens(i) for i in input_ids]
tokenised_sentence[0]

# get vectors
get_vector(hidden_layers_form_arch=hidden_states,
           token_index=0,
           mode='average',
           top_n_layers=4).shape

# get cosine similarity
mat, cos_dist = evaluate_vectors(input_hidden_states=hidden_states,
                                 input_tokenised_sentences=tokenised_sentence,
                                 attention_mask=attention_masks,
                                 max_len=30,
                                 mode='average',
                                 top_n_layers=4)
