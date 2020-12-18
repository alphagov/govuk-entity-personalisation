# create USE embeddings for content from content store

'''
demo of the Universal Sentence Encoder (USE) on some gov docs
to run this, you must first download:
- preprocessed_content_store_210920.csv from Google Drive
- USE models, which come in two flavours, if you do not have a graphics card, go for DAN
https://www.tensorflow.org/hub/tutorials/semantic_similarity_with_tf_hub_universal_encoder
https://tfhub.dev/google/universal-sentence-encoder-large/5

'''
import tensorflow_hub as hub
import tensorflow as tf
import numpy as np
import pandas as pd
from ast import literal_eval
import os
import pickle


def isNaN(string):
    return string != string


# tests presence of GPUs, to run the Transformer, GPU is necessary
# otherwise looking at a run time of order of days for scoring the whole corpus
os.chdir('/home/james/Documents/gds_nlp/govuk-entity-personalisation')
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

# DAN model, lighter A stands for averaging
# model = hub.load('/home/james/Downloads/universal-sentence-encoder_4')
# Transformer model, more performant, runs on GPU, if available
model = hub.load('/home/james/Downloads/universal-sentence-encoder-large_5')

pickle_file = open(os.path.join('data', 'relationship_weights.bin'), 'rb')
relationship_weights = pickle.load(pickle_file)

# find out whether the weights are directional
relationship_weights[1]
relationship_weights_dict = {}
cid_count = {}
for i, r in enumerate(relationship_weights):
    relationship_weights_dict[(r['m.contentID'], r['n.contentID'])] = r['r.weight']
    cid_count[r['m.contentID']] = cid_count.get(r['m.contentID'], 0) + 1
    cid_count[r['n.contentID']] = cid_count.get(r['n.contentID'], 0) + 1

# only 22.3k cids with a relationship to other cids
len(cid_count)

# looking at the counts for various pairs its clear that the counts are directional
count_1 = relationship_weights_dict[('0008c1e3-c14d-4307-9122-315c50339e49', '96709198-7d36-4cb4-88bc-006890f2c173')]
count_2 = relationship_weights_dict[('96709198-7d36-4cb4-88bc-006890f2c173', '0008c1e3-c14d-4307-9122-315c50339e49')]
assert count_1 == count_2, "not the same count"


def embed(input):
    return model(input)


# import data from the content store, an improvement here would be to download the same from neo4j
content_store_df = pd.read_csv("/home/james/Downloads/preprocessed_content_store_210920.csv",
                               compression='gzip', delimiter="\t", low_memory=False)
cid_df = pd.DataFrame({'content_id': list(cid_count.keys()), 'relationship_flag': 1})
cols_keep = ['document_type', 'content_id', 'first_published_at', 'details', 'description']
subset_content_df = content_store_df.merge(cid_df, on='content_id', how='inner')[cols_keep].copy()
subset_content_df['details'] = subset_content_df['details'].map(literal_eval)


def clean_xml(original_text):
    ''' strips out xml tagging from string'''
    extracted_sentence = []
    start_idx = 1
    end_idx = 1
    while (start_idx > 0) and (end_idx > 0):
        end_idx = original_text.find('<')
        if end_idx >= 0:
            extracted_sentence.append(original_text[:end_idx])
            start_idx = original_text.find('>')
            if (start_idx >= 0):
                original_text = original_text[start_idx + 1:]
    if len(original_text) > 0:
        extracted_sentence.append(original_text)
    return str(''.join(extracted_sentence))


def extract_paragraphs(original_text):
    ''' takes raw string text from gov uk and returns extracted paragraphs
    still contains xml tags'''
    extracted_paragraphs = []
    start_idx = 1
    end_idx = 1
    while (start_idx >= 0) and (end_idx >= 0):
        start_idx = original_text.find('<p>')
        end_idx = original_text.find('</p>')
        if (start_idx >= 0) and (end_idx >= 0):
            if (end_idx - start_idx) > 3:
                cleaned_text_segment = clean_xml(original_text[start_idx + 3:end_idx])
                extracted_paragraphs.append(cleaned_text_segment)
            original_text = original_text[end_idx + 3:]
    return extracted_paragraphs


