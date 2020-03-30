#! /bin/bash
#dataset="socialiqa-train-dev"
#dataset="physicaliqa-train-dev"
dataset="se2018t11"
config=''


python -m mowgli --dataset $dataset --output output/ 
