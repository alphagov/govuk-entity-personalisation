from src.make_features.subject_verb_object.subject_verb_object import SVOProcessor, EntityCombinationProcessor
from nltk import Tree

class TitleProcessor:
    def _to_nltk_tree(self, node):
        if node.n_lefts + node.n_rights > 0:
            return Tree(node.orth_, [self._to_nltk_tree(child) for child in node.children])
        else:
            return node.orth_

    def _debug_token(self, token):
        print(f"text: {token.text}")
        print(f"dep: {token.dep_}")
        print(f"head dep: {token.head.dep_}")
        print(f"head head pos: {token.head.head.pos_}")
        print(f"lefts: {list(token.lefts)}")
        print(f"rights: {list(token.rights)}")
        print()


class Title:
    def __init__(self, title, nlp):
        self.title = title
        self.doc = nlp(title)
        self.triples = []
        self.computed_triples = False
        self.combinations = []
        self.computed_combinations = False

    def subject_object_triples(self, debug=False):
        if self.computed_triples:
            return self.triples
        print(f"debug at title: {debug}")
        self.triples = SVOProcessor().process(self.doc, debug)
        self.computed_triples = True
        return self.triples

    def entity_combinations(self):
        if self.computed_combinations:
            return self.combinations
        self.combinations = EntityCombinationProcessor().process(self.doc)
        self.computed_combinations = True
        return self.combinations

class Page:
    def __init__(self, content_item, nlp):
        self.content_item = content_item
        self.extracted_titles = []

    def base_path(self):
        return self.content_item['base_path']

    def titles(self, nlp):
        if any(self.extracted_titles):
            return self.extracted_titles
        self.extracted_titles = [Title(self.content_item['title'], nlp)]
        return self.extracted_titles
