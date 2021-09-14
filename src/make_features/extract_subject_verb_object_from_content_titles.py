import os
import pandas as pd
from src.make_features.subject_verb_object.content import Page
from src.make_features.subject_verb_object.utils import spacy_model
import json
import multiprocessing
import itertools


def get_verbs_objects(processed_pages):
    found_objects = {}
    found_verbs = {}
    found_entities = {}
    num_pages = len(processed_pages)
    for index, page in enumerate(processed_pages):
        print(f"{index} of {num_pages}")
        if any(page.title.subject_object_triples()):
            for triple in page.title.subject_object_triples():
                triple_object = triple.cypher_object()
                triple_verb = triple.cypher_verb()
                if triple_object not in found_objects:
                    found_objects[triple_object] = []
                found_objects[triple_object].append([triple_verb, page.base_path(), page.title.title])
                if triple_verb not in found_verbs:
                    found_verbs[triple_verb] = []
                found_verbs[triple_verb].append([triple_object, page.base_path(), page.title.title])
        elif any(page.title.entities()):
            for entity in page.title.entities():
                cypher_entity = entity.cypher_entity()
                if cypher_entity not in found_entities:
                    found_entities[cypher_entity] = []
                found_entities[cypher_entity].append([cypher_entity, page.base_path(), page.title.title])
    print("Found all SVOs and entities, making them unique")
    unique_verbs = find_unique_entries(found_verbs)
    unique_objects = find_unique_entries(found_objects)
    unique_entities = find_unique_entries(found_entities)
    return unique_verbs, unique_objects, unique_entities


def find_unique_entries(verbs_or_objects):
    unique_entries = {}
    for key, value in verbs_or_objects.items():
        unique_values = []
        for item in value:
            found = False
            for unique_item in unique_values:
                if unique_item[0] == item[0]:
                    found = True
            if not found:
                unique_values.append(item)
        unique_entries[key] = unique_values
    return unique_entries


def build_page(content_item, nlp_instance):
    return Page(content_item[1], nlp_instance)


if __name__ == "__main__":
    DIR_RAW = os.getenv('DIR_DATA_RAW', 'data/raw')
    DIR_PROCESSED = os.getenv('DIR_DATA_PROCESSED', 'data/processed')
    all_content_items = pd.read_csv(DIR_RAW + "/preprocessed_content_store.csv.gz", sep="\t", compression="gzip")
    print("Finished reading from the preprocessed content store!")
    nlp = spacy_model()
    all_pages = []
    chunk_size = 50000
    num_work = int(multiprocessing.cpu_count())
    # Running this in one go uses tens of Gb of memory, splitting it up makes this less of a problem
    for i in range(0, all_content_items.shape[0], chunk_size):
        dataframe_chunk = all_content_items[i:i + chunk_size]
        num_docs = len(dataframe_chunk)
        chunksize, remainder = divmod(num_docs, num_work)
        if remainder:
            chunksize += 1
        pool = multiprocessing.Pool(processes=num_work)
        pages = pool.starmap(build_page, zip((content_item for content_item in
                                             dataframe_chunk.iterrows()),
                                             itertools.repeat(nlp)), chunksize=chunksize)
        pool.close()
        pool.join()
        all_pages += list(pages)
    print("Loaded pages, starting getting verbs/objects")
    verbs, objects, entities = get_verbs_objects(all_pages)
    print("Saving to file")
    with open(DIR_PROCESSED + '/objects.json', 'w') as json_file:
        json.dump(objects, json_file)
    with open(DIR_PROCESSED + '/verbs.json', 'w') as json_file:
        json.dump(verbs, json_file)
    with open(DIR_PROCESSED + '/entities.json', 'w') as json_file:
        json.dump(entities, json_file)
    print("Done!")
