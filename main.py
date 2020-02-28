import sys
sys.path.append('../')

import argparse
import yaml
import logging
import os
import logging

from configurator.configurator import Configurator
from end_to_end import EndToEnd


def process_dataset(input_dir, config_file, output_dir, pretrained_model):

    config = yaml.load(open(config_file))
    logging.debug("Using configuration: {}".format(config))
    configurator = Configurator(config)

    logging.debug("Processing directory: {}".format(input_dir))

    predictor = configurator.get_component("predictor")

    etoe = EndToEnd(predictor)

    # LOAD DATASET PARTITIONS
    dataset = etoe.load_dataset(input_dir, config['dataname'], int(
        config['datarows']) if 'datarows' in config.keys() else None)

    logging.debug("dataset loaded")
    train_data = etoe.get_data_partition(dataset, 'train')
    logging.debug('Preprocessing training data')
    train_data = etoe.preprocess_partition(train_data, 'train')
    logging.debug("Training examples: %d" % len(train_data))

    dev_data = etoe.get_data_partition(dataset, 'dev')
    dev_data = etoe.preprocess_partition(dev_data, 'dev')
    logging.debug("Dev examples: %d" % len(dev_data))

    test_data = etoe.get_data_partition(dataset, 'test')
    if test_data and len(test_data):
        test_data = etoe.preprocess_partition(test_data, 'test')
        logging.debug("Test examples: %d" % len(test_data))

    # Train your model, or load a pretrained one
    if pretrained_model:
        logging.debug('Pretrained model specified. Loading: %s ...')
        model = etoe.load_pretrained_model(pretrained_model)
    else:
        logging.debug('No pretrained model specified. Training a new model...')
        model = etoe.train_model(train_data, dev_data)

    # Make predictions on train, dev and test data
    if config['evaluate_training']:
        train_predictions = etoe.predict(
            model, train_data, config['store_predictions'], output_dir, 'train')
        train_acc = etoe.evaluate(train_data, train_predictions)
        logging.debug('Training accuracy: %f' % train_acc)

    dev_predictions = etoe.predict(
        model, dev_data, config['store_predictions'], output_dir, 'dev')
    dev_acc = etoe.evaluate(dev_data, dev_predictions)
    logging.debug('Dev set accuracy: %f' % dev_acc)

    if len(test_data):
        test_predictions = etoe.predict(
            model, test_data, True, output_dir, 'predictions')

    print('done!')

    return None


def main(args):

    logging.basicConfig(level=logging.DEBUG)

    process_dataset(input_dir=args.input, config_file=args.config,
                    output_dir=args.output, pretrained_model=args.pretrained)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process a machine commonsense dataset')
    parser.add_argument("--input", default="data/",
                        help="Data directory that contains input files in JSONL format and potentially labels.")
    parser.add_argument("--config", default="cfg/default.yaml",
                        help="config file to load")
    # Default is current directory
    parser.add_argument("--output", default="./",
                        help="Output directory for all output files")
    parser.add_argument("--pretrained", default=None,
                        help="(Optional) Predict using a pretrained model")

    args = parser.parse_args()

    main(args)
