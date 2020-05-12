import argparse
import logging
import os
import pkgutil

import hydra
import yaml
from omegaconf import DictConfig

from mowgli.configurator.configurator import Configurator
from mowgli.end_to_end import EndToEnd

logger = logging.getLogger(__name__)


def process_dataset(config: DictConfig = None):
    if config is None:
        config_path = pkgutil.get_data('mowgli', 'cfg/default.yaml').decode()
        config = yaml.load(config_path)

    logger.debug("Using configuration: {}".format(config))
    configurator = Configurator(config)

    dataname = config['dataset']
    output_dir = config['outdir']
    pretrained_model = config['pretrained'] if 'pretrained' in config.keys() else None

    logger.debug("Processing dataset: {}".format(dataname))

    predictor = configurator.get_component("predictor")

    os.makedirs(output_dir, exist_ok=True)

    etoe = EndToEnd(predictor)

    # LOAD DATASET PARTITIONS
    input_dir = 'data/%s' % dataname
    dataset = etoe.load_dataset(input_dir, dataname, int(
        config['datarows']) if 'datarows' in config.keys() else None)

    if hasattr(etoe.predictor, 'train'):
        etoe.predictor.train()

    logger.debug("dataset loaded")
    logger.debug('Preprocessing the dataset')
    dataset = etoe.preprocess_dataset(dataset, config)

    train_data = etoe.get_data_partition(dataset, 'tune')
    logger.debug("Training examples: %d" % len(train_data))

    dev_data = etoe.get_data_partition(dataset, 'dev')
    logger.debug("Dev examples: %d" % len(dev_data))

    test_data = etoe.get_data_partition(dataset, 'test')
    if test_data and len(test_data):
        logger.debug("Test examples: %d" % len(test_data))

    # Train your model, or load a pretrained one
    if pretrained_model:
        logger.debug('Pretrained model specified. Loading: %s ...')
        model = etoe.load_pretrained_model(pretrained_model)
    else:
        logger.debug('No pretrained model specified. Training a new model...')
        model = etoe.train_model(dataset, config)

    # Make predictions on tune, dev and test data
    if config['evaluate_training']:
        train_predictions = etoe.predict(
            model, dataset, config, 'tune')
        train_acc = etoe.evaluate(train_data, train_predictions)
        logger.debug('Training accuracy: %f' % train_acc)

    dev_predictions = etoe.predict(
        model, dataset, config, 'dev')
    dev_acc = etoe.evaluate(dev_data, dev_predictions)
    logger.debug('Dev set accuracy: %f' % dev_acc)

    if len(test_data):
        test_predictions = etoe.predict(
            model, dataset, config, 'test')

    print('done!')

    return None


@hydra.main(config_path="cfg/default.yaml")
def main(args: DictConfig):
    process_dataset(config=args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process a machine commonsense dataset')
    parser.add_argument("--config", default="",
                        help="config file to load")

    args = parser.parse_args()

    main(args)
