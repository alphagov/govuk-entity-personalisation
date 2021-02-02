from src.make_features.subject_verb_object.subject_verb_object import SVOProcessor
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

    def subject_object_triples(self, debug=False):
        if self.computed_triples:
            return self.triples
        self.triples = SVOProcessor().process(self.doc, debug)
        self.computed_triples = True
        return self.triples


class Page:
    def __init__(self, content_item, nlp):
        self.content_item = content_item
        self.title = Title(content_item['title'], nlp)

    def base_path(self):
        return self.content_item['base_path']
