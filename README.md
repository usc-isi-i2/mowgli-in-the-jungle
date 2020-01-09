# mowgli-dev-framework
Framework for development of solutions on the Machine commonsense development data.

Currently it supports `hellaswag`, `physicaliqa`, `socialiqa`. `anli` is now being implemented.

### Directory structure

**Important files**:
* `classes.py` describes two classes: `Dataset` and `Entry`. A dataset has a name and three attributes for the data partitions: `train`, `dev` and `test`. Each of these partition objects are arrays of entries. An `Entry` is described with the following attributes: `split`, `id`, `question`, `answers`, `correct_answers`, and `metadata`. We use this structure to unify the different terminology used in different datasets. See below for a description of what is a `question` in each of the datasets.
* `baseline.py` shows how we can run a system on any of the datasets. The provided baseline generates a random answer number between `0` and `len(answers)-1`. At the end of this script we also perform evaluation in terms of accuracy. It is probably a good starting point to make a copy of this script and work on the `make_predictions` function, which is essentially the only thing that needs to be changed here.
* `utils.py` contains useful functions that are used by other scripts. Currently, it only contains two evaluation-supporting functions.

**Folders**:

* The data can be found in the folder `bin`. This folder contains one file per dataset, with all entries for both the train and the dev partitions. Namely, each file is structured as a single Python object following the `classes.py` specification for a `Dataset`.
* The example baseline outputs a list of labels in the `output` folder. The destination folder can easily be modified by changing the value of the `outdir` variable in the baseline script.

**Other relevant files/folders:**
* `inspect_data.py` computes some general statistics about each of the datasets based on their `.bin` form. This can give you an idea of the amount of possible answers, or average length of the question.
* the folder `evaluation` has a python and a shell script that perform independent evaluation. These scripts can be adapted to perform multi-dataset evaluation in a single run.

### What is a question and what is an answer?

Even though we make efforts to unify the formats across datasets, make sure you understand what each field means in the context of the dataset you are working on. The main variation between datasets is found in the kind of information given in the question. Here is a specification of what is given within the question list of each of our 4 supported datasets:

|   question  |            element 0            |       element 1      |     element 2     |
|:-----------:|:-------------------------------:|:--------------------:|:-----------------:|
|     aNLI    |       observation 1 (obs1)      | observation 2 (obs2) |         /         |
|  HellaSWAG  | activity label (activity_label) |  context a  (ctx_a)  | context b (ctx_b) |
| PhysicalIQA |               goal              |           /          |         /         |
|  SocialIQA  |             context             |       question       |         /         |

The text in brackets is the original variable in the provided data, in case it is different than the human-readable label. 

**Answers** Compared to the questions, the answers are more uniform across datasets and typically ask for a natural following event given the one described in the question. 

The only exception here is aNLI, where the answer is the middle event between `observation 1` and `observation 2`, i.e., information that fills the gap between the two observations.

### Baseline

The current baseline picks a random number out of the possible answers. Given that the number of possible answers per dataset is between 2 and 4, the baseline accuracy varies between roughly 25 and 50%. Specifically:

|   dataset   | baseline accuracy |
|:-----------:|:-----------------:|
|     aNLI    |        50%        |
|  HellaSWAG  |        25%        |
| PhysicalIQA |        50%        |
|  SocialIQA  |      33.(3)%      |

To run the baseline, use the following command: `python baseline.py --dataset {dataname}`.

### Notes

* As mentioned above, developing your own solution should require *only* a modification of the `make_predictions()` function in `baseline.py`. Let me (Filip) know if you find that not to be the case.
* See `output/` for example predictions by a system.
* Make sure you review the metadata: for instance, the `split_type` stored for Hellaswag can be valuable, as it indicates whether the question is in- or out-of-domain.
* You might notice that the zeroth possible answer for the questions in the socialIQA dataset is an empty string. The reason for this is that the social IQA dataset labels are originally one-padded. This is already taken care of - you should be fine as long as your ssystem does not favor empty answers, but be careful when submitting an official system entry.
* The `.bin` data files should contain everything that is given in the original data. 

#### Additional info (skip): Extraction procedure

The extraction was performed using the scripts in `parsers` based on the data in `data`. You don't need to worry about this process. If you do, it consists of the following rough steps:
1. `wget` or manually download all Darpa datasets, and unzip them into subfolders of `data`.
2. run `parsers/prepare_*.py` to create python objects for all datasets in the `bin` folder. The objects follow the schema from `classes.py` and the parsers use the configuration specified in `config.py`.
