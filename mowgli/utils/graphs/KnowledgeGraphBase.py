import pathlib
from abc import ABC, abstractmethod
from typing import Any, Optional, Type, NoReturn, Union

import lazy_import

nx = lazy_import.lazy_module('networkx')
gtall = lazy_import.lazy_module('graph_tool.all')

NODE_T = Type[Any]
EDGE_T = Type[Any]
GRAPH_T = Optional[Any]


class KnowledgeGraphBase(ABC):
    LOAD_FORMAT = []

    def __init__(self, graph_path: Union[str, pathlib.Path], is_lazy: bool, *args, **kwargs):
        self._graph: GRAPH_T = None
        self.graph_path: pathlib.Path = self._check_path(graph_path)
        if not is_lazy:
            a = self._graph

    @property
    def graph(self):
        if self._graph is None:
            self._graph = self.load_graph(
                self._check_path(self.graph_path)
            )
        return self._graph

    @graph.setter
    def graph(self, value: GRAPH_T):
        self._graph = value

    @classmethod
    def load(cls: Type['KnowledgeGraphBase'], path: Union[pathlib.Path, str]) -> 'KnowledgeGraphBase':
        path = cls._check_path(path)
        return cls(path, is_lazy=False)

    @classmethod
    def load_lazy(cls: Type['KnowledgeGraphBase'], path: Union[pathlib.Path, str]) -> 'KnowledgeGraphBase':
        path = cls._check_path(path)
        return cls(path, is_lazy=True)

    @classmethod
    def _check_path(cls, path: Union[pathlib.Path, str]) -> pathlib.Path:
        if isinstance(path, str):
            path = pathlib.Path(path)
        assert path.suffix in cls.LOAD_FORMAT, f'Currently only support following formats: {cls.LOAD_FORMAT}'
        return path

    @abstractmethod
    @staticmethod
    def load_graph(path: Union[pathlib.Path, str]) -> nx.MultiDiGraph:
        pass

    @abstractmethod
    def save(self, path: Union[pathlib.Path, str]) -> NoReturn:
        pass


class NoNeighborError(Exception):
    pass


class LexicError(Exception):
    pass
