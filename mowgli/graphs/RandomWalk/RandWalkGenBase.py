import pathlib
from abc import ABC, abstractmethod
from typing import List, Any, Tuple
import lazy_import
import logging
import tqdm

from utils.graphs.KnowledgeGraphBase import NODE_T, GRAPH_T
from utils.graphs.KGGraphTool import GTKG
from utils.graphs.KGNetworkx import NxKG
from utils.graphs.Lexicalization.Lexicalizations import EntityLexicError

logger = logging.getLogger(__name__)
nx = lazy_import.lazy_module('networkx')
gtall = lazy_import.lazy_module('graph_tool.all')


class BadStartNodeError(Exception):
    pass


class NoNeighborError(Exception):
    pass


class RandomWalkGeneratorBase(ABC):
    @abstractmethod
    def _read_graph(self):
        pass

    @abstractmethod
    def _setup_all_nodes(self):
        pass

    @abstractmethod
    def _sample_one_node(self) -> NODE_T:
        pass

    @abstractmethod
    def _sample_neighbour(self, v, path: List[NODE_T]) -> Tuple[NODE_T, str, str]:
        pass

    @abstractmethod
    def _get_node_label(self, v) -> str:
        pass

    @abstractmethod
    def _get_edge_label(self, v: NODE_T, u: NODE_T) -> str:
        pass

    def create_random_walk_file(self, max_len: int):
        writer = self._setup_writer(max_len)
        logger.info('Starting the sampling loop')
        i = 0
        pbar = tqdm.trange(max_len)
        while i < max_len:
            start = self._sample_one_node()
            logger.debug(f'_sample_one_node: {start}')
            try:
                path = self.random_walk(start)
            except BadStartNodeError:
                logger.debug(f'BadStartNodeError for {start}')
                continue
            try:
                writer.send(path)
                i += 1
                pbar.update()
            except EntityLexicError:
                i -= 1
                continue

        writer.dump_buffer()

    def generate_bruteforce(self):
        self._read_graph()
        dataset_size = self._setup_dataset_sizes()

        for max_len in tqdm.tqdm(dataset_size, desc='Dataset Size'):
            self.create_random_walk_file(max_len)

    def _setup_writer(self, max_len):
        output_path = pathlib.Path(self.config.output_path)
        if output_path.is_dir():
            out_name = f'{pathlib.Path(self.config.graph_path).stem}_{max_len}.rw'
            output_path = output_path / out_name
            logger.info(f'Output Path: {output_path}')

        if self.config.lexicalization == 'hykas':
            writer = RWWriterLexical(output_path)
        elif self.config.lexicalization == 'none' or self.config.lexicalization is None:
            writer = RandWalkWriter(output_path)
        elif self.config.lexicalization == 'sep':
            writer = RWWriterSepToken(output_path)
        else:
            raise ValueError(f'Invalid lexicalization method: {self.config.lexicalization}')
        return writer

    def random_walk(self, start: typing.Any) -> List[str]:
        path: List[typing.Any] = [start]

        try:
            path_str: List[str] = [self._get_node_label(start)]
        except EntityLexicError:
            logger.debug(f'start node does not have label')
            raise BadStartNodeError('Start node does not have a label, try a new one.')

        while len(path) < self.config.max_walk_length:
            nxt_node = start
            predicate = None
            nxt_label = None

            count = 0
            while True:
                # sample a neighbour and get the edge
                try:
                    nxt_node, nxt_label, predicate = self._sample_neighbour(start, path)
                    logger.debug(f'new node found ({nxt_label}, {predicate})')
                    break
                except TypeError as e:
                    logger.error(f'ValueError: _sample_neighbour: {start}, path:{path}')
                    raise e
                except NoNeighborError:
                    count = 100
                except EntityLexicError as e:
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

            assert (not self.config.use_predicate) or (predicate is not None), \
                f'assertif ({self.config.use_predicate}) then ({predicate})'

            # get the label of predicate/edge
            if predicate is not None:
                path_str.append(predicate)

            assert nxt_label is not None, f'{nxt_node}'
            assert nxt_node is not None, f'{nxt_node}'
            path_str.append(nxt_label)
            path.append(nxt_node)
            logger.debug(f'path extended by ({predicate}, {nxt_label})')
            start = nxt_node

        return path_str

    def is_invalid_predicate(self, predicate):
        return predicate in ['vg:InImage', 'mw:OMWordnetOffset', 'vg:object', 'vg:subject',
                             'mw:PartOfSpeech'] or 'POS' in predicate

    def _setup_dataset_sizes(self):
        dataset_size = []
        if isinstance(self.config.num_samples, int):
            dataset_size = [self.config.num_samples]
        elif isinstance(self.config.num_samples, omegaconf.listconfig.ListConfig):
            dataset_size = list(self.config.num_samples)
        else:
            raise ValueError(f'input: {self.config.num_samples} has type: {type(self.config.num_samples)}')

        logger.info(f'dataset_size= {dataset_size}')
        return dataset_size


