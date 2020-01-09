import random
from typing import List, Any

from classes import Dataset, Entry
from predictor.predictor import Predictor

class ExamplePredictor(Predictor):
    def train(self, train_data:List, dev_data: List) -> Any:
        return None

    def predict(self, model: Any, entry: Entry) -> List:
        question=entry.question
        answers=entry.answers

        answer=random.randint(0,len(answers)-1)
        while answers[answer]=='':
            answer=random.randint(0,len(answers)-1)
        return str(answer)

