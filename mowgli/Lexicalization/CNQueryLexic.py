import logging
import subprocess
import os
import pathlib
import re
from typing import List, Tuple, NoReturn

from mowgli.Lexicalization.Lexicalizations import EntityLexicError, EdgeLexicalizer, SimplePathLexic
from mowgli.Lexicalization.RuleBasedLexic import COMMONSENSE_MAPPING

logger = logging.getLogger(__name__)


class RuleBasedEdgeLexic(EdgeLexicalizer):

    def __init__(self) -> NoReturn:
        super().__init__()
        self.cache_path: pathlib.Path = pathlib.Path('~/mowgli-cache').expanduser()
        self.cn_web_paths = [
            'https://s3.amazonaws.com/conceptnet/downloads/2018/omcs-sentences-more.txt',
            'https://s3.amazonaws.com/conceptnet/downloads/2018/omcs-sentences-free.txt',
        ]
        self._check_cn_data_exists()

    def _check_cn_data_exists(self):
        for p in self.cn_web_paths:
            file_name = p.split('/')[-1]
            if not (self.cache_path / file_name).exists():
                try:
                    subprocess.run(args=['wget', '-p', str(self.cache_path), p], check=True)
                except subprocess.CalledProcessError:
                    logger.error(f'Failed to download {p}')

    def convert(self, edge: Tuple[str, str, str]) -> str:
        """
        Converts the edge to the lexicalized sentence associated with it.
        The module assumes the edge consists of the string label of source/target nodes and the edge between them,
        in the format (source_label, edge_label, target_label)
        Args:
            edge: Tuple[NODE_T str, EDGE_T str, NODE_T str]

        Returns: str
            a sentence associated with the lexicalization of the edge
        """
        edge_clean = list(map(self._clean_relation_entity, edge))
        sent = self._triple2str(*edge_clean)
        return sent

    def _triple2str(self, s: str, p: str, e: str) -> str:
        all_matches = []
        for p in self.cn_web_paths:
            file_path = self.cache_path / p.split('/')[-1]
            assert file_path.exists(), f'{file_path} does not exist.'
            matches = self._lookup_in_file(words=[s, self._pred2str(p), e], path=file_path)
            all_matches += matches

        sent = self._filter_matches(matches=all_matches, words=[s, p, e])
        return sent

    def _filter_matches(self, matches: List[str], words: List[str]) -> str:
        return sorted(matches, key=len)[0]

    @staticmethod
    def _pred2str(pred: str) -> str:
        verb = COMMONSENSE_MAPPING.get(pred, None)
        if verb is None:
            logger.error(f'New predicate: {pred}')
            return pred
        else:
            return verb

    @staticmethod
    def _lookup_in_file(words: List[str], path: pathlib.Path) -> List[str]:
        cmd_words = " && ".join([f'/{w}/' for w in words])
        # command = f'awk \'{cmd_words}\' {path}'
        out = subprocess.run(['awk', cmd_words, path], check=True, capture_output=True, text=True)
        return [m.split('\t')[1] for m in out.stdout.split('\n')]

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


class RuleBasedPathLexic(SimplePathLexic):
    def __init__(self):
        super().__init__(RuleBasedEdgeLexic())
