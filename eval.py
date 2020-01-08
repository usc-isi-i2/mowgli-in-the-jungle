""" Downloaded from https://github.com/allenai/mosaic-leaderboard/blob/master/hellaswag/evaluator/eval.py, on 01-07-2020 """

import argparse
import json

import utils

def main(args):
    labels_file = args.labels_file
    preds_file = args.preds_file

    gold_answers = utils.load_predictions(labels_file)
    pred_answers = utils.load_predictions(preds_file)

    acc=utils.compute_accuracy(gold_answers, pred_answers)

    print('Accuracy: %f' % acc) 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Evaluate system predictions')
    # Required Parameters
    parser.add_argument('--labels_file', type=str, help='Location of labels', default=None)
    parser.add_argument('--preds_file', type=str, help='Location of predictions', default=None)

    args = parser.parse_args()
    print('====Input Arguments====')
    print(json.dumps(vars(args), indent=2, sort_keys=True))
    print("=======================")
    main(args)
