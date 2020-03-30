import pkgutil
import argparse
import yaml
import logging
import os
import logging

from mowgli.configurator.configurator import Configurator
from mowgli.end_to_end import EndToEnd


def process_dataset(dataset, config_file, output_dir, pretrained_model):

    if not config_file:
        config_data=pkgutil.get_data('mowgli', 'cfg/default.yaml').decode()
    else:
        config_data=open(config_file)

    config = yaml.load(config_data)
    logging.debug("Using configuration: {}".format(config))
    configurator = Configurator(config)

    logging.debug("Processing dataset: {}".format(dataset))

    predictor = configurator.get_component("predictor")

    os.makedirs(output_dir, exist_ok = True)
    
    etoe = EndToEnd(predictor)

    # LOAD DATASET PARTITIONS
    input_dir='data/%s' % dataset
    dataset = etoe.load_dataset(input_dir, dataset, int(
        config['datarows']) if 'datarows' in config.keys() else None)

    logging.debug("dataset loaded")
    logging.debug('Preprocessing the dataset')
    dataset = etoe.preprocess_dataset(dataset)
    
    train_data = etoe.get_data_partition(dataset, 'train')
    logging.debug("Training examples: %d" % len(train_data))

    dev_data = etoe.get_data_partition(dataset, 'dev')
    logging.debug("Dev examples: %d" % len(dev_data))

    test_data = etoe.get_data_partition(dataset, 'test')
    if test_data and len(test_data):
        logging.debug("Test examples: %d" % len(test_data))

    # Train your model, or load a pretrained one
    if pretrained_model:
        logging.debug('Pretrained model specified. Loading: %s ...')
        model = etoe.load_pretrained_model(pretrained_model)
    else:
        logging.debug('No pretrained model specified. Training a new model...')
        model = etoe.train_model(train_data, dev_data, 'data/conceptnet/graph.gt')

    # Make predictions on train, dev and test data
    if config['evaluate_training']:
        train_predictions = etoe.predict(
            model, dataset, config['store_predictions'], output_dir, 'train')
        train_acc = etoe.evaluate(train_data, train_predictions)
        logging.debug('Training accuracy: %f' % train_acc)

    dev_predictions = etoe.predict(
        model, dataset, config['store_predictions'], output_dir, 'dev')
    dev_acc = etoe.evaluate(dev_data, dev_predictions)
    logging.debug('Dev set accuracy: %f' % dev_acc)

    if len(test_data):
        test_predictions = etoe.predict(
            model, dataset, True, output_dir, 'test')

    print('done!')

    return None


def main(args):

    logging.basicConfig(level=logging.DEBUG)

    process_dataset(dataset=args.dataset, config_file=args.config,
                    output_dir=args.output, pretrained_model=args.pretrained)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process a machine commonsense dataset')
    parser.add_argument("--dataset", default="alphanli",
                        help="Dataset to process")
    parser.add_argument("--config", default="",
                        help="config file to load")
    # Default is current directory
    parser.add_argument("--output", default="./",
                        help="Output directory for all output files")
    parser.add_argument("--pretrained", default=None,
                        help="(Optional) Predict using a pretrained model")

    args = parser.parse_args()

    main(args)
