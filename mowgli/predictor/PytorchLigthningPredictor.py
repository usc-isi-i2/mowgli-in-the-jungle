from abc import abstractmethod
from typing import Any, List, Optional
import lazy_import

from mowgli.classes import Dataset
from mowgli.predictor.TrainablePredictor import TrainablePredictor
from mowgli.predictor.predictor import Predictor
# from mowgli.utils.graphs.KnowledgeGraphBase import KnowledgeGraphBase

# import pytorch_lightning as pl
pl = lazy_import.lazy_module('pytorch_lightning')


class PytorchLightningPredictor(TrainablePredictor):
    def __init__(self, *args, **kwargs):
        self._train_pl_module: Optional[pl.LightningModule] = None
        self._tune_pl_module: Optional[pl.LightningModule] = None

    @property
    @abstractmethod
    def train_pl_module(self):
        return self._train_pl_module

    @train_pl_module.setter
    def train_pl_module(self, value: pl.LightningModule):
        self._train_pl_module = value

    @property
    @abstractmethod
    def tune_pl_module(self):
        return self._tune_pl_module

    @tune_pl_module.setter
    def tune_pl_module(self, value: pl.LightningModule):
        self._tune_pl_module = value

    # def train(self, kg: KnowledgeGraphBase):
    #     pass
    #
    # def preprocess(self, dataset: Dataset, config: Any) -> Any:
    #     pass
    #
    # def tune(self, dataset: Dataset, config: Any) -> Any:
    #     pass
    #
    # def predict(self, model: Any, dataset: Dataset, config: Any, partition: str) -> List:
    #     pass
