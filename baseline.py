import pickle
import random
import os
import argparse

import classes
import utils
import config

def main(args):
    dataname=args.dataset

    if not dataname:
        print("Print enter a dataset")
        return
    data_bin=f"bin/{dataname}.bin"

    with open(data_bin, 'rb') as d:
        data=pickle.load(d)

    cfg=config.cfg[dataname]

    offset=cfg['answer_offset']

    # Make predictions on all partitions and store them as a list file
    for split in ['train', 'dev']:
        preds_file=f'output/{dataname}/{split}.lst'
        if os.path.isfile(preds_file):
            os.remove(preds_file)
        with open(preds_file, "a") as myfile:
            entries=getattr(data, split)
            for entry in entries:
                answers=entry.answers
                answer=str(random.randint(0,len(answers)-1) + offset)
                myfile.write(answer + '\n')

        # Perform evaluation
        gold_file='%s/%s' % (cfg["input_data_loc"], cfg[split + "_labels_file"])
        gold_preds=utils.load_predictions(gold_file)
        system_preds=utils.load_predictions(preds_file)
        acc=utils.compute_accuracy(gold_preds, system_preds)
        print(f"Acc on {split}: {acc}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Make baseline predictions')
    # Required Parameters
    parser.add_argument('--dataset', type=str, help='Name of the dataset', default=None)

    args = parser.parse_args()
    main(args)
    
