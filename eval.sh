#!/bin/sh

dataname='hellaswag'
part='train'

metrics_file="output/${dataname}/metrics_${part}.json"
labels_file="data/${dataname}/hellaswag-train-dev/${part}-labels.lst"
preds_file="output/${dataname}/${part}.lst"

python eval.py --labels_file $labels_file --preds_file $preds_file --metrics_output_file $metrics_file
cat $metrics_file
