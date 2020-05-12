import abc
from typing import List, Any

from mowgli.classes import Dataset
from mowgli.predictor.predictor import Predictor


class TrainablePredictor(Predictor):

    @abc.abstractmethod
    def train(self, config) -> Any:
        pass

