import pickle
import random
import os
import argparse

import classes
import utils

def make_prediction(question, answers):
    answer=random.randint(0,len(answers)-1)
    while answers[answer]=='':
        answer=random.randint(0,len(answers)-1)
    return answer

def main(args):
    # Prepare directories
    dataname=args.dataset
    if not dataname:
        print("Print enter a dataset")
        return
    data_bin=f"bin/{dataname}.bin"
    with open(data_bin, 'rb') as d:
        data=pickle.load(d)
    outdir='output'


    # Make predictions on all partitions and store them as a list file
    for split in ['train', 'dev']:
        preds_file=f'{outdir}/{dataname}/{split}.lst'
        if os.path.isfile(preds_file):
            os.remove(preds_file)

        labels=[]
        with open(preds_file, "a") as myfile:
            entries=getattr(data, split)
            for entry in entries:
                answer=make_prediction(entry.question, entry.answers)
                myfile.write(str(answer) + '\n')
                labels.append(entry.correct_answer)

        # Perform evaluation
        system_preds=utils.load_predictions(preds_file)
        acc=utils.compute_accuracy(labels, system_preds)
        print(f"Acc on {split}: {acc}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Make baseline predictions')
    # Required Parameters
    parser.add_argument('--dataset', type=str, help='Name of the dataset', default=None)

    args = parser.parse_args()
    main(args)
    
