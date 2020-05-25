import sys
sys.path.append('..')
from mowgli.grounding import uci_utils as grounding

sentences=["When boiling butter, when it's ready, you can Pour it onto a plate"]
emb_filename='../numberbatch-en-19.08.txt'
print(grounding.ground_dataset(sentences, embedding_file=emb_filename))




