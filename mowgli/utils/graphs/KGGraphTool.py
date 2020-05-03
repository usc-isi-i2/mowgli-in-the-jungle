import pathlib
from typing import Union, NoReturn
import lazy_import
import logging
from utils.graphs.KGNetworkx import NxKG

gtall = lazy_import.lazy_module('graph_tool.all')
logger = logging.getLogger(__name__)

class GTKG(NxKG):
    LOAD_FORMAT = ['.graphml', '.gt']

    @staticmethod
    def load_graph(path: Union[pathlib.Path, str]) -> gtall.Graph:
        return gtall.load_graph(path)

    def save(self, path: Union[pathlib.Path, str]) -> NoReturn:
        path = self._check_path(path)
        self._graph.save(path)