import logging
import re
from collections import deque
from typing import List, Union, Iterable, Generator, Tuple

from mowgli.Lexicalization.Lexicalizations import EdgeLexicalizer, PathLexicalizer, EntityLexicError
from mowgli.graphs.KGBase import NODE_T, EDGE_T, GRAPH_T

logger = logging.getLogger(__name__)


COMMONSENSE_MAPPING = {
    'Antonym': 'is antonym of',
    'AtLocation': 'is at location',
    'CapableOf': 'is capable of',
    'Causes': 'causes',
    'CausesDesire': 'causes desire',
    'CreatedBy': 'is created by',
    'DefinedAs': 'is defined as',
    'DerivedFrom': 'is derived from',
    'Desires': 'desires',
    'DistinctFrom': 'is distinct from',
    'Entails': 'entails',
    'EtymologicallyDerivedFrom': 'is etymologically derived from',
    'EtymologicallyRelatedTo': 'is etymologically related to',
    'fe:ExcludesFE': 'excludes frame element',
    'FormOf': 'is form of',
    'HasA': 'has a',
    'HasContext': 'has context',
    'HasFirstSubevent': 'has first subevent',
    'HasFrameElement': 'has frame element',
    'HasInstance': 'has instance',
    'HasLastSubevent': 'has last subevent',
    'HasLexicalUnit': 'has lexical unit',
    'HasPrerequisite': 'has prerequisite',
    'HasProperty': 'has property',
    'HasSemType': 'has semantic type',
    'HasSubevent': 'has subevent',
    'HasSubframe': 'has subframe',
    'InstanceOf': 'is instance of',
    'IsA': 'is a',
    'IsCausativeOf': 'is causative of',
    'IsInchoativeOf': 'is inchoative of',
    'IsInheritedBy': 'is inherited by',
    'IsPerspectivizedIn': 'is perspectivized in',
    'IsPOSFormOf': 'is part-of-speech form of',
    'IsPrecededBy': 'is preceded by',
    'IsUsedBy': 'is used by',
    'LocatedNear': ' has location near',
    'MadeOf': 'is made of',
    'MannerOf': 'is a manner of',
    'MotivatedByGoal': 'is motivated by goal',
    'object': 'object',
    'OMWordnetOffset': 'has wordnet offset',
    'NotCapableOf': 'is not capable of',
    'NotDesires': 'does not desire',
    'NotHasProperty': 'does not have property',
    'PartOf': 'is part of',
    'PartOfSpeech': 'has part-of-speech of',
    'PerspectiveOn': 'is perspective on',
    'POSForm': 'is part-of-speech form',
    'Precedes': 'precedes',
    'PWordnetSynset': 'has wordnet synset',
    'ReceivesAction': 'has received action',
    'ReframingMapping': 'has reframing mapping',
    'RelatedTo': 'is related to',
    'st:RootType': 'has root type',
    'fe:RequiresFE': 'requires frame element',
    'subject': 'subject',
    'SeeAlso': 'see also',
    'SimilarTo': 'is similar to',
    'subClassOf': 'is subclass of',
    'SubframeOf': 'is subframe of',
    'st:SubType': 'is subtype of',
    'st:SuperType': 'is supertype of',
    'SymbolOf': 'is symbol of',
    'Synonym': 'is synonym of',
    'UsedFor': 'is used for',
    'Uses': 'uses',
    'DesireOf': 'desire of',
    'InheritsFrom': 'inherits from',
    'LocationOfAction': 'is location of action',
    'dbpedia/capital': 'is capital of',
    'dbpedia/field': 'is field of',
    'dbpedia/genre': 'is genre of',
    'dbpedia/genus': 'is genus of',
    'dbpedia/influencedBy': 'is influenced by',
    'dbpedia/knownFor': 'is known for',
    'dbpedia/language': 'has language',
    'dbpedia/leader': 'is leader of',
    'dbpedia/occupation': 'has occupation',
    'dbpedia/product': 'is product of',
    # new relations
    'rdfs:subClassOf': 'is subclass of',

    # ATOMIC Predicates:
    'at:xNeed': 'needs to',
    'at:xAttr': 'is',
    'at:xWant': 'want to',
    'at:oReact': 'will be',
    'at:oEffect': 'will',
    'at:xEffect': 'gets',
    'at:xIntent': 'wanted to be',
    'at:oWant': 'will',
    'at:xReact': 'will feel',
}


class RuleBasedEdgeLexic(EdgeLexicalizer):
    def convert(self, edge: Tuple[str, str, str]) -> str:
        lexic = ""
        cleaned_edge = map(self._clean_relation_entity, edge)
        return lexic

    @staticmethod
    def _clean_relation_entity(s: str) -> str:
        if '/' not in s:
            return s
        for p in [r'\/c\/en\/([^\s\/]*)', r'\/r\/([^\s\/]*)', r'[^:]:([^\s\/]*)']:
            m = re.findall(p, s)
            if len(m) > 0:
                # assert len(m) == 1, f'multiple match (p={p}) in {s} :{m}'
                return m[0].replace('_', ' ')
        raise EntityLexicError(f'{s}')


class RuleBasedLexic(PathLexicalizer):
    def convert(self, path: List[str]) -> str:
        return self._lexicalize_path(path)
    
    def _lexicalize_path(self, random_path: List[str]) -> str:
        cleaned = map(self._clean_relation_entity, random_path)
        edges = self._separate_edges(cleaned)
        sents = map(lambda t: self._triple2str(*t), edges)
        lexic = f", and ".join(sents) + '.\n'
        return lexic

    @staticmethod
    def _triple2str(s: str, p: str, e: str) -> str:
        return f'{s} {RuleBasedLexic._pred2str(p)} {e}'

    @staticmethod
    def _pred2str(pred: str) -> str:
        verb = COMMONSENSE_MAPPING.get(pred, None)
        if verb is None:
            logger.error(f'New predicate: {pred}')
            return pred
        else:
            return verb

    @staticmethod
    def _separate_edges(path: Iterable[str]) -> Generator[List[str], None, None]:
        d = deque(maxlen=3)
        iterable = iter(path)
        for i, it in enumerate(iterable):
            d.append(it)
            if len(d) == 3:
                yield list(d)
                d.popleft()
                d.popleft()

    @staticmethod
    def _clean_relation_entity(s: str) -> str:
        if '/' not in s:
            return s
        for p in [r'\/c\/en\/([^\s\/]*)', r'\/r\/([^\s\/]*)', r'[^:]:([^\s\/]*)']:
            m = re.findall(p, s)
            if len(m) > 0:
                # assert len(m) == 1, f'multiple match (p={p}) in {s} :{m}'
                return m[0].replace('_', ' ')
        raise EntityLexicError(f'{s}')
