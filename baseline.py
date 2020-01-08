import pickle
import random
import os
import argparse

import classes

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Make baseline predictions')
    # Required Parameters
    parser.add_argument('--dataset', type=str, help='Name of the dataset', default=None)

    args = parser.parse_args()
    dataname=args.dataset

    data_bin=f"bin/{dataname}.bin"

    with open(data_bin, 'rb') as d:
        data=pickle.load(d)

    for split in ['train', 'dev']:
        preds_file=f'output/{dataname}/{split}.lst'
        if os.path.isfile(preds_file):
            os.remove(preds_file)
        with open(preds_file, "a") as myfile:
            entries=getattr(data, split)
            for entry in entries:
                answers=entry.answers
                answer=str(random.randint(0,len(answers)-1))
                myfile.write(answer + '\n')
