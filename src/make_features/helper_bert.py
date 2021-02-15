from tqdm import tqdm
import torch
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

    :param hidden_layers_form_arch: Tuple returned by the transformer library.
    :param token_index: Int of the token index for which a vector is desired.
    :param mode: String of the method we want to aggregate the top_n_layers by. Default is 4,
                 meaning take last 4 layer outputs as they typically have richer representation of words
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


def evaluate_vectors(input_hidden_states,
                     input_tokenised_sentences: list,
                     attention_mask,
                     max_len,
                     mode: str = 'concat',
                     top_n_layers: int = 4):
    """
    Get vectors for each word in each sentence and add the sentence number to the end of each word.
    Calculates the cosine distance between each pair of words.
    """

    vecs = list()
    labels = list()
    sent_lengths = attention_mask.sum(1).tolist()

    for token_ind in range(max_len):
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

    # create numpy matrix to compute cosine distance
    mat = torch.stack(vecs).detach().numpy()

    return mat, labels