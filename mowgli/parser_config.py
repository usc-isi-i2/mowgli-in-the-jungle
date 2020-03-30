# General
data_dir="../data"

parts=['train', 'dev']
cfg={}

# Hellaswag
cfg['hellaswag'] = {
            "dataname": "hellaswag",
            "train_input_file": "train.jsonl",
            "train_labels_file": "train-labels.lst",
            "dev_input_file": "valid.jsonl",
            "dev_labels_file": "valid-labels.lst",
            "answer_offset": 0
            }

# PhysicalIQA
cfg['physicaliqa'] = {
            "dataname": "physicaliqa",
            "train_input_file": "train.jsonl",
            "train_labels_file": "train-labels.lst",
            "dev_input_file": "dev.jsonl",
            "dev_labels_file": "dev-labels.lst",
            "answer_offset": 0
            }

# SocialIQA
cfg['socialiqa'] = {
            "dataname": "socialiqa",
            "train_input_file": "train.jsonl",
            "train_labels_file": "train-labels.lst",
            "dev_input_file": "dev.jsonl",
            "dev_labels_file": "dev-labels.lst",
            "answer_offset": 1
            }

cfg['anli'] = {
            "dataname": "anli",
            "train_input_file": "train.jsonl",
            "train_labels_file": "train-labels.lst",
            "dev_input_file": "dev.jsonl",
            "dev_labels_file": "dev-labels.lst",
            "answer_offset": 1
        }

cfg['se2018t11'] = {
            "dataname": "se2018t11",
            "train_input_file": "train_data.json",
            "dev_input_file": "dev_data.json",
            "test_input_file": "test_data.json",
            "trial_input_file": "trial_data.json",
            "answer_offset": 0,
            "parts": ['trial', 'train', 'dev', 'test']
        }

# CommonsenseQA
cfg['csqa'] = {
            "dataname": "csqa",
            "train_input_file": "train_cs.jsonl",
            "dev_input_file": "dev_cs.jsonl",
            "answer_offset": 0
            }
