from nltk import Tree

class SVO:
    def __init__(self):
        self.subject = None
        self.object = None
        self.verb = None

    def cypher_subject(self):
        return self._cypher_safe(self.subject)

    def cypher_object(self):
        return self._cypher_safe(self.object)

    def cypher_verb(self):
        return self._cypher_safe(self.verb)

    def _cypher_safe(self, token):
        if token is None:
            return ""
        if type(token) is list:
            text = ''.join([t.text_with_ws for t in token])
        else:
            text = token.text
        text = text.lower()
        text = text.strip()
        return text.replace("'", "")


# Superclass that is inherited by other classes that process titles in specific ways
# Currently, this is EntityCombinationProcessor and SVOProcessor
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
        print(f"head pos: {token.head.pos_}")
        print(f"head head pos: {token.head.head.pos_}")
        print(f"lefts: {list(token.lefts)}")
        print(f"rights: {list(token.rights)}")
        print()

# Extracts Subject Verb Object (SVO) triples from content titles
class SVOProcessor(TitleProcessor):
    def process(self, doc, debug=False):
        if debug:
            [self._to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]
        self.triples = []
        for token in doc:
            # If statements can be highly misleading (as a source of Truth)
            if token.text == "if":
                return []
            if debug:
                self._debug_token(token)
            subject_object_triples = self._find_triples(token, debug)
            if subject_object_triples:
                self.triples += subject_object_triples
        return self.triples

    def _find_triples(self, token, debug=False):
        for phrase_instance in [OpenClausalComplementPhrase(token, self.triples, debug),
                                PrepositionalPhrase(token, self.triples, debug),
                                ObjectPhrase(token, self.triples, debug)]:
            if phrase_instance.result():
                return phrase_instance.result()

class Phrase():
    def __init__(self, token, existing_triples, debug=False):
        self.token = token
        self.debug = debug
        self.triple = None
        self.existing_triples = existing_triples
        self.called = False

    def _verb(self, verb_token):
        verbs = [verb_token]
        for right_token in verb_token.rights:
            if right_token.dep_ == "prt":
                verbs.append(right_token)
        return verbs

    def _verb_types(self):
        return ["VERB", "AUX"]

    def _compound_left_compounds(self, compound_token, token_to_compound_to=None):
        compounded_lefts = []
        reversed_lefts = list(compound_token.lefts) or []
        reversed_lefts.reverse()
        if reversed_lefts:
            for left in reversed_lefts:
                if left.dep_ in ["compound", "amod"]:
                    compounded_lefts.append(left)
                    compounded_lefts += self._compound_left_compounds(left)
                else:
                    break
        if token_to_compound_to:
            compounded_lefts.reverse()
            return compounded_lefts + token_to_compound_to
        return compounded_lefts

    def _extract_subject(self):
        reversed_lefts = list(self.token.lefts) or []
        subject = []
        reversed_lefts.reverse()
        if reversed_lefts:
            for left in reversed_lefts:
                if left.dep_ == "poss":
                    subject.append(left)
        return subject

    def _return_cached_result(self):
        if self.called:
            return [self.triple]
        self.called = True

    def _print_identified_phrase_debug_info(self):
        if self.debug:
            print(f"is instance of {self.__class__.__name__}")

class OpenClausalComplementPhrase(Phrase):
    def result(self):
        self._return_cached_result()
        if self.token.dep_ == "xcomp" and self.token.head.pos_ in self._verb_types():
            self._print_identified_phrase_debug_info()
            self.triple = SVO()
            self.triple.verb = self._verb(self.token.head)
            self.triple.object = [self.token]
            self.triple.subject = []
            return [self.triple]

class ObjectPhrase(Phrase):
    def result(self):
        self._return_cached_result()
        # Finds simple objects
        # eg "Get a passport for your child"
        if self.token.dep_ == "dobj" and self.token.head.pos_ in self._verb_types():
            self.triple = SVO()
            self.triple.verb = self._verb(self.token.head.head)
            self.triple.object = [self.token]
            self.triple.object = self._compound_left_compounds(self.token, self.triple.object)
            return [self.triple]

class PrepositionalPhrase(Phrase):
    # Finds objects of prepositional phrases
    # eg "Apply online for a UK passport", "Apply for this licence"
    def result(self):
        self._return_cached_result()
        if (self.token.dep_ == "pobj" and self.token.head.dep_ == "prep") or \
                (self.token.dep_=="dobj" and self.token.head.dep_ == "xcomp") and self.token.head.pos_ in self._verb_types():
            # Needed for some complex phrases
            verb = self.token.head.head
            if self.token.head.pos_ in self._verb_types():
                verb = self.token.head
            # Needed for some complex phrases
            if self._if_verb_already_used(verb):
                return None
            self.triple = SVO()
            self.triple.verb = self._verb(verb)
            self.triple.object = [self.token]
            self.triple.subject = self._extract_subject()
            self.triple.object = self._compound_left_compounds(self.token, self.triple.object)
            return [self.triple]

    def _if_verb_already_used(self, verb):
        for existing_triple in self.existing_triples:
            if existing_triple.verb[0] == verb:
                return True


