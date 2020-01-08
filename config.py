# General
bin_dir="bin"

cfg={}

# Hellaswag
cfg['hellaswag'] = {
            "dataname": "hellaswag",
            "input_data_loc": "data/hellaswag-train-dev",
            "train_input_file": "train.jsonl",
            "train_labels_file": "train-labels.lst",
            "dev_input_file": "valid.jsonl",
            "dev_labels_file": "valid-labels.lst",
            "answer_offset": 0
            }

# PhysicalIQA
cfg['physicaliqa'] = {
            "dataname": "physicaliqa",
            "input_data_loc": "data/physicaliqa-train-dev",
            "train_input_file": "train.jsonl",
            "train_labels_file": "train-labels.lst",
            "dev_input_file": "dev.jsonl",
            "dev_labels_file": "dev-labels.lst",
            "answer_offset": 0
            }

# SocialIQA
cfg['socialiqa'] = {
            "dataname": "socialiqa",
            "input_data_loc": "data/socialiqa-train-dev",
            "train_input_file": "train.jsonl",
            "train_labels_file": "train-labels.lst",
            "dev_input_file": "dev.jsonl",
            "dev_labels_file": "dev-labels.lst",
            "answer_offset": 1
            }

