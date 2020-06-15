import logging
import pathlib
import random
from typing import Union, NoReturn, List, Tuple, Iterable

import lazy_import

from mowgli.utils.general import reservoir_sampling
from mowgli.graphs.KGBase import KnowledgeGraphBase, NODE_T, NoNeighborError, LexicError, BadStartNodeError

nx = lazy_import.lazy_module('networkx')
logger = logging.getLogger(__name__)

EDGE_T = Tuple[NODE_T, NODE_T]


class NxKG(KnowledgeGraphBase):
    LOAD_FORMAT = ['.graphml']

    @staticmethod
    def load_graph(path: Union[pathlib.Path, str]) -> nx.MultiDiGraph:
        if path.suffix == '.graphml':
            g = nx.read_graphml(path)
            return nx.MultiDiGraph(g)

    def save(self, path: Union[pathlib.Path, str]) -> NoReturn:
        path = self._check_path(path)
        if path.suffix == '.graphml':
            self.graph.write_graphml(path)

    @classmethod
    def _check_path(cls, path: Union[pathlib.Path, str]) -> pathlib.Path:
        path = super()._check_path(path)
        assert path.is_file(), f'{path}'
        return path

    ######################################################################
    def sample_node(self, n: int = 1) -> List[NODE_T]:
        nodes = reservoir_sampling(self.graph.nodes(), n)
        return nodes

    def sample_edge(self, n: int = 1) -> EDGE_T:
        edge_iter: Iterable[Tuple[NODE_T, NODE_T]] = self.graph.edges
        edges = reservoir_sampling(edge_iter, n)
        return edges

    def sample_neighbour(self, v: NODE_T, black_list: List[NODE_T] = None) -> Tuple[NODE_T, EDGE_T]:
        if black_list is None:
            black_list = []
        nl = list(filter(lambda n: n not in black_list, self.graph.neighbors(v)))
        if len(nl) == 0:
            raise NoNeighborError('No valid neighbors available')

        nxt = random.choice(nl)
        return nxt, (v, nxt)

    ######################################################################
    def get_node_label(self, v: NODE_T) -> str:
        nd_feat = self.graph._node[v]
        try:
            label = nd_feat['label']
        except KeyError:
            raise LexicError(f'Entity ({v}) does not have label')
        return label

    def get_edge_label(self, e: Union[Tuple[NODE_T, NODE_T], EDGE_T]) -> str:
        if isinstance(e, tuple):
            u, v = e
        else:
            raise ValueError(f'Networkx only considers an edge as a pair of nodes. Given: {e}')

        try:
            label = self.graph.get_edge_data(u, v)[0]['predicate']
        except KeyError:
            raise LexicError(f'Edge ({e}) does not have label')
        return label

    ######################################################################
    def random_walk(self, source: NODE_T) -> List[str]:
        path: List[NODE_T] = [source]
        path_str: List[str] = [self.get_node_label(source)]

        while len(path) < self.config.max_walk_length:
            nxt = source
            edge = None

            count = 0
            while True:
                # sample a neighbour and get the edge
                try:
                    nxt, edge = self.sample_neighbour(source, path)
                    logger.debug(f'new node found ({nxt}, {edge})')
                    break
                except TypeError as e:
                    logger.error(f'ValueError: sample_neighbour: {source}, path:{path}')
                    raise e
                except NoNeighborError:
                    count = 100
                except LexicError as e:
                    count += 1

                # If node does not have any neighbours end the random walk
                # and dump what it has so far
                if count >= 5:
                    # some pathes are not good enough but nevertheless we use them.
                    if len(path_str) >= 3:
                        logger.debug(f'returning with shorter path ({path_str})')
                        return path_str
                    else:
                        logger.debug(f'Deadend path reached ({path_str})')
                        raise BadStartNodeError('No path moving forward, try a new start node')

            assert edge is not None, f'({edge})'

            # get the label of predicate/edge
            path_str.append(self.get_edge_label(edge))

            nxt_label = self.get_node_label(nxt)
            assert nxt_label is not None, f'{nxt}'
            assert nxt is not None, f'{nxt}'
            path_str.append(nxt_label)
            path.append(nxt)
            logger.debug(f'path extended by ({edge}, {nxt_label})')
            source = nxt

        return path_str
