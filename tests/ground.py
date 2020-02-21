import sys
sys.path.append('../')

import utils.grounding.uci_utils as grounding

sentences=["When boiling butter, when it's ready, you can Pour it onto a plate"]
#sentences=['Chad went to get the wheel alignment measured on his car.']
import os
filename = '/nas/home/ilievski/mowgli-in-the-jungle/numberbatch-en-19.08.txt'
print(grounding.ground_dataset(sentences, embedding_file=filename))
