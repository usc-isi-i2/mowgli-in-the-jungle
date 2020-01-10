#!/bin/sh

dataname='hellaswag'
part='train'

labels_file="raw/hellaswag-train-dev/${part}-labels.lst"
preds_file="output/${dataname}/${part}.lst"

python eval.py --labels_file $labels_file --preds_file $preds_file 
