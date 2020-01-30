# mowgli-in-the-jungle framework
The `mowgli-in-the-jungle` framework facilitates the development of solutions on the DARPA Machine commonsense development datasets within the Mowgli project.

Currently it supports the following datasets: `anli`, `hellaswag`, `physicaliqa`, and `socialiqa`.

## I. Data and code

### Ia. Data

* The data can be found in the folder `data`. This folder contains one folder per dataset, with all entries for both the train and the dev partitions (no test data is provided for the DARPA datasets). 
All files that belong to a dataset are parsed together as a single Python object that follows the `classes.py` specification for a `Dataset`. 
* `classes.py` describes two classes: `Dataset` and `Entry`.
  * A `Dataset` has a `name` and three attributes for the data partitions: `train`, `dev`, and `test`. Each of these partition objects are lists of "entries".
  * An `Entry` is described with the following attributes: `split`, `id`, `question`, `answers`, `correct_answer`, and `metadata`.
  We use this structure to unify the different terminology used in different datasets. See below for a description of what is a `question` and an `answer` in each of the datasets.

### Ib. Code components

A prediction system on one of the datasets is based on the following files:
* `main.py` is the executable script that runs the system. It accepts the following command-line arguments: `input` (input directory), `config` (config file in YAML), `output` (location for storing of the produced predictions), and `pretrained` (an optional argument pointing to a location of a pretrained model, to skip retraining). An example configuration file can be found in `cfg/` and example outputs can be found in the `output/` folder. The configuration is loaded with help of a `configurator` code.
* `end_to_end.py` contains an `EndToEnd` class with a number of standard data science functions (loading of data, training a model, applying a model to make predictions, evaluating those predictions).
* `predictor/predictor.py` contains an abstract base class called `Predictor`, which should be extended in order to create an actual prediction system. This class defines three functions: `preprocess`, `train` and `predict`. In the subdirectory `example_predictor`, there is an `ExamplePredictor` class within `example_predictor.py` which shows how can we implement these functions for a random baseline.

## II. Prepare your environment

* `pip install -r requirements.txt` 
* `conda install -c conda-forge graph-tool`

If you experience issues, let me know.

## III. Developing a system

### IIIa. How to create a new system?

Creating a new system essentially requires three steps:
1. Create a new class in `predictor/` that extends the `Predictor` abstract base class (following the `ExamplePredictor` code). Essentially, you need to implement the three methods: `preprocess`, `train` and `predict`, or a subset of them. Note that you should be able to add any parameters to these functions (if this fails, open an issue and we will fix it). Please use separate repositories for development of your system. 
2. Update/create the config file in `cfg/` to point to your new class and to the dataset you are working on.
3. See the script `run_model.sh` for an example on how to run the example predictor over ANLI. If needed, update the `run_model.sh` script to use the right input/output directories and config file.

### IIIb. Utility functions

To help us easily build systems, reuse code, and avoid bugs, we are working on a base of utility functions. The list of utility functions that we are intending to build is kept in [UTILS.md](UTILS.md).

The functions can be found in the `utils/` folder. Overview of the functions implemented so far:
* `general.py` contains useful functions that are used by other scripts for evaluation or loading/storing predictions.
* `gt/` contains functions useful for the `graph-tool` library.

### IIIc. Submitting to the leaderboard

**Step 1: registration** Before submitting to the leaderboard, you need to contact AI2 (leaderboard@allenai.org) and ask for submission access.

**Step 2: creating a Docker image** 
* Make sure you have Docker installed on your machine
* all dependencies and prerequisites for your code should be placed in `docker/Dockerfile` (feel free to create a new customized `Dockerfile`).
* create a docker image by running:

  `docker build -t ${IMAGE_NAME} -f docker/Dockerfile .`

This will create a docker image with a name ${IMAGE_NAME} for you, based on the configuration in `docker/Dockerfile`. 

**Step 3: create a Beaker image** To create a Beaker image, follow these steps:
* [Sign up](https://beaker.org/) with Beaker
* [Install the beaker CLI](https://github.com/allenai/beaker/blob/master/README.md) on your machine.
* Create a Beaker image:

  `beaker image create --name ${NAMEYOURMODEL} ${USERNAM}/${REPO}:${TAG}`

**Step 4: upload to the leaderboard** Use your Beaker image to [create a submission](https://leaderboard.allenai.org/socialiqa/submission/create) on the official leaderboard.

## IV. Additional information

### IVa. What is a question and what is an answer?

Even though we make efforts to unify the formats across datasets, please make sure you understand what each field means in the context of the dataset you are working on. The main variation between the datasets is found in the kind of information given in the question. Here is a specification of what is given within the question of each of our 4 supported datasets (the elements 0, 1, and 2 constitute the `question` list):

|   question  |            element 0            |       element 1      |     element 2     |
|:-----------:|:-------------------------------:|:--------------------:|:-----------------:|
|     aNLI    |       observation 1 (obs1)      | observation 2 (obs2) |         /         |
|  HellaSWAG  | activity label (activity_label) |  context a  (ctx_a)  | context b (ctx_b) |
| PhysicalIQA |               goal              |           /          |         /         |
|  SocialIQA  |             context             |       question       |         /         |

The text in brackets is the original variable in the provided data, in case it is different than the human-readable label. 

For more (complementary) information, please consult the original dataset websites on [the AI2 leaderboard](https://leaderboard.allenai.org/).

**Answers** Compared to the questions, the answers are more uniform across datasets and typically ask for a natural following event given the one described in the question. 

The only exception here is aNLI, where the answer is the middle event between `observation 1` and `observation 2`, i.e., information that fills the gap between the two observations.

### IVb. `ExamplePredictor` random baseline performance

The current baseline picks an answer randomly out of the set of possible answers. Given that the number of possible answers per dataset is between 2 and 4, the baseline accuracy varies between roughly 25 and 50%. Specifically:

|   dataset   | baseline accuracy |
|:-----------:|:-----------------:|
|     aNLI    |        50%        |
|  HellaSWAG  |        25%        |
| PhysicalIQA |        50%        |
|  SocialIQA  |      33.(3)%      |

### IVc. Notes and suggestions

* Make sure you review the metadata: for instance, the `split_type` stored for Hellaswag can be valuable, as it indicates whether the question is in- or out-of-domain.
* You might notice that the zeroth possible answer for the questions in the socialIQA dataset is an empty string. The reason for this is that the social IQA dataset labels are originally one-padded. This is already taken care of - you should be fine as long as your ssystem does not favor empty answers, but be careful when submitting an official system entry.
* the folder `evaluation` has a python and a shell script that perform dedicated evaluation outside of the system script. These scripts can be useful to perform multi-dataset evaluation in a single run.

## V. Contact

Filip Ilievski (ilievski@isi.edu)
