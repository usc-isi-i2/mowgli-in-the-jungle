import json
import logging
import sys
import pathlib
from typing import List
import pdb
import IPython
import hydra
from omegaconf import DictConfig
import pprint


sys.path.append('../')

from mowgli.grounding.INK_Lab.KagNetGrounding import KagNetGrounding

vocab_path = pathlib.Path('/nas/home/qasemi/mowgli-in-the-jungle/mowgli/grounding/INK_Lab/ConceptVocab.txt')
patter_path = pathlib.Path('/nas/home/qasemi/mowgli-in-the-jungle/mowgli/grounding/INK_Lab/matcher_patterns.json')

grd = KagNetGrounding(vocab_path=vocab_path, patterns_path=patter_path)

sentences = [
    'someone can be at catch',
    'pen is about the same size as pencil',
    'ninja can be defined as awesome',
    'food is for hunger',
    'money is for needs',
    'Time is a circle',
    'Maratrea is made of souls',
    'Souls can merge.',
    'Souls can divide.',
]

# out = grd.ground_corpus_test(sentences)
# pprint.pprint(out)

out = grd.ground_corpus(sentences, n_jobs=2)
pprint.pprint(out)
