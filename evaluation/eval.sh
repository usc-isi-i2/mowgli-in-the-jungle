#!/bin/sh

dataname='hellaswag'
part='tune'

labels_file="raw/hellaswag-tune-dev/${part}-labels.lst"
preds_file="output/${dataname}/${part}.lst"

python eval.py --labels_file $labels_file --preds_file $preds_file 
