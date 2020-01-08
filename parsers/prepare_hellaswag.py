import numpy as np
import os
import json
import pandas as pd
import pickle
import sys
sys.path.append("../")

import classes
import config
import utils

def _part_a(item):
    if 'ctx_a' not in item:
        return item['ctx']
    if 'ctx' not in item:
        return item['ctx_a']
    if len(item['ctx']) == len(item['ctx_a']):
        return item['ctx']
    return item['ctx_a']

def _part_bs(item):
    if ('ctx_b' not in item) or len(item['ctx_b']) == 0:
        return ''
    else:
        return item['ctx_b']

if __name__ == '__main__':

    config_data=config.cfg['hellaswag']

    # Load dataset examples
    dataname=config_data['dataname']

    bindir=config.bin_dir
    inputdir=config_data['input_data_loc']

    binfile=f'{bindir}/{dataname}.bin'

    dataset=classes.Dataset(dataname)

    parts=['train', 'dev']

    offset=config_data['answer_offset']

    for split in parts:
        input_file='%s/%s' % (inputdir, config_data[f'{split}_input_file'])
        labels_file='%s/%s' % (inputdir, config_data[f'{split}_labels_file'])
        labels=utils.load_predictions(labels_file)

        with open(input_file, 'r') as f:
            for index, l in enumerate(f):
                item = json.loads(l)
                split_data=getattr(dataset, split)
                print(l)
                an_entry=classes.Entry(
                    split=split,
                    id='{}-{}'.format(split, item['ind']),
                    intro=_part_a(item),
                    question=_part_bs(item),
                    answers=['']*offset + item['ending_options'],
                    correct_answer=None if split == 'test' else labels[index],
                    metadata={'activity_label': item['activity_label'], 'dataset': item['dataset'], 'split_type': item['split_type']}
                )
                split_data.append(an_entry)

    with open(binfile, 'wb') as w:
        pickle.dump(dataset, w)
