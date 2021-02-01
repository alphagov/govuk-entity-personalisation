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


class EntityCombinationProcessor(TitleProcessor):
    # The basic idea is that there are plenty of content items whose title
    # is something like "Tourette's syndrome and driving" where the "and" combination
    # is important - as it indicates that it's specifically related to Tourette's
    # syndrome and it's relation to driving
    #
    # Known texts that perform well
    # Optic neuritis and driving
    # Tourette's syndrome and driving
    #
    # Texts that don't work/need further work
    # Kindertransport and the State Pension
    # Stroke (cerebrovascular accident) and driving
    def process(self, doc, debug = False):
        if debug:
            [self._to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]
        last_cc_token = None
        objects = []
        join = None
        for token in doc:
            if debug:
                self._debug_token(token)
            if token.dep_ == "cc":
                last_cc_token = token
            if token.dep_ == "conj" and last_cc_token:
                head_token = self._compound_left_compounds(token.head) + [token.head]
                print(f"after adding left compounds, token is now: {head_token}")
                objects.append(head_token)
                objects.append(token)
                join = last_cc_token
        if any(objects):
            return [objects, join]
        else:
            return []

    def _compound_left_compounds(self, token):
        compounded_lefts = []
        reversed_lefts = list(token.lefts) or []
        reversed_lefts.reverse()
        print(f"compounded lefts for token: {token.text} are {reversed_lefts}")
        if reversed_lefts:
            for left in reversed_lefts:
                print(f"left text: {left.text}")
                print(f"left dep: {left.dep_}")
                if left.dep_ == "amod":
                    compounded_lefts.append(left)
                    compounded_lefts += self._compound_left_compounds(left)
                else:
                    break
        return compounded_lefts


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
        is_open_clausal_complement = self._is_open_clausal_complement(token)
        if is_open_clausal_complement:
            return is_open_clausal_complement
        is_object_of_prepositional_phrase = self._is_object_of_prepositional_phrase(token)
        if is_object_of_prepositional_phrase:
            if debug:
                print("is_object_of_prepositional_phrase")
            return is_object_of_prepositional_phrase
        is_object = self._is_object(token)
        if is_object:
            if debug:
                print("is_object")
            return is_object


    def _verbs(self):
        return ["VERB", "AUX"]

    def _is_object_of_prepositional_phrase(self, token):
        # Finds objects of prepositional phrases
        # eg "Apply online for a UK passport", "Apply for this licence"
        if (token.dep_ == "pobj" and token.head.dep_ == "prep") or \
                (token.dep_=="dobj" and token.head.dep_ == "xcomp") and token.head.pos_ in self._verbs():
            print("is object of prepositional phrase")
            triple = SVO()
            verb = token.head.head
            if token.head.pos_ in self._verbs():
                verb = token.head
            for existing_triple in self.triples:
                if existing_triple.verb[0] == verb:
                    print(f"verb: {existing_triple.verb} is already taken!")
                    return None
            triple.verb = self._verb(verb)
            triple.object = [token]
            triple.subject = []
            reversed_lefts = list(token.lefts) or []
            reversed_lefts.reverse()
            print(f"reversed lefts are: {reversed_lefts}")
            if reversed_lefts:
                for left in reversed_lefts:
                    print(f"left text: {left.text}")
                    print(f"left dep: {left.dep_}")
                    if left.dep_ == "poss":
                        triple.subject.append(left)
                        print(f"After appending lefts, subject is now: {triple.subject}")
            compound_lefts = self._compound_left_compounds(token)
            if any(compound_lefts):
                compound_lefts.reverse()
                print(compound_lefts)
                triple.object = compound_lefts + triple.object
            return [triple]

    def _verb(self, verb_token):
        verbs = [verb_token]
        for right_token in verb_token.rights:
            if right_token.dep_ == "prt":
                verbs.append(right_token)
        return verbs

    def _is_open_clausal_complement(self, token):
        if token.dep_ == "xcomp" and token.head.pos_ in self._verbs():
            print("_is_open_clausal_complement")
            triple = SVO()
            triple.verb = self._verb(token.head)
            triple.object = [token]
            triple.subject = []
            return [triple]

    def _is_object(self, token):
        # Finds simple objects
        # eg "Get a passport for your child"
        # TODO: should probably extract "for your child" bit as a modifier of some kind
        if token.dep_ == "dobj" and token.head.pos_ in self._verbs():
            triple = SVO()
            triple.verb = self._verb(token.head.head)
            triple.object = [token]
            compound_lefts = self._compound_left_compounds(token)
            if any(compound_lefts):
                compound_lefts.reverse()
                print(f"reversed compound lefts are: {compound_lefts}")
                triple.object = compound_lefts + triple.object
                print(f"object is now: {triple.object}")
            return [triple]

    def _compound_left_compounds(self, token):
        print(f"compounded lefts for token: {token.text}")
        compounded_lefts = []
        reversed_lefts = list(token.lefts) or []
        reversed_lefts.reverse()
        print(reversed_lefts)
        if reversed_lefts:
            for left in reversed_lefts:
                print(f"left text: {left.text}")
                print(f"left dep: {left.dep_}")
                if left.dep_ in ["compound", "amod"]:
                    compounded_lefts.append(left)
                    compounded_lefts += self._compound_left_compounds(left)
                else:
                    break
        return compounded_lefts
