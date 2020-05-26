import logging
import pathlib
from typing import Union, NoReturn, List, Iterable, Tuple, Type
from random import random
import lazy_import

from mowgli.utils.general import reservoir_sampling
from mowgli.graphs.KGNetworkx import NxKG
from mowgli.graphs.KnowledgeGraphBase import NoNeighborError, LexicError

# import graph_tool.all as gtall
gtall = lazy_import.lazy_module('graph_tool.all')
logger = logging.getLogger(__name__)

NODE_T = Type[gtall.Vertex]
EDGE_T = Type[gtall.Edge]
GRAPH_T = Type[gtall.Graph]


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

    ######################################################################

    def make_filter(self, concepts: List[NODE_T], fltr):
        fltr.a = False
        for n in concepts:
            v = gtall.find_vertex(
                self.graph,
                prop=self.graph.properties[('v', '_graphml_vertex_id')],
                match=str(n))[0]
            # v = qtqu.get_nodes_by_node_prop(self.graph, '_graphml_vertex_id', n)[0]
            fltr[v] = True
            for vn in v.out_neighbors():
                fltr[vn] = True
        return fltr

    @staticmethod
    def reason_over_paths(g1: GRAPH_T, g2: GRAPH_T):
        return gtall.similarity(g1, g2)

    def produce_answer(self, entry, prune):
        qc_fltr = self.graph.new_vertex_property("bool")
        qc_fltr = self.make_filter(entry.qc, qc_fltr)
        qg = gtall.GraphView(self.graph, qc_fltr)
        qg = gtall.Graph(qg, prune=prune)

        best_score = 0.0
        answer = -1
        for i, ac in enumerate(entry.ac):
            ac_fltr = self.graph.new_vertex_property("bool")
            ac_fltr = None  # make_filter(g, ac, ac_fltr)
            ag = gtall.GraphView(self.graph, ac_fltr)
            ag = gtall.Graph(ag, prune=prune)
            score = self.reason_over_paths(qg, ag)
            if score > best_score:
                best_score = score
                answer = i
            del ac_fltr
        del qc_fltr
        return answer

    ######################################################################
