#! /bin/bash
dataset="socialiqa-train-dev"
config="default.yaml"

CUDA_VISIBLE_DEVICES="" python main.py --input data/$dataset --config cfg/$config --output output/ 
