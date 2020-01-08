# mowgli-dev-framework
Framework for development of solutions on the Machine commonsense development data.

Currently it supports `hellaswag`, `physicaliqa`, `socialiqa`. `anli` is now being implemented.

### Directory structure

The important files are the following:
* `classes.py` describes two classes: `Dataset` and `Entry`. A dataset has a name and three attributes for the data partitions: `train`, `dev` and `test`. Each of these partition objects are arrays of entries. An entry is described with the following attributes: `split`, `id`, `question`, `answers`, `intro`, `correct_answers`, `metadata`. We use this structure to unify the different terminology used in different datasets. Usually, the question is preceded by some introductory/contextual information. It is probably a good idea to consider these two together in some way.
* `baseline.py` shows how we can run a system on any of the datasets. This baseline generates a random answer number between 0 and len(answers)-1. It is probably a good starting point to make a copy of this script and work on the `make_predictions` function, which is essentially the only thing that needs to be changed here. At the end of this script we also perform evaluation in terms of accuracy.
* `utils.py` contains useful functions that are used by other code. Currently, it only contains two functions that are used for evaluation.

The data is structured as python objects following the `classes.py` specification. It can be found in `bin`. There is one `bin` file per dataset, which contains both the train and the dev partitions.

The example baseline outputs a list of labels in an `output` folder. This can easily be modified by changing the value of the `outdir` variable in this script.

Other relevant files/folders:
* `inspect_data.py` computes some general statistics about each of the datasets based on their `.bin` form. This can give you an idea of the amount of possible answers, or average length of the question.
* the folder `evaluation` has a python and a shell script that perform independent evaluation. These scripts can be adapted to perform multi-dataset evaluation in a single run.

### Notes

* Even though we make efforts to unify the formats across datasets, make sure you understand what each means in the context of the dataset. For instance, the introductory sentence is crucial in hellaswag as it gives the entire context; in physicalIQA on the other hand, it is empty and the full information (called "goal" is given in the question sentence).
* Make sure you review the metadata: for instance, the "activity_label" stored for Hellaswag can be very valuable.
* The social IQA dataset labels are originally one-padded. For this reason, I have added an empty zero-th possible answer for each entry.
* As mentioned above, developing your own solution should require *only* a modification of the `make_predictions()` function in `baseline.py`. Let me (Filip) know if you find that not to be the case.
* The bin files should contain everything that is given in the original data. 
* The extraction was performed using the scripts in `parsers` based on the data in `data`. You don't need to worry about this process.
* See `output/` for example predictions by a system.


### Additional info (skip): Extraction procedure
1. `wget` or manually download all Darpa datasets, and unzip them into subfolders of `data`.
2. run `parsers/prepare_*.py` to create python objects for all datasets in the `bin` folder. The objects follow the schema from `classes.py` and the parsers use the configuration specified in `config.py`.
