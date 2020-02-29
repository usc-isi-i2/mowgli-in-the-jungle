#! /bin/bash
#dataset="socialiqa-train-dev"
dataset="physicaliqa-train-dev"
config=''


python -m mowgli --dataset $dataset --output output/ 
