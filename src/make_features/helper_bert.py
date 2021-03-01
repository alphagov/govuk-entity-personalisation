from tqdm import tqdm
import numpy as np
import pandas as pd
import torch
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer


def preprocess_bert(data: list,
                    tokeniser_obj: BertTokenizer,
                    max_length: int = None) -> (torch.Tensor, torch.Tensor, torch.Tensor):
    """
    Preprocess text for applying pre-trained BERT model.
    References:
        - https://github.com/nidharap/Notebooks/blob/master/Word_Embeddings_BERT.ipynb

    :param data: List of the text to preprocess.
    :param tokeniser_obj: BertTokenizer object to tokenise data by.
    :param max_length: Integer of the maximum length to pad and truncate sentences to.
    :return: Tensor of token ids to be fed into BERT model.
    :return: Tensor of the indices specifying which tokens should be attended to by the BERT model.
    :return: Tensor of indicies specifing which tokens should be attended to by the BERT model,
             excluding special tokens (CLS.SEP).
    """

    # create empty list to store outputs
    input_ids = []
    attention_masks = []

    for sentence in tqdm(data):
        # for every sentences, `encode_plus` will:
        #   1. tokenise the sentence
        #   2. add the `[CLS]` and `[SEP]` tokens to the start and end
        #   3. truncate or pad the sentence to the maximum length specified by padding.
        #      Default is maximum length of a sequence.
        #   4. map tokens to their IDs
        #   5. create attention mask
        #   6. return a dictionary of outputs
        encoded_sentence = tokeniser_obj.encode_plus(text=sentence,
                                                     add_special_tokens=True,
                                                     max_length=max_length,
                                                     padding='max_length',
                                                     truncation=True,
                                                     return_attention_mask=True)
        # add outputs to list
        input_ids.append(encoded_sentence.get('input_ids'))
        attention_masks.append(encoded_sentence.get('attention_mask'))

    # convert lists to tensors
    input_ids = torch.tensor(data=input_ids)
    attention_masks = torch.tensor(data=attention_masks)

    # create another mask for averaging all word vectors,
    # where average all word vectors in a sentence, but excluding CLS and SEP tokens
    attention_masks_without_special_tokens = attention_masks.clone().detach()

    # set CLS token index to 0 for all sentences
    attention_masks_without_special_tokens[:, 0] = 0

    # get sentence lengths and use to set those indices to 0 for each length,
    # which is the last index for each sentence, the SEP token
    sentence_len = attention_masks_without_special_tokens.sum(1).tolist()

    # column indices set to zero
    col_idx = torch.LongTensor(sentence_len)
    # row indices for all rows
    row_idx = torch.arange(attention_masks.size(0)).long()

    # set the SEP indices for each sentence token to zero
    attention_masks_without_special_tokens[row_idx, col_idx] = 0

    return input_ids, attention_masks, attention_masks_without_special_tokens


def get_vector(hidden_layers_form_arch: tuple,
               token_index: int = 0,
               mode: str = 'average',
               top_n_layers: int = 4) -> torch.Size:
    """
    Retrieve vectors for a token_index from the top_n_layers and concatenate, average or sum.
    References:
        - https://towardsdatascience.com/beyond-classification-with-transformers-and-hugging-face-d38c75f574fb

    :param hidden_layers_form_arch: Tuple returned by the transformer library.
    :param token_index: Int of the token index for which a vector is desired.
    :param mode: String of the method we want to aggregate the top_n_layers by. Default is 4,
                 meaning take last 4 layer outputs as they typically have richer representation of words.
    :param top_n_layers: Int of the top layers to aggregate by.
    :return: Size of the batch_size, seq_len and dimensions.
    """

    layers = hidden_layers_form_arch[-top_n_layers:]

    # permute(1, 0, 2) swaps the batch and seq_len dim,
    # so it's easy to return all vectors for a particular token position
    if mode == 'concat':
        return torch.cat(layers, dim=2).permute(1, 0, 2)[token_index]
    if mode == 'average':
        return torch.stack(layers).mean(0).permute(1, 0, 2)[token_index]
    if mode == 'sum':
        return torch.stack(layers).sum(0).permute(1, 0, 2)[token_index]
    if mode == 'last':
        return hidden_layers_form_arch[-1:][0].permute(1, 0, 2)[token_index]
    if mode == 'second_last':
        return hidden_layers_form_arch[-2:-1][0].permute(1, 0, 2)[token_index]

    return None


