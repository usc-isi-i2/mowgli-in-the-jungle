import random
from typing import List, Any

from mowgli.classes import Dataset, Entry
from mowgli.predictor.predictor import Predictor

class ExamplePredictor(Predictor):

    def preprocess(self, part_data:List, partition:str) -> Any:
        return part_data
        
    def train(self, train_data:List, dev_data: List) -> Any:
        return None

    def predict(self, model: Any, entry: Entry) -> List:
        question=entry.question
        answers=entry.answers

        answer=random.randint(0,len(answers)-1)
        while answers[answer]=='':
            answer=random.randint(0,len(answers)-1)
        probs=['%.2f' % random.random() for i in range(len(answers))]
        return str(answer), probs

