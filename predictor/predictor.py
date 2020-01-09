import abc
from typing import List, Any

from classes import Entry

class Predictor(abc.ABC):
    @abc.abstractmethod
    def train(self, train_data:List, dev_data:List) -> Any:
        pass

    @abc.abstractmethod
    def predict(self, model: Any, entry: Entry) -> List:
        pass
