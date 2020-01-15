import random
from typing import List, Any

from sentence_transformers import SentenceTransformer
import scipy.spatial.distance
import numpy as np

from classes import Dataset, Entry
from predictor.predictor import Predictor

class ST(Predictor):
    def preprocess(self, part_data:List) -> Any:
        return part_data

    def train(self, train_data:List, dev_data: List) -> Any:
        #model_name='roberta-large-nli-mean-tokens'
        model_name='roberta-large-nli-stsb-mean-tokens'
        model = SentenceTransformer(model_name)
        return model

    def predict(self, model: Any, entry: Entry) -> List:
        question=entry.question
        answers=entry.answers

        answer_embeddings = model.encode(answers)
        query_embeddings = model.encode(question)

        summed_distances=np.array([0.0] * len(answers))
        for q, query_embedding in zip(question, query_embeddings):
            distances = scipy.spatial.distance.cdist([query_embedding], answer_embeddings, "cosine")[0]
            summed_distances+=np.array(distances)
        print(summed_distances)
        answer=np.argmin(summed_distances)

        return str(answer)
