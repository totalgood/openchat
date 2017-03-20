from __future__ import print_function, unicode_literals, division
"""
>>> twt = "I'd like to set up an #openspace 'Yoga 101' at 6 pm tomorrow in Room B-10."
...
>>> txt = 'Hello world, what do you think of this\nsentence on two (2) lines?'
>>> txt += " And here's\n1.0 more with a \"Quoted phrase.\" somone else said."
>>> txt += " But\ncouldn't there b 2. more with a \"A Life of Their Own?\" somone else wrote."
>>> tokens = nlp(txt, parse=True)
>>> [str(s) for s in tokens.sents]
>>> txt += " And someone\nin the U.S. of A. might not like all this fool'n\naround."
>>> print(txt)
Hello world, what do you think of this
sentence on two (2) lines? And here's
1.0 more with a "Quoted phrase." somone else said. But
couldn't there b 2. more with a "A Life of Their Own?" somone else wrote. And someone
in the U.S. of A. might not like all this fool'n
around.

>>> nlp = English()
>>> tokens = nlp(txt, parse=True)
>>> [str(s) for s in tokens.sents]
['Hello world, what do you think of this\nsentence on two (2) lines?',
 'And here\'s\n1.0 more with a "Quoted phrase.',
 '" somone else said.',
 "But\ncouldn't there b 2.",
 'more with a "A Life of Their Own?" somone else wrote.',
 "And someone\nin the U.S. of A. might not like all this fool'n\naround."]
"""

# from spacy.parts_of_speech import NOUN
# from spacy.parts_of_speech import ADP as PREP

from ast import literal_eval
import codecs

import spacy
from spacy.en import English
from spacy.strings import hash_string
from spacy.matcher import PhraseMatcher
# from preshed.maps import PreshMap  # faster hash table (dict)--assumes keys are prehashed
from preshed.counter import PreshCounter  # faster collections.Counter--assumes keys are prehashed

spacy.load('en')


def _span_to_tuple(span):
    start = span[0].idx
    end = span[-1].idx + len(span[-1])
    tag = span.root.tag_
    text = span.text
    label = span.label_
    return (start, end, tag, text, label)


def merge_spans(spans, doc):
    # This is a bit awkward atm. What we're doing here is merging the entities,
    # so that each only takes up a single token. But an entity is a Span, and
    # each Span is a view into the doc. When we merge a span, we invalidate
    # the other spans. This will get fixed --- but for now the solution
    # is to gather the information first, before merging.
    tuples = [_span_to_tuple(span) for span in spans]
    for span_tuple in tuples:
        doc.merge(*span_tuple)


def extract_currency_relations(doc):
    merge_spans(doc.ents, doc)
    merge_spans(doc.noun_chunks, doc)

    relations = []
    for money in filter(lambda w: w.ent_type_ == 'MONEY', doc):
        if money.dep_ in ('attr', 'dobj'):
            subject = [w for w in money.head.lefts if w.dep_ == 'nsubj']
            if subject:
                subject = subject[0]
                relations.append((subject, money))
        elif money.dep_ == 'pobj' and money.head.dep_ == 'prep':
            relations.append((money.head.head, money))

    return relations


def read_gazetteer(tokenizer, loc, n=-1):
    for i, line in enumerate(open(loc)):
        phrase = literal_eval('u' + line.strip())
        if ' (' in phrase and phrase.endswith(')'):
            phrase = phrase.split(' (', 1)[0]
        if i >= n:
            break
        phrase = tokenizer(phrase)
        if all((t.is_lower and t.prob >= -10) for t in phrase):
            continue
        if len(phrase) >= 2:
            yield phrase


# def read_text_lines(bz2_loc):
#     with BZ2File(bz2_loc) as file_:
#         for line in file_:
#             yield line.decode('utf8')


# def get_matches(tokenizer, phrases, texts, max_length=6):
#     matcher = PhraseMatcher(tokenizer.vocab, phrases, max_length=max_length)
#     print("Match")
#     for text in texts:
#         doc = tokenizer(text)
#         matches = matcher(doc)
#         for mwe in doc.ents:
#             yield mwe


class FullNameExtractor(object):
    """WIP, untested"""

    def __init__(self, tokenizer=None, phrases=None, max_len=6, max_phrases=1000000):
        self.max_phrases = max_phrases or 1000000
        self.max_len = max_len or 6
        self.nlp = English()
        if isinstance(phrases, basestring):
            self.phrases = read_gazetteer(self.nlp.tokenizer, phrases, n=self.max_phrases)
        else:
            self.phrases = phrases
        self.matcher = PhraseMatcher(self.nlp.tokenizer.vocab, self.phrases, max_length=self.max_len)

    def extract(self, text):
        tokens = self.nlp.tokenizer(text)
        # this may operate on the tokens in-place
        matches = self.matcher(tokens)
        for mwe in tokens.ents:
            yield mwe


def make_matcher(patterns_path, text_path, counts_loc, n=10000000):
    nlp = English(parser=False, tagger=False, entity=False)
    print("Make matcher")
    phrases = read_gazetteer(nlp.tokenizer, patterns_path, n=n)
    counts = PreshCounter()
    for mwe in get_matches(nlp.tokenizer, phrases, open(text_path)):
        counts.inc(hash_string(mwe.text), 1)

    with codecs.open(counts_loc, 'w', 'utf8') as file_:
        for phrase in read_gazetteer(nlp.tokenizer, patterns_path, n=n):
            text = phrase.string
            key = hash_string(text)
            count = counts[key]
            if count != 0:
                file_.write('%d\t%s\n' % (count, text))


def test_extract_money():
    nlp = English()
    texts = [
        u'Net income was $9.4 million compared to the prior year of $2.7 million.',
        u'Revenue exceeded twelve billion dollars, with a loss of $1b.',
    ]

    for text in texts:
        doc = nlp(text)
        relations = extract_currency_relations(doc)
        for r1, r2 in relations:
            print(r1.text, r2.ent_type_, r2.text)
