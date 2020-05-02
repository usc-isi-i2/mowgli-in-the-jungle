import abc
from typing import List, Any

from mowgli.classes import Entry, Dataset

class Predictor(abc.ABC):

    @abc.abstractmethod
    def preprocess(self, dataset:Dataset, config: Any) -> Any:
        pass

    @abc.abstractmethod
    def train(self, dataset:Dataset, config:Any) -> Any:
        pass

    @abc.abstractmethod
    def predict(self, model: Any, dataset: Dataset, config: Any, partition: str) -> List:
        pass
