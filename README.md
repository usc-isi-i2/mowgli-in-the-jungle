# mowgli-dev-framework
Framework for development of solutions on the Machine commonsense development data.

Currently it supports `alphanli`, `hellaswag`, `physicaliqa`, `socialiqa`.

### Procedure
1. `wget` or manually download all Darpa datasets, and unzip them into subfolders of `data`.
2. run `parsers/prepare_*.py` to create python objects for all 4 datasets in the `bin` folder. The objects follow the schema from `classes.py` and the parsers use the configuration specified in `config.py`.
3. run `baseline.py --dataset {DATASET_NAME}` to produce random system predictions for each dataset in the `output` folder. After processing all documents for a partition, the baseline is also evaluated against the gold labels.
4. One can also run `eval.py` separatelly to score a system on a dataset.
