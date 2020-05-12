import logging
import pickle
import time

import mowgli.parser as parser
import mowgli.utils.general as utils
from mowgli.predictor.predictor import Predictor


class EndToEnd:
    """
    Class for creating end-to-end data processors.
    These pipelines will perform prediction.
    """

    def __init__(self, predictor: Predictor):
        """

        :param predictor: Fully-qualified class name of a Predictor
        """
        self.predictor: Predictor = predictor

    def load_dataset(self, datadir, name, max_rows=None):
        data = parser.parse_dataset(datadir, name, max_rows)
        return data

    def get_data_partition(self, dataset, partition):
        return getattr(dataset, partition)

    def preprocess_dataset(self, dataset, config):
        return self.predictor.preprocess(dataset, config)

    def train_model(self, dataset, config):
        start_time = time.time()

        model = self.predictor.tune(dataset, config)

        end_time = time.time()
        logging.debug("Time taken to tune model: {}".format(end_time - start_time))

        return model

    def load_pretrained_model(self, path):
        with open(path, 'rb') as f:
            model = pickle.load(f)
        return model

    def predict(self, model, dataset, config, partition):
        answers, probs = self.predictor.predict(model, dataset, config, partition)
        if config['store_predictions']:
            filename = '%s/%s.lst' % (config['outdir'], partition)
            utils.save_predictions(filename, answers, probs)

        return answers

    def evaluate(self, data, predictions):
        gold_answers = []
        for entry in data:
            gold_answers.append(entry.correct_answer)
        logging.debug('Num of gold answers: %d' % len(gold_answers))
        logging.debug('Num of predictions: %d' % len(predictions))
        acc = utils.compute_accuracy(gold_answers, predictions)
        return acc
