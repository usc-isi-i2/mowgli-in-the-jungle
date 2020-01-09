import numpy as np
import os
import json
import pickle
import sys

sys.path.append("../")
import classes
import config
import utils

def combine_answers(item, offset):
    return ['']*offset + [item['hyp1'], item['hyp2']]

if __name__ == '__main__':

    config_data=config.cfg['anli']

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
                    id='{}-{}'.format(split, item["story_id"]),
                    question=[item['obs1'], item['obs2']],
                    answers=combine_answers(item, offset),
                    correct_answer=None if split == 'test' else labels[index]
                )
                split_data.append(an_entry)

    with open(binfile, 'wb') as w:
        pickle.dump(dataset, w)