class NxRandomWalkGenerator(RandomWalkGenerator):

    def _setup_all_nodes(self):
        if self.all_nodes is None:
            self.all_nodes = list(self.graph.nodes())

        # self.node_labels: typing.Dict[str, str] = nx.get_node_attributes(self.graph, 'label')

    def _read_graph(self):
        logger.info(f'import graphml file from {self.config.graph_path}')
        self.graph = nx.read_graphml(self.config.graph_path)
        if not self.config.directed:
            logger.info('Converting to undirected graph')
            self.graph: nx.MultiGraph = self.graph.to_undirected()

    def _sample_one_node(self):
        self._setup_all_nodes()
        start = random.choice(self.all_nodes)
        return start

    def _sample_neighbour(self, v, path: typing.List) -> typing.Tuple[typing.Any, str, str]:
        nl = list(filter(lambda n: n not in path, self.graph.neighbors(v)))
        if len(nl) == 0:
            raise NoNeighborError('No valid neighbors available')
            # return None, None

        nxt = random.choice(nl)

        nxt_label = self._get_node_label(nxt)
        edge = self._get_edge_label(v, nxt)

        if self.is_invalid_predicate(edge):
            raise EntityLexicError(f'blacklisted predicate')

        return nxt, nxt_label, edge

    def _get_edge_label(self, v: typing.Any, u: typing.Any) -> typing.Optional[str]:
        if not self.config.use_predicate:
            return None

        edge = self.graph.get_edge_data(v, u)[0]['predicate']
        return edge

    def _get_node_label(self, v) -> str:
        nd_feat = self.graph._node[v]
        try:
            label = nd_feat['label']
        except KeyError:
            logger.warning(f'Entity ({v}) does not have label')
            raise EntityLexicError(f'Entity ({v}) does not have label')
        if ('vg:' in label) or (label is None):
            raise EntityLexicError(f'Ignoring vg node or Nones {label}')
        return label


class GraphtoolRandomWalkGenerator(NxRandomWalkGenerator):
    def _setup_all_nodes(self):
        if self.all_nodes is None:
            pass
            # self.all_nodes = list(self.graph.nodes())

    def _read_graph(self):
        from graph_tool import load_graph, Graph
        logger.info(f'import graphml file from {self.config.graph_path}')
        self.graph: Graph = load_graph(self.config.graph_path)
        if not self.config.directed:
            logger.info('Converting to undirected graph')
            self.graph.set_directed(False)

    def _sample_one_node(self):
        # self._setup_all_nodes()
        start = self.graph.vertex(random.randint(0, self.graph.num_vertices()))
        # logger.info(f'_sample_one_node: {start}')
        return start

    def _sample_neighbour(self, v, path: typing.List):
        d = dict(zip(v.all_neighbors(), v.all_edges()))
        nl = list(d.keys())

        # if len(nl) == 0:
        if len(d) == 0 or all([n in path for n in nl]):
            return None, None

        u = random.choice(nl)

        try:
            edge = d[u]
            label = self.graph.properties[('e', 'predicate')][edge]
        except KeyError:
            label = None

        return u, label

    # @functools.lru_cache()
    def _get_node_label(self, v) -> str:
        label = self.graph.properties[('v', 'label')][v]
        # logger.info(f'_get_node_label({v}): {label}')
        return label

    # @functools.lru_cache()
    def _get_edge_label(self, v, u) -> str:
        pass
    #     d = dict(zip(v.all_neighbors(), v.all_edges()))
    #     edge = d[u]
    #     label = self.graph.properties[('e', 'predicate')][edge]
    #     # logger.info(f'_get_edge_label({v},{u}) = {label}')
    #     return label
