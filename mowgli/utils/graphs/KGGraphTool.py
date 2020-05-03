import pathlib
from random import random
from typing import Union, NoReturn, List, Iterable, Tuple
import lazy_import
import logging

from utils.general import reservoir_sampling
from utils.graphs.KGNetworkx import NxKG

gtall = lazy_import.lazy_module('graph_tool.all')
# import graph_tool.all as gtall

from utils.graphs.KnowledgeGraphBase import NoNeighborError, LexicError


logger = logging.getLogger(__name__)

NODE_T = gtall.Vertex
EDGE_T = gtall.Edge
GRAPH_T = gtall.Graph


class GTKG(NxKG):
    LOAD_FORMAT = ['.graphml', '.gt']

    @staticmethod
    def load_graph(path: Union[pathlib.Path, str]) -> GRAPH_T:
        return gtall.load_graph(path)

    def save(self, path: Union[pathlib.Path, str]) -> NoReturn:
        path = self._check_path(path)
        self._graph.save(path)

    ######################################################################
    def sample_node(self, n: int = 1) -> List[NODE_T]:
        nodes = [self.graph.vertex(random.randint(0, self.graph.num_vertices()))
                 for _ in range(n)]
        return nodes

    def sample_edge(self, n: int = 1) -> List[EDGE_T]:
        edge_iter: Iterable[EDGE_T] = self.graph.edges()
        edges = reservoir_sampling(edge_iter, n)
        return edges

    def sample_neighbour(self, v: NODE_T, black_list: List[NODE_T] = None) -> Tuple[NODE_T, EDGE_T]:
        if black_list is None:
            black_list = []
        d = dict(zip(v.all_neighbors(), v.all_edges()))
        nl = list(filter(lambda t: t[0] not in black_list, d.items()))

        if len(nl) == 0:
            raise NoNeighborError('No valid neighbors available')

        nxt, edge = random.choice(nl)
        # edge = d[nxt]

        return nxt, edge

    ######################################################################
    def get_node_label(self, v: NODE_T) -> str:
        try:
            label = self.graph.properties[('v', 'label')][v]
        except KeyError:
            raise LexicError(f'Entity ({v}) does not have label')
        return label

    def get_edge_label(self, e: Union[Tuple[NODE_T, NODE_T], EDGE_T]) -> str:
        if isinstance(e, tuple):
            u, v = e
            e = self.graph.edge(u, v)
        else:
            pass

        try:
            label = self.graph.properties[('e', 'predicate')][e]
        except KeyError:
            raise LexicError(f'Edge ({e}) does not have label')
        return label
