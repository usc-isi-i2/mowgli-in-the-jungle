import json
import logging
import sys
from typing import List

import IPython
import hydra
from omegaconf import DictConfig


sys.path.append('../')


from mowgli.predictor.BaseLMPredictor import BaseLMPredictor
from mowgli.predictor.example_predictor import ExamplePredictor as SamplePredictor
# from mowgli.end_to_end import EndToEnd
from mowgli.configurator.configurator import Configurator
import mowgli.classes as classes
import mowgli.parser_config as config
# import mowgli.utils.general as utils


logger = logging.getLogger(__name__)


@hydra.main(config_path="../mowgli/cfg/default.yaml")
def main(config: DictConfig):
    logger.debug("Using configuration: {}".format(config))
    configurator = Configurator(config)

    dataname = config['dataset']
    output_dir = config['outdir']

    logger.debug("Processing dataset: {}".format(dataname))

    predictor = BaseLMPredictor()

    # etoe = EndToEnd(predictor)

    # LOAD DATASET PARTITIONS
    dataset = prepare_physicaliqa()
    logger.debug("dataset loaded")
    # IPython.embed()

    if hasattr(predictor, 'train'):
        predictor.train(config)

    if hasattr(predictor, 'tune'):
        predictor.tune(dataset=dataset, config=config)

    predictor.predict(model=None, dataset=dataset, config=config, partition='test')
    logger.debug('Preprocessing the dataset')
    IPython.embed()


def prepare_physicaliqa(inputdir='/nas/home/qasemi/mowgli-in-the-jungle/mowgli/data/physicaliqa-train-dev',
                        dataname='physicaliqa', max_rows=None):
    config_data = config.cfg['physicaliqa']

    dataset = classes.Dataset(dataname)

    offset = config_data['answer_offset']
    # IPython.embed()
    for split in config.parts:
        input_file = '%s/%s' % (inputdir, config_data[f'{split}_input_file'])
        labels_file = '%s/%s' % (inputdir, config_data[f'{split}_labels_file'])
        labels = load_predictions(labels_file)

        with open(input_file) as fp:
            rows = fp.readlines()

        for index, l in enumerate(rows):
            if l:
                if max_rows and index >= max_rows: break
                item = json.loads(l)
                split_data = getattr(dataset, split)
                an_entry = classes.Entry(
                    split=split,
                    id='{}-{}'.format(split, item['id']),
                    context=item['goal'],
                    question='',
                    answers=combine_piqa_answers(item, offset),
                    correct_answer=None if split == 'test' else str(labels[index])
                )
                split_data.append(an_entry)
    return dataset


def combine_piqa_answers(item, offset):
    choice1 = classes.Choice(text=item['sol1'],
                             label=str(offset))
    choice2 = classes.Choice(text=item['sol2'],
                             label=str(1 + offset))
    return [choice1, choice2]


def load_predictions(input_file: str) -> List[str]:
    lines = []
    with open(input_file) as fp:
        rows = fp.readlines()
    for l in rows:
        lines.append(str(l).strip())
    return lines


if __name__ == "__main__":
    main()
