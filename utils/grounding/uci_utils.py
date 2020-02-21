import sys
sys.path.append('../../mowgli-uci')
sys.path.append('../mowgli-uci')
sys.path.append('mowgli-uci')

import graphify
import link

def generate_instances(l):
	for graph in l:
		yield graph

def ground_dataset(sentences, embedding_file):
    graphs=graphify.graphify_dataset(sentences)
    print('GRAPHIFY', graphs)
    linked_graphs=link.link(generate_instances(graphs), embedding_file=embedding_file)
    print('LINKIFY', linked_graphs)
    return linked_graphs
