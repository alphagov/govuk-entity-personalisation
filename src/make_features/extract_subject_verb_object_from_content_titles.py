import pandas as pd
from src.make_features.subject_verb_object.content import Page
import spacy
import json

def get_verbs_objects(pages, nlp):
    objects = {}
    verbs = {}
    for page in pages:
        for title in page.titles(nlp):
            for triple in title.subject_object_triples():
                triple_object = triple.cypher_object()
                triple_verb = triple.cypher_verb()
                if triple_object not in objects:
                    objects[triple_object] = []
                objects[triple_object].append([triple_verb, page.base_path(), title.title])
                if triple_verb not in verbs:
                    verbs[triple_verb] = []
                verbs[triple_verb].append([triple_object, page.base_path(), title.title])
    verbs = find_unique_entries(verbs)
    objects = find_unique_entries(objects)
    return verbs, objects

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

if __name__ == "__main__":
    all_content_items = pd.read_csv("data/processed/preprocessed_content_store_010221.csv", sep="\t", compression="gzip",
                                    low_memory=False)
    # all_content_items = pd.read_csv("data/processed/mini_content.csv")
    print("Finished reading from the preprocessed content store!")
    nlp = spacy.load("en_core_web_sm")
    pages = []
    for index, content_item in all_content_items.iterrows():
        pages.append(Page(content_item, nlp))
    verbs, objects = get_verbs_objects(pages, nlp)
    with open('outputs/objects.json', 'w') as json_file:
        json.dump(objects, json_file)
    with open('outputs/verbs.json', 'w') as json_file:
        json.dump(verbs, json_file)
