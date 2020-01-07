# mowgli-dev-framework
Framework for development of solutions on the Machine commonsense development data.

Currently it supports `alphanli`, `hellaswag`, `physicaliqa`, `socialiqa`.

### Procedure
1. `wget`/download all Darpa datasets, and unzip them into the following subfolders of `data`: `alphanli`, `hellaswag`, `physicaliqa`, `socialiqa`.
2. run `prepare.py` to create python objects for all 4 datasets in the `bin` folder. The objects follow the schema from `classes.py`.
3. run `baseline.py` to produce system scores for a dataset in the `output` folder.
4. run `evaluate.py` to score your system on a dataset.
