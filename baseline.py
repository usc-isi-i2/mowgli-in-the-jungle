import pickle
import random
import os

import classes

data_bin="bin/hellaswag.bin"

with open(data_bin, 'rb') as d:
    data=pickle.load(d)

dataname='hellaswag'

for split in ['train', 'dev']:
    preds_file=f'output/{dataname}/{split}.lst'
    os.remove(preds_file)
    with open(preds_file, "a") as myfile:
        entries=getattr(data, split)
        for entry in entries:
            answers=entry.answers
            answer=str(random.randint(0,len(answers)-1))
            myfile.write(answer + '\n')
