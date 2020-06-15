import logging
import pathlib
import re
from abc import ABC, abstractmethod
from collections import deque
from functools import partial
from typing import Any, Union, Tuple, Iterable, Generator, Dict, Set
from typing import List
import lazy_import
from tqdm import tqdm

from mowgli.grounding.Groundings import Grounding
from mowgli.utils.MapReduceJobManager import MapReduceJobManager

import spacy
import spacy.lang.en
from spacy.matcher import Matcher
import json
# spacy = lazy_import.lazy_module('spacy')
# lazy_import.lazy_module('spacy.lang.en.English')
# Matcher, = lazy_import.lazy_callable('spacy.matcher', 'Matcher')
# json = lazy_import.lazy_module('json')


logger = logging.getLogger(__name__)


class KagNetGrounding(Grounding):
    blacklist = {"-PRON-", "actually", "likely", "possibly", "want", "make", "my", "someone", "sometimes_people",
                 "sometimes", "would", "want_to", "one", "something", "sometimes", "everybody", "somebody", "could",
                 "could_be"}

    def __init__(self, vocab_path: pathlib.Path, patterns_path: pathlib.Path):

        self.vocabs: Set[str] = {}
        with open(str(vocab_path), "r", encoding="utf8") as f:
            self.vocabs: Set[str] = set(map(lambda l: l.strip().replace("_", " "), f.readlines()))

        self.nlp = None
        self.matcher = None
        self.pattern_path = patterns_path

    @staticmethod
    def _setup_pattern_matcher(patterns_path: pathlib.Path) \
            -> Tuple[spacy.lang.en.English, spacy.matcher.matcher.Matcher]:
        # load nlp modules
        nlp = spacy.load('en_core_web_sm', disable=['ner', 'parser', 'textcat'])
        nlp.add_pipe(nlp.create_pipe('sentencizer'))
        # load the matcher
        matcher = Matcher(nlp.vocab)
        with open(str(patterns_path), "r", encoding="utf8") as f:
            all_patterns = json.load(f)
        for concept, pattern in tqdm(all_patterns.items(), desc="Adding patterns to Matcher."):
            matcher.add(concept, None, pattern)

        return nlp, matcher

    def ground_sentence(self, sent: str) -> Dict[str, Union[str, List[str]]]:
        nlp, matcher = KagNetGrounding._setup_pattern_matcher(self.pattern_path)
        return self._ground_mentioned_concepts(s=sent, nlp=nlp, matcher=matcher)

    def ground_corpus_test(self, corpus: List[str]) -> List[Dict[str, Union[str, List[str]]]]:
        nlp, matcher = KagNetGrounding._setup_pattern_matcher(self.pattern_path)
        return [self._ground_mentioned_concepts(s=s, nlp=nlp, matcher=matcher) for s in corpus]

    def ground_corpus(self, corpus: List[str], n_jobs: int = 8) -> List[Dict[str, Union[str, List[str]]]]:
        def get_pre_func(path):
            nlp, matcher = KagNetGrounding._setup_pattern_matcher(path)
            return dict(nlp=nlp, matcher=matcher)
        
        jobs = list([{"s": s} for s in corpus])
        logger.info(f'# sentences: {len(jobs)}')
        res = MapReduceJobManager.map(
            func=self._ground_mentioned_concepts,
            kwargs_list=jobs,
            pre_func=partial(get_pre_func, self.pattern_path),
            n_worker=n_jobs
        )
        return res

    @staticmethod
    def _hard_ground(nlp, sent, cpnet_vocab) -> List[str]:
        sent = sent.lower()
        doc = nlp(sent)
        res = set()
        for t in doc:
            if t.lemma_ in cpnet_vocab:
                res.add(t.lemma_)
        sent = "_".join([t.text for t in doc])
        if sent in cpnet_vocab:
            res.add(sent)
        return list(res)

    @staticmethod
    def _lemmatize(nlp, concept):
        doc = nlp(concept.replace("_", " "))
        lcs = set()
        lcs.add("_".join([token.lemma_ for token in doc]))  # all lemma
        return lcs

    @staticmethod
    def _ground_mentioned_concepts(s: str, nlp, matcher) -> Dict[str, Union[str, List[str]]]:
        s = s.lower()
        doc = nlp(s)
        matches = matcher(doc)

        mentioned_concepts = set()
        span_to_concepts = {}

        for match_id, start, end in matches:
            span = doc[start:end].text  # the matched span

            original_concept = nlp.vocab.strings[match_id]

            if len(original_concept.split("_")) == 1:
                original_concept = list(KagNetGrounding._lemmatize(nlp, original_concept))[0]

            if span not in span_to_concepts:
                span_to_concepts[span] = set()

            span_to_concepts[span].add(original_concept)

        for span, concepts in span_to_concepts.items():
            concepts_sorted = list(concepts)
            concepts_sorted.sort(key=len)

            shortest = concepts_sorted[0:3]  #
            for c in shortest:
                if c in KagNetGrounding.blacklist:
                    continue
                lcs = KagNetGrounding._lemmatize(nlp, c)
                intersect = lcs.intersection(shortest)
                if len(intersect) > 0:
                    mentioned_concepts.add((span, list(intersect)[0]))
                else:
                    mentioned_concepts.add((span, c))

        return {"sent": s, "qc": list(mentioned_concepts)}
