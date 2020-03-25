import time
import pickle
import logging

from mowgli.predictor.predictor import Predictor
import mowgli.utils.general as utils
import mowgli.parser as parser

class EndToEnd:
    """
    Class for creating end-to-end data processors.
    These pipelines will perform prediction.
    """
    def __init__(self, predictor: Predictor):
        """

        :param predictor: Fully-qualified class name of a Predictor
        """
        self.predictor = predictor

    def load_dataset(self, datadir, name, max_rows=None):
        data=parser.parse_dataset(datadir, name, max_rows)
        return data

    def get_data_partition(self, dataset, partition):
        return getattr(dataset, partition)

    def preprocess_dataset(self, dataset):
        return self.predictor.preprocess(dataset)

    def train_model(self, train_data, dev_data, graph=None):
        start_time = time.time()

        model=self.predictor.train(train_data, dev_data, graph)

        end_time=time.time()
        logging.debug("Time taken to train model: {}".format(end_time - start_time))

        return model

    def load_pretrained_model(self, path):
        with open(path, 'rb') as f:
            model=pickle.load(f)
        return model

    def predict(self, model, entries, store_bool, output_dir, partition):
        answers=[]
        probs=[]
		
        for i, entry in enumerate(entries):
            answer, prob=self.predictor.predict(model, entry)
            probs.append(prob)
            answers.append(answer)
        if store_bool:
            filename='%s/%s.lst' % (output_dir, partition)
            utils.save_predictions(filename, answers, probs)

        return answers

    def evaluate(self, data, predictions):
        gold_answers=[]
        for entry in data:
            gold_answers.append(entry.correct_answer)
        logging.debug('Num of gold answers: %d' % len(gold_answers))
        logging.debug('Num of predictions: %d' % len(predictions))
        acc=utils.compute_accuracy(gold_answers, predictions)
        return acc
