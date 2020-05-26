from abc import ABC, abstractmethod
import re
from typing import Any
from collections import deque
from typing import List
import logging
from commonsense_mapping import COMMONSENSE_MAPPING

logger = logging.getLogger(__name__)


class EntityLexicError(Exception):
    pass


class Lexicalizer(ABC):
    @abstractmethod
    def convert(self, input: Any) -> str:
        pass

class RandWalkWriter:
    def __init__(self, filename: str):
        self.filename = filename
        self.buffer = []
        self.max_buf = 100

        self.sep = ' '

        with open(self.filename, 'w') as f:
            pass

    def send(self, path: List[str]):
        random_path = path

        text = self._lexicalize_path(random_path)

        self.buffer.append(text)
        if len(self.buffer) >= self.max_buf:
            self.dump_buffer()

    def _lexicalize_path(self, random_path: List[str]) -> str:
        return f"{self.sep}".join(map(self._clean_relation_entity, random_path)) + '\n'

    def dump_buffer(self):
        with open(self.filename, 'a') as f:
            f.writelines(self.buffer)
        self.buffer = []

    def __del__(self):
        if len(self.buffer) > 0:
            self.dump_buffer()

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


class RWWriterSepToken(RandWalkWriter):
    def __init__(self, filename: str):
        token_sep = self.get_sep_token()
        self.sep = f' {token_sep} '
        super().__init__(filename)

    @staticmethod
    def _get_sep_token(model: str = 'roberta-base') -> str:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(model.lower(), cache_dir="~/model_cache")
        return tokenizer.sep_token


class RWWriterLexical(RandWalkWriter):
    def __init__(self, filename: str):
        super().__init__(filename)

    def _lexicalize_path(self, random_path: List[str]) -> str:
        # logger.info(f'random_path: {random_path}')
        cleaned = map(self._clean_relation_entity, random_path)
        edges = self._separate_edges(cleaned)
        # sents = map(lambda t: f'{t[0]} {self.pred2str(t[1])} {t[2]}', edges)
        sents = map(lambda t: self.triple2str(*t), edges)
        lexic = f", and ".join(sents) + '.\n'
        # logger.info(f'lexic: {lexic}')
        return lexic

    @staticmethod
    def triple2str(s: str, p: str, e: str) -> str:
        return f'{s} {RWWriterLexical.pred2str(p)} {e}'

    @staticmethod
    def pred2str(pred: str) -> str:
        verb = COMMONSENSE_MAPPING.get(pred, None)
        if verb is None:
            logger.error(f'New predicate: {pred}')
            return pred
        else:
            return verb

    @staticmethod
    def _separate_edges(path: typing.Iterable[str]) -> typing.Generator[List[str], None, None]:
        d = deque(maxlen=3)
        iterable = iter(path)
        for i, it in enumerate(iterable):
            d.append(it)
            if len(d) == 3:
                yield list(d)
                d.popleft()
                d.popleft()