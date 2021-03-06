from src.make_features.subject_verb_object.subject_verb_object import SVOProcessor, EntityProcessor
from nltk import Tree


class Title:
    def __init__(self, title, nlp):
        self.title = title
        self.doc = nlp(title)
        self.triples = []
        self.computed_triples = False
        self.computed_entities = []
        self.has_computed_entities = False

    def subject_object_triples(self, debug=False):
        if self.computed_triples:
            return self.triples
        self.triples = SVOProcessor().process(self.doc, debug)
        self.computed_triples = True
        return self.triples

    def entities(self, debug=False):
        if self.has_computed_entities:
            return self.computed_entities
        self.computed_entities = EntityProcessor().process(self.doc, debug)
        self.has_computed_entities = True
        return self.computed_entities


class Page:
    def __init__(self, content_item, nlp):
        self.content_item = content_item
        self.title = Title(content_item['title'], nlp)

    def base_path(self):
        return self.content_item['base_path']
