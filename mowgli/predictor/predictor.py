import abc
from typing import List, Any

from mowgli.classes import Entry, Dataset

class Predictor(abc.ABC):

    @abc.abstractmethod
    def preprocess(self, dataset:Dataset) -> Any:
        pass

    @abc.abstractmethod
    def train(self, train_data:List, dev_data:List) -> Any:
        pass

    @abc.abstractmethod
    def predict(self, model: Any, dataset: Dataset, partition: str) -> List:
        pass
