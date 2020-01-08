# coding=utf-8
# Copyright 2018 The Google AI Language Team Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""BERT finetuning runner."""

import classes
import numpy as np
import os
import json
import pandas as pd
import pickle

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
        return []
    else:
        return [item['ctx_b']]

# Load dataset examples
dataname='hellaswag'
dataset=classes.Dataset(dataname)
binfile='bin/hellaswag.bin'

parts=['train', 'dev']

for split in parts:
    if split=='dev':
        filename=f'data/hellaswag/hellaswag-train-dev/valid.jsonl'
    else:
        filename=f'data/hellaswag/hellaswag-train-dev/{split}.jsonl'
    with open(filename, 'r') as f:
        for l in f:
            item = json.loads(l)
            split_data=getattr(dataset, split)
            print(l)
            an_entry=classes.Entry(
                split=split,
                id='{}-{}'.format(split, item['ind']),
                intro=_part_a(item),
                question=_part_bs(item),
                answers=item['ending_options'],
                correct_answer=None, # if split == 'test' else item['label'],
                metadata={'activity_label': item['activity_label'], 'dataset': item['dataset'], 'split_type': item['split_type']}
            )
            split_data.append(an_entry)

with open(binfile, 'wb') as w:
    pickle.dump(dataset, w)