def evaluate_vectors(input_hidden_states: tuple,
                     input_tokenised_sentences: list,
                     attention_mask: torch.tensor,
                     max_length: int,
                     mode: str = 'concat',
                     top_n_layers: int = 4) -> (np.ndarray, list):
    """
    Get vectors for each word in each sentence and add the sentence number to the end of each word.
    References:
        - https://towardsdatascience.com/beyond-classification-with-transformers-and-hugging-face-d38c75f574fb

    :param input_hidden_states: Tuple of hidden states of BERT model.
    :param input_tokenised_sentences: List of the tokenised sentences get word embeddings from.
    :param attention_mask: Tensor of the attention masks in BERT model for getting sentence length.
    :param max_length: Integer of the maximum length to pad and truncate sentences to.
    :param mode: String of the method we want to aggregate the top_n_layers by. Default is 4,
                 meaning take last 4 layer outputs as they typically have richer representation of words.
    :param top_n_layers: Int of the top layers to aggregate by.
    :return: Array of word embeddings and labels.
    """

    vecs = list()
    labels = list()
    sent_lengths = attention_mask.sum(1).tolist()

    for token_ind in range(max_length):
        if token_ind == 0:
            # ignore CLS
            continue
        vectors = get_vector(hidden_layers_form_arch=input_hidden_states,
                             token_index=token_ind,
                             mode=mode,
                             top_n_layers=top_n_layers)
        for sent_ind, sent_len in enumerate(sent_lengths):
            if token_ind < sent_len - 1:
                # ignore SEP which will be at the last index of each sentence
                vecs.append(vectors[sent_ind])
                labels.append(input_tokenised_sentences[sent_ind][token_ind] + '_' + str(sent_ind))

    # create numpy matrix of word embeddings
    mat = torch.stack(vecs).detach().numpy()

    return mat, labels


def get_similar_words(df: pd.DataFrame,
                      col_word: str,
                      similarity_score: float) -> pd.DataFrame:
    """
    Gets words and their synonyms, as defined by having a cosine-similarity score above a threshold.

    :param df: Dataframe of words and their embeddings.
    :param col_word: String of the column in df that has the word we want synonyms for.
    :param similarity_score: Float of the threshold cosine-similarity score that a word has to be above to be a synonym.
    :return: Dataframe of each word, their synonyms and the cosine-similarity score.
    """
    try:
        # separate word_embeddings and words from df
        word_embeddings = df.drop(columns=col_word)
        word_embeddings = word_embeddings.to_numpy()
        word = df[col_word].tolist()

        # create df of words and their cosine-similarity with other words
        cosine_similarities = cosine_similarity(X=word_embeddings)
        cosine_similarities = pd.DataFrame(data=cosine_similarities,
                                           columns=word)
        cosine_similarities['word'] = word

        # filter for only synonyms with cosine-similarity above threshold
        cosine_similarities = pd.melt(frame=cosine_similarities,
                                      id_vars='word',
                                      var_name='synonym',
                                      value_name='cosine_similarity_score')
        df_synonyms = cosine_similarities[cosine_similarities['cosine_similarity_score'] > similarity_score]

        # remove words and synonyms that are themselves
        df_synonyms = df_synonyms[df_synonyms['word'] != df_synonyms['synonym']]

        return df_synonyms

    except Exception:
        raise


def clean_similar_words(df: pd.DataFrame,
                        col_word_synonyms_score: list) -> pd.DataFrame:
    """
    Cleans a dataframe of words, synonyms and their similarity score through:
        - Removing underscores
        - Removing words that are BERT tokens
        - Removing words that are numbers or have numbers in them
        - Removing words that are the same after removing underscores
        - Dropping duplicates of words and their synonyms, keeping the highest cosine-similarity record


    :param df: Dataframe of words, their synonyms and cosine-similarity score.
    :param col_word_synonyms_score: List of three-elements of the column names in order of words, synonyms and score.
    :return Dataframe cleaned of words, synonyms and similarity scores.
    """
    try:
        col_length = len(col_word_synonyms_score)

        if col_length != 3:
            raise Exception(f"Passed in {col_length} columns for col_word_synonyms_score. It should have 3.")
        else:
            for col in col_word_synonyms_score[:2]:
                # remove underscore and numbers after underscore
                df[col] = df[col].str.replace(pat=r'_\d+', repl='')
                # remove word with BERT tokens and numbers
                df = df[~df[col].str.contains("#")]
                df = df[~df[col].str.contains("[0-9]")]

            # remove duplicates
            df = df[df[col_word_synonyms_score[0]] != df[col_word_synonyms_score[1]]]
            df = df.sort_values(by=col_word_synonyms_score,
                                ascending=[True, True, False])
            df = df.drop_duplicates(subset=[col_word_synonyms_score[0], col_word_synonyms_score[1]],
                                    keep='first')

            return df

    except Exception:
        raise