def document_embedding(paragraphs):
    '''
    average embeddings across sentences
    '''
    embedding = embed(paragraphs)
    average_embedding = tf.math.reduce_mean(embedding, axis=0).numpy()
    return average_embedding


# initialise an empty array for embeddings
collected_doc_embeddings = np.zeros((subset_content_df.shape[0], 512))

# fill array with embeddings for all docs
# problem with out of memory warnings on 8gb card: reduce extracted paragraphs to 128
# flake8 complaining with the complexity of code beneath which generates embeddings using the description
'''
for i in range(subset_content_df.shape[0]):
    try:
        doc = subset_content_df.iloc[i]['details']['body']
        if type(doc) == list:
            doc = doc[0]['content']
    except KeyError:
        try:
            doc = subset_content_df.iloc[i]['description']
            if isNaN(doc):
                continue
        except KeyError:
            continue
    extracted_paragraphs = extract_paragraphs(doc)
    if len(extracted_paragraphs) > 128:
        extracted_paragraphs = extracted_paragraphs[:128]
    if len(extracted_paragraphs) > 0:
        doc_embedding = document_embedding(extracted_paragraphs)
        collected_doc_embeddings[i, :] = doc_embedding
    if i % 1000 == 0:
        progress = i / subset_content_df.shape[0]
        print('%s' % float('%.2g' % progress))

# converts embeddings array into dataframe, with content id as unique key
embeddings_df = pd.DataFrame(collected_doc_embeddings)
embeddings_df['content_id'] = subset_content_df['content_id'].to_list()

# initialise list for storing raw text
collected_doc_text = []

# store the original raw text extracted from the documents
for i in range(subset_content_df.shape[0]):
    try:
        doc = subset_content_df.iloc[i]['details']['body']
        if type(doc) == list:
            doc = doc[0]['content']
    except KeyError:
        try:
            doc = subset_content_df.iloc[i]['description']
            if isNaN(doc):
                collected_doc_text.append('')
                continue
        except KeyError:
            collected_doc_text.append('')
            continue
    extracted_paragraphs = extract_paragraphs(doc)
    if len(extracted_paragraphs) > 0:
        collected_doc_text.append(' '.join(extracted_paragraphs))
    else:
        collected_doc_text.append('')
    if i % 1000 == 0:
        progress = i / subset_content_df.shape[0]
        print('%s' % float('%.2g' % progress))'''

# fill array with embeddings for all docs
for i in range(subset_content_df.shape[0]):
    try:
        doc = subset_content_df.iloc[i]['details']['body']
    except KeyError:
        continue
    extracted_paragraphs = extract_paragraphs(doc)
    if len(extracted_paragraphs) > 0:
        doc_embedding = document_embedding(extracted_paragraphs)
        collected_doc_embeddings[i, :] = doc_embedding
    if i % 1000 == 0:
        progress = i / subset_content_df.shape[0]
        print('%s' % float('%.2g' % progress))

# converts embeddings array into dataframe, with content id as unique key
embeddings_df = pd.DataFrame(collected_doc_embeddings)
embeddings_df['content_id'] = subset_content_df['content_id'].to_list()

# initialise list for storing raw text
collected_doc_text = []

# store the original raw text extracted from the documents
for i in range(subset_content_df.shape[0]):
    try:
        doc = subset_content_df.iloc[i]['details']['body']
    except KeyError:
        collected_doc_text.append('')
        continue
    extracted_paragraphs = extract_paragraphs(doc)
    if len(extracted_paragraphs) > 0:
        collected_doc_text.append(' '.join(extracted_paragraphs))
    else:
        collected_doc_text.append('')
    if i % 1000 == 0:
        progress = i / subset_content_df.shape[0]
        print('%s' % float('%.2g' % progress))

# converts the raw text into a dataframe
text_df = pd.DataFrame({'content_id': subset_content_df['content_id'].to_list(),
                        'doc_text': collected_doc_text,
                        'document_type': subset_content_df['document_type'].to_list(),
                        'first_published_at': subset_content_df['first_published_at'].to_list()})


# output dataframes
os.chdir('/home/james/Documents/gds_nlp/govuk-entity-personalisation/data')
text_df.to_csv('text_use_large_2000_df.csv', index=False, header=True, mode='w')
embeddings_df.to_csv('embeddings_use_large_2000_df.csv', index=False, header=True, mode='w')
embeddings_df.shape
